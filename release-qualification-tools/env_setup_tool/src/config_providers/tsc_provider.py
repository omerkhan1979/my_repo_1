from typing import Optional

from requests import HTTPError

from src.config.config import Config as GlobalConfig
from src import logger
from src.api.takeoff.ops_api import OpsApi
from src.api.takeoff.tsc import TSC
from src.copy_config.filter import compare_flow_racks
from env_setup_tool.src.config_providers.config_providers import BaseConfigProvider
from env_setup_tool.src.config_types import (
    TSCConfigType,
    Config,
    CompositeConfig,
    ConfigType,
)
from src.utils.helpers import remove_fields

log = logger.get_logger(__name__)


class TscProvider(BaseConfigProvider):
    def __init__(self, global_config: GlobalConfig):
        self.service = TSC(global_config)
        self.config_type_map = {
            TSCConfigType.CONFIG_ITEMS: "apply_config_items",
            TSCConfigType.STAGING_CONFIG: "apply_staging_config",
            TSCConfigType.STAGING_LOCATIONS: "apply_staging_locations",
            TSCConfigType.FLOW_RACKS: "apply_flow_racks",
            TSCConfigType.TOTE_TYPES: "apply_tote_types",
            TSCConfigType.LOCATIONS: "apply_locations",
            TSCConfigType.SPOKES: "apply_spokes",
            TSCConfigType.ROUTES: "apply_routes",
        }
        self.config_name = ConfigType.TSC.value

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
        subconfig_key (str, optional): tsc config type (one of tote_types, staging_config, flow_racks, etc. See
                                       TSCConfigType Enum for full list). If None, all sub-configurations in
                                       `config_data` will be applied.
        """
        results = {}  # store results of application of configs for future reference
        if subconfig_key:
            res = self.__apply_config(subconfig_key, config_data)
            results.update(res)
        else:
            for tsc_config in TSCConfigType:
                if tsc_config.value in config_data.configs.keys():
                    res = self.__apply_config(tsc_config.value, config_data)
                    results.update(res)
        return results

    def __apply_config(self, key: str, config_data: CompositeConfig) -> dict[str, bool]:
        """
        Internal function to apply tsc configuration using the provided key and CompositeConfig data

        Args:
        key (str): tsc config type (one of tote-types, staging-config, flow-racks, etc. See TSCConfigType Enum for
                   full list)
        config_data (CompositeConfig): An instance of CompositeConfig containing all the available configurations
                                       that were extracted from feature file.
        Return:
        dict[str, bool]: result of the apply operation in the format config_name: boolean
        """
        config_type = TSCConfigType.get_tsc_config_type(key)
        if not config_type:
            return {f"{self.config_name}.{key}": False}
        method_name = self.config_type_map.get(config_type)
        if not method_name:
            log.error(f"No method defined for config type: {key}")
            return {f"{self.config_name}.{key}": False}

        apply_func = getattr(self, method_name, None)
        if not apply_func:
            log.error(f"Method {method_name} not found in TSCProvider")
            return {f"{self.config_name}.{key}": False}
        return apply_func(config_data.configs[key])

    def apply_tote_types(self, config_obj: Config) -> dict[str, bool]:
        """
        This method compares tote types in `config_obj` with the existing tote types retrieved from the environment.
        If any new tote types are found in `config_obj`, they are posted using the TSC service. We are agnostic of ids
        and treat tote types as being a composite of their values. Existing tote types with the same ID and different
        values are created as a new tote type, not updated.

        Args:
        config_obj (Config): An instance of Config containing the tote types to be applied
        """
        log.info("Processing Tote Types")

        totes_to_apply = config_obj.data
        totes_from_env = self.service.get_tote_location_types()

        # Remove tote-type-id from env totes
        for i in totes_from_env:
            i.pop("tote-type-id", None)

        for tote_new in totes_to_apply:
            # Remove tote-type-id from new tote
            tote_new.pop("tote-type-id", None)
            # If tote type not in env, create it
            if tote_new not in totes_from_env:
                log.info("Creating Tote Type")
                try:
                    self.service.post_tote_type(tote_new, [201, 200])
                except HTTPError as e:
                    log.error(f"Couldn't POST Tote Type {tote_new}: {e}")
                    return {TSCConfigType.TOTE_TYPES.value: False}
        log.info("End processing Tote Types")
        return {f"{self.config_name}.{TSCConfigType.TOTE_TYPES.value}": True}

    def apply_staging_config(self, config_obj: Config) -> dict[str, bool]:
        staging_config = config_obj.data
        try:
            log.info("Updating staging configurations")
            self.service.post_staging_configurations(staging_config, [201, 200])
        except HTTPError as e:
            log.error(f"Couldn't POST Staging configurations: {e}")
            return {TSCConfigType.STAGING_CONFIG.value: False}
        return {f"{self.config_name}.{TSCConfigType.STAGING_CONFIG.value}": True}

    def apply_config_items(self, config_obj: Config) -> dict[str, bool]:
        if config_obj.data is not None:
            config_items = config_obj.data
            log.info("Updating config-items")
            try:
                self.service.put_config_items(config_items, [201, 200])
            except HTTPError as e:
                log.error(f"Couldn't PUT config-items: {e}")
                return {f"{self.config_name}.{TSCConfigType.CONFIG_ITEMS.value}": False}
            return {f"{self.config_name}.{TSCConfigType.CONFIG_ITEMS.value}": True}
        return {f"{self.config_name}.{TSCConfigType.CONFIG_ITEMS.value}": False}

    def apply_flow_racks(self, config_obj: Config) -> dict[str, bool]:
        flow_racks_to_apply = config_obj.data
        filter_flow_racks = compare_flow_racks(
            flow_racks_to_apply, self.service.get_flow_racks()
        )
        if filter_flow_racks:
            log.info("Updating flow racks")
            try:
                self.service.put_flow_racks(filter_flow_racks, [201, 200])
            except HTTPError as e:
                log.error(f"Couldn't PUT Flow racks: {e}")
                return {f"{self.config_name}.{TSCConfigType.FLOW_RACKS.value}": False}
        else:
            log.info("No differences of flow-racks config are detected. Update skipped")
        return {f"{self.config_name}.{TSCConfigType.FLOW_RACKS.value}": True}

    def apply_locations(self, config_obj: Config) -> dict[str, bool]:
        locations = config_obj.data
        success = True
        for location in locations:
            # check if location exist: update it; if not enabled - enable, else create and enable
            is_exist, is_enabled, found_locations = self.is_location_exist_and_enabled(
                location["location-code-tom"]
            )
            try:
                if is_exist:
                    # location exists, update it
                    log.info(
                        f'Updating location "{self.service.config.location_code_tom}"'
                    )
                    self.service.update_location(
                        found_locations[0]["location-id"],
                        remove_fields(
                            location,
                            [
                                "location-id",
                                "location-type",
                                "mfc-ref-code",
                                "location-code-gold",
                                "location-code-tom",
                            ],
                        ),
                    )
                    if not is_enabled:
                        # location exists, enable it
                        log.info(
                            f'Enabling mfc location {found_locations[0]["location-code-tom"]}'
                        )
                        self.service.set_location_availability(
                            found_locations[0]["location-id"]
                        )
                else:
                    tom_code = location["location-code-tom"]
                    # location does not exist, create it
                    log.info(f"Creating location {tom_code}")
                    location_body = remove_fields(
                        location, ["location-type", "mfc-ref-code", "location-id"]
                    )
                    location = self.service.post_mfc_location(location_body)
                    log.info(f"Successfully created location {tom_code}")
                    OpsApi(self.service.config).initialize_picking_queue(tom_code)
                    # enable it
                    self.service.set_location_availability(location["location-id"])

            except Exception as e:
                success = False
                log.error(e)
        return {f"{self.config_name}.{TSCConfigType.LOCATIONS.value}": success}

    def is_location_exist_and_enabled(
        self, mfc_tom_code: str, is_spoke: bool = False
    ) -> tuple[bool, bool, list]:
        is_exist = False
        is_active = False
        found_location = {}
        active_locations = self.service.get_tom_code_locations("true")
        if active_locations:
            found_location = self.filter_location_from_list(
                mfc_tom_code, active_locations, is_spoke
            )
            if found_location:
                is_active = True
                is_exist = True
        if not is_exist:
            disabled_locations = self.service.get_tom_code_locations("false")
            found_location = self.filter_location_from_list(
                mfc_tom_code, disabled_locations, is_spoke
            )
            if found_location:
                is_active = False
                is_exist = True

        return is_exist, is_active, found_location

    def filter_location_from_list(
        self, mfc_tom_code: str, locations_list: list, is_spoke: bool = False
    ) -> list:
        found_locations = []
        if not is_spoke and locations_list:
            found_locations = list(
                filter(
                    (
                        lambda location: (location["mfc-ref-code"] == mfc_tom_code)
                        and (location["location-type"] == "mfc")
                    ),
                    locations_list,
                )
            )
        elif locations_list:
            found_locations = list(
                filter(
                    (
                        lambda location: (location["location-code-tom"] == mfc_tom_code)
                        and (location["location-type"] == "spoke")
                    ),
                    locations_list,
                )
            )
        return found_locations

    def apply_spokes(self, config_obj: Config) -> dict[str, bool]:
        spokes = config_obj.data
        success = True
        if spokes:
            log.info("Updating spokes")
            for spoke in spokes:
                try:
                    log.info(
                        f'Updating spoke "{spoke["location-code-tom"]}" on location "{spoke["mfc-ref-code"]}'
                    )
                    mfc_id = self.service.get_location_id_by_code_tom(
                        spoke["mfc-ref-code"]
                    )
                    self.update_target_spoke(
                        mfc_id,
                        spoke,
                    )
                except HTTPError as e:
                    success = False
                    log.error(e)
            log.info(
                f"Finished posting spokes on {self.service.config.location_code_tom}"
            )
        else:
            log.info("No spokes to update")
        return {f"{self.config_name}.{TSCConfigType.SPOKES.value}": success}

    def update_target_spoke(self, mfc_id: int, spoke: dict) -> None:
        """Creates or updates spoke

        Args:
            mfc_id (int): mfc-id the spoke belongs to
            spoke (dict): content of spoke

        """
        is_exist, is_enabled, found_spokes = self.is_location_exist_and_enabled(
            spoke["location-code-tom"], True
        )
        if is_exist:
            for found_spoke in found_spokes:
                try:
                    self.service.update_location_spoke(
                        mfc_id,
                        found_spoke["location-id"],
                        remove_fields(
                            spoke,
                            [
                                "location-id",
                                "location-type",
                                "mfc-ref-code",
                                "location-code-gold",
                                "location-code-tom",
                            ],
                        ),
                    )
                    break
                except HTTPError as e:
                    log.error(e)

                if not is_enabled:
                    self.service.set_location_availability(found_spoke["location-id"])
        else:
            try:
                self.service.create_location_spoke(
                    mfc_id,
                    remove_fields(
                        spoke,
                        [
                            "location-type",
                            "mfc-ref-code",
                            "location-id",
                        ],
                    ),
                )
            except HTTPError as e:
                log.error(e)

    def apply_staging_locations(self, config_obj: Config) -> dict[str, bool]:
        staging_locations = config_obj.data
        success = True
        for staging_loc in staging_locations:
            log.info(f"Posting staging-location {staging_loc['staging-location-code']}")
            is_default = staging_loc.get("default")
            # "default" key is not allowed in the post_staging_location request body. Removing the key from the dict
            staging_loc.pop("default", None)
            try:
                self.service.post_staging_location(staging_loc)
                if is_default:
                    self.service.put_default_staging_location(
                        staging_loc["staging-location-code"],
                        staging_loc["mfc-tom-code"],
                    )
            except HTTPError as e:
                success = False
                log.error(e)
        return {f"{self.config_name}.{TSCConfigType.STAGING_LOCATIONS.value}": success}

    def apply_routes(self, config_obj: Config) -> dict[str, bool]:
        routes = config_obj.data
        success = True
        for route in routes:
            try:
                log.info(
                    f"POSTing route {route['route-code']} for mfc {route['mfc-tom-code']}"
                )
                self.service.post_route(route, [201, 200])
            except HTTPError as e:
                log.error(e)
                success = False
        return {f"{self.config_name}.{TSCConfigType.ROUTES.value}": success}
