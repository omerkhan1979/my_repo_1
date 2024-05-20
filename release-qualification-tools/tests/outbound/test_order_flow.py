from pytest import mark
from src.api.takeoff.tsc import TscReturnFormat
from src.config.config import Config
from src.config.constants import RETAILERS_WITHOUT_STAGING
from src.utils.console_printing import cyan, blue, red
from src.utils.helpers import wait_order_status_changed, get_order_status
from src.utils.order_picking import (
    assign_available_order_and_send_decisions_all_available,
    consolidate_order,
    stage_order,
    clear_dispatch_lane_order,
)
from src.api.collections import InitializedApis
from src.utils.place_order import place_order
from scripts.steps.orderflow.setup import prepare_orderflow_data
from src.utils.order_timings import MFCRelativeFutureTime
from src.config.constants import MANUALLY_ENQUEUE_RETAILERS


@mark.rq
@mark.smoke
@mark.outbound
@mark.order_flow
@mark.osr_picking
@mark.retailers("abs", "maf", "smu", "winter", "wings", "tienda")
@mark.parametrize(
    "product_type,flo,osr,manual,weighted_manual",
    [("OSR", 0, 1, 0, 0)],
)
@mark.testrail("486098")
def test_osr_order_flow(
    cfg: Config,
    product_type,
    staging_location,
    apis: InitializedApis,
    flo,
    osr,
    manual,
    weighted_manual,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
):
    """Order picking"""
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

    order_assigned = assign_available_order_and_send_decisions_all_available(
        apis.pickerman_facade, order_id, user_id=cfg.user_id, email=cfg.user
    )
    assert (
        order_assigned == order_id
    ), f"Assigned {order_assigned} but we are using order {order_id}"
    wait_order_status_changed(order_id, "picked", apis.oms)
    """Order consolidation"""
    consolidate_order(apis.pickerman_facade, order_id)
    wait_order_status_changed(order_id, "packed", apis.oms)
    """Order staging"""
    if cfg.retailer not in RETAILERS_WITHOUT_STAGING:
        stage_order(apis.pickerman_facade, apis.fft, order_id, staging_location)
        wait_order_status_changed(order_id, "staged", apis.oms)

    """Order status verification"""
    order_status_tsc = apis.tsc.get_config_item_value(
        "ORDER_STATUS_AFTER_PICKING", return_format=TscReturnFormat.json
    )
    try:
        wait_order_status_changed(order_id, order_status_tsc, apis.oms)
    except Exception:
        pass  # we'll let the assertion below actually fail the test
    order_status = get_order_status(order_id, apis.oms)
    if order_status == order_status_tsc:
        print(
            blue(
                f"Final status is {order_status} for order {order_id}, retailer: {cfg.retailer}"
            )
        )
        print(cyan(f"Test case {product_type} - osr_order_flow:"))
    else:
        assert False, red(
            f"Final Status {order_status_tsc} not found (have {order_status}), hence Test Case Failed"
        )

    print(blue(f"\nClearing dispatch lane(s) if needed for order: {order_id}\n"))
    clear_dispatch_lane_order(apis.ims, order_id)


@mark.rq
@mark.smoke
@mark.darkstore
@mark.outbound
@mark.order_flow
@mark.manual_picking
@mark.retailers("abs", "maf", "smu", "winter", "pinemelon")
@mark.parametrize(
    "product_type,flo,osr,manual,weighted_manual",
    [("manual", 0, 0, 1, 0)],
)
@mark.testrail("486097")
def test_manual_order_flow(
    cfg: Config,
    product_type: str,
    operator_user: dict,
    staging_location,
    apis: InitializedApis,
    flo,
    osr,
    manual,
    weighted_manual,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
):
    """Order picking"""
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

    order_assigned = assign_available_order_and_send_decisions_all_available(
        apis.pickerman_facade, order_id, user_id=cfg.user_id, email=cfg.user
    )
    assert (
        order_assigned == order_id
    ), f"Assigned {order_assigned} but we are using order {order_id}"
    wait_order_status_changed(order_id, "picked", apis.oms)
    """Order consolidation"""
    consolidate_order(apis.pickerman_facade, order_id)
    wait_order_status_changed(order_id, "packed", apis.oms)
    """Order staging"""
    if cfg.retailer not in RETAILERS_WITHOUT_STAGING:
        stage_order(apis.pickerman_facade, apis.fft, order_id, staging_location)
        wait_order_status_changed(order_id, "staged", apis.oms)

    """Order status verification"""
    order_status_tsc = apis.tsc.get_config_item_value(
        "ORDER_STATUS_AFTER_PICKING", return_format=TscReturnFormat.json
    )
    try:
        wait_order_status_changed(order_id, order_status_tsc, apis.oms)
    except Exception:
        pass  # we'll let the assertion below actually fail the test
    order_status = get_order_status(order_id, apis.oms)
    if order_status == order_status_tsc:
        print(
            blue(
                f"Final status is {order_status} for order {order_id}, retailer: {cfg.retailer}"
            )
        )
        print(cyan(f"Test case {product_type} - osr_order_flow:"))
    else:
        assert False, red(
            f"Final Status {order_status_tsc} not found (have {order_status}), hence Test Case Failed"
        )

    print(blue(f"\nClearing dispatch lane(s) if needed for order: {order_id}\n"))
    clear_dispatch_lane_order(apis.ims, order_id)


@mark.rq
@mark.outbound
@mark.order_flow
@mark.osr_manual_picking
@mark.retailers("abs", "maf", "smu", "winter")
@mark.parametrize(
    "product_type,flo,osr,manual,weighted_manual",
    [("OSR + manual", 0, 1, 1, 0)],
)
@mark.testrail("498135")
def test_osr_manual_order_flow(
    cfg: Config,
    product_type,
    staging_location,
    apis: InitializedApis,
    flo,
    osr,
    manual,
    weighted_manual,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
):
    """Order picking"""
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

    order_assigned = assign_available_order_and_send_decisions_all_available(
        apis.pickerman_facade, order_id, user_id=cfg.user_id, email=cfg.user
    )
    assert (
        order_assigned == order_id
    ), f"Assigned {order_assigned} but we are using order {order_id}"
    wait_order_status_changed(order_id, "picked", apis.oms)
    """Order consolidation"""
    consolidate_order(apis.pickerman_facade, order_id)
    wait_order_status_changed(order_id, "packed", apis.oms)
    """Order staging"""
    if cfg.retailer not in RETAILERS_WITHOUT_STAGING:
        stage_order(apis.pickerman_facade, apis.fft, order_id, staging_location)
        wait_order_status_changed(order_id, "staged", apis.oms)

    """Order status verification"""
    order_status_tsc = apis.tsc.get_config_item_value(
        "ORDER_STATUS_AFTER_PICKING", return_format=TscReturnFormat.json
    )
    try:
        wait_order_status_changed(order_id, order_status_tsc, apis.oms)
    except Exception:
        pass  # we'll let the assertion below actually fail the test
    order_status = get_order_status(order_id, apis.oms)
    if order_status == order_status_tsc:
        print(
            blue(
                f"Final status is {order_status} for order {order_id}, retailer: {cfg.retailer}"
            )
        )
        print(cyan(f"Test case {product_type} - osr_order_flow:"))
    else:
        assert False, red(
            f"Final Status {order_status_tsc} not found (have {order_status}), hence Test Case Failed"
        )

    print(blue(f"\nClearing dispatch lane(s) if needed for order: {order_id}\n"))
    clear_dispatch_lane_order(apis.ims, order_id)
