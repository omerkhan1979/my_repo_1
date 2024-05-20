from pprint import pprint
from time import time
from typing import Tuple

from src.api.takeoff.ims import IMS
from src.api.takeoff.oms import OMS
from src.api.takeoff.rint import RInt
from src.api.collections import InitializedApis
from src.config.config import Config
from src.utils.addresses import get_addresses_v2
from src.utils.assortment import Product
from src.utils.console_printing import blue, cyan, red, yellow
from src.utils.ims import wait_for_item_adjustment_from_ims
from src.config.constants import FLO_SLEEPING_AREAS
from src.utils.order_timings import MFCRelativeFutureTime

from scripts.steps.orderflow.setup import prepare_orderflow_data


def products_to_lineitems(
    retailer: str,
    products: list[Product],
    line_note="note",
    requested_quanity=3,
) -> list[dict]:
    lineitems = []

    if isinstance(products, list):
        n = 0
        for product in products:
            n += 1
            try:
                lineitem = {
                    "requested-quantity": requested_quanity,
                    "fulfillment-location": "mfc",
                    "ecom-item-id": product.ecom_id,
                    "line-note": line_note,
                    "ecom-line-id": str(n),
                }
                if retailer == "maf":
                    if product.is_weighted:
                        print(f"{product.tom_id} - {product.is_weighted}")
                        lineitem["requested-quantity"] = 1
                        lineitem["requested-unit-of-measure"] = product.unit_of_measure
                        lineitem["requested-weight"] = 1.5

                lineitems.append(lineitem)
            except IndexError:
                print(
                    red(
                        f"Not found product {product} in Distiller! Skipping adding to lineitems"
                    )
                )

    elif isinstance(products, dict):
        n = 0
        for product, quantity in products:
            n += 1
            try:
                lineitem = {
                    "requested-quantity": quantity,
                    "fulfillment-location": "mfc",
                    "ecom-item-id": product.ecom_id,
                    "line-note": "note",
                    "ecom-line-id": str(n),
                }
                if retailer == "abs":
                    lineitem = {
                        "requested-quantity": quantity,
                        "ecom-item-id": product.ecom_id,
                    }
                if retailer == "maf":
                    if product.is_weighted:
                        lineitem["requested-unit-of-measure"] = product.unit_of_measure
                        lineitem["requested-quantity"] = 1
                        lineitem["requested-weight"] = quantity
                lineitems.append(lineitem)
            except IndexError:
                print(
                    red(
                        f"Not found product {product} in Distiller! Skipping adding to lineitems"
                    )
                )

    assert len(lineitems) == len(products), red(
        "Some products lost during lineitems creation"
    )

    return lineitems


def products_to_lineitems_required_field(
    retailer, products: list[Product], weight=None
) -> list[dict]:
    lineitems = []

    if isinstance(products, list):
        n = 0
        for product in products:
            n += 1
            try:
                lineitem = {
                    "requested-quantity": 3,
                    "ecom-item-id": product.ecom_id,
                    "ecom-line-id": str(n),
                }
                if retailer == "maf":
                    if product.is_weighted:
                        print(f"{product.tom_id} - {product.is_weighted}")
                        lineitem["requested-quantity"] = 1
                        lineitem["requested-unit-of-measure"] = product.unit_of_measure
                        lineitem["requested-weight"] = weight

                lineitems.append(lineitem)
            except IndexError:
                print(
                    red(
                        f"Not found product {product} in Distiller! Skipping adding to lineitems"
                    )
                )

    elif isinstance(products, dict):
        n = 0
        for product, quantity in products:
            n += 1
            try:
                lineitem = {
                    "requested-quantity": quantity,
                    "ecom-item-id": product.ecom_id,
                    "ecom-line-id": str(n),
                }
                if retailer == "abs":
                    lineitem = {
                        "requested-quantity": quantity,
                        "ecom-item-id": product.ecom_id,
                    }
                if retailer == "maf":
                    if product.is_weighted:
                        lineitem["requested-unit-of-measure"] = product.unit_of_measure
                        lineitem["requested-quantity"] = 1
                        lineitem["requested-weight"] = quantity
                lineitems.append(lineitem)
            except IndexError:
                print(
                    red(
                        f"Not found product {product} in Distiller! Skipping adding to lineitems"
                    )
                )

    assert len(lineitems) == len(products), red(
        "Some products lost during lineitems creation"
    )

    return lineitems


