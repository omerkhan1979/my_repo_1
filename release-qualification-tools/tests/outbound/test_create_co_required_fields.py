from pytest import mark
from src.utils.helpers import wait_order_status_changed
from src.api.collections import InitializedApis
from scripts.steps.orderflow.setup import prepare_orderflow_data
from src.utils.place_order import place_order
from src.utils.order_timings import MFCRelativeFutureTime


@mark.rq
@mark.outbound
@mark.create_co_required_fields
@mark.retailers("winter", "wings", "abs", "maf", "smu", "tienda")
@mark.testrail("47991")
def test_co_required_fields(
    retailer,
    location_code_retailer,
    apis: InitializedApis,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
):
    orderflow_test_data = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        retailer,
        picklist_weighted_qty=0,
        osr_products_qty=2,
        manual_non_weighted_qty=0,
        manual_weighted_qty=0,
        stage_by_data=stage_by_in_1_minutes_1_min_cutoff,
    )
    order_id = place_order(
        rint=apis.rint,
        retailer=retailer,
        products=orderflow_test_data["all_products"],
        store_id=orderflow_test_data["store_id"],
        spoke_id=orderflow_test_data["spoke_id"],
        stage_by_datetime=orderflow_test_data["stage_by_datetime"],
        service_window_start=orderflow_test_data["service_window_start"],
        route_id=orderflow_test_data["route_id"],
        ims=apis.ims_admin,
        oms=apis.oms,
    )
    print(order_id)
    assert wait_order_status_changed(order_id, "queued", apis.oms)
