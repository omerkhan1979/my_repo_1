from pytest import mark

from src.utils.console_printing import yellow, green, cyan
from src.utils.helpers import wait_order_status_changed, get_order_status
from src.api.collections import InitializedApis
from src.utils.place_order import place_order
from scripts.steps.orderflow.setup import prepare_orderflow_data
from src.utils.order_timings import MFCRelativeFutureTime


@mark.rq
@mark.outbound
@mark.update_ecom_status
@mark.retailers("winter")
@mark.parametrize(
    "target_ecom_status,expected_mfc_status,flo,osr,manual,weighted_manual",
    [
        ("PickingDownloaded", "new", 0, 0, 2, 0),
        ("CustomerCancelled", "cancelled", 0, 0, 2, 0),
    ],
)
@mark.testrail("30307", "47573", "30308")
def test_update_ecom_status_winter(
    cfg,
    target_ecom_status,
    expected_mfc_status,
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

    order_status = apis.oms.get_order(order_id)["response"]["status"]
    print(yellow(f"\nOrder status: {order_status}"))
    assert order_status == "draft"
    location_code_retailer = apis.tsc.get_location_code("location-code-retailer")
    apis.rint.update_co_ecom_status(
        location_code_retailer, order_id, target_ecom_status
    )

    wait_order_status_changed(order_id, expected_mfc_status, apis.oms)
    order_status = get_order_status(order_id, apis.oms)
    print(green(f"\nOrder status: {order_status}"))
    assert order_status == expected_mfc_status
    print(cyan("Test case update_ecom_status is:"))