def place_order(
    rint: RInt,
    retailer: str,
    products: list[Product],
    ims: IMS,
    oms: OMS,
    add_stock_if_needed=True,
    add_flo_stock=True,
    **kwargs,
) -> str:
    if add_stock_if_needed:
        for product in products:
            item = product.tom_id
            current_quantity = 0
            if "K" in product.sleeping_area:
                shelf_state_pre = ims.v2_snapshot(
                    products=[item], addresses=["01K"], include_zeros=True
                )
                for address in shelf_state_pre["addresses"]:
                    if address["address"] == "01K":
                        current_quantity = address["quantity"]
                        break
                # only increase quantity for product if current quantity is less than 10
                if current_quantity >= 10:
                    print(cyan(f"\nQuantity: {current_quantity} for item: {item}"))
                    continue
                time_past = str(int(round(time() * 1000)))

                ims.shelf_adjust("01K", item, 10, "IB")
                adjustments_response = wait_for_item_adjustment_from_ims(
                    ims, time_past, None, rint.config.location_code_tom
                )
                pprint(adjustments_response)
                shelf_state_post = ims.v2_snapshot(
                    products=[item], addresses=["01K"], include_zeros=True
                )
                for address in shelf_state_post["addresses"]:
                    if address["address"] == "01K":
                        quantity_after_increase = address["quantity"]
                    print(blue(f'\nItem "{item}" quantity has increased by 10.'))
                    print(
                        cyan(f"\nQuantity: {quantity_after_increase} for item: {item}")
                    )
                    print(
                        yellow(
                            f"\nNow test is searching the needed pubsub message for the item {item} with quantity after "
                            f"increasing {quantity_after_increase}"
                        )
                    )
            elif product.sleeping_area not in FLO_SLEEPING_AREAS:
                manual_addresses = get_addresses_v2(
                    ims=ims,
                    qty_of_addresses=1,
                )
                manual_tom_ids_and_addresses = dict(
                    zip(manual_addresses, [product.tom_id])
                )
                for address, manual_product in manual_tom_ids_and_addresses.items():
                    ims.shelf_adjust(address, manual_product, 10, "IB")
                    shelf_state_pre = ims.v2_snapshot(
                        products=[item], addresses=[address], include_zeros=True
                    )
                for address in shelf_state_pre["addresses"]:
                    if address["address"] != "01K":
                        current_quantity = address["quantity"]
                        break
                    # only increase quantity for product if current quantity is less than 10
                if current_quantity >= 10:
                    print(
                        cyan(
                            f"\nQuantity: {current_quantity} for item: {item} in sleeping area: {product.sleeping_area}"
                        )
                    )
                    continue
                time_past = str(int(round(time() * 1000)))
                ims.shelf_adjust(product.sleeping_area, item, 10, "IB")
                adjustments_response = wait_for_item_adjustment_from_ims(
                    ims, time_past, None, rint.config.location_code_tom
                )
                pprint(adjustments_response)
                shelf_state_post = ims.v2_snapshot(
                    products=[item],
                    addresses=[product.sleeping_area],
                    include_zeros=True,
                )
                for address in shelf_state_post["addresses"]:
                    if address["address"] == product.sleeping_area:
                        quantity_after_increase = address["quantity"]
                    print(blue(f'\nItem "{item}" quantity has increased by 10.'))
                    print(
                        cyan(
                            f"\nQuantity: {quantity_after_increase} for item: {item} in sleeping area: {product.sleeping_area}"
                        )
                    )
                    print(
                        yellow(
                            f"\nNow test is searching the needed pubsub message for the item {item} with quantity after "
                            f"increasing {quantity_after_increase}"
                        )
                    )
            else:
                # FLO items.. not sure if anything else lands in the bucket
                if product.sleeping_area in FLO_SLEEPING_AREAS and add_flo_stock:
                    adjustment_made = False
                    snapshot_data = [
                        shelf
                        for shelf in ims.shelves_snapshot(
                            rint.config.location_code_tom
                        )["success"]
                        if shelf["product-id"] == product.tom_id
                    ]
                    for address_detail in snapshot_data:
                        if (
                            address_detail["address"] != "01K"
                        ):  # not sure we need this line here, but to be safe...
                            if address_detail["qty-available"] < 10:
                                ims.shelf_adjust(
                                    address_detail["address"], product.tom_id, 10, "IB"
                                )
                                adjustment_made = True
                    if adjustment_made:
                        print(
                            cyan(
                                f"Stock for {product.tom_id} adjusted: {[x for x in ims.shelves_snapshot(rint.config.location_code_tom)['success'] if x['product-id'] == product.tom_id]}"
                            )
                        )

    # added stock (if desired), ready to send order to rint
    if kwargs.keys().__contains__("line_note"):
        line_note = kwargs["line_note"]
    else:
        line_note = "note"
    lineitems = products_to_lineitems(retailer, products, line_note)
    order_id = rint.create_customer_order(lineitems, **kwargs)
    print(
        blue(
            f"Cutoff Time for {order_id} is {oms.get_order(order_id)['response']['cutoff-datetime']}"
        )
    )
    return order_id


