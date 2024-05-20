import unittest
from pathlib import Path
from unittest import mock

import pytest

from env_setup_tool.src.utils import load_feature
from src.utils.git import GitRepository

CONFIGS_DATA_REPO_URL = "https://github.com/takeoff-com/environment-configs.git"
OUTPUT_FOLDER = "test-tmp-git"
BASE_CONFIGS_FILE = "features_data/base/base.yaml"


def test_git_clone():
    # Verify repository was checked out and files are accessible
    with GitRepository(CONFIGS_DATA_REPO_URL, OUTPUT_FOLDER) as repo:
        base_config_file_path = Path(repo) / BASE_CONFIGS_FILE
        assert base_config_file_path.exists()

    # Verify repository was deleted when context was exited
    assert not base_config_file_path.exists()


def test_git_alternate_branch():
    with GitRepository(CONFIGS_DATA_REPO_URL, OUTPUT_FOLDER, "unit_test") as repo:
        testfile = Path(repo) / "unit_test_file.txt"
        assert testfile.exists()


def test_git_clone_file_exists():
    # Verify we cannot clone repository to a file
    try:
        tmpfile = Path("tmpfile")
        tmpfile.touch()
        with GitRepository(CONFIGS_DATA_REPO_URL, tmpfile):
            pass
        assert False, "Did not catch an exception when cloning repository to file"
    except ValueError:
        pass
    except Exception as error:
        # We expect a ValueError, other exceptions should be investigated
        assert False, f"{error}"
    finally:
        tmpfile.unlink()


def test_git_clone_dir_exists():
    # Verify we can clone repository into an existing directory
    try:
        tmpdir = Path("tmpdir")
        tmpdir.mkdir()
        with GitRepository(CONFIGS_DATA_REPO_URL, tmpdir, "unit_test"):
            pass

        # Make sure we did not delete the existing directory
        assert tmpdir.exists()
    except Exception as error:
        assert False, f"{error}"
    finally:
        tmpdir.rmdir()


@mock.patch("env_setup_tool.src.utils.GitRepository")
def test_load_parent_features(mock_git_repo):
    mock_git_repo.return_value.__enter__.return_value = "env_setup_tool/tests/test_data"
    result = load_feature("feature1-1-1")
    assert len(result) == 4
    assert result[0].file_path.endswith("base.yaml")
    assert result[1].file_path.endswith("feature-feature1.yaml")
    assert result[2].file_path.endswith("feature-feature1-1.yaml")
    assert result[3].file_path.endswith("feature-feature1-1-1.yaml")


@mock.patch("env_setup_tool.src.utils.GitRepository")
def test_load_base_level_feature(mock_git_repo):
    mock_git_repo.return_value.__enter__.return_value = "env_setup_tool/tests/test_data"
    result = load_feature("base")
    assert len(result) == 1
    assert result[0].file_path.endswith("base.yaml")


@mock.patch("env_setup_tool.src.utils.GitRepository")
def test_feature_not_found(mock_git_repo):
    mock_git_repo.return_value.__enter__.return_value = ""
    with pytest.raises(FileNotFoundError):
        load_feature("unknown-feature")


if __name__ == "__main__":
    unittest.main()
