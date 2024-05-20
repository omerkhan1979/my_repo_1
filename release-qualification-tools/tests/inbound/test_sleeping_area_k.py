from pprint import pprint
from pytest import mark
from src.api.takeoff.distiller import Distiller
from src.utils.console_printing import cyan


@mark.smoke
@mark.inbound
@mark.sleeping_area_k
@mark.testrail("374358")
def test_get_rules_sleeping_area(distiller: Distiller, location_code_retailer):
    sleeping_area_response = distiller.get_rules_sleeping_area(location_code_retailer)

    found = False
    for x in sleeping_area_response["data"][0]["rules"]:
        if x["sleeping-area"] == "K":
            found = True
    assert found, "Sleeping Area K is Not Found"
    pprint(sleeping_area_response)
    print(cyan("Test case sleeping_area_k is:"))
