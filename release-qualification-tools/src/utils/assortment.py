from random import shuffle, sample

from dataclasses import dataclass
from typing import Optional
import exrex

from src.api.takeoff.distiller import Distiller, DistillerProductV6
from src.config.constants import FLO_SLEEPING_AREAS, ALL_SLEEPING_AREAS
from src.utils.console_printing import red, bold, waiting


@dataclass
class Product:
    """Internal representation of 'Product' entity, with only essential data, specific for this project"""

    tom_id: str  # is a main product identifier
    ecom_id: (
        str  # is used for some retailers on retailer-integration layer to place orders
    )
    name: str  # human-readable product name (e.g. 'Diet Mountain Dew 0.9999 oz' etc)
    barcode: (
        str  # used in 'hybrid' scripts to generate barcode and scan it by Android app
    )
    sleeping_area: str  # product attribute
    is_weighted: (
        bool  # sometimes system behaves differently based on this, we need to know it
    )
    is_chemical: bool  # for some test cases with decanting
    is_raw: bool
    requires_exp_date: bool
    unit_of_measure: str  # used for MAF, need to specify this when placing orders
    temp_zone: str


def get_product_from_list_by_tom_id(
    products: list[Product], tom_id: str
) -> Optional[Product]:
    for product in products:
        if product.tom_id == tom_id:
            return product
    print("Couldn't find product with such tom-id, returning None")
    return None


def get_product_from_list_by_attribute(
    products: list[Product],
    chemical=[True, False, None],
    req_exp_date=[True, False, None],
    temp_zones=["ambient", "chilled", "frozen"],
    sleeping_areas=ALL_SLEEPING_AREAS,
    raw=[True, False, None],
) -> list[Product]:
    found = list(
        filter(
            lambda p: p.is_chemical in chemical
            and p.requires_exp_date in req_exp_date
            and p.temp_zone in temp_zones
            and p.sleeping_area in sleeping_areas
            and p.is_raw in raw,
            products,
        )
    )
    return found


def check_if_product_data_is_valid(retailer: str, product: DistillerProductV6) -> bool:
    """
    Function that checks if product JSON, as returned by Distiller,
    has attributes that allow to use it in various testing flows
    """
    if (
        not product.mfc_stop_fulfill
        and (
            # FLO (batch) with 1-letter name ('A', 'K") might have issues with displaying in ISPS
            product.sleeping_area not in FLO_SLEEPING_AREAS
            or len(product.name) > 1
        )
        and (
            # weighted products should have a barcode, where weight value can be inserted:
            # end with 00000X where X is a check digit. See ../api/barcode.py.weighted_barcode
            # to see how weight value is inserted
            not product.is_weight_variable_on_receipt
            or list(filter(lambda b: b[-6:-1] == "00000", product.barcodes))
        )
        and (
            # if "barcodes" are empty list, we don't want to use product
            product.barcodes
        )
        and (product.ecom_ids)
    ):
        return True
    else:
        print(f"Notice: rejecting {product}\n")
        return False


def transform_json_to_product(
    product_json: DistillerProductV6, retailer: str
) -> Product:
    ecom_id = product_json.ecom_ids[0]

    # if weighted product has multiple barcodes, need to pick one where weight can be inserted
    is_weighted = product_json.is_weight_variable_on_receipt or False
    if not is_weighted:
        barcode = product_json.barcodes[0]
    else:
        barcode = list(filter(lambda b: b[-6:-1] == "00000", product_json.barcodes))[0]

    return Product(
        tom_id=product_json.tom_id,
        ecom_id=ecom_id,
        name=product_json.name,
        barcode=barcode,
        sleeping_area=product_json.sleeping_area or "",
        is_weighted=is_weighted,
        is_chemical=product_json.feature_attributes.is_chemical or False,
        temp_zone=product_json.temperature_zone[0],
        unit_of_measure=product_json.retail_item.weight.unit_of_measure.lower(),
        requires_exp_date=product_json.requires_expiration_date,
        is_raw=product_json.feature_attributes.is_raw or False,
    )


def transform_list_of_jsons_to_list_of_products(
    list_of_jsons: list, retailer: str
) -> list[Product]:
    result = []
    for product_json in list_of_jsons:
        product = transform_json_to_product(product_json, retailer)
        result.append(product)
    return result


def get_products(
    distiller: Distiller,
    retailer: str,
    sleeping_area: str,
    num_of_products: int,
    is_weighted: bool,
) -> list[Product]:
    # might call function with 0 products requested
    if not num_of_products:
        return []
    all_products_data = distiller.get_products_for_sleeping_area(
        (sleeping_area,),
        is_weighted,
    )
    shuffle(all_products_data)
    selected: list[Product] = []
    if all_products_data:
        for product_data in all_products_data:
            if len(selected) == num_of_products:
                break
            if check_if_product_data_is_valid(retailer, product_data):
                selected.append(transform_json_to_product(product_data, retailer))
    return selected


