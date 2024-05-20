from pytest import mark
from src.config.constants import MANUALLY_ENQUEUE_RETAILERS
from src.api.takeoff.pickerman_facade import PickermanFacade

from src.utils.helpers import wait_order_status_changed, get_order_status
from src.api.collections import InitializedApis
from src.utils.place_order import place_order
from scripts.steps.orderflow.setup import prepare_orderflow_data
from src.utils.order_timings import MFCRelativeFutureTime
from src.utils.console_printing import blue
from src.utils.order_picking import clear_dispatch_lane_order


@mark.osr_smoke_test
@mark.outbound_smoke
@mark.parametrize("product_type,flo,osr,manual,weighted_manual", [("OSR", 0, 1, 0, 0)])
@mark.testrail("166248")
def test_osr_smoke_test(
    cfg,
    pickerman_facade: PickermanFacade,
    product_type,
    apis: InitializedApis,
    flo,
    osr,
    manual,
    weighted_manual,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
):
    """This test is used in OSR Replicator deploy workflow"""
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

    records = []
    pickerman_facade.post_manual_picking_item_decision(order_id, records)
    wait_order_status_changed(order_id, "picked", apis.oms)
    order_status = get_order_status(order_id, apis.oms)
    assert order_status == "picked"

    print(blue(f"\nClearing dispatch lane(s) if needed for order: {order_id}\n"))
    clear_dispatch_lane_order(apis.ims, order_id)
