from pytest import mark
from src.utils.assortment import generate_non_existing_product
from src.utils.assortment import Product
from src.utils.console_printing import cyan
from src.api.collections import InitializedApis
from src.utils.place_order import place_order
from scripts.steps.orderflow.setup import prepare_orderflow_data
from src.utils.order_timings import MFCRelativeFutureTime


@mark.rq
@mark.outbound
@mark.delete_unrecognized_items
@mark.retailers("abs")
@mark.testrail("294148")
def test_delete_unrecognized_items(
    retailer,
    env,
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
        osr_products_qty=1,
        manual_non_weighted_qty=0,
        manual_weighted_qty=0,
        stage_by_data=stage_by_in_1_minutes_1_min_cutoff,
    )
    recognized_product: list[Product] = orderflow_test_data["all_products"]
    unrecognized_product = generate_non_existing_product(
        distiller=apis.distiller, location_code_retailer=location_code_retailer
    )
    both_products = recognized_product + [unrecognized_product]
    print(both_products)
    order_id = place_order(
        rint=apis.rint,
        retailer=retailer,
        products=both_products,
        store_id=orderflow_test_data["store_id"],
        spoke_id=orderflow_test_data["spoke_id"],
        stage_by_datetime=orderflow_test_data["stage_by_datetime"],
        service_window_start=orderflow_test_data["service_window_start"],
        route_id=orderflow_test_data["route_id"],
        ims=apis.ims_admin,
        oms=apis.oms,
    )

    response_from_get_order_rint = apis.rint.get_customer_order_v4(
        location_code_retailer, order_id
    )
    actual_lineitems = response_from_get_order_rint["data"].get("line-items")
    actual_tom_ids = actual_lineitems[0]["takeoff-item-ids"]
    assert len(actual_lineitems) == 1
    assert recognized_product[0].tom_id in actual_tom_ids

    print(f"https://{retailer}-{env}.tom.takeoff.com/orders/details/?id={order_id}")
    print(cyan("Test case delete_unrecognized_items is:"))
