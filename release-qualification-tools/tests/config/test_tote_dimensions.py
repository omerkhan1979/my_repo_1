from pprint import pprint
from pytest import mark
from src.api.takeoff.tsc import TSC
from src.utils.console_printing import cyan


@mark.rq
@mark.smoke
@mark.config
@mark.tote_dimensions
@mark.testrail("374357")
def test_tote_dimensions(tsc: TSC, location_code_tom):
    tote_location_types = tsc.get_tote_location_types(location_code_tom)

    assert len(tote_location_types) > 1, "Tote dimensions is not found"
    pprint(tote_location_types)
    print(cyan("Test case tote_dimensions is:"))
