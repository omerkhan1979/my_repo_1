from src.api.collections import InitializedApis
from pytest_bdd import scenarios, parsers, when, then
from src.utils.place_order import place_order
from src.utils.console_printing import red, blue

scenarios("../features/order_note.feature")


@when(
    parsers.parse('order is created with type "{service_type}" and "{order_note}"'),
    target_fixture="orderid",
)
def create_order_with_note(
    apis: InitializedApis,
    retailer: str,
    service_type: str,
    order_note: str,
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
        order_note=order_note,
    )
    return order_id


@then(parsers.parse('order note field is correctly displayed as "{order_note}"'))
def order_note_field_is_correct(apis: InitializedApis, order_note: str, orderid: str):
    response_note = apis.oms.get_order(orderid)["response"]["order-note"]
    if response_note == order_note:
        print(blue(f"{order_note} for order {orderid} is correctly displayed"))
    else:
        assert False, red(f"{order_note} for order {orderid} is incorrect")
