from typing import Tuple
from src.api.takeoff.tsc import TSC
from src.copy_config.exception import CopyConfigErrorCodes, CopyConfigException
from src.copy_config.filter import (
    DEPRECATED_FIELDS,
    EXCLUDE_FOR_ODE,
    ExcludeTSC,
    filter_tsc_payload,
)
from src.utils.console_printing import error_print, error
from src.utils.helpers import remove_fields


def del_dict_list_by_name(dict_list: list, name: str) -> list:
    """Returns a new list with a specified dictionary key deleted

    Args:
        dict_list (list): list of dictionaries to modify
        name (str): key to look for

    Returns:
        list: newly formed list of dictionaries
    """
    return list(filter(lambda i: i["name"] != name, dict_list))


def check_config_items(
    source_config_items: list[dict],
    target_config_items: list[dict],
    is_ode: bool = True,
    require_no_unexpected_data: bool = False,
) -> bool:
    """Compares 2 lists of dictionaries of configuration data from service
    catalog API:configuration/get_api_v1_configuration_config_items

    Args:
        source_config_items (list[dict]): source config
        target_config_items (list[dict]): target list

    Returns:
        bool: True if they match, False otherwise
    """
    check_passed = True
    for item in source_config_items:
        if (any(enum_value.name in item["name"] for enum_value in ExcludeTSC)) or (
            any(item["name"] == i for i in DEPRECATED_FIELDS)
            or (is_ode and str(item["name"]) == EXCLUDE_FOR_ODE)
        ):
            target_config_items = del_dict_list_by_name(
                target_config_items, item["name"]
            )
        else:
            # look for matching item name
            res = next(
                (sub for sub in target_config_items if sub["name"] == item["name"]),
                None,
            )
            if res:
                if res["value"] != item["value"]:
                    # value didn't match when it should have
                    check_passed = False
                    print(
                        error(
                            f"source config item: {item} did not match with\ntarget config item: {res}"
                        )
                    )

                target_config_items = del_dict_list_by_name(
                    target_config_items, item["name"]
                )
            else:
                # value didn't exist on source
                check_passed = False
                print(
                    error(
                        f"source config item: {item} did not exist in target configuration"
                    )
                )

    filtered_target_items_map = filter_tsc_payload(
        {"filter": target_config_items}, is_ode
    )
    for _, filtered_target_items in filtered_target_items_map.items():
        if require_no_unexpected_data and len(filtered_target_items) > 0:
            # target list should have been empty
            check_passed = False
            print(
                error(
                    "target configuration had config items that didn't exist in source, see list below:"
                )
            )
            print(error(filtered_target_items))
    return check_passed


def check_values(
    source_items: list[dict],
    target_items: list[dict],
    ignore_fields: list[str] = [],
    print_differences=True,
) -> Tuple[bool, list]:
    """Checks two lists looking for differences. Prints out the differences if
    there are any.

    Args:
        source_items (list[dict]): list 1 to compare
        target_items (list[dict]): list 2 to compare
        ignore_fields (list[str]): fields to ignore in comparison

    Returns:
        bool: True if the lists are identical, False otherwise
        list: list of dicts that are different
    """
    result = []
    if source_items and target_items:
        for i in remove_fields(source_items, ignore_fields):
            if i not in remove_fields(target_items, ignore_fields):
                if print_differences:
                    print("Found a difference")
                    print(i)
                result.append(i)
    if not result:
        return True, []
    if print_differences:
        print(error(f"The difference was: {result}"))
    return False, result


