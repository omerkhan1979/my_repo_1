import os
from unittest.mock import patch, Mock

import pytest
from typer.testing import CliRunner

from env_setup_tool.src.env_setup import env_setup_tool
from env_setup_tool.src.feature_file import FeatureFile


@pytest.fixture
def runner():
    return CliRunner()


@patch.dict(
    os.environ,
    {
        "SERVICE_WORKER_TOKEN": "ondemand_dummy_worker_token",
        "RETAILER_CONFIGURATION": "retailer",
    },
)
@patch("env_setup_tool.src.cli_helpers.tsc_cli.TscProvider")
def test_apply_all_configs(mock_tsc_provider, runner):
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
                mock_tsc_provider_instance = Mock()
                mock_tsc_provider.return_value = mock_tsc_provider_instance
                result = runner.invoke(env_setup_tool, ["tsc", "apply-configs"])
                mock_tsc_provider_instance.apply.assert_called_once()
                assert result.exit_code == 0


test_data = [
    ("apply-flow-racks", "flow_racks"),
    ("apply-tote-types", "tote_types"),
    ("apply-spokes", "spokes"),
    ("apply-staging-config", "staging_config"),
    ("apply-config-items", "config_items"),
    ("apply-staging-locations", "staging_locations"),
    ("apply-locations", "locations"),
    ("apply-routes", "routes"),
]


@patch.dict(
    os.environ,
    {
        "SERVICE_WORKER_TOKEN": "ondemand_dummy_worker_token",
        "RETAILER_CONFIGURATION": "retailer",
    },
)
@pytest.mark.parametrize("apply_func, apply_arg", test_data)
@patch("env_setup_tool.src.cli_helpers.tsc_cli.TscProvider")
def test_apply_different_configs(mock_tsc_provider, runner, apply_func, apply_arg):
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
                mock_tsc_provider_instance = Mock()
                mock_tsc_provider.return_value = mock_tsc_provider_instance
                result = runner.invoke(env_setup_tool, ["tsc", apply_func])
                mock_tsc_provider_instance.apply.assert_called_once()
                mock_tsc_provider_instance.apply.assert_called_with(
                    ff_file[0].configs["tsc"], apply_arg
                )
                assert result.exit_code == 0


@patch("env_setup_tool.src.utils.GitRepository")
@patch.dict(
    os.environ,
    {
        "SERVICE_WORKER_TOKEN": "ondemand_dummy_worker_token",
        "RETAILER_CONFIGURATION": "retailer",
    },
)
@patch("env_setup_tool.src.cli_helpers.tsc_cli.TscProvider")
def test_apply_config_that_present_only_in_one_feature(
    mock_tsc_provider, mock_git_repo, runner
):
    mock_git_repo.return_value.__enter__.return_value = "env_setup_tool/tests/test_data"
    with patch(
        "src.config.config.get_gcp_project_id",
        return_value="random-gcp-project-id",
    ), patch(
        "src.config.config.get_firebase_key",
        return_value="FIREBASE_KEY",
    ):
        # This test checks that if a specific config was called it will be applied only if it present in the
        # feature config file and/or it's parent feature config file.
        # The tool is called with passed --feature argument. In below example routes config only present in the base.yaml
        # feature config file. As a result TSCProvider will be called only once

        mock_tsc_provider_instance = Mock()
        mock_tsc_provider.return_value = mock_tsc_provider_instance
        result = runner.invoke(
            env_setup_tool, ["--feature", "feature1-1-1", "tsc", "apply-routes"]
        )
        assert result.exit_code == 0
        assert len(mock_tsc_provider_instance.mock_calls) == 1

        # In below example locations config present in the base.yaml, feature-feature1-1.yaml and feature-feature1-1-1.yaml
        # feature config file. As a result TSCProvider will be called three times
        # The same mock for TSCProvider can be re-used, but here it will be easy to show the call count on the new mock object

        mock_tsc_provider_instance2 = Mock()
        mock_tsc_provider.return_value = mock_tsc_provider_instance2
        result2 = runner.invoke(
            env_setup_tool, ["--feature", "feature1-1-1", "tsc", "apply-locations"]
        )
        assert result2.exit_code == 0
        assert len(mock_tsc_provider_instance2.mock_calls) == 3
