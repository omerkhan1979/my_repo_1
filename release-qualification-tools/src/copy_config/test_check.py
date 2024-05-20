from unittest.mock import patch
import pytest
import requests_mock
from src.api.takeoff.tsc import TSC
from src.config.config import Config

from src.copy_config.check import check_config_items, check_values, sanity_check
from src.copy_config.exception import CopyConfigErrorCodes, CopyConfigException
from src.copy_config.filter import DISABLE_GOLD_CONFIG_ITEM
from src.utils.config import get_url_builder
from src.utils.os_helpers import get_cwd
from src.utils.locations import locations_endpoint

project_root_dir = get_cwd()


@pytest.fixture
def tsc_fixture():
    url_builder = get_url_builder("api/", "service-catalog")
    request_url = url_builder(
        retailer="fake",
        env="qai",
        rel=locations_endpoint,
    )
    with patch(
        "src.config.config.is_location_code_tom_valid",
        return_value="9999",
    ):
        with requests_mock.Mocker() as n:
            n.get(
                "https://fake-qai.tom.takeoff.com/",
                status_code=200,
                json={},
            )
            with requests_mock.Mocker() as m:
                m.get(request_url, status_code=200, json={})
                cfg = Config(
                    "fake",
                    "qai",
                    "9999",
                    "anything",
                    "",
                    disallow=False,
                )
                return TSC(cfg)


def test_empty_sanity_check():
    assert check_config_items([], []) is True, []


def test_empty_source_sanity_check(capsys):
    json_payload = [{"name": "STEVEN"}]
    assert (
        check_config_items([], json_payload, require_no_unexpected_data=True) is False
    )
    out, err = capsys.readouterr()
    assert (
        "target configuration had config items that didn't exist in source, see list below:\x1b[0m\n\x1b[1m❌ [{'name': 'STEVEN'}]"
        in out
    )
    assert err == ""


def test_check_config_items(capsys):
    json_payload = [{"name": "STEVEN"}]
    json_payload_others = [{"name": "FTP_CONNECTION"}]
    assert (
        check_config_items(
            json_payload, json_payload_others, require_no_unexpected_data=True
        )
        is False
    )
    out, err = capsys.readouterr()
    assert err == ""
    assert "[{'name': 'FTP_CONNECTION'}]" in out
    assert "target configuration had config items that didn't exist in source" in out


def test_check_config_items_string_failure(capsys):
    json_payload = [
        {
            "categories": ["rint-sinfonietta"],
            "name": "RINT_SINFONIETTA__INFO__OWNER",
            "value": '"\\"Team Pineapple\\"',
            "location-code-tom": None,
            "value-type": "string",
        }
    ]
    json_payload_others = [
        {
            "categories": ["rint-sinfonietta"],
            "name": "RINT_SINFONIETTA__INFO__OWNER",
            "value": '"\\"\\\\\\"Team Pineapple\\\\\\"',
            "location-code-tom": None,
            "value-type": "string",
        }
    ]
    assert check_config_items(json_payload, json_payload_others) is False
    out, err = capsys.readouterr()
    assert err == ""
    assert "'name': 'RINT_SINFONIETTA__INFO__OWNER'" in out
    assert "did not match with\ntarget config item" in out


def test_check_config_items_string_ok(capsys):
    json_payload = [
        {
            "categories": ["rint-sinfonietta"],
            "name": "RINT_SINFONIETTA__INFO__OWNER",
            "value": '"\\"Team Pineapple\\""',
            "location-code-tom": None,
            "value-type": "string",
        }
    ]
    json_payload_others = [
        {
            "categories": ["rint-sinfonietta"],
            "name": "RINT_SINFONIETTA__INFO__OWNER",
            "value": '"\\"Team Pineapple\\""',
            "location-code-tom": None,
            "value-type": "string",
        }
    ]
    assert check_config_items(json_payload, json_payload_others) is True
    out, err = capsys.readouterr()
    print(out)
    assert err == ""
    assert out == ""


