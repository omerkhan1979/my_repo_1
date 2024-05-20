from unittest.mock import patch
import pytest
import os
import sys

from src.copy_config.copy_tsc import (
    ConfigurationSet,
    CopyTsc,
    config_from_yaml,
)
from src.copy_config.filter import DISABLE_GOLD_CONFIG_ITEM
from src.copy_config.main import cli_parser, main
from src.copy_config.exception import CopyConfigErrorCodes
from src.utils.os_helpers import delete_file

project_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_root_dir)


expected_cli_output = (
    "usage: Copy Configuration [-h] -r RETAILER -s SOURCE_ENV [--path PATH]\n"
    "                          [-t TARGET_ENV] [-l LOCATIONS [LOCATIONS ...]]\n"
    "                          [-ode ODE_PROJECT_NAME] [-p PREVIEW]\n"
    "                          {pull_from_prod,copy_config}\n"
)

expected_required_output = f"{expected_cli_output}Copy Configuration: error: the following arguments are required: "

expected_no_required_cli_output = f"{expected_cli_output} argument "


def nop(iterable, *args, **kwargs):
    return None


def no_location(iterable, *args, **kwargs):
    return [{"location-code-tom": 555, "retailer": "abs"}]


@pytest.fixture
def config_path():
    file_path = f"{project_root_dir}/tests/config-data/abs-0068.yaml"
    yield "resource"
    if os.path.isfile(file_path):
        # after test - remove resource
        os.remove(file_path)


def test_cli_parser_no_args(capsys):
    c = CopyTsc()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli_parser(c, [])
    out, err = capsys.readouterr()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 2
    assert out == ""
    assert expected_cli_output in str(err).strip()


def test_cli_parser_no_retailer(capsys):
    c = CopyTsc()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli_parser(c, ["-s", "abs:qai:9999", "-t", "abs:qai:9999"])
    out, err = capsys.readouterr()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 2
    assert out == ""
    assert expected_cli_output in str(err).strip()
    assert "-r/--retailer" in str(err).strip()


def test_cli_parser_with_source(capsys):
    c = CopyTsc()
    with pytest.raises(Exception) as pytest_wrapped_e:
        cli_parser(c, ["copy_config", "-s", "qai:9999", "-r", "abs"])
    out, err = capsys.readouterr()
    assert pytest_wrapped_e.type == Exception
    assert out == ""
    assert "No target details provided" in str(err).strip()


def test_cli_parser_with_source_target(capsys):
    c = CopyTsc()
    cli_parser(
        c, ["copy_config", "-s", "abs:qai:9999", "-t", "abs:dev:9999", "-r", "maf"]
    )
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""
    assert c.retailer == "maf"
    assert c.mfc_locations == ["D02", "D03"]
    assert c.preview is False


def test_cli_parser_with_source_no_location(capsys):
    capsys.readouterr()  # clear stdouterr
    c_tsc = CopyTsc()
    cli_parser(
        c_tsc, ["copy_config", "-s", "abs:qai:", "-t", "abs:dev:", "-r", "winter"]
    )
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""
    assert c_tsc.retailer == "winter"
    assert c_tsc.preview is False
    assert c_tsc.mfc_locations == ["WF0001", "WF0608"]


def test_cli_parser_with_source_target_preview_invalid(capsys):
    capsys.readouterr()  # clear stdouterr
    c = CopyTsc()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli_parser(
            c, ["-s", "abs:qai:9999", "-t", "abs:dev:9998", "-r", "winter", "-p"]
        )
    out, err = capsys.readouterr()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 2
    assert out == ""
    assert expected_cli_output in str(err).strip()


def test_cli_parser_with_source_target_preview(capsys):
    copy_tsc = CopyTsc()
    cli_parser(
        copy_tsc,
        [
            "copy_config",
            "-s",
            "qai:9999",
            "-t",
            "dev:9998",
            "-r",
            "winter",
            "-p",
            "true",
        ],
    )
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""
    assert copy_tsc.preview is True
    assert copy_tsc.retailer == "winter"
    assert copy_tsc.env_source == "qai"
    assert copy_tsc.env_target == "dev"
    assert copy_tsc.mfc_locations == ["WF0001", "WF0608"]


