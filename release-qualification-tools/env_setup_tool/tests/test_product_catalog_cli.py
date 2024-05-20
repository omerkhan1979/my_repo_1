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
@patch("env_setup_tool.src.cli_helpers.product_catalog_cli.ProductCatalogProvider")
def test_apply_product_catalog(mock_pc_provider, runner):
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
                mock_pc_provider_instance = Mock()
                mock_pc_provider.return_value = mock_pc_provider_instance
                result = runner.invoke(env_setup_tool, ["product-catalog", "upload"])
                mock_pc_provider_instance.apply.assert_called_once()
                assert result.exit_code == 0
