from argparse import ArgumentParser
import os
import sys

project_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_root_dir)
config_data_dir = os.path.join(project_root_dir, "tests/config-data")

from src.api.takeoff.tsc import TSC
from src.copy_config.check import (
    compare_configuration_sets,
)
from src.copy_config.copy_tsc import (
    ConfigurationSet,
    CopyTsc,
    config_from_yaml,
    config_to_yaml,
    get_configs_file_path,
)
from src.copy_config.exception import CopyConfigErrorCodes, CopyConfigException
from src.copy_config.filter import (
    apply_location_osr_values,
    filter_tsc_payload,
)
from src.utils.console_printing import blue, error, error_print, green, red
from src.config.constants import RETAILERS_DEFAULT_LOCATION


def main():
    """Update the Target ENVs
    If some of the configuration items fail to be updated stop the flow and
    report the error to caller mechanism. Combine all results and send back
    to caller.
    """

    try:
        print(green("----Executing Copy Configuration----"))
        c = CopyTsc()
        print(blue("----Parsing passed in arguments----"))
        # Exits here with a raised exception if the arguments have issues
        try:
            command = cli_parser(c, sys.argv[1:])
        except SystemExit as e:
            error_print(CopyConfigException(CopyConfigErrorCodes.PARSE_ERROR))
            raise e

        if command == "pull_from_prod":
            c.env_source = "prod"
            # get all enabled locations from prod
            tsc = TSC(c.get_source_config(RETAILERS_DEFAULT_LOCATION.get(c.retailer)))

            c.mfc_locations = [
                loc["location-code-tom"] for loc in tsc.get_enabled_mfc_locations()
            ]
            for location in c.mfc_locations:
                config_set = pull_config_from_source(c, location)
                config_to_yaml(get_configs_file_path(c.retailer, location), config_set)

        elif command == "copy_config":
            copy_config(c)
    except CopyConfigException as e:
        raise e


def copy_config(cpy_tsc: CopyTsc) -> bool:
    success = False
    try:
        for site_number, location in enumerate(cpy_tsc.mfc_locations):
            # ftp users start at 1, so shift up one
            # see: https://github.com/takeoff-com/infra-tgim-ftp/blob/24574eade9d87626bd0cbb1946067e416310c685/entrypoint.sh#L27
            site_number = site_number + 1
            print(
                blue(
                    f'----Retrieving the tsc data from source evn "{cpy_tsc.env_source}"'
                    f' for retailer "{cpy_tsc.retailer}" for location "{location}"----'
                )
            )
            try:
                if cpy_tsc.env_source == "file":
                    # pull config from existing retailer/retailer-location.yaml file
                    if not cpy_tsc.file_path:
                        file_path = get_configs_file_path(cpy_tsc.retailer, location)
                        config_set = config_from_yaml(file_path)
                    # pull config from provided file
                    else:
                        config_set = config_from_yaml(cpy_tsc.file_path)
                else:
                    config_set = pull_config_from_source(cpy_tsc, location)

                # Skip location if its not in the config set and go to next
                if not config_set.locations:
                    print(
                        error(
                            f'Location "{location}" is not a valid location '
                            f'for retailer "{cpy_tsc.retailer}"'
                        )
                    )
                    continue

            except CopyConfigException as e:
                error_print(e)
                raise e
            except Exception as e:
                error_print(e)
                raise CopyConfigException(CopyConfigErrorCodes.FAILED_SOURCE_RETRIEVAL)
            except SystemExit as e:
                error_print(e)
                raise CopyConfigException(CopyConfigErrorCodes.FAILED_SOURCE_RETRIEVAL)
            # Need to confirm that the Excluded config_items exist else
            # we need to provide some default values for them
            try:
                tsc_tgt = TSC(cpy_tsc.get_target_config(location))
            except SystemExit as e:
                error_print(e)
                raise CopyConfigException(CopyConfigErrorCodes.TARGET_TOKEN_INVALID)

            # need to create location first before updating anything
            if cpy_tsc.env_target == "ode":
                tsc_tgt.config.location_code_tom = location

            if cpy_tsc.preview is True:
                print(blue("----Preview was requested----"))
                print(
                    blue(
                        "----The following would be the list of config items that would be updated:"
                    )
                )
                print(green(config_set.config_items))
                print(blue("Preview ended"))

            else:
                cpy_tsc.update_target_location(
                    tsc_tgt, config_set.locations, site_number, config_set.spokes
                )

                if cpy_tsc.env_target == "ode":
                    apply_location_osr_values(tsc_tgt, site_number)

                updating_env = (
                    cpy_tsc.ode_project_name
                    if cpy_tsc.env_target == "ode"
                    else cpy_tsc.env_target
                )
                print(
                    blue(
                        f'----Updating the tsc data on target env "{updating_env}" '
                        f'for retailer "{cpy_tsc.retailer}"----'
                    )
                )
                try:
                    for _, config_items in config_set.config_items.items():
                        tsc_tgt.put_config_items(config_items, [201, 200])

                    print(
                        blue(
                            "----Sucessfully completed the updates to config "
                            f'item values for retailer "{cpy_tsc.retailer}" for location'
                            f' "{location}"----'
                        )
                    )

                    # update the non standard tsc
                    cpy_tsc.update_non_standard_tsc(
                        flow_racks=config_set.flow_racks,
                        tote_types=config_set.tote_types,
                        staging_config=config_set.staging_config,
                        staging_locations=config_set.staging_locations,
                        routes=config_set.src_routes,
                        location=location,
                    )
                except Exception as e:
                    error_print(e)
                    if isinstance(e, CopyConfigException):
                        # we already created a copy config exception
                        raise e
                    else:
                        raise CopyConfigException(
                            CopyConfigErrorCodes.FAILED_TARGET_UPDATE
                        )

                print(
                    blue(
                        "----Performing sanity check for location " f'"{location}"----'
                    )
                )

                if not compare_configuration_sets(
                    config_set,
                    retrieval_source(tsc_tgt, location, cpy_tsc.env_target == "ode"),
                    cpy_tsc.env_target == "ode",
                ):
                    raise CopyConfigException(CopyConfigErrorCodes.SANITY_CHECK_FAILURE)
        success = True
    finally:
        if success:
            print(green("----Copy Configuration Completed----"))
        else:
            error_print(red("----Copy Configuration Failed----"))
        return success


