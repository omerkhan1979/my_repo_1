from src.api.takeoff.distiller import Distiller
from src.api.takeoff.oms import OMS
from src.api.takeoff.rint import RInt
from src.utils.assortment import get_product_from_list_by_tom_id
from src.utils.barcode import weighted_barcode
from src.utils.console_printing import blue
from src.utils.order_picking import generate_picking_decision_record


def get_data_weighted_item(
    distiller: Distiller, product: list, barcodes: list, qty: int
):
    product_data = distiller.get_products_by_tom_ids(product)
    if product_data:
        product_data = product_data[0]
        zero_barcode = product_data.barcodes[-1]
        average_weight = product_data.retail_item.weight.weight

        if zero_barcode and average_weight is not None:
            total_weight = [qty * average_weight]
            product_barcode = weighted_barcode(zero_barcode, str(average_weight))
        # The qty of sent barcodes for picking_item_decision have to be equal "picked-quantity"
        # to divide 'picked-weight' value in rint responce:
        for i in range(1, qty + 1):
            barcodes.append(product_barcode)
    return barcodes, total_weight


def records_for_decision_with_weighted_item(
    distiller: Distiller, manual_picking_path, products, order_id, totes
):
    non_weighted_product_decision = {}
    weighted_product_decision = {}
    qty_weighted_item = {}
    records = []
    for item in manual_picking_path:
        product = [item["product-id"]]
        product_data = distiller.get_products_by_tom_ids(product)
        print("********Get Products***************", product_data)
        if product_data:
            product_data = product_data[0]

            if not product_data.is_weight_variable_on_receipt:
                barcodes = [
                    get_product_from_list_by_tom_id(
                        products, item["product-id"]
                    ).barcode
                ]
                weight = []
                non_weighted_product_decision = {
                    "barcodes": barcodes,
                    "weight": weight,
                    "item_id": item["product-id"],
                }
            else:
                qty_weighted_item = item["quantity-unit-to-prepare"]
                barcodes = []
                barcodes, weight = get_data_weighted_item(
                    distiller, product, barcodes, qty_weighted_item
                )
                weighted_product_decision = {
                    "barcodes": barcodes,
                    "weight": weight,
                    "item_id": item["product-id"],
                }
            record = generate_picking_decision_record(
                order_id,
                item["product-id"],
                item["quantity-unit-to-prepare"],
                barcodes,
                item["picking-address"],
                totes,
                weight,
            )
            records.append(record)
    return (
        records,
        non_weighted_product_decision,
        weighted_product_decision,
        qty_weighted_item,
    )


def verify_oms_rint_responses(
    weighted_product_decision,
    location_code_retailer,
    order_id,
    rint: RInt,
    oms: OMS,
    non_weighted_product_decision=None,
    osr_item_id=None,
):
    rint_get_order_line_items = rint.get_customer_order_v4(
        location_code_retailer, order_id
    )["data"]["line-items"]
    get_rint_data = {}
    get_rint_data_item = {}
    for line_items in rint_get_order_line_items:
        if non_weighted_product_decision is None:
            pass
        else:
            if line_items["takeoff-item-ids"][0] == non_weighted_product_decision.get(
                "item_id"
            ):
                picked_weight_non_weighted_item = line_items["totes"][0][
                    "picked-weight"
                ]
                picked_upc_non_weighted_item = line_items["totes"][0]["picked-upc"]
                get_rint_data_item = {
                    "picked_weight_non_weighted_item": picked_weight_non_weighted_item,
                    "picked_upc_non_weighted_item": picked_upc_non_weighted_item,
                }
        if line_items["takeoff-item-ids"][0] == weighted_product_decision.get(
            "item_id"
        ):
            picked_weight_weighted_item = line_items["totes"][0]["picked-weight"]
            picked_upc_weighted_item = line_items["totes"][0]["picked-upc"]
            get_rint_data_item = {
                "picked_weight_weighted_item": picked_weight_weighted_item,
                "picked_upc_weighted_item": picked_upc_weighted_item,
            }
        if osr_item_id is None:
            pass
        else:
            if line_items["takeoff-item-ids"][0] == osr_item_id:
                picked_weight_osr_item = line_items["totes"][0]["picked-weight"]
                picked_upc_osr_item = line_items["totes"][0]["picked-upc"]
                get_rint_data_item = {
                    "picked_weight_osr_item": picked_weight_osr_item,
                    "picked_upc_osr_item": picked_upc_osr_item,
                }
        get_rint_data.update(get_rint_data_item)
    print(blue(f"RINT data for order {order_id}:"), get_rint_data)

    oms_get_order_line_items = oms.get_order(order_id)["response"]["line-items"]
    get_oms_data = {}
    get_oms_data_item = {}
    for line_item in oms_get_order_line_items:
        if non_weighted_product_decision is None:
            pass
        else:
            if line_item["takeoff-item-ids"][0] == non_weighted_product_decision.get(
                "item_id"
            ):
                picked_weight_non_weighted_item = line_item["tom-items"][0]["decision"][
                    0
                ]["picked-weight"]
                picked_upc_non_weighted_item = line_item["tom-items"][0]["decision"][0][
                    "picked-upc"
                ]
                get_oms_data_item = {
                    "picked_weight_non_weighted_item": picked_weight_non_weighted_item,
                    "picked_upc_non_weighted_item": picked_upc_non_weighted_item,
                }
        if line_item["takeoff-item-ids"][0] == weighted_product_decision.get("item_id"):
            picked_weight_weighted_item = line_item["tom-items"][0]["decision"][0][
                "picked-weight"
            ]
            picked_upc_weighted_item = line_item["tom-items"][0]["decision"][0][
                "picked-upc"
            ]
            get_oms_data_item = {
                "picked_weight_weighted_item": picked_weight_weighted_item,
                "picked_upc_weighted_item": picked_upc_weighted_item,
            }
        if osr_item_id is None:
            pass
        else:
            if line_item["takeoff-item-ids"][0] == osr_item_id:
                picked_weight_osr_item = line_item["tom-items"][0]["decision"][0][
                    "picked-weight"
                ]
                picked_upc_osr_item = line_item["tom-items"][0]["decision"][0][
                    "picked-upc"
                ]
                get_oms_data_item = {
                    "picked_weight_osr_item": picked_weight_osr_item,
                    "picked_upc_osr_item": picked_upc_osr_item,
                }
        get_oms_data.update(get_oms_data_item)
    print(blue(f"OMS data for order {order_id}:"), get_oms_data)

    return get_rint_data, get_oms_data