def place_order_for_rq_service(
    rint: RInt, retailer, products: list[Product], weight, **kwargs
) -> str:
    lineitems = products_to_lineitems_required_field(retailer, products, weight)
    order_id = rint.create_customer_order(lineitems, **kwargs)

    return order_id


def get_placed_order_details(
    rint: RInt,
    oms: OMS,
    ims: IMS,
    retailer,
    products,
    order_timeslot_and_spoke,
    store_id,
):
    order_id: str = place_order(
        rint=rint,
        retailer=retailer,
        products=products,
        store_id=store_id,
        spoke_id=order_timeslot_and_spoke["spoke_id"],
        stage_by_datetime=order_timeslot_and_spoke["stage_by_datetime"],
        service_window_start=order_timeslot_and_spoke["service_window_start"],
        ims=ims,
        oms=oms,
    )
    order = oms.get_order(order_id)["response"]
    return order_id, order


def prepare_and_place_order(
    cfg: Config,
    apis: InitializedApis,
    mfc_cutoff: MFCRelativeFutureTime,
    flo_items: int = 0,
    flo_weighted_items: int = 0,
    manual_items: int = 0,
    osr_items: int = 0,
    manual_weighted_items: int = 0,
    add_stock_for_flo_items: bool = True,
) -> Tuple[str, str]:
    """Select products and add stock as needed, then place order and return (cutoff time, order_id)"""
    order_flow_data = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        cfg.retailer,
        picklist_non_weighted_qty=flo_items,
        picklist_weighted_qty=flo_weighted_items,
        osr_products_qty=osr_items,
        manual_non_weighted_qty=manual_items,
        manual_weighted_qty=manual_weighted_items,
        stage_by_data=mfc_cutoff,
    )

    order_id = place_order(
        rint=apis.rint,
        retailer=cfg.retailer,
        products=order_flow_data["all_products"],
        store_id=mfc_cutoff.location_code_retailer,
        spoke_id=mfc_cutoff.location_code_spoke,
        stage_by_datetime=mfc_cutoff.timestamp,
        service_window_start=mfc_cutoff.timestamp,
        ecom_service_type="DELIVERY",
        ims=apis.ims_admin,
        oms=apis.oms,
        add_flo_stock=add_stock_for_flo_items,
    )

    return apis.oms.get_order(order_id)["response"]["cutoff-datetime"], order_id
