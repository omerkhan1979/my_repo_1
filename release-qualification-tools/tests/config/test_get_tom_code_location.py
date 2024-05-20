from pprint import pprint
from pytest import mark

from src.api.takeoff.tsc import TSC


@mark.config
@mark.rq
@mark.get_tom_code_location
@mark.testrail("166265")
def test_get_tom_code_locations(tsc: TSC, location_code_tom):
    get_tom_code_response = tsc.get_tom_code_locations()
    for x in get_tom_code_response:
        if x["location-code-tom"] == location_code_tom:
            found = True
    assert found, "Not Found!"
    pprint(get_tom_code_response)
