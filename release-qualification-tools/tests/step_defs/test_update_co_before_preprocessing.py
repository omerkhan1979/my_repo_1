from src.api.collections import InitializedApis
from pytest_bdd import scenarios, parsers, then
from tests.conftest import _stage_by_with_configured_waveplan
from src.utils.update_order import (
    update_order_specific_fields,
    remove_product_from_customer_order,
    add_product_to_customer_order,
)

scenarios("../features/update_co_before_preprocessing.feature")


@then(
    "Update order by removing one item and validate product count",
    target_fixture="add_item",
)
def update_order_by_removing_one_item(
    apis: InitializedApis,
    location_code_tom: str,
    orderid: str,
) -> dict:
    order_details = apis.rint.get_customer_order_v4(location_code_tom, orderid)
    number_of_products_before = len(order_details["data"]["line-items"])

    add_item = remove_product_from_customer_order(apis, location_code_tom, orderid)

    order_details = apis.rint.get_customer_order_v4(location_code_tom, orderid)
    number_of_products_after = len(order_details["data"]["line-items"])
    assert number_of_products_before > number_of_products_after

    return add_item


@then("Update order by adding one item and validate product count")
def update_order_by_adding_one_item(
    apis: InitializedApis,
    location_code_tom: str,
    retailer: str,
    orderid: str,
    add_item: dict,
) -> None:
    order_details = apis.rint.get_customer_order_v4(location_code_tom, orderid)
    number_of_products_before = len(order_details["data"]["line-items"])
    add_product_to_customer_order(apis, location_code_tom, orderid, add_item)

    _stage_by_with_configured_waveplan(retailer, apis, stage_by_in_minutes=1600)

    order_details = apis.rint.get_customer_order_v4(location_code_tom, orderid)
    number_of_products_after = len(order_details["data"]["line-items"])
    assert number_of_products_after > number_of_products_before


@then(parsers.parse('Update order with "{field_name}" and "{field_value}"'))
def update_order_with_given_field(
    apis: InitializedApis,
    location_code_tom: str,
    orderid: str,
    field_name: str,
    field_value: str,
) -> None:
    update_order_specific_fields(
        apis, location_code_tom, orderid, field_name, field_value
    )
    check_updated_field = ""
    order_details = apis.rint.get_customer_order_v4(location_code_tom, orderid)

    if field_name in order_details["data"]["line-items"][0].keys():
        for line_item in order_details["data"]["line-items"]:
            check_updated_field = str(line_item[field_name])
    elif field_name in order_details["data"].keys():
        check_updated_field = order_details["data"][field_name]
    elif field_name in order_details["data"]["delivery-route"].keys():
        check_updated_field = order_details["data"]["delivery-route"][field_name]

    assert check_updated_field == field_value
