from src.api.takeoff.distiller import Distiller
from src.api.takeoff.ims import IMS
from src.api.takeoff.tsc import TSC
from src.config.constants import (
    FLO_SLEEPING_AREAS,
    DEFAULT_WEIGHT,
    MANUAL_SLEEPING_AREAS,
    RETAILERS_WITHOUT_STAGING,
)
from src.utils.addresses import get_addresses_v2
from src.utils.assortment import Product, get_products_for_possible_areas
from src.utils.barcode import weighted_barcode
from src.utils.console_printing import cyan, red, bold
from src.utils.order_timings import order_slot_for_tomorrow, MFCRelativeFutureTime
from typing import Optional


def prepare_picklist_flow_data(
    ims: IMS,
    distiller: Distiller,
    retailer: str,
    num_of_non_weighted_products: int = 0,
    num_of_weighted_products: int = 0,
    user_products: list[Product] = None,
    temp_zone: Optional[list[str]] = None,
    chemical: Optional[list[bool]] = None,
    is_raw: Optional[list[bool]] = None,
    requires_exp: Optional[list[bool]] = None,
) -> tuple:
    if user_products:
        flo_products = [
            p for p in user_products if p.sleeping_area in FLO_SLEEPING_AREAS
        ]
        weighted_products = [p for p in flo_products if p.is_weighted]
        non_weighted_products = [p for p in flo_products if not p.is_weighted]
    else:
        non_weighted_products = []
        if num_of_non_weighted_products > 0:
            non_weighted_products = get_products_for_possible_areas(
                distiller=distiller,
                retailer=retailer,
                possible_areas=FLO_SLEEPING_AREAS,
                required_count=num_of_non_weighted_products,
                is_weighted_options=[False],
                temp_zone=temp_zone,
                chemical=chemical,
                is_raw=is_raw,
                requires_exp=requires_exp,
            )
            print(cyan(f"Picklist non-weighted found: {len(non_weighted_products)}"))
        weighted_products = []
        if num_of_weighted_products > 0:
            weighted_products = get_products_for_possible_areas(
                distiller=distiller,
                retailer=retailer,
                possible_areas=FLO_SLEEPING_AREAS,
                required_count=num_of_weighted_products,
                is_weighted_options=[True],
                temp_zone=temp_zone,
                chemical=chemical,
                is_raw=is_raw,
                requires_exp=requires_exp,
            )
            print(cyan(f"Picklist weighted found: {len(weighted_products)}"))

    # Inserting weight value in weighted product barcodes
    for product in weighted_products:
        product.barcode = weighted_barcode(product.barcode, DEFAULT_WEIGHT)

    # intersection between weighted and non-weighted is impossible
    all_picklist_products = non_weighted_products + weighted_products

    # Look for duplicate ecom_ids at the picklist flow level
    remove_duplicate_ecoms(all_picklist_products, "picklist flow data")

    print(cyan(f"Picklist total found: {len(all_picklist_products)}"))

    if (
        num_of_weighted_products + num_of_non_weighted_products > 0
        and len(all_picklist_products) == 0
    ):
        raise ValueError(
            "Could not find any picklist products when there should have been at least 1."
        )

    dynamic_addresses = get_addresses_v2(
        ims=ims,
        qty_of_addresses=len(weighted_products) + len(non_weighted_products),
        dynamic=True,
    )
    picklist_products_barcodes = [p.barcode for p in all_picklist_products]

    # Will be needed in orderflow for putaway from store
    dynamic_addresses_and_picklist_barcodes = dict(
        zip(dynamic_addresses, picklist_products_barcodes)
    )
    if all_picklist_products:
        ims.zero_stock_for_products_or_addresses(
            [p.tom_id for p in all_picklist_products]
        )

    return (
        all_picklist_products,
        dynamic_addresses,
        dynamic_addresses_and_picklist_barcodes,
    )


