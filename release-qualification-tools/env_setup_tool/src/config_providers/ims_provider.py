from typing import Optional

from dataclasses import dataclass, asdict
from requests import HTTPError

from src.config.config import Config as GlobalConfig
from env_setup_tool.src.config_providers.config_providers import BaseConfigProvider
from env_setup_tool.src.config_types import (
    IMSConfigType,
    Config,
    CompositeConfig,
    ConfigType,
)
from src import logger
from src.api.takeoff.ims import IMS

log = logger.get_logger(__name__)


@dataclass
class Address:
    address: str
    location_id: str
    area: str
    temp_zone: str
    aisle: str
    bay: str
    shelf: str
    stack: str
    overstock: bool
    dynamic: bool
    pickable: bool
    active: bool

    def get_create_values(self) -> dict:
        return self.clean_address_dict(
            [
                "address",
                "location_id",
                "area",
                "temp_zone",
                "aisle",
                "bay",
                "shelf",
                "stack",
            ],
        )

    def clean_address_dict(self, key_filter: list) -> dict:
        """
        This method takes an Address in the form of a dict and filters out extraneous values. The values
        that we must filter out depends on whether we are doing a create or update operation.
        This method also changes underscores '_' for dashes '-' for use with JSON calls.

        Args:
        address (dict): An instance of an Address for use with IMS
        key_filter (list): Return a dictionary with only keys contained in key_filter
        """

        addr = asdict(self)
        return {
            k.replace("_", "-"): addr.get(k)
            for k in key_filter
            if addr.get(k) is not None
        }


class ImsProvider(BaseConfigProvider):
    def __init__(self, global_config: GlobalConfig):
        self.service = IMS(global_config)
        self.config_type_map = {
            IMSConfigType.ADDRESSES: "apply_addresses",
            IMSConfigType.REASON_CODES: "apply_reason_codes",
        }
        self.config_name = ConfigType.IMS.value

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
        subconfig_key (str, optional): ims config type (See IMSConfigType Enum for full list).
                                       If None, all sub-configurations in `config_data` will be applied.
        """
        results = {}  # store results of application of configs for future reference
        if subconfig_key:
            res = self.__apply_config(subconfig_key, config_data)
            results.update(res)
        else:
            for ims_config in IMSConfigType:
                if ims_config.value in config_data.configs.keys():
                    res = self.__apply_config(ims_config.value, config_data)
                    results.update(res)
        return results

    def __apply_config(self, key: str, config_data: CompositeConfig) -> dict[str, bool]:
        """
        Internal function to apply ims configuration using the provided key and CompositeConfig data

        Args:
        key (str): ims config type (See IMSConfigType Enum for full list)
        config_data (CompositeConfig): An instance of CompositeConfig containing all the available configurations
                                       that were extracted from feature file.
        Return:
        dict[str, bool]: result of the apply operation in the format config_name: boolean
        """
        config_type = IMSConfigType.get_ims_config_type(key)
        if not config_type:
            return {f"{self.config_name}.{key}": False}
        method_name = self.config_type_map.get(config_type)
        if not method_name:
            log.error(f"No method defined for config type: {key}")
            return {f"{self.config_name}.{key}": False}

        apply_func = getattr(self, method_name, None)
        if not apply_func:
            log.error(f"Method {method_name} not found in IMSProvider")
            return {f"{self.config_name}.{key}": False}
        return apply_func(config_data.configs[key])

    def apply_addresses(self, config_obj: Config) -> dict[str, bool]:
        """
        This method gets addresses from the environment and compares them to input configuration.
        - If an address is in configuration but not environment, it is added to the environment using
          a create call and an update call to set attributes (not all attributes can be set at create time).
        - If an address is in configuration and also environment, we attempt to update whatever attributes
          can be updated.
        - If an address exists in environment but not configuration, it is noted as an unidentified address.
        - There is currently no endpoint for altering creation time attributes or deleting addresses.

        Args:
        config_obj (Config): An instance of Config containing the addresses to be applied
        """
        address_objs_config = {
            addr["address"]: address_transform(addr) for addr in config_obj.data
        }
        location_ids = {addr["location_id"] for addr in config_obj.data}
        address_objs_service = {}
        try:
            address_objs_service = {
                addr["address"]: address_transform(addr)
                for addr in self.service.v2_get_addresses(
                    location_ids=list(location_ids)
                )
            }
        except HTTPError as e:
            log.error(f"Failed to get existing addresses: {e}")
            return {f"{self.config_name}.{IMSConfigType.ADDRESSES.value}": False}

        addresses_to_update = set(address_objs_config.keys()).intersection(
            set(address_objs_service.keys())
        )
        addresses_to_add = set(address_objs_config.keys()).difference(
            set(address_objs_service.keys())
        )
        addresses_unidentified = set(address_objs_config.keys()).difference(
            set(address_objs_service.keys())
        )

        log.debug(
            f"Addresses to be added -> These are new addresses from configuration which will be added to the environment: {addresses_to_add}"
        )
        log.debug(
            f"Addresses to be updated -> These are addresses that are in the existing environment which we will update as best we can (not all parameters can be updated in IMS): {addresses_to_update}"
        )
        log.debug(
            f"Unidentified addresses -> These are addresses that are in the existing environment that are not in our configuration: {addresses_unidentified}"
        )

        # Run create operation on new addresses
        if len(addresses_to_add) > 0:
            try:
                self.service.v2_create_addresses(
                    [
                        addr.get_create_values()
                        for addr in address_objs_config.values()
                        if addr.address in addresses_to_add
                    ]
                )
            except HTTPError as e:
                log.error(f"Failed to create new addresses: {e}")
                return {f"{self.config_name}.{IMSConfigType.ADDRESSES.value}": False}

        # Run through all addresses in config
        # If existing, update address attributes
        # If new, attributes cannot be set on create and must be set here
        update_error = False
        for address in address_objs_config.values():
            exist_addr = address_objs_service.get(address.address)
            if (
                exist_addr is None
                or exist_addr.dynamic != address.dynamic
                or exist_addr.overstock != address.overstock
                or exist_addr.pickable != address.pickable
                or exist_addr.active != address.active
                or exist_addr.temp_zone != address.temp_zone
            ):
                try:
                    self.service.v2_update_address_attributes(
                        address=address.address,
                        location_code=address.location_id,
                        dynamic=address.dynamic,
                        overstock=address.overstock,
                        pickable=address.pickable,
                        active=address.active,
                        temp_zone=address.temp_zone,
                    )
                except HTTPError as e:
                    log.error(f"Failed to update attributes for {address.address}: {e}")
                    update_error = True
        if update_error:
            return {f"{self.config_name}.{IMSConfigType.ADDRESSES.value}": False}
        return {f"{self.config_name}.{IMSConfigType.ADDRESSES.value}": True}

    def apply_reason_codes(self, config_obj: Config) -> dict[str, bool]:
        log.info("Applying reason_codes")
        reason_codes_data = config_obj.data
        try:
            self.service.replace_reason_codes(reason_codes_data)
            return {f"{self.config_name}.{IMSConfigType.REASON_CODES.value}": True}
        except HTTPError as e:
            log.error(f"Failed to Post reason_codes: {e}")
            return {f"{self.config_name}.{IMSConfigType.REASON_CODES.value}": False}


def address_transform(addr: dict) -> Address:
    addr["temp_zone"] = addr["temp-zone"]
    del addr["temp-zone"]
    addr["location_id"] = addr["location-id"]
    del addr["location-id"]
    return Address(**addr)