def test_ode_check_config_items(capsys):
    json_payload = [
        {"name": "STEVEN", "value": "HELLO"},
        {
            "categories": ["features"],
            "name": "is_gold_enabled",
            "value": True,
            "location-code-tom": None,
            "value-type": "boolean",
        },
    ]
    json_payload_others = [
        {"name": "STEVEN", "value": "HELLO"},
        DISABLE_GOLD_CONFIG_ITEM,
    ]
    assert check_config_items(json_payload, json_payload_others, True) is True
    out, err = capsys.readouterr()
    assert err == ""
    assert out == ""


def test_check_value_name_differs(capsys):
    json_payload = [{"name": "STEVEN"}]
    json_payload_others = [{"name": "FTP_CONNECTION"}]
    assert check_values(json_payload, json_payload_others) == (
        False,
        [{"name": "STEVEN"}],
    )
    out, err = capsys.readouterr()
    assert err == ""
    assert "\x1b[1m❌ The difference was: [{'name': 'STEVEN'}]\x1b[0m\n" in out


def test_check_value_value_differs(capsys):
    json_payload = [{"name": "STEVEN", "value": "HAPPYNO"}]
    json_payload_others = [{"name": "STEVEN", "value": "HAPPY"}]
    assert check_values(json_payload, json_payload_others) == (
        False,
        [{"name": "STEVEN", "value": "HAPPYNO"}],
    )
    out, err = capsys.readouterr()
    assert err == ""
    assert (
        "\x1b[1m❌ The difference was: [{'name': 'STEVEN', 'value': 'HAPPYNO'}]\x1b[0m\n"
        in out
    )


def test_check_value(capsys):
    json_payload = [{"name": "STEVEN", "value": "HAPPY"}]
    json_payload_others = [{"name": "STEVEN", "value": "HAPPY"}]
    assert check_values(json_payload, json_payload_others) == (True, [])
    out, err = capsys.readouterr()
    assert err == ""
    assert out == ""


def test_check_config_items_with_same(capsys):
    json_payload = [
        {"name": "STEVEN", "value": "does not matter"},
        {"name": "FTP__CONNECTION", "value": "XXXXX"},
    ]
    json_payload_others = [
        {"name": "STEVEN", "value": "does not matter"},
        {"name": "FTP__CONNECTION", "value": "does not matter"},
    ]
    assert check_config_items(json_payload, json_payload_others) is True
    out, err = capsys.readouterr()
    assert err == ""
    assert "[{'name': 'FTP__CONNECTION'}]" not in out
    assert (
        "source config item: {'name': 'STEVEN', 'value': 'does not matter'} did not exist in target configuration"
        not in out
    )
    assert (
        "target configuration had config items that didn't exist in source" not in out
    )


@pytest.mark.usefixtures("gcp_config_mocks")
def test_empty_target_sanity_check(tsc_fixture, capsys):
    with pytest.raises(CopyConfigException) as pytest_wrapped_e:
        with patch(
            "src.api.takeoff.tsc.TSC.get_config_items",
            return_value=[{"name": "STEVEN"}],
        ):
            sanity_check(tsc_fixture, tsc_fixture, True)
    out, err = capsys.readouterr()
    assert out == ""
    assert pytest_wrapped_e.type == CopyConfigException
    assert (
        pytest_wrapped_e.value.code_exception
        == CopyConfigErrorCodes.SANITY_CHECK_FAILURE
    )
    assert "Valid token must be provided as the sys env TSC_X_TOKEN" not in err


@pytest.mark.usefixtures("gcp_config_mocks")
def test_ode_target_sanity_check(tsc_fixture, capsys):
    with pytest.raises(CopyConfigException) as pytest_wrapped_e:
        with patch(
            "src.api.takeoff.tsc.TSC.get_config_items",
            return_value=[{"name": "STEVEN"}],
        ):
            sanity_check(tsc_fixture, None)
    out, err = capsys.readouterr()
    assert out == ""
    assert pytest_wrapped_e.type == CopyConfigException
    assert (
        pytest_wrapped_e.value.code_exception
        == CopyConfigErrorCodes.SANITY_CHECK_FAILURE
    )
    assert "Valid token must be provided as the sys env TSC_X_TOKEN" not in err