def prepare_manual_flow_data(
    ims: IMS,
    distiller: Distiller,
    retailer: str,
    num_of_non_weighted_products: int = 0,
    num_of_weighted_products: int = 0,
    user_products: list[Product] = None,
    temp_zone: Optional[list[str]] = None,
    chemical: Optional[list[bool]] = None,
    is_raw: Optional[list[bool]] = None,
    requires_exp: Optional[list[bool]] = None,
) -> list[Product]:
    if user_products:
        manual = [p for p in user_products if p.sleeping_area in MANUAL_SLEEPING_AREAS]
        non_weighted_products = [p for p in manual if not p.is_weighted]
        weighted_products = [p for p in manual if p.is_weighted]
    else:
        non_weighted_products = []
        if num_of_non_weighted_products > 0:
            non_weighted_products = get_products_for_possible_areas(
                distiller=distiller,
                retailer=retailer,
                possible_areas=MANUAL_SLEEPING_AREAS,
                required_count=num_of_non_weighted_products,
                is_weighted_options=[False],
                temp_zone=temp_zone,
                chemical=chemical,
                is_raw=is_raw,
                requires_exp=requires_exp,
            )
            if len(non_weighted_products) < num_of_non_weighted_products:
                non_weighted_products = get_products_for_possible_areas(
                    distiller=distiller,
                    retailer=retailer,
                    possible_areas=MANUAL_SLEEPING_AREAS,
                    required_count=num_of_non_weighted_products,
                    is_weighted_options=[True],
                    temp_zone=temp_zone,
                    chemical=chemical,
                    is_raw=is_raw,
                    requires_exp=requires_exp,
                )
                print(
                    red(
                        "Could Not find non-weighted manual products, replaced with weighted"
                    )
                )
            print(cyan(f"Manual non-weighted found: {len(non_weighted_products)}"))
        weighted_products = []
        if num_of_weighted_products > 0:
            weighted_products = get_products_for_possible_areas(
                distiller=distiller,
                retailer=retailer,
                possible_areas=MANUAL_SLEEPING_AREAS,
                required_count=num_of_weighted_products,
                is_weighted_options=[True],
                temp_zone=temp_zone,
                chemical=chemical,
                is_raw=is_raw,
                requires_exp=requires_exp,
            )
            print(cyan(f"Manual weighted found: {len(weighted_products)}"))

    # Inserting weight value in weighted product barcodes
    for product in weighted_products:
        product.barcode = weighted_barcode(product.barcode, DEFAULT_WEIGHT)
    # intersection between weighted and non-weighted is impossible
    all_manual_products = weighted_products + non_weighted_products

    # Look for duplicate ecom_ids at the manual flow level
    remove_duplicate_ecoms(all_manual_products, "manual flow data")

    print(cyan(f"Manual total found: {len(all_manual_products)}"))

    if all_manual_products:
        manual_addresses = get_addresses_v2(
            ims=ims,
            qty_of_addresses=len(weighted_products) + len(non_weighted_products),
        )
        manual_tom_ids = [p.tom_id for p in all_manual_products]
        manual_tom_ids_and_addresses = dict(zip(manual_addresses, manual_tom_ids))
        ims.zero_stock_for_products_or_addresses(manual_tom_ids)
        for address, product in manual_tom_ids_and_addresses.items():
            ims.shelf_adjust(address, product, 10, "IB")

    if (
        num_of_weighted_products + num_of_non_weighted_products > 0
        and len(all_manual_products) == 0
    ):
        raise ValueError(
            "Could not find any manual products when there should have been at least 1."
        )
    return all_manual_products


def prepare_osr_flow_data(
    ims: IMS,
    distiller: Distiller,
    retailer: str,
    num_of_products: int = 0,
    user_products: list[Product] = None,
    temp_zone: Optional[list[str]] = None,
    chemical: Optional[list[bool]] = None,
    is_raw: Optional[list[bool]] = None,
    requires_exp: Optional[list[bool]] = None,
):
    if user_products:
        osr_products = [p for p in user_products if p.sleeping_area == "K"]
    else:
        osr_products: list[Product] = []
        num_retries = 0
        while len(osr_products) == 0 and num_retries < 10:
            osr_products = get_products_for_possible_areas(
                distiller=distiller,
                retailer=retailer,
                possible_areas=["K"],
                required_count=num_of_products,
                is_weighted_options=[False],
                temp_zone=temp_zone,
                chemical=chemical,
                is_raw=is_raw,
                requires_exp=requires_exp,
            )
            num_retries += 1
            num_of_products += 1

    print(cyan(f"OSR found: {len(osr_products)}"))

    # Look for duplicate ecom_ids at the osr flow level
    remove_duplicate_ecoms(osr_products, "osr flow data")

    if osr_products:
        osr_tom_ids = [p.tom_id for p in osr_products]
        for product in osr_tom_ids:
            ims.shelf_adjust("01K", product, 10, "IB")

    return osr_products