def test_cli_parser_with_invalid_client(capsys):
    c = CopyTsc()
    with pytest.raises(Exception):
        cli_parser(
            c,
            [
                "copy_config",
                "-s",
                "abs:qai:9999",
                "-t",
                "invalid:dev:9998",
                "-r",
                "invalid",
                "-p",
                "true",
            ],
        )
    out, err = capsys.readouterr()
    assert out == ""
    assert "Client was provided but not valid" in err


def test_cli_parser_with_target_ode(capsys):
    c = CopyTsc()
    cli_parser(
        c,
        [
            "copy_config",
            "-s",
            "abs:qai:9999",
            "-t",
            "ode:ode",
            "-r",
            "abs",
            "-p",
            "true",
        ],
    )
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""
    assert c.mfc_locations == ["0068", "2508"]
    cli_parser(
        c,
        [
            "copy_config",
            "-s",
            "abs",
            "-t",
            "ode",
            "-r",
            "abs",
            "-l",
            "9999",
            "99",
            "-p",
            "true",
        ],
    )
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""
    assert c.mfc_locations == ["9999", "99"]


def test_cli_parser_with_target_ode_project(capsys):
    c = CopyTsc()
    cli_parser(
        c,
        [
            "copy_config",
            "-l",
            "9999",
            "99",
            "-s",
            "qai",
            "-r",
            "abs",
            "-t",
            "ode",
            "--ode_project_name",
            "cc-steve",
            "-p",
            "true",
        ],
    )
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""
    assert c.mfc_locations == ["9999", "99"]
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli_parser(
            c,
            [
                "copy_config",
                "-l" "9999",
                "99",
                "-s",
                "qai",
                "-r",
                "abs",
                "-t",
                "ode",
                "--ode_project_name",
                "cc-steve",
                "-p",
                "true",
            ],
        )
    out, err = capsys.readouterr()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 2
    assert out == ""
    assert expected_cli_output in err


def test_cli_parser_with_multiple_locations_different_order(capsys):
    c = CopyTsc()
    cli_parser(
        c,
        [
            "copy_config",
            "-r",
            "abs",
            "-l",
            "6666",
            "99",
            "-s",
            "abs:qai",
            "-t",
            "abs:ode",
            "--ode_project_name",
            "cc-steve",
        ],
    )
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""
    assert c.mfc_locations == ["6666", "99"]


def test_cli_parser_with_multiple_locations(capsys):
    c = CopyTsc()
    cli_parser(
        c,
        [
            "copy_config",
            "-s",
            "qai",
            "-t",
            "ode",
            "--ode_project_name",
            "cc-steve",
            "-r",
            "abs",
            "-l",
            "9999",
            "99",
        ],
    )
    out, err = capsys.readouterr()
    assert out == ""
    assert err == ""
    assert c.mfc_locations == ["9999", "99"]
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        cli_parser(
            c,
            [
                "copy_config",
                "-s",
                "qai",
                "-t",
                "ode",
                "--ode_project_name",
                "-r",
                "abs",
                "-l",
                "9999",
                "99",
            ],
        )
    out, err = capsys.readouterr()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 2
    assert out == ""
    assert expected_cli_output in err


