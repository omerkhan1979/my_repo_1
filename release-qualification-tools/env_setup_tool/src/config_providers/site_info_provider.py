from typing import Optional

from requests import HTTPError

from src.api.third_party.gcp import create_firebase_document
from src.config.config import Config as GlobalConfig
from env_setup_tool.src.config_providers.config_providers import BaseConfigProvider
from env_setup_tool.src.config_types import (
    CompositeConfig,
    SiteInfoConfigType,
    Config,
    ConfigType,
)
from src import logger
from src.api.takeoff.site_info_service import (
    SiteInfoSvc,
    SiteInfoRetailerPayload,
    SiteInfoRetailerQuery,
)
from src.config.constants import (
    AUTH_SVC_SECRET,
    AUTH_SVC_USER_ID,
    BASE_DOMAIN,
    FIREBASE_PROJECT,
)

log = logger.get_logger(__name__)


class SiteInfoProvider(BaseConfigProvider):

    def __init__(self, global_config: GlobalConfig):
        self.global_config = global_config
        self.service = SiteInfoSvc(BASE_DOMAIN, AUTH_SVC_USER_ID, AUTH_SVC_SECRET)
        self.config_type_map = {
            SiteInfoConfigType.SITES: "apply_sites",
            SiteInfoConfigType.RETAILER: "apply_retailer",
        }
        self.config_name = ConfigType.SITE_INFO.value

    def apply_simple_config(self, config_data: Config) -> dict[str, bool]:
        raise NotImplementedError("This provider only handles composite configurations")

    def apply_composite_config(
        self, config_data: CompositeConfig, subconfig_key: Optional[str] = None
    ) -> dict[str, bool]:
        """
        Applies configurations based on the provided CompositeConfig data.

        This method applies all configurations in `config_data` if no `subconfig_key` is provided. If a specific
        `subconfig_key` is given, only the corresponding sub-configuration is applied.

        Args:
        config_data (CompositeConfig): An instance of CompositeConfig containing the configurations to be applied,
                                       previously read from feature file
        subconfig_key (str, optional): site-info-svc config type (See SiteInfoConfigType Enum for full list).
                                       If None, all sub-configurations in `config_data` will be applied.

        Return:
        dict[str, bool]: result of the apply operation in the format config_name: boolean
        """
        results = {}  # store results of application of configs for future reference
        if subconfig_key:
            res = self.__apply_config(subconfig_key, config_data)
            results.update(res)
        else:
            for site_info_config in SiteInfoConfigType:
                if site_info_config.value in config_data.configs.keys():
                    res = self.__apply_config(site_info_config.value, config_data)
                    results.update(res)
        return results

    def __apply_config(self, key: str, config_data: CompositeConfig) -> dict[str, bool]:
        """
        Internal function to apply SiteInfo configuration using the provided key and CompositeConfig data

        Args:
        key (str): site info config type (See SiteInfoConfigType Enum for full list)
        config_data (CompositeConfig): An instance of CompositeConfig containing all the available configurations
                                       that were extracted from feature file.
        Return:
        dict[str, bool]: result of the apply operation in the format config_name: boolean
        """
        config_type = SiteInfoConfigType.get_site_info_config_type(key)
        if not config_type:
            return {f"{self.config_name}.{key}": False}
        method_name = self.config_type_map.get(config_type)
        if not method_name:
            log.error(f"No method defined for config type: {key}")
            return {f"{self.config_name}.{key}": False}

        apply_func = getattr(self, method_name, None)
        if not apply_func:
            log.error(f"Method {method_name} not found in SiteInfoProvider")
            return {f"{self.config_name}.{key}": False}
        return apply_func(config_data.configs[key])

    def apply_retailer(self, config_obj: Config) -> dict[str, bool]:
        retailer_payload = SiteInfoRetailerPayload.from_dict(config_obj.data)  # type: ignore
        # get existing retailers list and compare retailer code
        ret_list = self.service.get_retailers(
            parameters=SiteInfoRetailerQuery(code=retailer_payload.code)
        )
        retailer_id = ""
        retailer_exist = False
        for ret in ret_list:
            # skip retailer creation if it exist
            if ret.code == retailer_payload.code:
                retailer_exist = True
                log.info(
                    f"Retailer '{retailer_payload.code}' already exist. Skipping retailer creation"
                )
                retailer_id = ret.id
                break
        # if retailer does not exist -> create
        if not retailer_exist:
            retailer_id = self._create_retailer(retailer_payload)
        if retailer_id is None:
            return {f"{self.config_name}.{SiteInfoConfigType.RETAILER.value}": False}

        log.info(f"Creating audience document for retailer {retailer_payload.code}")
        success = _create_audience_document(retailer_id)
        if not success:
            log.error(
                f"Failed to create/update audience document for retailer with id {retailer_id}"
            )
            return {f"{self.config_name}.{SiteInfoConfigType.RETAILER.value}": False}
        return {f"{self.config_name}.{SiteInfoConfigType.RETAILER.value}": True}

    # TODO: Implement me PROD-12983
    def apply_sites(self, config_obj: Config) -> dict[str, bool]:
        log.info("Applying sites")
        return {f"{self.config_name}.{SiteInfoConfigType.SITES.value}": True}

    def _create_retailer(self, payload) -> str | None:
        log.info(f"Creating retailer '{payload.code}'")
        try:
            retailer_response = self.service.create_retailer(payload)
            return retailer_response.id
        except HTTPError as e:
            log.error(f"Failed to create retailer: {e}")
            return None


def _create_audience_document(doc_id: str) -> bool:
    audience_data = {
        "audience": FIREBASE_PROJECT,
        "retailer_id": doc_id,
    }
    return create_firebase_document("auth-svc-retailer-audience", doc_id, audience_data)
