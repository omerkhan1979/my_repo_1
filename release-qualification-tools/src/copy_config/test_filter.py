from io import StringIO
import json
import os
import pytest
from src.copy_config.exception import CopyConfigErrorCodes, CopyConfigException
from src.copy_config.filter import (
    DISABLE_GOLD_CONFIG_ITEM,
    compare_flow_racks,
    filter_staging_configurations,
    filter_tsc_payload,
)
from src.utils.service_catalog import modify_value
from src.utils.os_helpers import get_cwd

project_root_dir = get_cwd()


def test_empty_filter_tsc_payload():
    assert filter_tsc_payload({"empty": []}) == {"empty": []}


def test_no_change_filter_tsc_payload():
    json_payload = {"no_change": [({"name": "STEVEN", "value": "HELLO"})]}
    result_payload = filter_tsc_payload(json_payload)
    assert len(result_payload) == 1
    assert result_payload["no_change"][0] == json_payload["no_change"][0]


def test_change_filter_tsc_payload():
    json_payload = {
        "change": [
            {"name": "OSR_FTP_HELLO", "value": "HELLO"},
            {"name": "osr_ftp_HELLO", "value": "HELLO"},
            {"name": "WINTER_API__URL", "value": "HELLO"},
            {"name": "TANGERINE_API__URL", "value": "HELLO"},
            {"name": "EXCLUDE", "value": "https://doesnotmatter"},
        ]
    }
    payload = filter_tsc_payload(json_payload)
    assert payload["change"] != json_payload["change"]
    assert len(payload["change"]) == 0


def test_singlechange_filter_tsc_payload():
    json_payload = {
        "singlechange": [
            {"name": "THIS_IS_OK", "value": "\\\\nHELLO", "value-type": "string"},
        ]
    }
    json_expected_payload = {
        "singlechange": [
            {"name": "THIS_IS_OK", "value": "\\nHELLO", "value-type": "string"},
        ]
    }
    assert filter_tsc_payload(json_payload) == json_expected_payload


def test_ode_filter_tsc_payload():
    json_payload = {
        "string_change": [
            {
                "categories": ["features"],
                "name": "is_gold_enabled",
                "value": "true",
                "location-code-tom": None,
                "value-type": "boolean",
            },
        ]
    }
    json_expected_payload = {"string_change": [DISABLE_GOLD_CONFIG_ITEM]}
    assert filter_tsc_payload(json_payload, True) == json_expected_payload


def test_string_change_filter_tsc_payload():
    json_payload = {
        "string_change": [
            {
                "name": "WE ARE OK",
                "value": '"[\\n      {\\n        \\"preliminary\\": \\"23:00\\",\\n        \\"cutoffs\\": [\\n          \\"06:30\\",\\"08:30\\",\\"11:00\\"\\n        ]\\n      },\\n      {\\n        \\"preliminary\\": \\"08:30\\",\\n        \\"cutoffs\\": [\\n          \\"13:00\\",\\"15:00\\",\\"17:00\\"\\n        ]\\n      },\\n      {\\n        \\"delta\\": \\"05:15\\",\\n        \\"cutoffs\\": [\\n          \\"06:30\\"\\n        ]\\n      },\\n    {\\n      \\"delta\\": \\"07:15\\",\\n      \\"cutoffs\\": [\\n        \\"08:30\\"\\n      ]\\n    },\\n    {\\n      \\"delta\\": \\"08:15\\",\\n      \\"cutoffs\\": [\\n        \\"11:00\\"\\n      ]\\n    },\\n    {\\n      \\"delta\\": \\"11:15\\",\\n      \\"cutoffs\\": [\\n        \\"13:00\\"\\n      ]\\n    },\\n\\n    {\\n      \\"delta\\": \\"13:15\\",\\n      \\"cutoffs\\": [\\n        \\"15:00\\"\\n      ]\\n    },\\n    {\\n      \\"delta\\": \\"15:15\\",\\n      \\"cutoffs\\": [\\n        \\"17:00\\"\\n      ]}\\n    ]"',
                "value-type": "string",
            },
        ]
    }
    json_expected_payload = {
        "string_change": [
            {
                "name": "WE ARE OK",
                "value": '[\n      {\n        "preliminary": "23:00",\n        "cutoffs": [\n          "06:30","08:30","11:00"\n        ]\n      },\n      {\n        "preliminary": "08:30",\n        "cutoffs": [\n          "13:00","15:00","17:00"\n        ]\n      },\n      {\n        "delta": "05:15",\n        "cutoffs": [\n          "06:30"\n        ]\n      },\n    {\n      "delta": "07:15",\n      "cutoffs": [\n        "08:30"\n      ]\n    },\n    {\n      "delta": "08:15",\n      "cutoffs": [\n        "11:00"\n      ]\n    },\n    {\n      "delta": "11:15",\n      "cutoffs": [\n        "13:00"\n      ]\n    },\n\n    {\n      "delta": "13:15",\n      "cutoffs": [\n        "15:00"\n      ]\n    },\n    {\n      "delta": "15:15",\n      "cutoffs": [\n        "17:00"\n      ]}\n    ]',
                "value-type": "string",
            },
        ]
    }
    assert filter_tsc_payload(json_payload) == json_expected_payload