@pytest.mark.usefixtures("gcp_config_mocks")
@patch("src.copy_config.copy_tsc.CopyTsc.update_target_location", nop)
@patch("src.api.takeoff.tsc.TSC.put_config_items", nop)
@patch("src.copy_config.copy_tsc.CopyTsc.update_non_standard_tsc", nop)
def test_main(capsys):
    with patch(
        "sys.argv",
        ["copy_tsc", "copy_config", "-s", "qai:9999", "-t", "dev:999", "-r", "abs"],
    ):
        with patch(
            "src.copy_config.check.check_values",
            return_value=[True, True],
        ):
            with patch(
                "src.config.config.is_location_code_tom_valid",
                return_value="9999",
            ):
                with patch(
                    "src.api.takeoff.tsc.TSC.get_config_items",
                    return_value=[{"value": "STEVE", "name": "HELLLOTHERE"}],
                ):
                    with patch(
                        "src.copy_config.main.retrieval_source",
                        return_value=ConfigurationSet(
                            config_items={
                                "9999": [{"value": 9999, "name": "mfc"}],
                                "env": [{"value": "value", "name": "name2"}],
                            },
                            flow_racks={
                                "location-code-tom": "9999",
                                "flow-racks": {"1": "Hello"},
                            },
                            spokes={
                                "9999": [{"location-id": 9999, "mfc-ref-code": "mfc"}]
                            },
                            tote_types={"Hello": 1},
                            staging_config={
                                "staging-configurations": [
                                    {
                                        "staging-location-code": "0405H010011A",
                                        "mapped-routes": [
                                            {
                                                "type": "ROUTE",
                                                "code": "codeRoute",
                                                "last-modified-at": "2023-05-15T22:14:10Z",
                                            }
                                        ],
                                    }
                                ]
                            },
                            staging_locations={
                                "staging-locations": [
                                    {
                                        "default": "false",
                                        "mfc-tom-code": "9999",
                                        "staging-location-code": "0405H010011A",
                                    }
                                ]
                            },
                            src_routes={
                                "routes": [
                                    {
                                        "mfc-tom-code": "9999",
                                        "route-code": "codeRoute",
                                    }
                                ]
                            },
                            locations={
                                "timezone": "America/New_York",
                                "location-type": "spoke",
                                "mfc-ref-code": "WF0001",
                                "location-address": {
                                    "state": "NJ",
                                    "iso-state": "US-NJ",
                                    "city": "Wayne",
                                    "street": "Wayne Hills Mall",
                                    "zip-code": "07470",
                                },
                                "location-pickup": {
                                    "lat": 40.9626000,
                                    "lon": 74.2401000,
                                },
                                "location-name": "ShopRite of Wayne Hills Mall",
                                "location-contact-phone": "0000-000-000",
                                "location-service-info": {
                                    "phone": "0000-000-000",
                                    "desctext": "Text Placeholder",
                                    "email": "testqa@takeoff.com",
                                },
                                "location-id": 30,
                                "location-code-retailer": "217",
                                "location-code-tom": "9999",
                            },
                        ),
                    ):
                        main()
                    out, err = capsys.readouterr()
                    assert "----Executing Copy Configuration----" in out
                    assert "----Copy Configuration Completed----" in out
                    assert err == ""


@pytest.mark.usefixtures("gcp_config_mocks")
@patch.dict(os.environ, {"SERVICE_WORKER_TOKEN": "ondemand_dummy_worker_token"})
@patch("src.copy_config.copy_tsc.CopyTsc.update_target_location", nop)
@patch("src.api.takeoff.tsc.TSC.put_config_items", nop)
@patch("src.copy_config.copy_tsc.CopyTsc.update_non_standard_tsc", nop)
def test_main_ode(capsys):
    with patch(
        "sys.argv",
        [
            "copy_tsc",
            "copy_config",
            "-s",
            "qai",
            "-t",
            "ode",
            "--ode_project_name",
            "cc-steve",
            "-r",
            "abs",
        ],
    ):
        with patch(
            "src.copy_config.check.check_values",
            return_value=[True, True],
        ):
            with patch(
                "src.config.config.is_location_code_tom_valid",
                return_value="9999",
            ):
                with patch(
                    "src.api.takeoff.tsc.TSC.get_config_items",
                    return_value=[{"value": "STEVE", "name": "HELLLOTHERE"}],
                ):
                    with patch(
                        "src.copy_config.main.retrieval_source",
                        return_value=ConfigurationSet(
                            config_items={
                                "env": [
                                    {
                                        "value": 9999,
                                        "name": "mfc",
                                    }
                                ],
                                "9999": [DISABLE_GOLD_CONFIG_ITEM],
                            },
                            flow_racks={},
                            spokes={},
                            tote_types={},
                            staging_config={
                                "staging-configurations": [
                                    {
                                        "staging-location-code": "0405H010011A",
                                        "mapped-routes": [
                                            {
                                                "type": "ROUTE",
                                                "code": "codeRoute",
                                                "last-modified-at": "2023-05-15T22:14:10Z",
                                            }
                                        ],
                                    }
                                ]
                            },
                            staging_locations={
                                "staging-locations": [
                                    {
                                        "default": "false",
                                        "mfc-tom-code": "9999",
                                        "staging-location-code": "0405H010011A",
                                    }
                                ]
                            },
                            src_routes={
                                "routes": [
                                    {
                                        "mfc-tom-code": "9999",
                                        "route-code": "codeRoute",
                                    }
                                ]
                            },
                            locations={
                                "location-id": 1,
                                "mfc-ref-code": "mfc",
                                "location-code-tom": "9999",
                                "location-service-info": {"desctext": "some text Test"},
                            },
                        ),
                    ):
                        with patch(
                            "src.api.takeoff.tsc.TSC.get_locations",
                            return_value=[
                                {
                                    "location-type": "spoke",
                                    "mfc-ref-code": "4443",
                                    "location-pickup": {"lat": 0, "lon": 0},
                                    "location-name": "test1234",
                                    "location-id": 1234,
                                    "location-code-retailer": "test",
                                    "location-code-tom": "test",
                                    "location-code-gold": "test",
                                }
                            ],
                        ):
                            main()
                        out, err = capsys.readouterr()
                        assert "----Executing Copy Configuration----" in out
                        assert "----Copy Configuration Completed----" in out
                        assert err == ""


