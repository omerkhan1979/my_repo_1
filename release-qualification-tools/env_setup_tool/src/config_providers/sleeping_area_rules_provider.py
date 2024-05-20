from typing import Optional

from src.config.config import Config as GlobalConfig
from requests import HTTPError
from env_setup_tool.src.config_providers.config_providers import BaseConfigProvider
from env_setup_tool.src.config_types import Config, CompositeConfig, ConfigType
from src import logger
from src.api.takeoff.distiller import Distiller

log = logger.get_logger(__name__)


class SleepingAreaRulesProvider(BaseConfigProvider):
    def __init__(self, global_config: GlobalConfig):
        self.service = Distiller(global_config)

    def apply_composite_config(
        self, config_data: CompositeConfig, subconfig_key: Optional[str] = None
    ) -> dict[str, bool]:
        raise NotImplementedError("This provider only handles composite configurations")

    def apply_simple_config(self, config_data: Config) -> dict[str, bool]:
        """
        Applies configuration based on the provided config.

        Args:
        config (Config): An instance of the configuration to be applied,
                        previously read from feature file
        """

        if config_data.data is not None:
            success = True
            log.info("Updating sleeping area rule configurations")
            for rule in config_data.data["rules"]:
                try:
                    self.service.upsert_rule_sleeping_area(rule)
                except HTTPError as e:
                    log.error(f"Couldn't POST sleeping area configurations: {e}")
                    success = False
            return {ConfigType.SleepingAreaRules.value: success}
        else:
            log.info("No sleeping area rules provided - Skipping configuration.")
            return {ConfigType.SleepingAreaRules.value: False}
