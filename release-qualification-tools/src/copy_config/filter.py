import copy
from enum import Enum
from src.api.takeoff.tsc import TSC
from src.utils.service_catalog import modify_value

from src.utils.console_printing import error_print
from src.copy_config.exception import CopyConfigErrorCodes, CopyConfigException
from src.utils.helpers import remove_fields

DEPRECATED_FIELDS = (
    "PICK_BY_REQUEST_WEIGHT",
    "LAUNCH_DARKLY_CONFIG_MOBILE_KEY",
    "AUTO_BATCH_INTERVAL_SECONDS",
    "AUTO_CREATE_BATCH_ORDERS",
    "AUTO_SPLIT_INTERVAL_AFTER_SECONDS",
    "AUTO_SPLIT_INTERVAL_BEFORE_SECONDS",
    "AUTO_SPLIT_INTERVAL_SECONDS",
    "BATCH_BLOCK_STATUS_CHANGE_ENABLED",
    "BATCH_ENABLED",
    "BATCH_ORDER_PRINTER_PAGE_SIZE",
    "BATCH_PICKING_SERVICE_GAP",
    "BATCH_PICKING_WINDOW",
    "BATCH_SCHEDULER_DELAY_SECONDS",
    "BATCHING_AREAS",
    "CUTOFF_UPDATE_PERIOD_MINUTE",
    "CUTOFF_UPDATE_THRESHOLD_MINUTES",
    "DELIVERY_SLOTS_SHIFT_MINUTES",
    "FULFILLMENT_READY_CHECK",
    "HIDE_PRELIMINARY_ITEMS",
    "HOME_DELIVERY_ENABLED",
    "IS_NEW_OSR_STAGING_FLOW_ENABLED",
    "IS_NEW_STAGING_FLOW_ENABLED",
    "ITEMS_AVAILABILITY",
    "MARK_ORDER_AS_EMPTY",
    "mfc_flow_racks",
    "NEED_DISABLE_SCALABLE_PLUS_BUTTON",
    "NEEDS_ORDER_READY_AFTER_PICKING",
    "ORDER_STATUS_AFTER_PICKING_READY",
    "ORDER_STATUS_AFTER_PICKING_SERVED",
    "ORDER_STATUS_AFTER_PICKING_SHIPPED",
    "PRELIMINARY_BATCH_CUTOFF_MINUTE",
    "PRELIMINARY_BATCH_ENABLED",
    "PRINTING_PRINT_RECEIPT",
    "PRODUCTS_SYNC_CHUNK",
    "SPLIT_SCHEDULER_DELAY_SECONDS",
    "STAGE_BY_DATETIME_PREP_INTERVAL",
    "SUMMARY_PICKS",
    "SUMMARY_REQUEST_IN_PICKS_ENABLED",
    "SUMMARY_SERVE",
    "TOTE_CONSOLIDATION_ENABLED",
    "TRUCK_LOAD_UNLOAD_SESSION_STATUS",
    "TRUCK_LOAD_UNLOAD_SESSION_STATUS_ENABLED",
    "FEATURE__FRIENDS_FAMILY__FILTER__TURN_ON",
    "RINT_API__FRIENDS_FAMILY__CONFIG_FILE",
    "RINT_ETL__FEATURE__MONITORING__APM_TRACING__TURN_ON",
    "RINT_GOLD__FEATURE__MONITORING__APM_TRACING__TURN_ON",
    "RINT_SINFONIETTA__FEATURE__MONITORING__APM_TRACING__TURN_ON",
)


class ExcludeTSC(Enum):
    """Values or prefix/suffixes of tsc configuration names to exclude
    Args:
        Enum (strng): String representation of Config Items that should not be
        modified
    """

    OSR_FTP = "OSR_FTP"
    osr_ftp = "osr_ftp"
    LAUNCH_DARKLY = "LAUNCH_DARKLY"
    NREPL__HOST = "NREPL__HOST"
    NREPL__PORT = "NREPL__PORT"
    FTP__CONNECTION = "FTP__CONNECTION"
    GCP_STORAGE_URL = "GCP_STORAGE_URL"
    SERVICE_TOKEN = "SERVICE_TOKEN"
    RPC__CONTEXTS__ALLOWLIST = "RPC__CONTEXTS__ALLOWLIST"
    RPC__CONTEXTS__BLOCKLIST = "RPC__CONTEXTS__BLOCKLIST"
    HEALTH__EXCLUSIONS = "HEALTH__EXCLUSIONS"
    POSTGRES = "POSTGRES"
    INFO__DOMAIN_SLACK_CHANNEL = "INFO__DOMAIN_SLACK_CHANNEL"
    SLACK__WEBHOOK = "SLACK__WEBHOOK"
    RPC__SERVER__PORT = "RPC__SERVER__PORT"
    RPC__SERVER__HOST = "RPC__SERVER__HOST"
    AUTH_API = "AUTH_API"
    ENV = "ENV"
    WINTER_API__URL = "WINTER_API__URL"
    TANGERINE_API__URL = "TANGERINE_API__URL"
    WINTER_API__PUSH_INVENTORY_ADJUSTMENT__PATH = (
        "WINTER_API__PUSH_INVENTORY_ADJUSTMENT__PATH"
    )


EXCLUDE_FOR_ODE = "is_gold_enabled"