@pytest.mark.usefixtures("gcp_config_mocks")
@patch("src.api.takeoff.tsc.TSC.get_enabled_mfc_locations", no_location)
def test_main_pull_from_prod(capsys):
    retrieval_source = ConfigurationSet(
        config_items={
            "9999": [{"value": 9999, "name": "mfc"}],
            "env": [{"value": "value", "name": "name2"}],
        },
        flow_racks={
            "location-code-tom": "9999",
            "flow-racks": {"1": "Hello"},
        },
        spokes={"9999": [{"location-id": 9999, "mfc-ref-code": "mfc"}]},
        tote_types={"Hello": 1},
        staging_config={
            "staging-configurations": [
                {
                    "staging-location-code": "0405H010011A",
                    "mapped-routes": [
                        {
                            "type": "ROUTE",
                            "code": "codeRoute",
                            "last-modified-at": "2023-05-15T22:14:10Z",
                        }
                    ],
                }
            ]
        },
        staging_locations={
            "staging-locations": [
                {
                    "default": "false",
                    "mfc-tom-code": "9999",
                    "staging-location-code": "0405H010011A",
                }
            ]
        },
        src_routes={
            "routes": [
                {
                    "mfc-tom-code": "9999",
                    "route-code": "codeRoute",
                }
            ]
        },
        locations={
            "timezone": "America/New_York",
            "location-type": "spoke",
            "mfc-ref-code": "WF0001",
            "location-address": {
                "state": "NJ",
                "iso-state": "US-NJ",
                "city": "Wayne",
                "street": "Wayne Hills Mall",
                "zip-code": "07470",
            },
            "location-pickup": {
                "lat": 40.9626000,
                "lon": 74.2401000,
            },
            "location-name": "ShopRite of Wayne Hills Mall",
            "location-contact-phone": "0000-000-000",
            "location-service-info": {
                "phone": "0000-000-000",
                "desctext": "Text Placeholder",
                "email": "testqa@takeoff.com",
            },
            "location-id": 30,
            "location-code-retailer": "217",
            "location-code-tom": "9999",
        },
    )
    with patch(
        "sys.argv",
        [
            "copy_tsc",
            "pull_from_prod",
            "-s",
            "prod",
            "-t",
            "ode",
            "--ode_project_name",
            "prj-oz1111",
            "-r",
            "abs",
            "--locations",
            "555",
        ],
    ):
        with patch(
            "src.config.config.is_location_code_tom_valid",
            return_value="555",
        ):
            with patch(
                "src.copy_config.main.retrieval_source", return_value=retrieval_source
            ):
                test_file = "tests/config-data/abs-555.yaml"
                project_root_dir = os.path.dirname(
                    os.path.dirname(os.path.dirname(__file__))
                )
                path = os.path.join(project_root_dir, test_file)
                with patch(
                    "src.copy_config.main.get_configs_file_path", return_value=path
                ):
                    main()
                    out, err = capsys.readouterr()
                    assert "Parsing passed in arguments" in out
                    assert err == ""
                    with patch(
                        "src.copy_config.copy_tsc.copy_file_from_repo",
                        return_value=path,
                    ):
                        loaded_config = config_from_yaml(path)
                        assert loaded_config == retrieval_source
                        delete_file(path)


