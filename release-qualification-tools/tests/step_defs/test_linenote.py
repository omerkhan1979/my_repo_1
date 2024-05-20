from src.api.collections import InitializedApis
from pytest_bdd import scenarios, parsers, when, then
from src.utils.place_order import place_order

scenarios("../features/line_note.feature")


@when(
    parsers.parse(
        'order is created with type "{service_type}" and "{line_note}" for the product in order'
    ),
    target_fixture="orderid",
)
def create_order_with_line_note(
    apis: InitializedApis,
    retailer: str,
    service_type: str,
    line_note: str,
    products: dict,
) -> str:
    order_id = place_order(
        rint=apis.rint,
        retailer=retailer,
        products=products["order_flow_data"]["all_products"],
        store_id=products["order_flow_data"]["store_id"],
        spoke_id=products["order_flow_data"]["spoke_id"],
        stage_by_datetime=products["order_flow_data"]["stage_by_datetime"],
        service_window_start=products["order_flow_data"]["service_window_start"],
        route_id=products["order_flow_data"]["route_id"],
        ims=apis.ims_admin,
        oms=apis.oms,
        add_flo_stock=products["flo_stock"],
        ecom_service_type=service_type,
        line_note=line_note,
    )
    return order_id


@then(
    parsers.parse(
        "the line_note field for the product in the order is returned as {line_note} via API call"
    )
)
def line_note_field_is_correct(apis: InitializedApis, line_note: str, orderid: str):
    response_note = apis.oms.get_order(orderid)
    assert line_note == response_note["response"]["line-items"][0]["line-note"]