DISABLE_GOLD_CONFIG_ITEM = {
    "categories": ["features"],
    "name": "is_gold_enabled",
    "value": False,
    "location-code-tom": None,
    "value-type": "boolean",
}


osr_ftp_default_config_items = [
    {
        "categories": ["osr"],
        "name": "send_mrsl_to_kisoft",
        "value": False,
        "value-type": "boolean",
    },
    {
        "categories": ["osr"],
        "name": "osr_ftp_username",
        "value": "k1705kch",
        "value-type": "string",
    },
    {
        "categories": ["osr"],
        "name": "osr_ftp_password",
        "value": "k1705kch",
        "value-type": "string",
    },
    {
        "categories": ["osr"],
        "name": "osr_ftp_port",
        "value": 21,
        "value-type": "integer",
    },
    {
        "categories": ["osr"],
        "name": "osr_ftp_protocol",
        "value": "ftp",
        "value-type": "string",
    },
    {
        "categories": ["osr"],
        "name": "osr_ftp_host",
        "value": "tgim-ftp",
        "value-type": "string",
    },
    {
        "categories": ["osr"],
        "name": "osr_ftp_passive_mode",
        "value": True,
        "value-type": "boolean",
    },
]


def filter_tsc_payload(
    config_items_map: dict[list[dict]], is_ode=False
) -> dict[list[dict]]:
    """Goes through a json body and removes entries that should not be modified
    Args:
        json_body (list[dict]): the content to filter

    Raises:
        CopyConfigException: Filter TSC PAYLOAD

    Returns:
        list: list of dictionaries that copy config cares about
    """
    try:
        return_json: dict = {}
        # go through each mfc
        for mfc_key in config_items_map.keys():
            return_mfc_list = []
            # go through each mfc list of config items
            for item in config_items_map[mfc_key]:
                # found means its part of the exclude tsc enum
                found = False
                if any(enum_value.name in item["name"] for enum_value in ExcludeTSC):
                    found = True
                elif is_ode and str(item["name"]) == EXCLUDE_FOR_ODE:
                    return_mfc_list.append(DISABLE_GOLD_CONFIG_ITEM)
                    found = True
                elif any(item["name"] == i for i in DEPRECATED_FIELDS):
                    found = True
                    # exclude ones that start with http as well
                elif item.get("value") and str(item["value"]).upper().startswith(
                    "HTTP"
                ):
                    found = True

                if not found:
                    return_mfc_list.append(modify_value(item))
            return_json[mfc_key] = copy.deepcopy(return_mfc_list)

        return return_json
    except Exception as e:
        error_print(e)
        raise CopyConfigException(CopyConfigErrorCodes.FILTER_FAILURE)


def filter_staging_configurations(json_body: dict) -> dict:
    """Goes through a json body and removes entries that should not be in the
    dict

    Args:
        json_body (dict): content to filter

    Raises:
        CopyConfigException: Filter TSC PAYLOAD

    Returns:
        dict: modified dict that can be used in post/put call
    """
    try:
        return remove_fields(json_body, ["last-modified-at"])
    except Exception as e:
        error_print(e)
        raise CopyConfigException(CopyConfigErrorCodes.FILTER_FAILURE)


def compare_flow_racks(source_flow_racks: dict, target_flow_racks: dict) -> dict:
    """Compares two flow_rack dictionaries
    Generates a new dictionary based on the differences of the two
    If they are the same returns None, else creates new keys for each of the
    different flowrack value

    Args:
        source_flow_racks (dict): source
        target_flow_racks (dict): _description_

    Returns:
        dict: updated flow rack dict
    """
    result: dict = None
    if not source_flow_racks:
        return None
    try:
        remaining_flow_racks: dict = copy.deepcopy(source_flow_racks["flow-racks"])
    except Exception as e:
        error_print(e)
        raise CopyConfigException(CopyConfigErrorCodes.FLOW_RACK_COMPARE_SOURCE)

    try:
        remove_matching_items(remaining_flow_racks, target_flow_racks)
    except Exception as e:
        error_print(e)
        raise CopyConfigException(CopyConfigErrorCodes.FLOW_RACK_COMPARE_TARGET)
    try:
        if remaining_flow_racks:
            existing_tgt_keys = target_flow_racks["flow-racks"].keys()
            if existing_tgt_keys:
                starting_int_key = int(max(existing_tgt_keys)) + 1
            else:
                starting_int_key = 1
            result = {
                "location-code-tom": source_flow_racks["location-code-tom"],
                "flow-racks": {},
            }
            for value in remaining_flow_racks.values():
                result["flow-racks"][str(starting_int_key)] = value
                starting_int_key += 1
        return result
    except Exception as e:
        error_print(e)
        raise CopyConfigException(CopyConfigErrorCodes.FLOW_RACK_COMPARE_GENERATE)


def remove_matching_items(remaining_items, target_items):
    for value in dict(target_items["flow-racks"]).values():
        matching_keys = {k for k, v in remaining_items.items() if v == value}
        if matching_keys:
            del remaining_items[matching_keys.pop()]


def apply_location_osr_values(tsc_tgt: TSC, site_number: int):
    for item in osr_ftp_default_config_items:
        item["location-code-tom"] = tsc_tgt.config.location_code_tom
        if item["name"] == "osr_ftp_username":
            item["value"] = f"k1705kch_{site_number}"

    return tsc_tgt.put_config_items(osr_ftp_default_config_items, [201, 200])