@pytest.mark.usefixtures("gcp_config_mocks")
def test_main_preview(capsys):
    with patch(
        "sys.argv",
        [
            "copy_tsc",
            "copy_config",
            "-s",
            "qai",
            "-t",
            "dev",
            "-r",
            "winter",
            "-p",
            "true",
        ],
    ):
        with patch(
            "src.config.config.is_location_code_tom_valid",
            return_value="WF0001",
        ):
            with patch(
                "src.api.takeoff.tsc.TSC.get_config_items",
                return_value=[{"value": "STEVE", "name": "HELLLOTHERE"}],
            ):
                with patch(
                    "src.copy_config.main.retrieval_source",
                    return_value=ConfigurationSet(
                        config_items={
                            "WF0001": [
                                {
                                    "value": 1001,
                                    "name": "RINT_ETL__RETRY_POLICY__DEFAULT__WAIT_DURATION_IN_MS",
                                }
                            ],
                            "env": [
                                {
                                    "name": "DECANTING_UI_APPROX_LONG_DIVIDER_WEIGHT",
                                    "value": 0.837757,
                                }
                            ],
                        },
                        flow_racks={},
                        spokes={
                            "WF0001": [{"location-id": 9990, "mfc-ref-code": "mfc"}]
                        },
                        tote_types={},
                        staging_config={
                            "staging-configurations": [
                                {
                                    "staging-location-code": "0405H010011A",
                                    "mapped-routes": [
                                        {
                                            "type": "ROUTE",
                                            "code": "cancel",
                                            "last-modified-at": "2023-05-15T22:14:10Z",
                                        }
                                    ],
                                }
                            ]
                        },
                        staging_locations={
                            "staging-locations": [
                                {
                                    "default": "false",
                                    "mfc-tom-code": "WF0001",
                                    "staging-location-code": "0405H010011A",
                                }
                            ]
                        },
                        src_routes={
                            "routes": [
                                {"mfc-tom-code": "WF0001", "route-code": "cancel"}
                            ]
                        },
                        locations={
                            "location-id": 1,
                            "mfc-ref-code": "mfc",
                            "location-code-tom": "WF0001",
                            "location-service-info": {"desctext": "some text Test"},
                        },
                    ),
                ):
                    main()
                    out, err = capsys.readouterr()
                    assert err == ""
                    assert "----Executing Copy Configuration----" in out
                    assert (
                        '----Retrieving the tsc data from source evn "qai" for retailer "winter" for location "WF0001"----'
                        in out
                    )
                    assert "----Parsing passed in arguments----" in out
                    assert "Preview was requested" in out
                    assert (
                        "The following would be the list of config items that would be updated:"
                        in out
                    )
                    assert "Preview ended" in out
                    assert "----Copy Configuration Completed----" in out


@pytest.mark.usefixtures("gcp_config_mocks")
@patch("src.copy_config.copy_tsc.CopyTsc.update_target_location", nop)
def test_main_error_target_update(capsys, config_path):
    with patch(
        "sys.argv",
        ["copy_tsc", "copy_config", "-r", "abs", "-s", "qai:9990", "-t", "dev:9990"],
    ):
        with patch(
            "src.config.config.is_location_code_tom_valid",
            return_value="9990",
        ):
            with patch(
                "src.copy_config.main.retrieval_source",
                return_value=ConfigurationSet(
                    config_items={"WF0001": {"value": 9999, "name": "mfc"}},
                    flow_racks={},
                    spokes={"WF0001": [{"location-id": 9990, "mfc-ref-code": "mfc"}]},
                    tote_types={},
                    staging_config={},
                    staging_locations={"Hello": 1},
                    src_routes={},
                    locations={"0068": [{"location-id": 68, "mfc-ref-code": "mfc"}]},
                ),
            ):
                main()
                out, err = capsys.readouterr()
                assert "----Executing Copy Configuration----" in out
                assert "----Copy Configuration Completed----" not in out
                assert CopyConfigErrorCodes.FAILED_TARGET_UPDATE.name in err
                assert "----Copy Configuration Failed----" in err


