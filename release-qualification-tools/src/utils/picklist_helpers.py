from dateutil import tz
from datetime import datetime
from time import time
from typing import Tuple

from src.api.takeoff.ims import IMS
from src.api.takeoff.ops_api import OpsApi
from src.api.collections import InitializedApis

from src.utils.console_printing import blue, yellow
from src.utils.addresses import get_addresses_v2
from src.utils.console_printing import green, waiting, done
from src.utils.ims import wait_for_item_adjustment_from_ims
from src.api.takeoff.oms import OMS
from src.utils.place_order import prepare_and_place_order
from src.config.config import Config
from src.utils.order_timings import MFCRelativeFutureTime
from src.utils.user import AuthServiceUser
from src.utils.helpers import wait_order_status_changed
from src.utils.order_picking import (
    assign_available_order_and_send_decisions_all_available,
)


def force_picklist_creation(oms: OMS, cutoff: str, picklist_type: str):
    """
    Picklist creation is scheduled automatically based on orders'
    cutoff time; in tests we can manually trigger picklist creation
    earlier than normally scheduled

    Picklist type - either "PRELIM" or "DELTA"
    Cutoff time - timestamp in ISO format, converted to str
    """

    print(waiting("Triggering picklist creation..."))

    oms.trigger_picklist_creation(cutoff, picklist_type)

    print(done("Picklist creation triggered!"))


def get_picklist_name_in_tma(cutoff: str, picklist_type: str) -> str:
    """
    Function for user convenience; transforms picklist 'due' time
    into user's local time format; they need to find it on mobile device
    where it's displayed in the format provided by the function
    """

    # Telling the script that cutoff time is UTC
    utc_cutoff = datetime.strptime(cutoff, "%Y-%m-%dT%H:%M:%SZ")
    utc_cutoff = utc_cutoff.replace(tzinfo=tz.tzutc())

    # Transforming cutoff time for picklist into users time zone, so they can easily find it in Pickerman
    picklist_local_time = utc_cutoff.astimezone(tz.tzlocal()).strftime(
        "%m/%d - %I:%M %p"
    )

    return green(f"\n{picklist_local_time} - {picklist_type}\n")


def put_away_from_store(
    admin_ims: IMS,
    ops_api: OpsApi,
    product_id,
    location_code_tom,
    quantity,
    reason_code,
):
    time_past = str(int(round(time() * 1000)))
    shelf_id = get_addresses_v2(ims=admin_ims)[0]
    ops_api.inventory_adjust(
        shelf_id, product_id, quantity, reason_code
    )  # Pickerman backend Put away form store via Platform
    put_away_from_store_verification = wait_for_item_adjustment_from_ims(
        admin_ims, time_past, None, location_code_tom
    )
    return put_away_from_store_verification


def create_and_get_picklist(
    apis: InitializedApis, cutoff: str, picklist_type: str
) -> str:
    # Triggering picklist
    print("Triggering picklist creation manually until OUTBOUND-6675 is resolved")
    force_picklist_creation(apis.oms, cutoff, picklist_type)
    picklist_code = apis.isps.find_picklists_by_cutoff_and_status(cutoff, "SPLIT")[0][
        "code"
    ]
    print(
        blue(
            f"\nPicklist is created, picklist ID is {picklist_code}. "
            f"\nYour picklist in TOM UI with cutoff-datetime in UTC: {cutoff}"
        )
    )

    get_picklist = apis.isps.get_picklist_by_code(picklist_code)
    picklist_status_after_creating = get_picklist["status"]
    print(
        yellow("The picklist status after creation is:"),
        blue(picklist_status_after_creating),
    )
    return picklist_code


def get_work_order_codes(apis: InitializedApis, picklist_code: str) -> Tuple[str, str]:
    work_order_code = apis.isps.get_workorders_for_picklist(picklist_code)[0]["code"]
    wo_status_after_creating = apis.isps.get_workorders_status(work_order_code)
    print(
        yellow("The workorder status after creation is:"),
        blue(wo_status_after_creating),
    )
    wo_items = apis.isps.get_workorder_items(work_order_code)
    work_order_item_code = wo_items[0]["code"]
    return work_order_code, work_order_item_code


def assign_workorders(
    apis: InitializedApis,
    work_order_code: str,
    operator_user_id: str,
    picklist_code: str,
) -> None:
    apis.isps.workorders_assign(work_order_code, operator_user_id)
    check_picklist_status_after_assign = apis.isps.get_picklist_by_code(picklist_code)[
        "status"
    ]
    print(
        yellow("The picklist status after assign is:"),
        blue(check_picklist_status_after_assign),
    )


