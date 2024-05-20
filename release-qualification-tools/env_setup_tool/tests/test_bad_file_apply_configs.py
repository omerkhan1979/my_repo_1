from unittest.mock import patch

import pytest

from env_setup_tool.src.feature_file import FeatureFile

# poetry run pytest env_setup_tool/tests/test_bad_file_apply_configs.py


def test_bad_file_apply_configs_sequence():
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            FeatureFile.from_yaml(
                "env_setup_tool/tests/test_data",
                "base-bad-file.yaml",
            )