def test_main_error_get_source(capsys):
    with patch(
        "sys.argv",
        [
            "copy_tsc",
            "copy_config",
            "-r",
            "abs",
            "-s",
            "qai:9999",
            "-t",
            "dev",
            "-l",
            "9999",
        ],
    ):
        with patch(
            "src.api.takeoff.tsc.TSC.get_config_items",
            side_effect=KeyError("bad"),
        ):
            main()
            out, err = capsys.readouterr()
            assert "----Executing Copy Configuration----" in out
            assert "----Copy Configuration Completed----" not in out
            assert CopyConfigErrorCodes.FAILED_SOURCE_RETRIEVAL.name in err
            assert "----Copy Configuration Failed----" in err


@pytest.mark.usefixtures("gcp_config_mocks")
@patch("src.copy_config.copy_tsc.CopyTsc.update_target_location", nop)
@patch("src.api.takeoff.tsc.TSC.put_config_items", nop)
@patch("src.copy_config.copy_tsc.CopyTsc.update_non_standard_tsc", nop)
def test_main_from_file(capsys):
    with patch(
        "sys.argv",
        [
            "copy_tsc",
            "copy_config",
            "-s",
            "file",
            "-t",
            "dev",
            "-r",
            "winter",
            "-l",
            "9999",
        ],
    ):
        with patch(
            "src.copy_config.check.check_values",
            return_value=[True, True],
        ):
            with patch(
                "src.config.config.is_location_code_tom_valid",
                return_value="9999",
            ):
                with patch(
                    "src.copy_config.main.retrieval_source",
                    return_value=ConfigurationSet(
                        config_items={
                            "9999": [{"value": 9999, "name": "mfc"}],
                            "env": [{"value": "value", "name": "name2"}],
                        },
                        flow_racks={"flow-racks": {"1": "Hello"}},
                        spokes={},
                        tote_types={},
                        staging_config={
                            "staging-configurations": [
                                {
                                    "staging-location-code": "0069H010011C",
                                    "mapped-routes": [
                                        {
                                            "type": "ROUTE",
                                            "code": "codeRoute",
                                            "last-modified-at": "2023-05-15T22:14:10Z",
                                        }
                                    ],
                                }
                            ]
                        },
                        staging_locations={
                            "staging-locations": [
                                {
                                    "default": "false",
                                    "mfc-tom-code": "9999",
                                    "staging-location-code": "0405H010011A",
                                }
                            ]
                        },
                        src_routes={
                            "routes": [
                                {
                                    "mfc-tom-code": "9999",
                                    "route-code": "codeRoute",
                                }
                            ]
                        },
                        locations={
                            "location-id": 1,
                            "mfc-ref-code": "mfc",
                            "location-code-tom": "9999",
                            "location-service-info": {"desctext": "some text Test"},
                        },
                    ),
                ):
                    with patch(
                        "src.copy_config.main.get_configs_file_path",
                        return_value="tests/config-data/winter-9999.yaml",
                    ):
                        test_file = "tests/config-data/winter-9999.yaml"
                        project_root_dir = os.path.dirname(
                            os.path.dirname(os.path.dirname(__file__))
                        )
                        path = os.path.join(project_root_dir, test_file)
                        with patch(
                            "src.copy_config.copy_tsc.copy_file_from_repo",
                            return_value=path,
                        ):
                            main()
                    out, err = capsys.readouterr()
                    assert "----Executing Copy Configuration----" in out
                    assert "----Copy Configuration Completed----" in out
                    assert err == ""
