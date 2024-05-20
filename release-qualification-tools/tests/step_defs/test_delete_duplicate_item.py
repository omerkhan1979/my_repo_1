from src.api.collections import InitializedApis
from pytest_bdd import scenarios, given, then
from src.utils.console_printing import red
from src.utils.assortment import Product

scenarios("../features/delete_duplicate_line.feature")


@given(
    "duplicate products are added to the order content",
    target_fixture="duplicate_product",
)
def add_duplicate_products(products: dict) -> list[Product]:
    products_list: list[Product] = products["order_flow_data"]["all_products"]
    products_list.append(products_list[0])
    return products_list[0]


@then("duplicate items are not included in the order")
def duplicate_items_not_included(
    apis: InitializedApis,
    location_code_retailer: str,
    orderid: str,
    duplicate_product: list[Product],
):
    response_from_get_order_rint = apis.rint.get_customer_order_v4(
        location_code_retailer, orderid
    )
    actual_lineitems = response_from_get_order_rint["data"].get("line-items")
    count = 0
    for ecom_id in actual_lineitems:
        if duplicate_product.ecom_id == ecom_id["ecom-item-id"]:
            count = count + 1

    if count == 2:
        assert False, red(
            f"duplicate product {duplicate_product.ecom_id} found in order {orderid}"
        )
