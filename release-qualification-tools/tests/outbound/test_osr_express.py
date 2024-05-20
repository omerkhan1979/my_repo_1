from pytest import mark
from src.config.config import Config
from src.config.constants import (
    RETAILERS_WITHOUT_STAGING,
)
from src.api.takeoff.tsc import TscReturnFormat
from src.utils.console_printing import cyan, blue, red
from src.utils.helpers import wait_order_status_changed, get_order_status
from src.utils.order_picking import (
    assign_available_order_and_send_decisions_all_available,
    consolidate_order,
    stage_order,
)
from src.utils.order_timings import MFCRelativeFutureTime
from src.utils.place_order import place_order
from src.api.collections import InitializedApis
from scripts.steps.orderflow.setup import prepare_orderflow_data

# TODO: this lives in the wrong spot at a minimum


@mark.rq
@mark.outbound
@mark.order_flow
@mark.osr_express_picking
@mark.retailers("abs", "maf", "smu", "wings")
@mark.testrail("571329")
def test_osr_express_order_flow(
    cfg: Config,
    apis: InitializedApis,
    staging_location: str,
    stage_by_in_10_minutes_1_min_cutoff: MFCRelativeFutureTime,
):
    """This test does not explicitly call split. It has an order that
    misses the current cutoff but is early for the next."""
    orderflow_test_data = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        cfg.retailer,
        picklist_weighted_qty=0,
        osr_products_qty=1,
        manual_non_weighted_qty=0,
        manual_weighted_qty=0,
        stage_by_data=stage_by_in_10_minutes_1_min_cutoff,
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
        ecom_service_type="EXPRESS",
    )

    wait_order_status_changed(order_id, "queued", apis.oms)

    # Order picking
    order_assigned = assign_available_order_and_send_decisions_all_available(
        apis.pickerman_facade, order_id, user_id=cfg.user_id, email=cfg.user
    )
    assert (
        order_assigned == order_id
    ), f"Assigned {order_assigned} but we are using order {order_id}"
    wait_order_status_changed(order_id, "picked", apis.oms)
    print(
        blue(f"Details for {order_id} are {apis.oms.get_order(order_id)['response']}")
    )

    # Order consolidation
    consolidate_order(apis.pickerman_facade, order_id)
    wait_order_status_changed(order_id, "packed", apis.oms)

    # Order staging
    if cfg.retailer not in RETAILERS_WITHOUT_STAGING:
        stage_order(apis.pickerman_facade, apis.fft, order_id, staging_location)
        wait_order_status_changed(order_id, "staged", apis.oms)

    # Order status verification

    order_status_tsc = apis.tsc.get_config_item_value(
        "ORDER_STATUS_AFTER_PICKING", return_format=TscReturnFormat.json
    )
    try:
        wait_order_status_changed(order_id, order_status_tsc, apis.oms)
    except Exception:
        pass  # status will be asserted with nicer message below
    order_status = get_order_status(order_id, apis.oms)
    if order_status == order_status_tsc:
        print(
            blue(
                f"Final status is {order_status} for order {order_id}, retailer: {cfg.retailer}"
            )
        )
        print(cyan("Test case test_express_osr_order_flow is:"))
    else:
        assert False, red(
            f"Final Status {order_status_tsc} not found (we have: {order_status}), hence Test Case Failed"
        )
