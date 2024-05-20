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
@patch("env_setup_tool.src.cli_helpers.ims_cli.ImsProvider")
def test_apply_all_configs(mock_ims_provider, runner):
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
                mock_ims_provider_instance = Mock()
                mock_ims_provider.return_value = mock_ims_provider_instance
                result = runner.invoke(env_setup_tool, ["ims", "apply-configs"])
                mock_ims_provider_instance.apply.assert_called_once()
                assert result.exit_code == 0


test_data = [("apply-addresses", "addresses"), ("apply-reason-codes", "reason_codes")]


@patch.dict(
    os.environ,
    {
        "SERVICE_WORKER_TOKEN": "ondemand_dummy_worker_token",
        "RETAILER_CONFIGURATION": "retailer",
    },
)
@pytest.mark.parametrize("apply_func, apply_arg", test_data)
@patch("env_setup_tool.src.cli_helpers.ims_cli.ImsProvider")
def test_apply_different_configs(mock_ims_provider, runner, apply_func, apply_arg):
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
                mock_ims_provider_instance = Mock()
                mock_ims_provider.return_value = mock_ims_provider_instance
                result = runner.invoke(env_setup_tool, ["ims", apply_func])
                mock_ims_provider_instance.apply.assert_called_once()
                mock_ims_provider_instance.apply.assert_called_with(
                    ff_file[0].configs["ims"], apply_arg
                )
                assert result.exit_code == 0
