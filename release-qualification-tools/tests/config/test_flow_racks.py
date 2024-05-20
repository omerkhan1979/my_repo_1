from pytest import mark
from src.api.takeoff.tsc import TSC
from src.utils.console_printing import cyan


@mark.smoke
@mark.config
@mark.flowracks
@mark.testrail("374356")
def test_flow_racks(tsc: TSC, location_code_tom):
    flow_racks_response = tsc.get_flow_racks(location_code_tom)
    is_flow_racks_enabled = tsc.get_config_item_value("IS_FLOW_RACKS_ENABLED")
    flow_racks = flow_racks_response["flow-racks"]
    if bool(is_flow_racks_enabled):
        assert len(flow_racks) > 2, "Flow racks are not found"
    else:
        assert len(flow_racks) == 0, "There should be no flow racks as its disabled"
    print(cyan("Test case flow_racks is:"))
