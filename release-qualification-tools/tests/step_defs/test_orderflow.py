from src.utils.place_order import products_to_lineitems_required_field
from src.api.collections import InitializedApis
from pytest_bdd import scenarios, when, parsers, then

scenarios("../features/order_flow.feature")


@when(
    parsers.parse(
        'order is created and split naturally with required fields and type "{service_type}"'
    ),
    target_fixture="orderid",
)
def create_order_with_required_fields(
    apis: InitializedApis, retailer: str, service_type: str, products: dict
) -> str:
    weight = None
    lineitems = products_to_lineitems_required_field(
        retailer, products["order_flow_data"]["all_products"], weight
    )

    order_id = apis.rint.create_customer_order_required_field(
        stage_by_datetime=products["order_flow_data"]["stage_by_datetime"],
        service_window_start=products["order_flow_data"]["service_window_start"],
        store_id=products["order_flow_data"]["store_id"],
        spoke_id=products["order_flow_data"]["spoke_id"],
        lineitems=lineitems,
        ecom_service_type=service_type,
    )
    return order_id


@then("view and validate order details json structure")
def view_order_details_and_validate_order(apis: InitializedApis, orderid: str):
    order_details = apis.outbound_backend.order_details(orderid)
    assert order_details["success"]
    assert len(order_details["data"]["order"]["line_items"]) > 0
    for line_item in order_details["data"]["order"]["line_items"]:
        assert line_item["requested_quantity"] == 3
