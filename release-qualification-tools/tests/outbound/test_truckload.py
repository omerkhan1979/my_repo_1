from pytest import mark
from src.api.takeoff.mobile import Mobile
from src.api.takeoff.tsc import TscReturnFormat
from src.utils.order_timings import MFCRelativeFutureTime
from src.utils.place_order import place_order
from src.api.collections import InitializedApis
from scripts.steps.orderflow.setup import prepare_orderflow_data
from src.config.config import Config
from src.utils.console_printing import cyan
from src.utils.helpers import wait_order_status_changed
from src.utils.order_picking import (
    assign_available_order_and_send_decisions_all_available,
    stage_order,
    consolidate_order,
)


@mark.rq
@mark.smoke
@mark.outbound
@mark.truckload
@mark.retailers("winter")
@mark.parametrize(
    "product_type,flo,osr,manual,weighted_manual",
    [("OSR", 0, 1, 0, 0)],
)
@mark.testrail("137643")
def test_truckload(
    cfg: Config,
    product_type,
    staging_location,
    mobile: Mobile,
    apis: InitializedApis,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
    flo,
    osr,
    manual,
    weighted_manual,
):
    orderflow_test_data = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        cfg.retailer,
        picklist_weighted_qty=0,
        osr_products_qty=osr,
        manual_non_weighted_qty=0,
        manual_weighted_qty=0,
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
    if apis.tsc.get_config_item_value(
        "STAGING_CONFIGURATION_ENABLED", return_format=TscReturnFormat.json
    ):
        stage_order(apis.pickerman_facade, apis.fft, order_id, staging_location)
        wait_order_status_changed(order_id, "staged", apis.oms)

    """Order status verification for truckload"""
    order_status_after_picking = apis.tsc.get_config_item_value(
        "ORDER_STATUS_AFTER_PICKING", return_format=TscReturnFormat.json
    )

    # wait for transition (we'll let the validation catch if we didn't get the expectation)
    try:
        wait_order_status_changed(order_id, order_status_after_picking, apis.oms)
    except Exception:
        pass  # we'll let the nicer logging/assertion below fail this test

    """ Getting the route details for the retailers"""
    route_code = apis.tsc.get_routes()["routes"][0]["route-code"]
    print(f"Route code: {route_code}")
    truckload_orders = mobile.get_truckload_orders(
        route_code, order_status_after_picking
    )

    truck_load_session_status = "served"
    print(
        f"Get all the order_ids which are in status '{order_status_after_picking}' and validate if the orders are '{truck_load_session_status}' or not "
    )
    order_ids = [data["order_id"] for data in truckload_orders]

    print(f"Truckload order ids: {order_ids}")
    assert order_ids, "Need at least on truckload order"
    for order_id in order_ids:
        final_status = mobile.post_truckload([order_id], truck_load_session_status)
        assert (
            final_status == truck_load_session_status
        ), f"Truckload status for order {order_id} is {final_status}, expected '{truck_load_session_status}'."

    print(cyan(f"Truckload is successfully served for {route_code}"))
