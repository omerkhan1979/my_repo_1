from pytest import mark, param
import pyjokes

from src.utils.console_printing import blue, cyan
from src.utils.helpers import wait_order_status_changed, get_order_status
from src.api.collections import InitializedApis
from scripts.steps.orderflow.setup import prepare_orderflow_data
from src.utils.place_order import place_order
from src.utils.order_timings import MFCRelativeFutureTime

random_order_note = pyjokes.get_joke(language="en", category="all")


@mark.rq
@mark.outbound
@mark.order_note
@mark.retailers("winter", "wings", "smu", "abs", "maf", "tienda")
@mark.parametrize(
    "order_note",
    [
        param(None, marks=mark.testrail("185392")),
        param("", marks=mark.testrail("185315")),
        param(random_order_note, marks=mark.testrail("185320")),
    ],
)
def test_order_note(
    retailer,
    location_code_retailer,
    order_note,
    apis: InitializedApis,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
):
    orderflow_test_data = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        retailer,
        picklist_weighted_qty=0,
        osr_products_qty=1,
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
        order_note=order_note,
    )

    expected_status = "new" if retailer == "winter" else "queued"
    wait_order_status_changed(order_id, expected_status, apis.oms)
    order_status = get_order_status(order_id, apis.oms)
    print(
        blue(
            f'The order {order_id} has split successfully. Order_note field: "{order_note}"'
        )
    )
    assert order_status == expected_status
    print(
        cyan(
            f'Test case order_note with order id is "{order_id}" and order note "{order_note}" is:'
        )
    )
