import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, Dict

import yaml

from src import logger

log = logger.get_logger(__name__)


class ConfigType(Enum):
    """
    An enumeration of available configuration types.

    This enumeration is used to define and categorize the various types of configurations that can be
    read from the YAML feature files. Each member of this enum represents a distinct configuration
    type, and its value is typically a string identifier used in the YAML files.

    When adding a new configuration type, ensure to append it to this enumeration. Update the
    associated YAML files to use the new configuration type's value as an identifier.

    Important: The order of this enum will determine ingestion order.
    """

    TSC = "tsc"
    IMS = "ims"
    SleepingAreaRules = "sleeping_area_rules"
    PRODUCT_CATALOG = "product_catalog"
    WAVE_PLANS = "waves"
    SITE_INFO = "site_info"


class TSCConfigType(Enum):
    LOCATIONS = "locations"
    CONFIG_ITEMS = "config_items"
    SPOKES = "spokes"
    STAGING_LOCATIONS = "staging_locations"
    ROUTES = "routes"
    STAGING_CONFIG = "staging_config"
    FLOW_RACKS = "flow_racks"
    TOTE_TYPES = "tote_types"

    @staticmethod
    def get_tsc_config_type(key: str) -> "TSCConfigType":
        if key not in [type.value for type in TSCConfigType]:
            log.error(f"{key} not found in the provided TSC config data.")
        return TSCConfigType(key)


class IMSConfigType(Enum):
    ADDRESSES = "addresses"
    REASON_CODES = "reason_codes"

    @staticmethod
    def get_ims_config_type(key: str) -> "IMSConfigType":
        if key not in [type.value for type in IMSConfigType]:
            log.error(f"{key} not found in the provided IMS config data.")
        return IMSConfigType(key)


class SiteInfoConfigType(Enum):
    RETAILER = "retailer"
    SITES = "sites"

    @staticmethod
    def get_site_info_config_type(key: str) -> "SiteInfoConfigType":
        if key not in [type.value for type in SiteInfoConfigType]:
            log.error(f"{key} not found in the provided SiteInfo config data.")
        return SiteInfoConfigType(key)


@dataclass
class Config:
    path: Path
    data: Optional[dict] = field(default_factory=dict)

    def load_data(self) -> None:
        try:
            if self.path.name.endswith(".yaml"):
                with self.path.open("r") as file:
                    self.data = yaml.safe_load(file)
            elif self.path.name.endswith(".json"):
                with self.path.open("r") as file:
                    self.data = json.load(file)
            else:
                raise ValueError(f"Unsupported file format for {self.path}")
        except FileNotFoundError:
            log.info(f"File {self.path} not found")
            raise FileNotFoundError(f"File {self.path} not found")


@dataclass
class CompositeConfig:
    configs: Dict[str, Config]
