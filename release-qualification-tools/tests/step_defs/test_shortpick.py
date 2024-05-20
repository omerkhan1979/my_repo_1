from pytest_bdd import scenarios, then, when, parsers
from src.api.collections import InitializedApis
from src.utils.console_printing import green, blue
from src.utils.helpers import wait_order_status_changed
from src.utils.picklist_helpers import process_picklist_OOS
from src.utils.user import AuthServiceUser

scenarios("../features/short_pick.feature")


@when(
    parsers.parse('user processes "{picklist_type}" picklist for zero quantity'),
    target_fixture="orderid",
)
def process_picklist_without_quantity(
    apis: InitializedApis,
    close_all_open_picklists,
    operator_user: AuthServiceUser,
    picklist_type: str,
    orderid_zero_stock_products: dict,
) -> str:
    orderid = orderid_zero_stock_products.get("orderid")
    close_all_open_picklists,
    cutoff = apis.oms.get_order(orderid)["response"]["cutoff-datetime"]
    process_picklist_OOS(
        apis,
        cutoff,
        operator_user,
        picklist_type,
    )
    return orderid


@when(parsers.parse('order status changed to "{status}"'))
def check_status(apis: InitializedApis, orderid: str, status: str) -> None:
    if wait_order_status_changed(orderid, status, apis.oms):
        print(blue(f"Order's status changed to {status}"))


@then("validate the product is short picked and line note updated to out of stock")
def check_out_of_stock(apis: InitializedApis, orderid: str) -> None:
    data = apis.outbound_backend.order_details(orderid)
    value = data["data"]["order"]["line_items"][0]["value"]
    if value == 0:
        print(green("Products are out of Stock"))
        print("Test Pass: Product is getting short picked")
    else:
        raise AssertionError("Test fails: Product is not getting short picked")
