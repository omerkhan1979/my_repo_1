from pytest import mark, approx

from src.utils.console_printing import cyan, blue

from src.utils.helpers import wait_order_status_changed

from src.utils.totes import generate_target_tote
from src.utils.weighted_items_helpers import (
    records_for_decision_with_weighted_item,
    verify_oms_rint_responses,
)
from src.utils.place_order import place_order
from scripts.steps.orderflow.setup import prepare_orderflow_data
from src.utils.order_timings import MFCRelativeFutureTime
from src.api.collections import InitializedApis
from src.config.constants import MANUALLY_ENQUEUE_RETAILERS
from src.utils.order_picking import clear_dispatch_lane_order


@mark.rq
@mark.outbound
@mark.verify_picked_upc_weighted_item
@mark.retailers("winter")
@mark.parametrize(
    "product_type,flo,osr,manual, weighted_manual",
    [("OSR+manual+weighted_manual", 0, 1, 1, 1)],
)
@mark.testrail("185477")
def test_verify_picked_upc_weighted_item(
    cfg,
    apis: InitializedApis,
    product_type,
    orderflow_test_data,
    location_code_retailer,
    flo,
    osr,
    manual,
    weighted_manual,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
):
    orderflow_test_data = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        cfg.retailer,
        picklist_weighted_qty=flo,
        osr_products_qty=osr,
        manual_non_weighted_qty=manual,
        manual_weighted_qty=weighted_manual,
        stage_by_data=stage_by_in_1_minutes_1_min_cutoff,
    )
    order_id = place_order(
        rint=apis.rint,
        retailer=cfg.retailer,
        products=orderflow_test_data["all_products"],
        store_id=orderflow_test_data["store_id"],
        spoke_id=orderflow_test_data["spoke_id"],
        stage_by_datetime=orderflow_test_data["stage_by_datetime"],
        service_window_start=orderflow_test_data["service_window_start"],
        route_id=orderflow_test_data["route_id"],
        ims=apis.ims_admin,
        oms=apis.oms,
    )

    wait_order_status_changed(order_id, "new", apis.oms)
    if cfg.retailer in MANUALLY_ENQUEUE_RETAILERS:
        apis.oms.start_picking(order_id)
    wait_order_status_changed(order_id, "queued", apis.oms)
    apis.pickerman_facade.assign()

    osr_item_id = str(orderflow_test_data["osr_products"][0].tom_id)
    manual_picking_path = list(
        filter(
            lambda i: i["picking-address"] != "01K",
            apis.ims.get_reserved_picking_path_for_order(order_id),
        )
    )
    products = orderflow_test_data["all_products"]
    totes = [generate_target_tote()]
    (
        records,
        non_weighted_product_decision,
        weighted_product_decision,
        qty_weighted_item,
    ) = records_for_decision_with_weighted_item(
        apis.distiller, manual_picking_path, products, order_id, totes
    )
    # Process the order to the status PICKED
    apis.pickerman_facade.post_manual_picking_item_decision(order_id, records)
    wait_order_status_changed(order_id, "picked", apis.oms)

    # To verify 'picked-upc' and weight for weighted, OSR, regular manual products:
    get_rint_data, get_oms_data = verify_oms_rint_responses(
        weighted_product_decision,
        location_code_retailer,
        order_id,
        apis.rint,
        apis.oms,
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
    print(cyan("Test case test_verify_picked_upc_weighted_item result is: "))
    print(blue(f"\nClearing dispatch lane(s) if needed for order: {order_id}\n"))
    clear_dispatch_lane_order(apis.ims, order_id)


@mark.rq
@mark.outbound
@mark.verify_picked_weight
@mark.retailers("winter")
@mark.parametrize(
    "product_type,flo,osr,manual, weighted_manual",
    [("weighted_manual", 0, 0, 0, 1)],
)
@mark.testrail("173232")
def test_verify_picked_weight_weighted_item(
    cfg,
    apis: InitializedApis,
    product_type,
    location_code_retailer,
    flo,
    osr,
    manual,
    weighted_manual,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
):
    orderflow_test_data = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        cfg.retailer,
        picklist_weighted_qty=flo,
        osr_products_qty=osr,
        manual_non_weighted_qty=manual,
        manual_weighted_qty=weighted_manual,
        stage_by_data=stage_by_in_1_minutes_1_min_cutoff,
    )
    order_id = place_order(
        rint=apis.rint,
        retailer=cfg.retailer,
        products=orderflow_test_data["all_products"],
        store_id=orderflow_test_data["store_id"],
        spoke_id=orderflow_test_data["spoke_id"],
        stage_by_datetime=orderflow_test_data["stage_by_datetime"],
        service_window_start=orderflow_test_data["service_window_start"],
        route_id=orderflow_test_data["route_id"],
        ims=apis.ims_admin,
        oms=apis.oms,
    )
    manual_picking_path = list(
        filter(
            lambda i: i["picking-address"] != "01K",
            apis.ims.get_reserved_picking_path_for_order(order_id),
        )
    )
    products = orderflow_test_data["all_products"]
    totes = [generate_target_tote()]
    (
        records,
        _,
        weighted_product_decision,
        qty_weighted_item,
    ) = records_for_decision_with_weighted_item(
        apis.distiller, manual_picking_path, products, order_id, totes
    )
    # Process the order to the status PICKED
    apis.pickerman_facade.post_manual_picking_item_decision(order_id, records)
    wait_order_status_changed(order_id, "picked", apis.oms)

    # To verify 'picked-upc' and weight for weighted product:
    get_rint_data, get_oms_data = verify_oms_rint_responses(
        weighted_product_decision,
        location_code_retailer,
        order_id,
        apis.rint,
        apis.oms,
    )
    """ Rint-'picked-weight' value divided equally in size of 'picked-upc' for weighted_item for winter:"""
    #  SPLIT aggregated weight in rint response:
    assert (
        len(get_rint_data["picked_upc_weighted_item"])
        == len(get_rint_data["picked_weight_weighted_item"])
        == qty_weighted_item
    )
    # Aggregated weight in OMS response:
    assert len(get_oms_data["picked_weight_weighted_item"]) == 1
    assert (
        get_oms_data["picked_weight_weighted_item"]
        == weighted_product_decision["weight"]
        != get_rint_data["picked_weight_weighted_item"]
    )
    # Aggregated weight in OMS is equal sum split weights in RINT:
    total_rint_weight = 0
    for weight in get_rint_data["picked_weight_weighted_item"]:
        total_rint_weight += weight
    oms_picked_weight_weighted_item = get_oms_data["picked_weight_weighted_item"][0]
    assert oms_picked_weight_weighted_item == approx(
        total_rint_weight, 0.05 * oms_picked_weight_weighted_item
    )

    print(cyan("Test case test_verify_picked_weight_weighted_item result is: "))
    print(blue(f"\nClearing dispatch lane(s) if needed for order: {order_id}\n"))
    clear_dispatch_lane_order(apis.ims, order_id)
