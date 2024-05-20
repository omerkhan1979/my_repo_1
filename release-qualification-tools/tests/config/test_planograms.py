from pprint import pprint
from pytest import mark
from src.api.takeoff.tsc import TSC
from src.utils.console_printing import cyan
from src.utils.service_catalog import modify_value


@mark.smoke
@mark.config
@mark.planograms
@mark.testrail("374354")
def test_planograms(tsc: TSC):
    planograms = tsc.get_config_item("MFC_PLANOGRAM", level="mfc")
    parsed_planograms = modify_value(planograms)
    print(parsed_planograms)

    assert "value" in parsed_planograms, "Planogram config item is invalid"
    plaograms = parsed_planograms.get("value")
    assert len(plaograms) > 0, "Should have been at least one planogram"
    pprint(parsed_planograms)
    print(cyan("Test case planograms is:"))
