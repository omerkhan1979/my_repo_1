from src.api.collections import InitializedApis
from pytest_bdd import scenarios, given, then
from src.utils.assortment import (
    generate_non_existing_product,
    Product,
)
from src.utils.console_printing import red

scenarios("../features/delete_unrecognize_item.feature")


@given(
    "unrecognized products are added to the order content",
    target_fixture="unrecognized_product",
)
def add_unrecognized_products(
    apis: InitializedApis, location_code_retailer: str, products: dict
) -> list[Product]:
    unrecognized_product = generate_non_existing_product(
        apis.distiller, location_code_retailer
    )
    both_products = products["order_flow_data"]["all_products"] + [unrecognized_product]
    products["order_flow_data"]["all_products"] = both_products
    return unrecognized_product


@then("unrecognzied items are not included in the order")
def unrecognized_items_not_included(
    apis: InitializedApis,
    location_code_retailer: str,
    orderid: str,
    unrecognized_product: list[Product],
):
    response_from_get_order_rint = apis.rint.get_customer_order_v4(
        location_code_retailer, orderid
    )
    actual_lineitems = response_from_get_order_rint["data"].get("line-items")
    for ecom_id in actual_lineitems:
        if unrecognized_product.ecom_id == ecom_id["ecom-item-id"]:
            assert False, red(
                f"unrecognized product {unrecognized_product.ecom_id} found in order {orderid}"
            )