def sanity_check(source: TSC, target: TSC, is_ode=True) -> bool:
    """Goes through a series Get calls for service_catalog

    Args:
        source (TSC): source tsc
        target (TSC): target tsc

    Raises:
        CopyConfigException: SANITY_CHECK_FAILURE

    Returns:
        bool: true if every checks out, false otherwise
    """
    try:
        location_code = source.config.location_code_tom
        check_passed = check_config_items(
            source.get_config_items(True, level=None, location_tom_code=location_code),
            target.get_config_items(True, level=None, location_tom_code=location_code),
            is_ode,
        )
        source_location_details = remove_fields(
            source.get_location_code(
                location_code_type=None, location_tom_code=location_code
            ),
            ["location-id", "location-code-gold"],
        )
        target_location_details = remove_fields(
            target.get_location_code(
                location_code_type=None, location_tom_code=location_code
            ),
            "location-id",
        )
        if False in check_values(
            source_location_details, target_location_details, "location-code-gold"
        ):
            print(
                error(
                    "Source ENV location details did not match Target ENV location details"
                )
            )
            check_passed = False
            print(
                error(
                    f"source locations:\n {source_location_details} \ndid not "
                    f"match target locations:\n {target_location_details}"
                )
            )

        if False in check_values(
            source.get_tote_location_types(),
            target.get_tote_location_types(),
            ["tote-type-id"],
        ):
            # check failed - totes don't match even when not comparing
            # tote-type-id
            print(
                error(
                    "source tote_location_types did not match target tote_location_types"
                )
            )
            check_passed = False
        if not check_values(source.get_routes(), target.get_routes()):
            print(
                error(
                    f"source routes {source.get_routes()} did not match target routes {target.get_routes()}"
                )
            )
            check_passed = False
        if not check_values(source.get_flow_racks(), target.get_flow_racks()):
            print(
                error(
                    f"source flow_racks {source.get_flow_racks()} did not match target flow_racks {target.get_flow_racks()}"
                )
            )
            check_passed = False
        if not check_values(
            source.get_staging_configurations(), target.get_staging_configurations()
        ):
            print(
                error(
                    "source staging_configurations: "
                    f"{source.get_staging_configurations()} did not match "
                    "target staging_configurations: "
                    + target.get_staging_configurations()
                )
            )
            check_passed = False
        if not check_values(
            source.get_staging_locations(), target.get_staging_locations()
        ):
            print(
                error("source staging_locations did not match target staging_locations")
            )
            check_passed = False
        return check_passed
    except Exception as e:
        error_print(e)
        raise CopyConfigException(CopyConfigErrorCodes.SANITY_CHECK_FAILURE)


def compare_configuration_sets(source, target, is_ode=True) -> bool:
    """Goes through dictionaries of config data

    Args:
        source (ConfigurationSet): source configuration set
        target (ConfigurationSet): target tsc

    Raises:
        CopyConfigException: SANITY_CHECK_FAILURE

    Returns:
        bool: true if every checks out, false otherwise
    """
    try:
        location = source.locations["location-code-tom"]
        check_passed = check_config_items(
            source.config_items[location],
            target.config_items[location],
            is_ode,
        )
        if not check_config_items(
            source.config_items["env"],
            target.config_items["env"],
            is_ode,
        ):
            print(
                error(
                    "Source ENV mfc config items did not match Target ENV mfc config items"
                )
            )
            check_passed = False
        source_location_details = remove_fields(
            source.locations,
            ["location-id", "location-code-gold"],
        )
        target_location_details = remove_fields(
            target.locations,
            "location-id",
        )
        if not check_values(
            source_location_details, target_location_details, "location-code-gold"
        ):
            print(
                error(
                    "Source ENV location details did not match Target ENV location details"
                )
            )
            check_passed = False
            print(
                error(
                    f"source locations:\n {source_location_details} \ndid not "
                    f"match target locations:\n {target_location_details}"
                )
            )

        if not check_values(
            source.tote_types,
            target.tote_types,
            ["tote-type-id"],
        ):
            # check failed - totes don't match even when not comparing
            # tote-type-id
            print(
                error(
                    "source tote_location_types did not match target tote_location_types"
                )
            )
            check_passed = False
        if not check_values(source.src_routes, target.src_routes):
            print(
                error(
                    f"source routes {source.src_routes} did not match target routes {target.src_routes}"
                )
            )
            check_passed = False
        if not check_values(source.flow_racks, target.flow_racks):
            print(
                error(
                    f"source flow_racks {source.flow_racks} did not match target flow_racks {target.flow_racks}"
                )
            )
            check_passed = False
        if not check_values(source.staging_config, target.staging_config):
            print(
                error(
                    "source staging_configurations: "
                    f"{source.staging_config} did not match "
                    "target staging_configurations: " + target.staging_config
                )
            )
            check_passed = False
        if not check_values(source.staging_locations, target.staging_locations):
            print(
                error("source staging_locations did not match target staging_locations")
            )
            check_passed = False
        return check_passed
    except Exception as e:
        error_print(e)
        raise CopyConfigException(CopyConfigErrorCodes.SANITY_CHECK_FAILURE)
