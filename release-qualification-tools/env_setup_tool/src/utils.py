import fnmatch
import os
from typing import List

from src import logger
from src.utils.git import GitRepository
from env_setup_tool.src.feature_file import FeatureFile

CONFIGS_DATA_REPO_URL = "https://github.com/takeoff-com/environment-configs.git"
CONFIG_DATA_DEFAULT_BRANCH = "master"
log = logger.get_logger(__name__)


def load_feature(
    feature: str, branch: str = CONFIG_DATA_DEFAULT_BRANCH
) -> List[FeatureFile]:
    """
    Load feature file and all its parent feature files based on the provided feature name and branch from CONFIGS_DATA_REPO_URL.

    feature: The name of the feature to load.
    branch: The branch of the repository to search in, defaults to CONFIG_DATA_DEFAULT_BRANCH.
    :return: A list of FeatureFile objects loaded from the YAML files.
    :raises FileNotFoundError If no feature file is found.
    """

    log.info("Loading feature configuration files ...")
    target_feature_file = (
        "base.yaml" if feature == "base" else f"feature-{feature}.yaml".lower()
    )
    with GitRepository(
        CONFIGS_DATA_REPO_URL, "env_setup_data", branch
    ) as config_repo_local:
        for root, dirs, files in os.walk(config_repo_local):
            if target_feature_file in files:
                file_path = os.path.join(root, target_feature_file)
                ff_paths_to_apply = get_parent_features(file_path)
                return [
                    FeatureFile.from_yaml(
                        config_repo_local, os.path.relpath(ff_path, config_repo_local)
                    )
                    for ff_path in ff_paths_to_apply
                ]
        raise FileNotFoundError(
            f"No feature file found in environment-config repo for feature {feature}"
        )


def get_parent_features(feature_path: str) -> List[str]:
    """
    Recursively searches for and collects paths to YAML feature files in all parent directories of a specified file path.
    This function looks for files that match the pattern 'feature-*.yaml' and 'base.yaml'.

    Parameters:
    feature_path (str): The full file path of the target feature file. This path serves as the base
                        for the upward search in parent directories.

    Returns:
    List[str]: A list containing the paths of all discovered feature files in parent directories. The list
               includes files named 'feature-*.yaml' and 'base.yaml'.
    """

    current_dir = os.path.dirname(feature_path)
    parent_feature_files = []
    parent_dirs = []
    while current_dir:
        parent_dirs.append(current_dir)
        current_dir, _ = os.path.split(current_dir)

    for directory in reversed(parent_dirs):
        for file in os.listdir(directory):
            if (
                fnmatch.fnmatch(file, "feature-*.yaml")
                or os.path.basename(file) == "base.yaml"
            ):
                feature_file_path = os.path.join(directory, file)
                parent_feature_files.append(feature_file_path)
    return parent_feature_files