def test_multiplechange_filter_tsc_payload():
    json_payload = {
        "multiplechange": [
            {
                "name": "OSR_FTP_HELLO",
                "value": "uppercase_HELLO",
                "value-type": "string",
            },
            {
                "name": "osr_ftp__HELLO",
                "value": "lowercase_HELLO",
                "value-type": "string",
            },
            {"name": "THIS_IS_OK", "value": "\\\\nHELLO", "value-type": "string"},
            {"name": "ISPS_CONFIGURATION_1", "value": '""[]""', "value-type": "string"},
            {"name": "ISPS_CONFIGURATION", "value": '"[]"', "value-type": "string"},
            {"name": "SERVICE_TOKEN", "value": "TOKEN"},
        ]
    }
    json_expected_payload = {
        "multiplechange": [
            {"name": "THIS_IS_OK", "value": "\\nHELLO", "value-type": "string"},
            {"name": "ISPS_CONFIGURATION_1", "value": '"[]"', "value-type": "string"},
            {"name": "ISPS_CONFIGURATION", "value": "[]", "value-type": "string"},
        ]
    }
    assert filter_tsc_payload(json_payload) == json_expected_payload


def test_real_case_filter_tsc_payload():
    with open(os.path.join(f"{project_root_dir}/data/test_config.json"), "r") as file:
        payload = json.loads(file.read())

    results = filter_tsc_payload({"real_case": payload})

    with open(
        os.path.join(f"{project_root_dir}/data/expected_test_config.json"), "r"
    ) as file:
        actual_expected = {"real_case": json.loads(file.read())}
    assert len(results) == len(actual_expected)
    for i in range(len(results["real_case"])):
        assert results["real_case"][i] == actual_expected["real_case"][i]


def test_real_case_maf_filter_tsc_payload():
    with open(
        os.path.join(f"{project_root_dir}/data/test_maf_config.json"), "r"
    ) as file:
        payload = {"real_case_maf": json.loads(file.read())}

    results = filter_tsc_payload(payload)

    with open(
        os.path.join(f"{project_root_dir}/data/expected_maf_copy_config.json"), "r"
    ) as file:
        actual_expected = {"real_case_maf": json.loads(file.read())}
    assert len(results) == len(actual_expected)
    for i in range(len(results["real_case_maf"])):
        assert results["real_case_maf"][i] == actual_expected["real_case_maf"][i]


def test_modify_value():
    expected_value = {
        "categories": ["decanting-ui"],
        "name": "DECANTING_UI_APPROX_LONG_DIVIDER_WEIGHT",
        "value": 0.3800001831,
        "location-code-tom": None,
        "value-type": "numeric",
    }
    input_value = {
        "categories": ["decanting-ui"],
        "name": "DECANTING_UI_APPROX_LONG_DIVIDER_WEIGHT",
        "value": "0.3800001831",
        "location-code-tom": None,
        "value-type": "numeric",
    }
    assert modify_value(input_value) == expected_value


def test_modify_value_string():
    expected_value = {
        "categories": ["rint-sinfonietta"],
        "name": "RINT_SINFONIETTA__INFO__OWNER",
        "value": '"Team Pineapple"',
        "location-code-tom": None,
        "value-type": "string",
    }
    input_value = {
        "categories": ["rint-sinfonietta"],
        "name": "RINT_SINFONIETTA__INFO__OWNER",
        "value": '"\\"Team Pineapple\\""',
        "location-code-tom": None,
        "value-type": "string",
    }
    actual_value = modify_value(input_value)
    print(actual_value)
    assert actual_value == expected_value


def test_modify_value_set():
    input_value = {
        "categories": ["features-ui"],
        "name": "PICK_BY_REQUEST_WEIGHT_ENABLED_MFC",
        "value": '#{"D03" "D02" "SD2"}',
        "value-type": "set",
    }
    expected_value = {
        "categories": ["features-ui"],
        "name": "PICK_BY_REQUEST_WEIGHT_ENABLED_MFC",
        "value": ["D03", "D02", "SD2"],
        "value-type": "set",
    }
    assert modify_value(input_value) == expected_value