def prepare_orderflow_data(
    ims: IMS,
    distiller: Distiller,
    tsc: TSC,
    retailer,
    picklist_non_weighted_qty=0,
    picklist_weighted_qty=0,
    osr_products_qty=0,
    manual_non_weighted_qty=0,
    manual_weighted_qty=0,
    user_products: list[Product] = None,
    stage_by_data: MFCRelativeFutureTime = None,
    temp_zone: Optional[list[str]] = None,
    chemical: Optional[list[bool]] = None,
    is_raw: Optional[list[bool]] = None,
    requires_exp: Optional[list[bool]] = None,
) -> dict:
    if temp_zone is None:
        temp_zone = ["ambient", "chilled"]

    if chemical is None:
        chemical = [True, False, None]

    if is_raw is None:
        is_raw = [True, False, None]

    if requires_exp is None:
        requires_exp = [True, False, None]

    # preparing products
    (
        picklist_products,
        dynamic_addresses,
        dynamic_addresses_and_picklist_barcodes,
    ) = prepare_picklist_flow_data(
        ims=ims,
        distiller=distiller,
        retailer=retailer,
        num_of_non_weighted_products=picklist_non_weighted_qty,
        num_of_weighted_products=picklist_weighted_qty,
        user_products=user_products,
        temp_zone=temp_zone,
        chemical=chemical,
        is_raw=is_raw,
        requires_exp=requires_exp,
    )
    osr_products = []
    if osr_products_qty > 0:
        osr_products = prepare_osr_flow_data(
            ims=ims,
            distiller=distiller,
            retailer=retailer,
            num_of_products=osr_products_qty,
            user_products=user_products,
            temp_zone=temp_zone,
            chemical=chemical,
            is_raw=is_raw,
            requires_exp=requires_exp,
        )
    if len(osr_products) != osr_products_qty and len(osr_products) > 0:
        # raise an error only if OSR count is 0 when OSR requested amount
        # should have been greater 0. Allow less
        raise ValueError("No OSR products where found")
    manual_products = prepare_manual_flow_data(
        ims=ims,
        distiller=distiller,
        retailer=retailer,
        num_of_non_weighted_products=manual_non_weighted_qty,
        num_of_weighted_products=manual_weighted_qty,
        user_products=user_products,
        temp_zone=temp_zone,
        chemical=chemical,
        is_raw=is_raw,
        requires_exp=requires_exp,
    )
    all_products = picklist_products + manual_products + osr_products

    # Look for duplicate ecom_ids at the order flow level
    remove_duplicate_ecoms(all_products, "orderflow data")

    # preparing timeslots
    # if we have "stage_by_data" that's configured in conjunction
    # with waveplanner and should be the preferred flow, but not all
    # inputs to this use that yet so we have "temporary" if here
    if stage_by_data:
        order_timeslot = {
            "stage_by_datetime": stage_by_data.timestamp,
            "service_window_start": stage_by_data.timestamp,
            "spoke_id": stage_by_data.location_code_spoke,
            "location-code-retailer": stage_by_data.location_code_retailer,
        }
    else:
        order_timeslot = order_slot_for_tomorrow(tsc)
    print(bold("stage_by_datetime: ") + bold(order_timeslot["stage_by_datetime"]))
    print(
        bold("service_window_start: ")
        + bold(f"{order_timeslot['service_window_start']}\n")
    )

    # all this data is needed for orderflow
    return {
        "picklist_tom_ids": [k for k in picklist_products],
        "picklist_products": picklist_products,
        "dynamic_addresses": dynamic_addresses,
        "dynamic_addresses_and_picklist_barcodes": dynamic_addresses_and_picklist_barcodes,
        "osr_products": osr_products,
        "manual_products": manual_products,
        "all_products": all_products,
        "spoke_id": order_timeslot["spoke_id"],
        "store_id": tsc.get_location_code("location-code-retailer"),
        "service_window_start": order_timeslot["service_window_start"],
        "stage_by_datetime": order_timeslot["stage_by_datetime"],
        "route_id": (
            tsc.get_routes()["routes"][0]["route-code"]
            if retailer not in RETAILERS_WITHOUT_STAGING
            else None
        ),
        "staging_location": (
            tsc.get_default_or_first_staging_location()
            if retailer not in RETAILERS_WITHOUT_STAGING
            else None
        ),
    }


def remove_duplicate_ecoms(products: list[Product], type_of_products):
    ecomIds = []
    for p in products:
        if p.ecom_id in ecomIds:
            products.remove(p)
            print(
                red(
                    f"While preparing {type_of_products} data, product: "
                    f"{p.tom_id}, ecom: {p.ecom_id} was removed from product "
                    "list as it would cause duplicate ecom_id error if used."
                )
            )
        else:
            # add to list
            ecomIds.append(p.ecom_id)
