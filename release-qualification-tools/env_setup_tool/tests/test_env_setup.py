import os
from unittest.mock import patch, Mock

import pytest
import requests_mock
from typer.testing import CliRunner
from env_setup_tool.src.config_types import ConfigType

from env_setup_tool.src.env_setup import env_setup_tool
from env_setup_tool.src.feature_file import FeatureFile


@pytest.fixture
def runner():
    return CliRunner()


# poetry run pytest env_setup_tool/tests/test_env_setup.py -s --tb=long


@patch.dict(
    os.environ,
    {
        "SERVICE_WORKER_TOKEN": "ondemand_dummy_worker_token",
        "RETAILER_CONFIGURATION": "retailer",
    },
)
@patch(
    "env_setup_tool.src.config_providers.sleeping_area_rules_provider.SleepingAreaRulesProvider"
)
@patch("env_setup_tool.src.config_providers.ims_provider.ImsProvider")
@patch("env_setup_tool.src.config_providers.tsc_provider.TscProvider")
@patch(
    "env_setup_tool.src.config_providers.product_catalog_provider.ProductCatalogProvider"
)
@patch("env_setup_tool.src.config_providers.wave_planner_provider.WavePlannerProvider")
def test_apply_configs_sequence(
    mock_wave_planner_provider,
    mock_product_catalog_provider,
    mock_tsc_provider,
    mock_ims_provider,
    mock_sleeping_area_rules_provider,
    runner,
):
    ff_file = [
        FeatureFile.from_yaml(
            "env_setup_tool/tests/test_data",
            "base.yaml",
        )
    ]
    with patch("env_setup_tool.src.utils.load_feature", return_value=ff_file):
        with patch(
            "src.config.config.get_gcp_project_id",
            return_value="random-gcp-project-id",
        ):
            with patch(
                "src.config.config.get_firebase_key",
                return_value="FIREBASE_KEY",
            ):
                call_order = []
                manager = Mock()
                with patch.object(
                    mock_tsc_provider,
                    "apply",
                    return_value=True,
                    side_effect=call_order.append("tsc"),
                ), patch.object(
                    mock_ims_provider,
                    "apply",
                    return_value=True,
                    side_effect=call_order.append("ims"),
                ), patch.object(
                    mock_sleeping_area_rules_provider,
                    "apply",
                    return_value=True,
                    side_effect=call_order.append("sleeping_area_rules"),
                ), patch.object(
                    mock_wave_planner_provider,
                    "apply",
                    return_value=True,
                    side_effect=call_order.append("waves"),
                ), patch.object(
                    mock_product_catalog_provider,
                    "apply",
                    return_value=True,
                    side_effect=call_order.append("product_catalog"),
                ):
                    expected_sequence = [
                        "tsc",
                        "ims",
                        "sleeping_area_rules",
                        "waves",
                        "product_catalog",
                    ]
                    manager.attach_mock(mock_tsc_provider.apply, expected_sequence[0])
                    manager.attach_mock(mock_ims_provider.apply, expected_sequence[1])
                    manager.attach_mock(
                        mock_sleeping_area_rules_provider.apply, expected_sequence[2]
                    )
                    manager.attach_mock(
                        mock_wave_planner_provider.apply, expected_sequence[3]
                    )
                    manager.attach_mock(
                        mock_product_catalog_provider.apply, expected_sequence[4]
                    )
                    with patch.dict(
                        "env_setup_tool.src.config_providers.config_provider_mapping.config_providers",
                        {
                            ConfigType.TSC: mock_tsc_provider,
                            ConfigType.IMS: mock_ims_provider,
                            ConfigType.SleepingAreaRules: mock_sleeping_area_rules_provider,
                            ConfigType.WAVE_PLANS: mock_wave_planner_provider,
                            ConfigType.PRODUCT_CATALOG: mock_product_catalog_provider,
                        },
                    ):
                        manager.attach_mock(env_setup_tool, "env_setup_tool")
                        result = runner.invoke(env_setup_tool, ["apply-configs"])
                        assert result.exit_code == 0
                        expected = ".".join(expected_sequence)
                        actual = ".".join(call_order)
                        assert expected == actual


@patch.dict(
    os.environ,
    {
        "SERVICE_WORKER_TOKEN": "ondemand_dummy_worker_token",
        "RETAILER_CONFIGURATION": "retailer",
    },
)
def test_apply_sleeping_area_rules(runner):
    ff_file = [
        FeatureFile.from_yaml(
            "env_setup_tool/tests/test_data",
            "base.yaml",
        )
    ]
    with patch("env_setup_tool.src.utils.load_feature", return_value=ff_file):
        with requests_mock.Mocker() as n:
            n.post(
                "https://distiller-retailer-ode.tom.takeoff.com/api/v1/rules/sleeping-area/upsert-rule",
                status_code=200,
                json='{"datax":{"rules":[{"rule": {"priority": 10,"rule": "#and [#eq[#arg[:temperature-zone],[\\"frozen\\"]], #or [#eq [#arg [:location-info :item-type], \\"REG\\"], #eq[#arg[:storage-zone], \\"manual\\"]]]","sleeping-area": "B","store-id": "9999","update-note": "B for frozen REG or manual zone products"}}]}}',
            )
            with patch(
                "src.config.config.get_gcp_project_id",
                return_value="random-gcp-project-id",
            ):
                with patch(
                    "src.config.config.get_firebase_key",
                    return_value="FIREBASE_KEY",
                ):
                    result = runner.invoke(
                        env_setup_tool, ["apply-sleeping-area-rules"]
                    )
                    assert result.exit_code == 0


@patch("env_setup_tool.src.config_providers.wave_planner_provider.WavePlannerProvider")
@patch.dict(
    os.environ,
    {
        "SERVICE_WORKER_TOKEN": "ondemand_dummy_worker_token",
        "RETAILER_CONFIGURATION": "retailer",
    },
)
def test_apply_wave_plans(wave_planner_provider_mock, runner):
    ff_file = [
        FeatureFile.from_yaml(
            "env_setup_tool/tests/test_data",
            "base.yaml",
        )
    ]
    with patch("env_setup_tool.src.utils.load_feature", return_value=ff_file), patch(
        "src.config.config.get_gcp_project_id",
        return_value="random-gcp-project-id",
    ), patch(
        "src.config.config.get_firebase_key",
        return_value="FIREBASE_KEY",
    ), patch(
        "src.api.takeoff.wave_planner.get_or_create_user_token",
        return_value="user_KEY",
    ):
        with patch.dict(
            "env_setup_tool.src.env_setup.config_providers",
            {ConfigType.WAVE_PLANS: wave_planner_provider_mock},
        ):
            result = runner.invoke(env_setup_tool, ["apply-wave-plans"])
            assert result.exit_code == 0
            wave_planner_provider_mock.assert_called()
