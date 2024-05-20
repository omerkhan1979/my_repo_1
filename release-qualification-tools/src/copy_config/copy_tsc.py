import os
import pathlib
import sys
from dataclasses import dataclass, field
from typing import Optional, List

from requests import HTTPError

import yaml

from src.api.takeoff.ops_api import OpsApi
from src.api.takeoff.tsc import TSC, get_default_staging_location_code
from src.copy_config.check import check_values
from src.copy_config.filter import (
    apply_location_osr_values,
    compare_flow_racks,
    filter_staging_configurations,
)
from src.utils.helpers import remove_fields

from src.copy_config.exception import CopyConfigErrorCodes, CopyConfigException
from src.utils.console_printing import blue, error_print, red
from src.config.constants import BASE_DOMAIN, RETAILERS_DEFAULT_LOCATION
from src.config.config import Config, get_token
from src.utils.git import copy_file_from_repo


# for retailers with multiple locations, this is useful
# for some tests. Used by copy_config in ODE context.
RETAILERS_SECONDARY_LOCATION = {
    "abs": "2508",
    "maf": "D03",
    "smu": "1917",
    "wings": "2006",
    "winter": "WF0608",
    "tienda": "0044",
}


CONFIGS_DATA_REPO_URL = "https://github.com/takeoff-com/environment-configs.git"
SERVICE_CATALOG_CONFIGS_DIR = "service-catalog-configs/"

project_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_root_dir)


@dataclass
class ConfigurationSet:
    """Class for holding all configuration entities."""

    config_items: dict = field(default_factory=dict)
    flow_racks: dict = field(default_factory=dict)
    spokes: dict = field(default_factory=dict)
    tote_types: dict = field(default_factory=dict)
    staging_config: dict = field(default_factory=dict)
    staging_locations: dict = field(default_factory=dict)
    src_routes: dict = field(default_factory=dict)
    locations: dict = field(default_factory=dict)


def configurationset_constructor(loader, node) -> ConfigurationSet:
    values = loader.construct_mapping(node)
    return ConfigurationSet(**values)


def get_loader():
    """Add constructors to PyYAML loader."""
    loader = yaml.SafeLoader
    loader.add_constructor("!ConfigurationSet", configurationset_constructor)
    return loader


def configurationset_representer(
    dumper: yaml.SafeDumper, config_set: ConfigurationSet
) -> yaml.nodes.MappingNode:
    """Represent a ConfigurationSet instance as a YAML mapping node."""
    return dumper.represent_mapping(
        "!ConfigurationSet",
        {
            "config_items": config_set.config_items,
            "flow_racks": config_set.flow_racks,
            "spokes": config_set.spokes,
            "tote_types": config_set.tote_types,
            "staging_config": config_set.staging_config,
            "staging_locations": config_set.staging_locations,
            "src_routes": config_set.src_routes,
            "locations": config_set.locations,
        },
    )


def get_dumper():
    """Add representers to a YAML seriailizer."""
    safe_dumper = yaml.SafeDumper
    safe_dumper.add_representer(ConfigurationSet, configurationset_representer)
    return safe_dumper


def config_from_yaml(file_path: str):
    """Load a configuration file from the source information

    Returns:
    ConfigurationSet: source
    context
    of
    configuration

    """
    # get file from the git repo
    file_path_out = copy_file_from_repo(CONFIGS_DATA_REPO_URL, file_path)
    print(blue(f'----Config file saved to "{file_path_out}"'))
    # Load the config and check the file type (yaml)
    with open(file_path_out, "r") as file:
        try:
            config = yaml.load(file, Loader=get_loader())
            if not isinstance(config, ConfigurationSet):
                raise TypeError(
                    "Invalid file format. The file must contain ConfigurationSet."
                )
        except yaml.YAMLError as e:
            error_print(red(f"Error reading file {file_path}: {str(e)}"))

    return config


def config_to_yaml(file_path: str, config_set: ConfigurationSet):
    """Dump a ConfigurationSet to a YAML file."""
    pathlib.Path(os.path.dirname(file_path)).mkdir(parents=True, exist_ok=True)
    with open(file_path, "w+") as fh:
        fh.write(yaml.dump(config_set, Dumper=get_dumper()))


def get_configs_file_path(
    retailer: str,
    location: str,
    configs_folder=SERVICE_CATALOG_CONFIGS_DIR,
) -> str:
    """Returns file path to a config yaml file for a given retailer and location. Creates directory if doesn't exist"""
    file_name = f"{retailer}-{location}.yaml"
    config_data_dir = f"{configs_folder}{retailer}"
    file_path = os.path.join(config_data_dir, file_name)
    return file_path