def pull_config_from_source(cpy_tsc: CopyTsc, location: str) -> ConfigurationSet:
    """Method performs a retrieval of service catalog configurations from a production

    Args:
        cpy_tsc (CopyTsc): Source configuration
        location (str): mfc location to pull the data for

    Returns:
        tuple: tuple of the configuration values
    """
    tsc_src = TSC(cpy_tsc.get_source_config(location))
    config_set = retrieval_source(tsc_src, location, cpy_tsc.env_target == "ode")
    source = "Production" if cpy_tsc.env_source == "prod" else cpy_tsc.env_source
    print(green(f"----Pull Configuration from {source.upper()} Completed----"))
    return config_set


def retrieval_source(tsc_src: TSC, location, is_ode=False) -> ConfigurationSet:
    """Method performs a retrieval from a source service catalog API of all the
    possible configuration needed to be copied the target

    Args:
        c (CopyTsc): Source configuration

    Returns:
        tuple: tuple of the configuration values
    """
    # Get all the environment non MFC specific configuration items
    config_set = ConfigurationSet()
    config_items = {}
    config_items["env"] = tsc_src.get_config_items(True, level="env")
    config_set.flow_racks = tsc_src.get_flow_racks(location)
    config_set.spokes = tsc_src.get_all_spokes_for_mfc_tom(location)
    config_set.tote_types = tsc_src.get_tote_location_types(location)
    config_set.staging_config = tsc_src.get_staging_configurations(location)
    config_set.staging_locations = tsc_src.get_staging_locations(location)
    config_set.src_routes = tsc_src.get_routes(location)
    config_set.locations = tsc_src.get_location_details(location)
    config_items[f"{location}"] = tsc_src.get_config_items(True, "mfc", location)

    print(blue("----Filtering the tsc data for the unique items----"))
    config_set.config_items = filter_tsc_payload(config_items, is_ode)
    return config_set


def cli_parser(c: CopyTsc, args: list[str]) -> str:
    """Performs the parsing of the arguments passed into the copy tsc CLI.
    Error(s) are thrown if the arguments don't suffice the requirements. Every
    effort is made to return a message that specifically states what is wrong
    with what was provide in the CLI.

    Args:
        c (CopyTsc): object that will contain the data needed to perform the
        operations
        args (list[str]): arguments passed into the CLI

    Raises:
        CopyConfigException: NO_SOURCE_DETAILS, NO_SOURCE_ENV,
        NO_TARGET_DETAILS or DIFFERENT_CLIENTS

    Return:
          str - command to execute
    """
    parser = ArgumentParser(
        prog="Copy Configuration",
        description="Takes a source configuration and copies the relative"
        "configuration items to the target",
    )
    parser.add_argument(
        "command", choices=["pull_from_prod", "copy_config"], help="Command to execute"
    )
    parser.add_argument(
        "-r",
        "--retailer",
        nargs=1,
        type=str,
        required=True,
        help="The name of the retailer to mimic",
    )
    parser.add_argument(
        "-s",
        "--source_env",
        nargs=1,
        type=str,
        required=True,
        help="Source env in the following format {env}, For example, 'prod' or 'file'. Cannot be a ode",
    )
    parser.add_argument(
        "--path", type=str, default=False, help="Path to a custom config file"
    )
    parser.add_argument(
        "-t",
        "--target_env",
        nargs=1,
        type=str,
        required=False,
        help="Target env in the following format {env}, For example, dev uat or ode. Target env CANNOT be prod",
    )
    parser.add_argument(
        "-l",
        "--locations",
        nargs="+",
        required=False,
        help="A list of MFC locations {location} {location}. For example, "
        "D02 SD02 or D02. If location is not provided the default location for "
        "retailer is used.  Some retailers will get a second location supplied "
        "if no locations are provided.",
    )
    parser.add_argument(
        "-ode",
        "--ode_project_name",
        type=str,
        required=False,
        help="Specify the ode configuration name (project name) to update.",
    )
    # order matters this must be last
    parser.add_argument(
        "-p",
        "--preview",
        type=lambda x: (str(x).lower() == "true"),
        default=False,
        help="Allow to preview the changes before they happen otherwise update"
        " target (default: False)",
    )
    c_args = parser.parse_args(args=args)
    errors = c.validate_args(c_args)

    if errors:
        cc_exceptions = []
        # raise all exceptions
        for err in errors:
            cc_exceptions.append(err)
        raise Exception(cc_exceptions)

    return c_args.command


if __name__ == "__main__":
    main()