def start_picking(
    apis: InitializedApis, work_order_code: str, work_order_item_code: str
) -> dict:
    decision_for_workorder_item = apis.isps.put_workorder_changes_to_picking(
        work_order_code, work_order_item_code, picked_qty=3, reason_code="PICKED"
    )
    return decision_for_workorder_item


def finish_picking(
    apis: InitializedApis, work_order_code: str, picklist_code: str
) -> None:
    apis.isps.put_workorder_changes(work_order_code, "COMPLETED")
    print(
        yellow("The picklist status after finishing picking:"),
        blue(apis.isps.get_picklist_by_code(picklist_code)["status"]),
    )
    print(
        yellow("The workorder status after finishing picking:"),
        blue(apis.isps.get_workorders_status(work_order_code)),
    )


def close_picklist(
    apis: InitializedApis, work_order_code: str, picklist_code: str
) -> None:
    apis.isps.post_picklist_close(picklist_code)
    print(
        yellow("The picklist status after close is:"),
        blue(apis.isps.get_picklist_by_code(picklist_code)["status"]),
    )
    print(
        yellow("The workorder status after close is:"),
        blue(apis.isps.get_workorders_status(work_order_code)),
    )


def process_and_complete_picklist(
    apis: InitializedApis,
    cutoff: str,
    mfc_cutoff: MFCRelativeFutureTime,
    operator_user: AuthServiceUser,
    picklist_type="PRELIM",
) -> object:
    # Trigger picklist creation and return code
    picklist_code = create_and_get_picklist(apis, cutoff, picklist_type=picklist_type)

    work_order_code, work_order_item_code = get_work_order_codes(apis, picklist_code)

    # Assign order by user
    assign_workorders(apis, work_order_code, operator_user.id, picklist_code)

    # Start picking:
    decision_for_workorder_item = start_picking(
        apis, work_order_code, work_order_item_code
    )
    product_id = decision_for_workorder_item["product-id"]
    picked_qty = decision_for_workorder_item["picked-qty"]

    # Finish picking
    finish_picking(apis, work_order_code, picklist_code)

    # Put away form store:
    put_away_from_store(
        apis.ims_admin,
        apis.ops_api,
        product_id,
        mfc_cutoff.location_code_tom,
        picked_qty,
        "ST",
    )
    print(blue(f"The put away from store for item {product_id} has been done"))

    # Manual close picklist:
    close_picklist(apis, work_order_code, picklist_code)


def process_picklist_OOS(
    apis: InitializedApis,
    cutoff: str,
    operator_user: AuthServiceUser,
    picklist_type="PRELIM",
) -> object:
    # Trigger picklist creation and return code
    picklist_code = create_and_get_picklist(apis, cutoff, picklist_type=picklist_type)

    work_order_code, work_order_item_code = get_work_order_codes(apis, picklist_code)

    # Assign order by user
    assign_workorders(apis, work_order_code, operator_user.id, picklist_code)

    # Start picking:
    apis.isps.put_workorder_changes_to_picking(
        work_order_code, work_order_item_code, picked_qty=0, reason_code="OOS"
    )

    # Finish picking
    finish_picking(apis, work_order_code, picklist_code)

    # Manual close picklist:
    close_picklist(apis, work_order_code, picklist_code)


def transition_order_to_picked(
    apis: InitializedApis, order_id, operator_user: AuthServiceUser
):
    wait_order_status_changed(order_id, "new", apis.oms)
    wait_order_status_changed(order_id, "queued", apis.oms)
    assign_available_order_and_send_decisions_all_available(
        apis.pickerman_facade,
        order_id,
        user_id=operator_user.id,
        email=operator_user.email,
    )
    wait_order_status_changed(order_id, "picked", apis.oms)


def prepare_isps_test(
    cfg: Config,
    apis: InitializedApis,
    mfc_cutoff: MFCRelativeFutureTime,
    operator_user: AuthServiceUser,
    flo_items: int = 0,
    manual_items: int = 0,
    osr_items: int = 0,
) -> str:
    """
    Add stock, place order, try to trigger and find picklist. Get
    workorder for the picklist, assign the workorder, close the picklist
    return the order_id.

    This is an overworked method currently hidden away in the
    test file itself.  It'd be nice to move this off to utility
    methods, but let's keep it close to the tests for now.
    """
    cutoff, order_id = prepare_and_place_order(
        cfg,
        apis,
        mfc_cutoff,
        flo_items=flo_items,
        manual_items=manual_items,
        osr_items=osr_items,
        add_stock_for_flo_items=False,  # we DO NOT want stock in dynamic, etc so in store picking happens
    )

    process_and_complete_picklist(apis, cutoff, mfc_cutoff, operator_user)
    transition_order_to_picked(apis, order_id, operator_user)

    return order_id