def get_products_for_possible_areas(
    distiller: Distiller,
    retailer,
    possible_areas: tuple[str, ...],
    is_weighted_options: list[bool],
    required_count: int = 1,
    temp_zone: Optional[list[str]] = None,
    chemical: Optional[list[bool]] = None,
    is_raw: Optional[list[bool]] = None,
    requires_exp: Optional[list[bool]] = None,
) -> list[Product]:
    """
    Function can be used when you need many products from range of particular sleeping areas,
    but out of those areas, it can be any. For example, to pick products that are eligible
    for picklist (brought from store with ISPS) you  might need products from FLO sleeping
    areas; if you need many of them, it's likely that you won't find enough valid products
    from one area only; it's better to search in multiple
    """
    all_products_found = []
    for area in possible_areas:
        for option in is_weighted_options:
            all_products_found += get_products(
                distiller=distiller,
                retailer=retailer,
                sleeping_area=area,
                num_of_products=100,
                is_weighted=option,
            )

    result: list[Product] = []
    filtered = get_product_from_list_by_attribute(
        products=all_products_found,
        chemical=chemical,
        req_exp_date=requires_exp,
        temp_zones=temp_zone,
        sleeping_areas=possible_areas,
        raw=is_raw,
    )
    try:
        # trying to ensure there's no bias for particular sleeping area - randomly select required number
        result = sample(filtered, required_count)
    except ValueError:
        print(
            red(
                f"WARNING: {len(filtered)} products for areas {possible_areas}, weighted {is_weighted_options} found"
            )
        )
        return filtered

    for p in result:
        print(
            bold(
                f"Selected: {p.tom_id}, ecom: {p.ecom_id}, area: {p.sleeping_area}, weighted: {p.is_weighted}"
            )
        )
    return result


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def find_products_by_criteria(
    distiller: Distiller,
    location_code_retailer,
    retailer: str,
    required_count: int,
    chemical=[True, False, None],
    req_exp_date=[True, False, None],
    temp_zones=["ambient", "chilled", "frozen"],
    sleeping_areas=ALL_SLEEPING_AREAS,
    raw=[True, False, None],
) -> list[Product]:
    # not to do anything at all if 0 is  requested
    if not required_count:
        return []
    print(
        waiting(
            f"\nLooking for {required_count} products from {sleeping_areas}, "
            f"exp-date - {req_exp_date}, chem - {chemical},\n"
            f"temp_zones - {temp_zones}, raw: - {raw}"
        )
    )

    product_ids = distiller.get_product_ids(location_code_retailer)
    shuffle(product_ids)
    print(bold(f"Total: {len(product_ids)} products to check"))
    # splitting huge products-ids list into chunks of 100
    chunks_of_ids = list(chunks(product_ids, 100))
    matching_products = []
    products_checked_count = 0
    for chunk in chunks_of_ids:
        # resetting valid_products so it's not filtered again
        valid_products = []
        # once we found enough valid products, we stop iterating over the chunks
        if len(matching_products) >= required_count:
            break
        # getting product data with attributes for the chunk of 100 ids
        products_data = distiller.get_products_by_tom_ids(chunk)

        for product_json_record in products_data:
            if check_if_product_data_is_valid(retailer, product_json_record):
                # if product is valid, transforming its json to instance of Product to easily filter
                product = transform_json_to_product(product_json_record, retailer)
                valid_products.append(product)

        filtered = get_product_from_list_by_attribute(
            valid_products, chemical, req_exp_date, temp_zones, sleeping_areas, raw
        )
        matching_products += filtered
        products_checked_count += len(valid_products)
        print(
            bold(
                f"Checked {products_checked_count}, found {len(matching_products)} matching..."
            )
        )
    try:
        # trying to ensure there's no bias for particular "chunk" - randomly select required number
        matching_products = sample(matching_products, required_count)
    except ValueError:
        print(red(f"WARNING: {len(matching_products)} matching your criteria found"))
    finally:
        return matching_products


def generate_non_existing_product(distiller: Distiller, location_code_retailer):
    # Generate random product id and compare it with all
    # returned recognized products at the location to make
    # sure that the generated product is unrecognized"""
    item_id = exrex.getone("[0-9]{14}")
    products_ids = distiller.get_product_ids(location_code_retailer)
    while item_id in products_ids:
        item_id = exrex.getone("[0-9]{14}")
    product = Product(
        item_id,
        item_id,
        "non_existing_product",
        "00000000000000",
        "K",
        False,
        False,
        False,
        False,
        "kg",
        "ambient",
    )
    return product


# This method avoids getting double temp_zone items via Distiller v4/qa endpoint
# if you need only chilled or ambient item
def products_by_criteria(
    distiller: Distiller,
    retailer: str,
    required_count: int,
    chemical=[True, False, None],
    req_exp_date=[True, False, None],
    temp_zones=["ambient", "chilled", "frozen"],
    sleeping_areas=ALL_SLEEPING_AREAS,
    raw=[True, False, None],
    is_weighted=[True, False, None],
):
    products_data = distiller.get_products_for_sleeping_area(
        sleeping_areas, is_weighted, temp_zones
    )
    valid_products = []
    matching_products = []
    products_checked_count = 0
    for product_json_record in products_data:
        if check_if_product_data_is_valid(retailer, product_json_record):
            # if product is valid, transforming its json to instance of Product to easily filter
            product = transform_json_to_product(product_json_record, retailer)
            valid_products.append(product)
    filtered = get_product_from_list_by_attribute(
        valid_products, chemical, req_exp_date, temp_zones, sleeping_areas, raw
    )
    matching_products += filtered
    products_checked_count += len(valid_products)
    print(
        bold(
            f"Checked {products_checked_count}, found {len(matching_products)} matching..."
        )
    )
    try:
        # trying to ensure there's no bias for particular "chunk" - randomly select required number
        matching_products = sample(matching_products, required_count)
    except ValueError:
        print(red(f"WARNING: {len(matching_products)} matching your criteria found"))
    finally:
        return matching_products
