from pathlib import Path
import yaml

from env_setup_tool.src.config_types import (
    ConfigType,
    Config,
    TSCConfigType,
    IMSConfigType,
    CompositeConfig,
    SiteInfoConfigType,
)
from src import logger

log = logger.get_logger(__name__)


class FeatureFile:
    """
    A representation of a feature configuration file.

    This class abstracts the reading and processing of the feature YAML files, including the base
    configuration and individual feature-specific configurations. For each configuration type defined
    in the `ConfigType` enum, this class extracts the corresponding configuration details from the
    provided YAML file.

    Attributes:
    -----------
    configs : dict
        A dictionary containing the configuration details for each configuration type. The keys are
        the members of the `ConfigType` enum, and the values are the extracted configuration details or
        path to corresponding config detail file from the YAML file.
    """

    def __init__(
        self, key=None, title=None, description=None, configs=None, file_path=None
    ):
        self.key = key
        self.title = title
        self.description = description
        self.configs = (
            configs if configs else {config_type: None for config_type in ConfigType}
        )
        self.file_path = file_path

    @classmethod
    def from_yaml(cls, config_repo: str, config_file_path: str):
        """
        Creates an instance of the class from a YAML file.

        Parameters:
        - config_repo (str): The local path to the cloned repository that contains the configurations.
        - config_file (str): The filepath for the Feature File to be read.

        Returns:
        - An instance of the class, populated with the data from the YAML file.
        """
        repo_path = Path(config_repo)
        cfile_path = Path(config_file_path)
        yaml_path = repo_path / cfile_path
        log.info(f"Loading feature configs from file: {yaml_path}")
        with open(yaml_path, "r") as file:
            content = yaml.safe_load(file)

            key = content.get("key")
            title = content.get("title")
            description = content.get("description")
            configs_content = content.get("configs", {})
            configs = {}
            for config_key, config_data in configs_content.items():
                if config_key not in [e.value for e in ConfigType]:
                    raise ValueError(f"Unsupported config key: {config_key}")

                if config_key in [
                    ConfigType.TSC.value,
                    ConfigType.IMS.value,
                    ConfigType.SITE_INFO.value,
                ]:
                    subconfigs = {}
                    for sub_key, sub_value in config_data.items():
                        if (
                            sub_key not in [e.value for e in TSCConfigType]
                            and sub_key not in [e.value for e in IMSConfigType]
                            and sub_key not in [e.value for e in SiteInfoConfigType]
                        ):
                            raise ValueError(
                                f"Unsupported {config_key} config key: {sub_key}"
                            )
                        sub_config = Config(
                            path=repo_path / sub_value.get("path"),
                        )
                        log.info(
                            f"Loading sub-config {config_key}.{sub_key} from {sub_config.path}"
                        )
                        sub_config.load_data()
                        subconfigs[sub_key] = sub_config
                    configs[config_key] = CompositeConfig(configs=subconfigs)
                else:
                    config = Config(
                        path=repo_path / config_data.get("path"),
                    )
                    log.info(f"Loading config {config_key} from {config.path}")
                    config.load_data()
                    configs[config_key] = config
            return cls(key, title, description, configs, config_file_path)

    def __repr__(self):
        return f"<FeatureFileContent key={self.key}, title={self.title}, configs = {self.configs}>"