class CopyTsc:
    """CopyTsc is the main class that performs the necessary operation for the
    process
    """

    retailer: str = ""
    env_source: str = "prod"
    env_target: str = ""
    mfc_locations: list = []
    preview: bool = False
    ode_project_name: str = ""
    file_path: str = ""

    def __init__(
        self,
        retailer: Optional[str] = None,
        env_source: Optional[str] = None,
        env_target: Optional[str] = None,
        mfc_locations: Optional[List[str]] = None,
        preview: Optional[bool] = None,
        ode_project_name: Optional[str] = None,
        file_path: Optional[str] = None,
    ):
        self.retailer = retailer or ""
        self.env_source = env_source or ""
        self.env_target = env_target or ""
        self.mfc_locations = mfc_locations or []
        self.preview = preview or False
        self.ode_project_name = ode_project_name or ""
        self.file_path = file_path or ""

    def __str__(self):
        """String representation of the class"""
        return (
            f"CopyTsc {{retailer: {self.retailer}, "
            f"env_source: {self.env_source}, "
            f"env_target: {self.env_target}, preview: {self.preview}, "
            f"mfc_locations: {self.mfc_locations}, "
            f"ode_project_name: {self.ode_project_name}}}"
            f"file_path: {self.file_path}"
        )

    def validate_args(self, c_args) -> list[CopyConfigErrorCodes]:
        """
        Goes through the the list of args that were captured and confirms if
        they are appropriate.

        Returns:
            CopyConfigErrorCodes: Error code if error occurred, otherwise 0
        """
        if c_args.locations:
            if len(c_args.locations) == 1:
                self.mfc_locations = c_args.locations[0].split(" ")
            else:
                self.mfc_locations = c_args.locations
        errors: list[CopyConfigErrorCodes] = []
        # lets check source env is available
        source_details: list = str(c_args.source_env[0]).split(":")
        if len(source_details) == 0:
            errors.append(CopyConfigErrorCodes.NO_SOURCE_DETAILS)
            error_print(CopyConfigErrorCodes.NO_SOURCE_DETAILS.error_message)
        else:
            self.env_source = source_details[0].lower().strip("'").strip()

        if c_args.command == "copy_config":
            # For command 'copy_config', require the --target_env argument
            if not c_args.target_env:
                errors.append(CopyConfigErrorCodes.NO_TARGET_DETAILS)
                error_print(CopyConfigErrorCodes.NO_TARGET_DETAILS.error_message)
            else:
                target_details: list = str(c_args.target_env[0]).split(":")
                # lets check target env is available
                if len(target_details) == 0:
                    errors.append(CopyConfigErrorCodes.NO_TARGET_DETAILS)
                    error_print(CopyConfigErrorCodes.NO_TARGET_DETAILS.error_message)
                self.env_target = target_details[0].lower().strip("'").strip()

        self.retailer = c_args.retailer[0].lower().strip()
        if self.retailer:
            if not RETAILERS_DEFAULT_LOCATION.get(self.retailer):
                errors.append(CopyConfigErrorCodes.NOT_VALID_CLIENT)
                error_print(CopyConfigErrorCodes.NOT_VALID_CLIENT.error_message)
        else:
            errors.append(CopyConfigErrorCodes.NO_CLIENT)
            error_print(CopyConfigErrorCodes.NO_CLIENT.error_message)

        if len(self.mfc_locations) == 0 and self.retailer != "file":
            self.mfc_locations.append(RETAILERS_DEFAULT_LOCATION.get(self.retailer))
            if self.retailer in RETAILERS_SECONDARY_LOCATION:
                self.mfc_locations.append(RETAILERS_SECONDARY_LOCATION[self.retailer])
        if c_args.preview:
            self.preview = c_args.preview
        if c_args.path:
            self.file_path = c_args.path
        return errors

    def get_source_config(self, location_source) -> Config:
        """Generates a Config object from the source information
        Returns:
            Config: source context of configuration
        """
        return Config(
            self.retailer,
            self.env_source,
            location_source,
            token=get_token(self.retailer, self.env_source),
            disallow=False,
        )

    def get_target_config(self, location_target) -> Config:
        """Generates a Config object from the target information

        Returns:
            Config: target context of configuration
        """
        env = self.env_target
        if self.env_target == "ode" and not BASE_DOMAIN.startswith(
            self.ode_project_name
        ):
            env = f"ode.{self.ode_project_name}"
        return Config(
            retailer=self.retailer,
            env=env,
            location_code_tom=location_target,
            token=get_token(self.retailer, self.env_target),
            disallow=False,
            skip_location_check=True if self.env_target == "ode" else False,
        )

    def update_target_location(
        self, tsc_tgt: TSC, location: dict, site_number: int, spokes: list = None
    ):
        """Creates/updates/enables location

        Args:
            tsc_tgt (TSC): endpoint to check/update
            locations (dict): content of locations from a source

        Raises:
            CopyConfigException: LOCATION_CREATION_FAILED error
        """
        print(
            blue(
                f'----Getting locations available for "{self.env_target}" '
                f'for "{self.retailer}"----'
            )
        )
        # check if location exist: update it; if not enabled - enable, else create and enable
        is_exist, is_enabled, found_locations = self.is_location_exist_and_enabled(
            tsc_tgt, tsc_tgt.config.location_code_tom
        )
        try:
            if is_exist:
                print(
                    blue(
                        f'----Updating location "{tsc_tgt.config.location_code_tom}" for '
                        f'"{tsc_tgt.config.retailer}"----'
                    )
                )
                tsc_tgt.update_location(
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
                    self.enable_location(tsc_tgt, found_locations[0])
            else:
                # create location
                print(
                    blue(
                        "----Creating location "
                        f'"{tsc_tgt.config.location_code_tom}" for '
                        f'"{tsc_tgt.config.retailer}"----'
                    )
                )
                location_body = remove_fields(
                    location, ["location-type", "mfc-ref-code", "location-id"]
                )
                if isinstance(location_body, list):
                    if len(location_body) == 1:
                        location_body = location_body[0]
                    else:
                        print(red("More than one location not expected"))
                        raise CopyConfigException(
                            CopyConfigErrorCodes.LOCATION_CREATION_FAILED
                        )
                location = tsc_tgt.post_mfc_location(location_body)
                print(
                    blue(
                        "----Successfully created location "
                        f'"{tsc_tgt.config.location_code_tom}" for '
                        f'"{tsc_tgt.config.retailer}"----'
                    )
                )
                OpsApi(tsc_tgt.config).initialize_picking_queue(
                    tsc_tgt.config.location_code_tom
                )
                # enable it
                self.enable_location(tsc_tgt, location)

                print(
                    blue(
                        "----Applying default profile on location "
                        f'"{tsc_tgt.config.location_code_tom}" for {tsc_tgt.config.retailer}"'
                        "----"
                    )
                )
                tsc_tgt.apply_profile()
                print(
                    blue(
                        "----Successfully applied default profile on location "
                        f'"{tsc_tgt.config.location_code_tom}" for "'
                        f'{tsc_tgt.config.retailer}"----'
                    )
                )
                print(
                    blue(
                        "----Applying default OSR values on location "
                        f'"{tsc_tgt.config.location_code_tom}" for "'
                        f'{tsc_tgt.config.retailer}"----'
                    )
                )
                apply_location_osr_values(tsc_tgt, site_number)
                print(
                    blue(
                        "----Successfully applied default OSR values on location "
                        f'"{tsc_tgt.config.location_code_tom}" for "'
                        f'{tsc_tgt.config.retailer}"----'
                    )
                )
        except Exception as e:
            error_print(e)
            raise CopyConfigException(
                CopyConfigErrorCodes.LOCATION_CREATION_FAILED, message=e
            )

        if spokes:
            print(
                blue(
                    f'----Updating spokes on "{tsc_tgt.config.env}" for retailer "{tsc_tgt.config.retailer}"----'
                )
            )
            for spoke in spokes:
                print(
                    blue(
                        f'----Updating spoke "{spoke["location-code-tom"]}" on location "{location["location-code-tom"]}"----'
                    )
                )
                self.update_target_spoke(
                    tsc_tgt,
                    tsc_tgt.get_location_id_by_code_tom(location["location-code-tom"]),
                    spoke,
                )
            print(
                blue(
                    f'----Finished posting spokes on "{tsc_tgt.config.env}" for retailer "{tsc_tgt.config.retailer}"----'
                )
            )
        else:
            print(
                blue(
                    f'----No spokes to update on "{tsc_tgt.config.env}" for retailer "{tsc_tgt.config.retailer}"----'
                )
            )

    def is_location_exist_and_enabled(
        self, tsc: TSC, mfc_tom_code: str, is_spoke: bool = False
    ) -> bool:
        is_exist = False
        is_active = False
        found_locations = {}
        active_locations = tsc.get_tom_code_locations("true")
        if active_locations:
            found_locations = self.filter_location_from_list(
                mfc_tom_code, active_locations, is_spoke
            )
            if found_locations:
                is_active = True
                is_exist = True
        else:
            disabled_locations = tsc.get_tom_code_locations("false")
            found_locations = self.filter_location_from_list(
                mfc_tom_code, disabled_locations, is_spoke
            )
            if found_locations:
                is_active = False
                is_exist = True

        return is_exist, is_active, found_locations

    def filter_location_from_list(
        self, mfc_tom_code: str, locations_list, is_spoke: bool = False
    ):
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

    def enable_location(self, tsc_tgt: TSC, location: dict):
        print(
            blue(
                f'----Enabling mfc location "{tsc_tgt.config.location_code_tom}" for '
                f'"{tsc_tgt.config.retailer}"----'
            )
        )
        tsc_tgt.set_location_availability(location["location-id"])
        print(
            blue(
                f'----Completed updated of location "{tsc_tgt.config.location_code_tom}" for '
                f'"{tsc_tgt.config.retailer}"----'
            )
        )
        return

    def update_target_spoke(self, tsc_tgt: TSC, mfc_id: int, spoke: dict):
        """Creates or updates spoke

        Args:
            tsc_tgt (TSC): endpoint to check/update
            spoke (dict): content of spoke from a source

        Raises:
            CopyConfigException: SPOKE_CREATION_FAILED error
        """
        is_exist, is_enabled, found_spokes = self.is_location_exist_and_enabled(
            tsc_tgt, spoke["location-code-tom"], True
        )
        if is_exist:
            updated_spoke = False
            for found_spoke in found_spokes:
                if found_spoke.get("mfc_ref_code") != mfc_id:
                    print(
                        f"Not making spoke for other mfc: {found_spoke.get('mfc_ref_code')} have mfc_id: {mfc_id}"
                    )
                    continue
                try:
                    tsc_tgt.update_location_spoke(
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
                    updated_spoke = True
                    break
                except HTTPError as e:
                    error_print(e)
                    error_print(
                        CopyConfigException(CopyConfigErrorCodes.SPOKE_UPDATE_FAILED)
                    )

            if not updated_spoke:
                # Probably Got 404 try creating the spoke
                self.create_spoke(
                    tsc_tgt,
                    mfc_id,
                    remove_fields(
                        spoke,
                        [
                            "location-id",
                        ],
                    ),
                )
            else:
                print(
                    blue(
                        "----Successfully updated spoke "
                        f'"{found_spoke["location-code-tom"]}" for '
                        f'"{tsc_tgt.config.retailer}"----'
                    )
                )
                if not is_enabled:
                    self.enable_location(tsc_tgt, found_spoke)

        else:
            self.create_spoke(
                tsc_tgt,
                mfc_id,
                remove_fields(
                    spoke,
                    [
                        "location-id",
                    ],
                ),
            )

    def create_spoke(self, tsc_tgt: TSC, mfc_id: int, spoke: dict):
        """Creates spokes

        Args:
            tsc_tgt (TSC): endpoint to check/update
            spoke (dict): content of spoke from a source

        Raises:
            CopyConfigException: SPOKE_CREATION_FAILED error
        """
        try:
            # Spoke doesn't exist at all lets create it
            print(
                blue(
                    f'----Creating spoke "{spoke["location-code-tom"]}" for "{tsc_tgt.config.retailer}"----'
                )
            )
            tsc_tgt.create_location_spoke(
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
            print(
                blue(
                    f'----Successfully created spoke "{spoke["location-code-tom"]}" for "{tsc_tgt.config.retailer}"----'
                )
            )
        except Exception as e:
            error_print(e)
            print("To work around some data issues, not raising here, See PROD-12474")
            # raise CopyConfigException(CopyConfigErrorCodes.SPOKE_CREATION_FAILED)

    def update_non_standard_tsc(
        self,
        flow_racks: dict,
        tote_types: dict,
        staging_config: dict,
        staging_locations: dict,
        routes: dict,
        location: str,
    ):
        """Performs the updates to target of the non standard config, i.e. the
        configuration items that have their own path to the service catalog
        API.

        Args:
            tsc_tgt (TSC): CopyTSC object of the target
            flow_racks (dict): dictionary of the different flow_racks
            tote_types (list): list of all the tote_types from source
            staging_config (dict): body to be used for the post of staging config
            staging_locations (dict): _description_
            routes (dict): dictionary of the different routes
            location
        """
        tsc_tgt = TSC(self.get_target_config(location))

        if routes:
            print(
                blue(
                    f'----Updating routes on "{tsc_tgt.config.env}" for '
                    f'retailer "{tsc_tgt.config.retailer}"----'
                )
            )
            for route in routes["routes"]:
                print(blue(f'----Updating route "{route}"----'))
                tsc_tgt.post_route(route, [201, 200])
            print(
                blue(
                    f'----Finished posting routes on "{tsc_tgt.config.env}"'
                    f'for retailer "{tsc_tgt.config.retailer}"----'
                )
            )
        else:
            print(
                blue(
                    f'----No route to update on "{tsc_tgt.config.env}" for '
                    f'retailer "{tsc_tgt.config.retailer}" for location "'
                    f'{location}"----'
                )
            )
        filter_flow_racks = compare_flow_racks(flow_racks, tsc_tgt.get_flow_racks())
        if filter_flow_racks:
            print(
                blue(
                    f'----Updating flow racks on "{tsc_tgt.config.env}" for'
                    f' retailer "{tsc_tgt.config.retailer}" for location "'
                    f'{location}"----'
                )
            )
            tsc_tgt.put_flow_racks(filter_flow_racks, [201, 200])
            print(
                blue(
                    "----Completed Updating flow racks on "
                    f'"{tsc_tgt.config.env}" for retailer '
                    f'"{tsc_tgt.config.retailer}" for location "'
                    f'{location}"----'
                )
            )
        else:
            print(
                blue(
                    f'----No flow racks to update on "{tsc_tgt.config.env}'
                    f'" for retailer "{tsc_tgt.config.retailer}" for '
                    f'location "{location}"----'
                )
            )

        result, totes = check_values(
            tote_types,
            tsc_tgt.get_tote_location_types(),
            ["tote-type-id"],
            False,
        )
        if result:
            print(
                blue(
                    "----No need to update tote types on "
                    f'"{tsc_tgt.config.env}" for retailer '
                    f'"{tsc_tgt.config.retailer}" for '
                    f'location "{location}"----'
                )
            )
        else:
            print(
                blue(
                    "----Creating tote types on "
                    f'"{tsc_tgt.config.env}" for retailer '
                    f'"{tsc_tgt.config.retailer}" for '
                    f'location "{location}"----'
                )
            )
            for tote_type in totes:
                tsc_tgt.post_tote_type(tote_type, [201, 200])
            print(
                blue(
                    "----Completed with creating tote type on "
                    f'"{tsc_tgt.config.env}" for retailer '
                    f'"{tsc_tgt.config.retailer}" for '
                    f'location "{location}"----'
                )
            )

        print(
            blue(
                f'----Updating staging locations on "{tsc_tgt.config.env}"'
                f'for retailer "{tsc_tgt.config.retailer}" for location "'
                f'{location}"----'
            )
        )

        for staging_location in staging_locations["staging-locations"]:
            # "default" key is not allowed in the post_staging_location request body. Removing the key from the dict
            # before posting staging location to the target env
            location_to_post = staging_location.copy()
            if "default" in location_to_post:
                location_to_post.pop("default")
            tsc_tgt.post_staging_location(location_to_post, [201, 200])

        print(
            blue(
                '----Updating staging configurations on "'
                f'{tsc_tgt.config.env}" for retailer "'
                f'{tsc_tgt.config.retailer}" for location "'
                f'{location}"----'
            )
        )
        post_body: dict = filter_staging_configurations(staging_config)
        post_body["mfc-tom-code"] = tsc_tgt.config.location_code_tom
        tsc_tgt.post_staging_configurations(post_body, [201, 200])

        print(
            blue(
                '----Updating default staging location on "'
                f'{tsc_tgt.config.env}" for retailer "'
                f'{tsc_tgt.config.retailer}" for location "'
                f'{location}"----'
            )
        )

        default_location = get_default_staging_location_code(staging_locations)
        if default_location:
            tsc_tgt.put_default_staging_location(
                default_location, tsc_tgt.config.location_code_tom, [201, 200]
            )
        else:
            print(blue("----No default staging location found in source config----"))
