from pytest import mark

from src.api.takeoff.tsc import TscReturnFormat
from src.config.config import Config
from src.config.constants import RETAILERS_WITHOUT_STAGING
from src.config.constants import MANUALLY_ENQUEUE_RETAILERS
from src.utils.console_printing import blue, cyan, red
from src.utils.helpers import wait_order_status_changed, get_order_status
from src.utils.order_picking import (
    tma_assign_available_order_and_send_decisions,
    tma_stage_order,
    clear_dispatch_lane_order,
)
from src.api.collections import InitializedApis
from src.utils.place_order import place_order
from scripts.steps.orderflow.setup import prepare_orderflow_data
from src.utils.order_timings import MFCRelativeFutureTime


@mark.rq
@mark.outbound
@mark.tma_manual_fullfilment
@mark.retailers("winter", "abs", "maf", "smu", "pinemelon")
@mark.parametrize(
    "product_type,flo,osr,manual,weighted_manual",
    [("manual", 0, 0, 1, 0)],
)
@mark.testrail("644648")
def test_tma_manual_fulfillment(
    cfg: Config,
    product_type: str,
    operator_user: dict,
    apis: InitializedApis,
    flo,
    osr,
    manual,
    weighted_manual,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
):
    """order id"""
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

    """assign order to the picker using fulfillment task assign endpoints"""
    fulfillment_id = tma_assign_available_order_and_send_decisions(
        apis.pickerman_facade,
        apis.mobile,
        order_id,
        user_id=cfg.user_id,
        email=cfg.user,
    )
    print("fulfillment id", fulfillment_id)
    wait_order_status_changed(order_id, "picked", apis.oms)
    tote = apis.mobile.get_totes_fulfillment(fulfillment_id)

    apis.mobile.put_pack(fulfillment_id)

    wait_order_status_changed(order_id, "packed", apis.oms)

    """Order staging"""
    if cfg.retailer not in RETAILERS_WITHOUT_STAGING:
        tma_stage_order(apis.mobile, cfg, fulfillment_id, tote, order_id)
        wait_order_status_changed(order_id, "staged", apis.oms)

    """Order status verification"""
    order_status_tsc = apis.tsc.get_config_item_value(
        "ORDER_STATUS_AFTER_PICKING", return_format=TscReturnFormat.json
    )
    try:
        wait_order_status_changed(order_id, order_status_tsc, apis.oms)
    except Exception:
        pass  # we'll let the nicer logging/assertion below fail this test
    order_status = get_order_status(order_id, apis.oms)
    if order_status == order_status_tsc:
        print(
            blue(
                f"Final status is {order_status} for order {order_id}, retailer: {cfg.retailer}"
            )
        )
        print(cyan(f"Test case {product_type} - tma_manual_fullfilment:"))
    else:
        assert False, red(
            f" Final Status {order_status} not found, hence Test Case Failed"
        )

    print(blue(f"\nClearing dispatch lane(s) if needed for order: {order_id}\n"))
    clear_dispatch_lane_order(apis.ims, order_id)
