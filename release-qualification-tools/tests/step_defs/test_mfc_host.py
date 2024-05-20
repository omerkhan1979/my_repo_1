from src.api.collections import InitializedApis
from pytest_bdd import scenarios, then, when, parsers
from src.utils.place_order import products_to_lineitems
from pprint import pprint
from src.utils.helpers import wait_order_status_changed
from src.utils.assortment import Product

scenarios("../features/mfc_to_host.feature")


@when(
    parsers.parse('order is created with zero stock and with type "{service_type}"'),
    target_fixture="orderid_zero_stock_products",
)
def create_order_with_zero_stock(
    apis: InitializedApis,
    retailer,
    service_type: str,
    products: dict,
    location_code_retailer: str,
):
    products_list: list[Product] = products["order_flow_data"]["all_products"]
    apis.ims.zero_stock_for_products_or_addresses([products_list[0].tom_id])
    product_stock = apis.ims.v2_snapshot([products_list[0].tom_id])
    pprint(product_stock)
    lineitems = products_to_lineitems(
        retailer, products["order_flow_data"]["all_products"]
    )
    order_id = apis.rint.create_customer_order(
        spoke_id=products["order_flow_data"]["spoke_id"],
        stage_by_datetime=products["order_flow_data"]["stage_by_datetime"],
        service_window_start=products["order_flow_data"]["service_window_start"],
        lineitems=lineitems,
        store_id=location_code_retailer,
        ecom_service_type=service_type,
    )
    return {"orderid": order_id, "product_zero_stock": products_list[0].tom_id}


@then("product that are not fully available should be fulfilled by host")
def fulfillment_host(
    apis: InitializedApis,
    location_code_retailer: str,
    orderid_zero_stock_products: dict,
):
    wait_order_status_changed(
        orderid_zero_stock_products["orderid"], "queued", apis.oms
    )
    lineitems = apis.rint.get_customer_order_v4(
        location_code_retailer, orderid_zero_stock_products["orderid"]
    )["data"]["line-items"]
    host_lineitem = [
        i
        for i in lineitems
        if orderid_zero_stock_products["product_zero_stock"] in i["takeoff-item-ids"]
    ][0]

    assert host_lineitem["fulfillment-location"] == "host"
