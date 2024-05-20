from pytest import mark
from src.api.takeoff.decanting import Decanting
from src.utils.console_printing import cyan
from src.api.takeoff.tsc import TSC


@mark.rq
@mark.inbound
@mark.view_po
@mark.testrail("185251")
def test_get_view_po_not_started(decanting: Decanting, tsc: TSC):
    mfc_code = tsc.get_location_code("location-code-gold")

    view_po_response = decanting.get_decanting_tasks_for_view_po(mfc_code)
    found = False
    for x in view_po_response["tasks"]:
        if x["status"] == "not_started":
            found = True
    assert found, "You have more than 1 not started PO"
    print(cyan("Test case view_po_not_started is:"))


@mark.rq
@mark.darkstore
@mark.inbound
@mark.view_po
@mark.retailers("abs", "maf", "smu", "winter", "pinemelon", "tienda")
@mark.testrail("185251")
def test_get_view_po_in_progress(decanting: Decanting, tsc: TSC):
    mfc_code = tsc.get_location_code("location-code-gold")

    view_po_response = decanting.get_decanting_tasks_for_view_po(mfc_code)
    found = False
    for x in view_po_response["tasks"]:
        if x["status"] == "in_progress":
            found = True
    assert found, "You have more than 1 in progress PO"
    print(cyan("Test case view_po_in_progress is:"))
