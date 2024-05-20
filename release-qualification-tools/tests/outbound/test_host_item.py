from pprint import pprint
from pytest import mark
from src.api.collections import InitializedApis
from src.utils.place_order import place_order
from scripts.steps.orderflow.setup import prepare_orderflow_data
from src.utils.order_timings import MFCRelativeFutureTime
from src.utils.assortment import Product
from src.utils.console_printing import cyan


# @mark.rq - disabled per PROD-12009. Re-enable as part of AC for PROD-11886.
@mark.outbound
@mark.host_item
@mark.retailers("wings")
@mark.testrail("294153")
def test_item_with_not_enough_stock_note(
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
    products: list[Product] = orderflow_test_data["all_products"]
    product_without_stock = products[1]
    apis.ims.zero_stock_for_products_or_addresses([product_without_stock.tom_id])
    product_stock = apis.ims.v2_snapshot([product_without_stock.tom_id])
    pprint(product_stock)

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

    lineitems = apis.rint.get_customer_order_v4(location_code_retailer, order_id)[
        "data"
    ]["line-items"]
    host_lineitem = [
        i for i in lineitems if product_without_stock.tom_id in i["takeoff-item-ids"]
    ][0]
    assert host_lineitem["fulfillment-location"] == "host"
    print(cyan("Test case host_item is:"))
