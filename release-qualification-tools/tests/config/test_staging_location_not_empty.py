from pprint import pprint
from pytest import mark
from src.api.takeoff.tsc import TSC
from src.utils.console_printing import cyan


@mark.smoke
@mark.config
@mark.staging_location_not_empty
@mark.testrail("374355")
def test_get_staging_location(tsc: TSC, location_code_tom):
    staging_location_response = tsc.get_staging_locations(location_code_tom)

    staging_locations = staging_location_response["staging-locations"]

    assert len(staging_locations) > 0, "Staging location has no info!"
    pprint(staging_location_response)
    print(cyan("Test case staging_location_not_empty is:"))