def test_filter_staging_configurations():
    json_data = StringIO(
        """{
        "staging-configurations": [{
            "staging-location-code": "0102H010011B",
            "mapped-routes": [{
                "type": "ROUTE",
                "code": "R48",
                "last-modified-at": "2021-12-29T17:13:30Z"
            },  {
                "type": "ROUTE",
                "code": "S61",
                "last-modified-at": "2021-12-29T17:13:30Z"
            }]
        }, {
            "staging-location-code": "0102H010011S",
            "mapped-routes": [{
                "type": "ROUTE",
                "code": "R65",
                "last-modified-at": "2021-12-29T17:13:30Z"
            }, {
                "type": "ROUTE",
                "code": "R42",
                "last-modified-at": "2021-12-29T17:13:30Z"
            }]
        }, {
            "staging-location-code": "0102H010011A",
            "mapped-routes": [{
                "type": "ROUTE",
                "code": "R24",
                "last-modified-at": "2021-12-29T17:13:30Z"
            }, {
                "type": "ROUTE",
                "code": "R01",
                "last-modified-at": "2021-12-29T17:13:30Z"
            }, {
                "type": "ROUTE",
                "code": "R90", "last-modified-at": "2021-12-29T17:13:30Z"
            }]
        }, {
            "staging-location-code": "0102H010012B",
            "mapped-routes": [{
                "type": "ROUTE",
                "code": "R67",
                    "last-modified-at": "2021-12-29T17:13:30Z"
            }, {
                "type": "ROUTE",
                "code": "R44",
                "last-modified-at": "2021-12-29T17:13:30Z"
            }]
        }
        ]
    }
    """
    )
    data = json.load(json_data)
    staging_config = filter_staging_configurations(data)
    assert len(staging_config) == 1
    assert staging_config["staging-configurations"] is not None
    assert len(staging_config["staging-configurations"]) == 4
    assert (
        any("last-modified-at" in d for d in staging_config["staging-configurations"])
        is False
    )


def test_compare_flow_racks_no_source():
    assert compare_flow_racks(None, []) is None


def test_compare_flow_racks_source_error(capsys):
    with pytest.raises(CopyConfigException) as pytest_wrapped_e:
        compare_flow_racks({"OK"}, [])
    out, err = capsys.readouterr()
    assert out == ""
    assert pytest_wrapped_e.type == CopyConfigException
    assert (
        pytest_wrapped_e.value.code_exception
        == CopyConfigErrorCodes.FLOW_RACK_COMPARE_SOURCE
    )
    assert "'set' object is not subscriptable" in err


def test_compare_flow_racks_target_error(capsys):
    with pytest.raises(CopyConfigException) as pytest_wrapped_e:
        compare_flow_racks({"flow-racks": {"OK": "STEVE"}}, [])
    out, err = capsys.readouterr()
    assert out == ""
    assert pytest_wrapped_e.type == CopyConfigException
    assert (
        pytest_wrapped_e.value.code_exception
        == CopyConfigErrorCodes.FLOW_RACK_COMPARE_TARGET
    )
    assert "list indices must be integers or slices" in err


def test_compare_flow_racks_same():
    hello = compare_flow_racks(
        {"flow-racks": {"OK": "STEVE"}, "location-code-tom": "HELLO"},
        {"flow-racks": {"1234": "STEVE"}, "location-code-tom": "HELLO"},
    )
    assert hello is None


def test_compare_flow_racks_generate_error(capsys):
    with pytest.raises(CopyConfigException) as pytest_wrapped_e:
        compare_flow_racks(
            {"flow-racks": {"OK": "STEVE"}}, {"flow-racks": {"1234": "TEVE"}}
        )
    out, err = capsys.readouterr()
    assert out == ""
    assert pytest_wrapped_e.type == CopyConfigException
    assert (
        pytest_wrapped_e.value.code_exception
        == CopyConfigErrorCodes.FLOW_RACK_COMPARE_GENERATE
    )
    assert "location-code-tom" in err


def test_compare_flow_racks():
    assert compare_flow_racks(
        {"location-code-tom": "D02", "flow-racks": {"111111": "STEVE"}},
        {"location-code-tom": "D02", "flow-racks": {"1234": "TEVE"}},
    ) == {"flow-racks": {"1235": "STEVE"}, "location-code-tom": "D02"}
