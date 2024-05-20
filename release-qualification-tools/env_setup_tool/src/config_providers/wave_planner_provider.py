from typing import Optional

from requests import HTTPError
from src.config.config import Config as GlobalConfig
from env_setup_tool.src.config_providers.config_providers import BaseConfigProvider
from env_setup_tool.src.config_types import Config, CompositeConfig, ConfigType
from src import logger
from src.api.takeoff.wave_planner import WavePlanner, CreateWavePlanRequestBody

log = logger.get_logger(__name__)


class WavePlannerProvider(BaseConfigProvider):
    def __init__(self, global_config: GlobalConfig):
        self.global_config = global_config
        self.service = WavePlanner(global_config)
        self.config_name = ConfigType.WAVE_PLANS.value

    def apply_composite_config(
        self, config_data: CompositeConfig, subconfig_key: Optional[str] = None
    ) -> dict[str, bool]:
        raise NotImplementedError("This provider only handles composite configurations")

    def apply_simple_config(self, config: Config) -> dict[str, bool]:
        """
         Applies wave plans based on the provided config.

         Args:
         config (Config): An instance of the configuration to be applied,
                         previously read from feature file
        return bool: result of the application
        """
        if config.data is not None:
            try:
                mfc_id = list(config.data.keys())[0]
                waves = config.data[mfc_id]
                log.info(f"Updating wave plans configurations for {mfc_id}")
                self.service.post_wave_plan(
                    retailer_id=self.global_config.retailer,
                    mfc_id=mfc_id,
                    waves=CreateWavePlanRequestBody(waves),
                )
            except HTTPError as e:
                log.error(f"Couldn't POST wave plans configurations: {e}")
                return {self.config_name: False}
            return {self.config_name: True}
        else:
            log.error("No wave plans provided - Skipping configuration.")
            return {self.config_name: False}
