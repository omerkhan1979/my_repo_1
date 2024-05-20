from src.api.collections import InitializedApis
from pytest_bdd import scenarios, when, then, parsers
from src.utils.console_printing import green, cyan
from src.utils.helpers import wait_order_status_changed, get_order_status

scenarios("../features/update_ecom_status.feature")


@when(parsers.parse('ecom status is updated with "{target_ecom_status}"'))
def update_ecom_status(apis: InitializedApis, orderid: str, target_ecom_status: str):
    location_code_retailer = apis.tsc.get_location_code("location-code-retailer")
    apis.rint.update_co_ecom_status(location_code_retailer, orderid, target_ecom_status)


@then(parsers.parse('ecom status after update should be "{expected_mfc_status}"'))
def ecom_status_after_update(
    apis: InitializedApis, orderid: str, expected_mfc_status: str
):
    wait_order_status_changed(orderid, expected_mfc_status, apis.oms)
    order_status = get_order_status(orderid, apis.oms)
    print(green(f"\nOrder status: {order_status}"))
    assert order_status == expected_mfc_status
    print(cyan("Test case update_ecom_status is:"))
