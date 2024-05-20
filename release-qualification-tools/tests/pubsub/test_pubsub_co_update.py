import pytest
from pytest import mark
from pprint import pprint

from src.utils.console_printing import cyan, yellow
from src.utils.helpers import (
    wait_for_pubsub_message_after_co_update,
    wait_order_status_changed,
)
from src.api.collections import InitializedApis
from src.utils.place_order import place_order
from scripts.steps.orderflow.setup import prepare_orderflow_data
from src.utils.order_timings import MFCRelativeFutureTime
from src.config.constants import MANUALLY_ENQUEUE_RETAILERS
from src.api.takeoff.pickerman_facade import PickermanFacade


@mark.rq
@mark.pubsub
@mark.outbound
@mark.pubsub_co_update
@mark.retailers("wings", "maf", "smu", "tienda")
@mark.parametrize("product_type,flo,osr,manual,weighted_manual", [("OSR", 0, 1, 0, 0)])
@mark.testrail("61108")
def test_pubsub_co_update(
    product_type,
    retailer,
    env,
    cfg,
    flo,
    osr,
    manual,
    weighted_manual,
    apis: InitializedApis,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
    pickerman_facade: PickermanFacade,
):
    # TODO: Fixing of this issue will be taken care with ticket PROD-11888, currently we did add this to skip the execution from ODE env.
    if cfg.env == "ode":
        pytest.skip(
            "We can skip this test from ODE for now, need to fix the script from failing"
        )
        return

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
    pickerman_facade.assign()

    print(
        yellow(
            f"\nNow test is searching the needed pubsub message for the order {order_id} after status update"
        )
    )

    count = 0
    success = False
    while count < 10:
        payload = wait_for_pubsub_message_after_co_update(retailer, env)
        count += 1
        ecom_order_id = payload.get("order-id")
        status_after_update = payload.get("status")
        status = "new" or "queued"
        if ecom_order_id == order_id and status_after_update == status:
            success = True
            pprint(payload)
            break
    assert success
    print(cyan("Test case pubsub_stock_update is:"))
