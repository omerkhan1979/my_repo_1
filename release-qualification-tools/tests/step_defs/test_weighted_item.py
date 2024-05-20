from pytest_bdd import scenarios, when
from src.api.collections import InitializedApis
from src.api.takeoff.oms import OMS
from src.api.takeoff.rint import RInt
from src.utils.helpers import wait_order_status_changed
from src.utils.totes import generate_target_tote
from src.utils.weighted_items_helpers import (
    records_for_decision_with_weighted_item,
    verify_oms_rint_responses,
)

scenarios("../features/pick_weighted_item.feature")


@when("verify the weighted items are aggregated during the picking stage")
def aggregate_weight(
    apis: InitializedApis,
    orderid,
    products: dict,
    location_code_retailer,
    rint: RInt,
    oms: OMS,
):
    wait_order_status_changed(orderid, "new", oms)
    oms.start_picking(orderid)
    wait_order_status_changed(orderid, "queued", oms)
    apis.pickerman_facade.assign()

    osr_item_id = str(products["order_flow_data"]["osr_products"][0].tom_id)
    manual_picking_path = list(
        filter(
            lambda i: i["picking-address"] != "01K",
            apis.ims.get_reserved_picking_path_for_order(orderid),
        )
    )
    products = products["order_flow_data"]["all_products"]
    totes = [generate_target_tote()]
    (
        records,
        non_weighted_product_decision,
        weighted_product_decision,
        qty_weighted_item,
    ) = records_for_decision_with_weighted_item(
        apis.distiller, manual_picking_path, products, orderid, totes
    )
    # Process the order to the status PICKED
    apis.pickerman_facade.post_manual_picking_item_decision(orderid, records)
    wait_order_status_changed(orderid, "picked", apis.oms)

    # To verify 'picked-upc' and weight for weighted, OSR, regular manual products:
    get_rint_data, get_oms_data = verify_oms_rint_responses(
        weighted_product_decision,
        location_code_retailer,
        orderid,
        rint,
        oms,
        non_weighted_product_decision,
        osr_item_id,
    )
    assert len(get_rint_data["picked_weight_weighted_item"]) == qty_weighted_item
    assert len(get_rint_data["picked_upc_weighted_item"]) == qty_weighted_item
    # rint data is the same as OMS and as sent decision for non_weighted_item and osr_item:
    assert (
        get_oms_data["picked_weight_non_weighted_item"]
        == non_weighted_product_decision["weight"]
        == get_rint_data["picked_weight_non_weighted_item"]
    )
    assert (
        get_oms_data["picked_weight_osr_item"]
        == get_rint_data["picked_weight_osr_item"]
        == []
    )
    assert (
        get_oms_data["picked_upc_non_weighted_item"]
        == non_weighted_product_decision["barcodes"]
        == get_rint_data["picked_upc_non_weighted_item"]
    )
    assert get_oms_data["picked_upc_osr_item"] == get_rint_data["picked_upc_osr_item"]

    # rint data differs from OMS and sent decision for weighted_item:
    assert (
        get_oms_data["picked_weight_weighted_item"]
        == weighted_product_decision["weight"]
        != get_rint_data["picked_weight_weighted_item"]
    )
    assert (
        get_oms_data["picked_upc_weighted_item"]
        == weighted_product_decision["barcodes"]
        != get_rint_data["picked_upc_weighted_item"]
    )
