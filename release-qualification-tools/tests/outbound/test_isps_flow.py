from pytest import mark
from src.api.collections import InitializedApis
from src.api.takeoff.tsc import TscReturnFormat
from src.config.config import Config

from src.config.constants import RETAILERS_WITHOUT_STAGING
from src.utils.console_printing import cyan, blue, red
from src.utils.helpers import get_order_status, wait_order_status_changed
from src.utils.order_picking import (
    consolidate_order,
    stage_order,
)

from src.utils.order_timings import MFCRelativeFutureTime

from src.utils.user import AuthServiceUser
from src.utils.picklist_helpers import prepare_isps_test


@mark.rq
@mark.outbound
@mark.order_flow
@mark.osr_flo_manual_picking
@mark.isps
@mark.retailers("abs", "maf", "smu")
@mark.testrail("459553")
def test_isps_flow(
    cfg: Config,
    apis: InitializedApis,
    staging_location: str,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
    close_all_open_picklists,
    operator_user: AuthServiceUser,
):
    # "product_type,flo,osr,manual,weighted_manual",
    # [("OSR + flo + manual", 1, 1, 1, 0)],
    order_id = prepare_isps_test(
        cfg,
        apis,
        stage_by_in_1_minutes_1_min_cutoff,
        operator_user,
        flo_items=1,
        manual_items=1,
        osr_items=1,
    )

    apis.outbound_backend.bulk_action()

    """Order consolidation"""
    consolidate_order(apis.pickerman_facade, order_id)
    wait_order_status_changed(order_id, "packed", apis.oms)
    """Order staging"""
    if cfg.retailer not in RETAILERS_WITHOUT_STAGING:
        stage_order(
            apis.pickerman_facade,
            apis.fft,
            order_id,
            staging_location,
        )
        wait_order_status_changed(order_id, "staged", apis.oms)

    """Order status verification"""
    order_status_tsc = apis.tsc.get_config_item_value(
        "ORDER_STATUS_AFTER_PICKING", return_format=TscReturnFormat.json
    )
    try:
        wait_order_status_changed(order_id, order_status_tsc, apis.oms)
    except Exception:
        pass  # we'll let the nicer logging/assertion below fail this test
    order_status = get_order_status(order_id, apis.oms)
    if order_status == order_status_tsc:
        print(
            blue(
                f"Final status is {order_status} for order {order_id}, retailer: {cfg.retailer}"
            )
        )
        print(cyan("Test case ISPS osr_flo_manual_picking is:"))
    else:
        assert False, red(
            f"Final Status {order_status_tsc} not found (have {order_status}), hence Test Case Failed"
        )


@mark.rq
@mark.outbound
@mark.order_flow
@mark.flo_picking
@mark.isps
@mark.retailers("abs", "maf", "smu")
@mark.testrail("50965")
def test_flo_order_flow(
    cfg: Config,
    apis: InitializedApis,
    staging_location: str,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
    close_all_open_picklists,
    operator_user: AuthServiceUser,
):
    # "product_type,flo,osr,manual,weighted_manual",
    # [("flo", 1, 0, 0, 0)],
    order_id = prepare_isps_test(
        cfg,
        apis,
        stage_by_in_1_minutes_1_min_cutoff,
        operator_user,
        flo_items=1,
        manual_items=0,
        osr_items=0,
    )
    apis.outbound_backend.bulk_action()

    """Order picking"""

    wait_order_status_changed(order_id, "picked", apis.oms)
    """Order consolidation"""
    consolidate_order(apis.pickerman_facade, order_id)
    wait_order_status_changed(order_id, "packed", apis.oms)
    """Order staging"""
    if cfg.retailer not in RETAILERS_WITHOUT_STAGING:
        stage_order(apis.pickerman_facade, apis.fft, order_id, staging_location)
        wait_order_status_changed(order_id, "staged", apis.oms)
    """Order status verification"""
    order_status_tsc = apis.tsc.get_config_item_value(
        "ORDER_STATUS_AFTER_PICKING", return_format=TscReturnFormat.json
    )
    try:
        wait_order_status_changed(order_id, order_status_tsc, apis.oms)
    except Exception:
        pass  # we'll let the nicer logging/assertion below fail this test
    order_status = get_order_status(order_id, apis.oms)
    if order_status == order_status_tsc:
        print(
            blue(
                f"Final status is {order_status} for order {order_id}, retailer: {cfg.retailer}"
            )
        )
        print(cyan("Test case ISPS flo_picking is:"))
    else:
        assert False, red(
            f"Final Status {order_status_tsc} not found (have {order_status}), hence Test Case Failed"
        )


@mark.rq
@mark.outbound
@mark.order_flow
@mark.osr_flo_picking
@mark.isps
@mark.retailers("abs", "maf", "smu")
@mark.testrail("50968")
def test_osr_flo_order_flow(
    cfg: Config,
    apis: InitializedApis,
    staging_location: str,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
    close_all_open_picklists,
    operator_user: AuthServiceUser,
):
    # "product_type,flo,osr,manual,weighted_manual",
    # [("flo + OSR", 1, 1, 0, 0)],
    order_id = prepare_isps_test(
        cfg,
        apis,
        stage_by_in_1_minutes_1_min_cutoff,
        operator_user,
        flo_items=1,
        manual_items=0,
        osr_items=1,
    )

    apis.outbound_backend.bulk_action()
    """Order picking"""

    wait_order_status_changed(order_id, "picked", apis.oms)
    """Order consolidation"""
    consolidate_order(apis.pickerman_facade, order_id)
    wait_order_status_changed(order_id, "packed", apis.oms)
    """Order staging"""
    if cfg.retailer not in RETAILERS_WITHOUT_STAGING:
        stage_order(apis.pickerman_facade, apis.fft, order_id, staging_location)
        wait_order_status_changed(order_id, "staged", apis.oms)
    """Order status verification"""
    order_status_tsc = apis.tsc.get_config_item_value(
        "ORDER_STATUS_AFTER_PICKING", return_format=TscReturnFormat.json
    )
    try:
        wait_order_status_changed(order_id, order_status_tsc, apis.oms)
    except Exception:
        pass  # we'll let the nicer logging/assertion below fail this test
    order_status = get_order_status(order_id, apis.oms)
    if order_status == order_status_tsc:
        print(
            blue(
                f"Final status is {order_status} for order {order_id}, retailer: {cfg.retailer}"
            )
        )
        print(cyan("Test case ISPS osr_flo_picking is:"))
    else:
        assert False, red(
            f"Final Status {order_status_tsc} not found (have {order_status}), hence Test Case Failed"
        )


@mark.rq
@mark.outbound
@mark.order_flow
@mark.osr_flo__manual_picking
@mark.isps
@mark.retailers("abs", "maf", "smu")
@mark.testrail("50967")
def test_flo_manual_order_flow(
    cfg: Config,
    apis: InitializedApis,
    staging_location: str,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
    close_all_open_picklists,
    operator_user: AuthServiceUser,
):
    # "product_type,flo,osr,manual,weighted_manual",
    # [("flo + manual", 1, 0, 1, 0)],
    order_id = prepare_isps_test(
        cfg,
        apis,
        stage_by_in_1_minutes_1_min_cutoff,
        operator_user,
        flo_items=1,
        manual_items=1,
        osr_items=0,
    )

    apis.outbound_backend.bulk_action()
    """Order picking"""

    wait_order_status_changed(order_id, "picked", apis.oms)
    """Order consolidation"""
    consolidate_order(apis.pickerman_facade, order_id)
    wait_order_status_changed(order_id, "packed", apis.oms)
    """Order staging"""
    if cfg.retailer not in RETAILERS_WITHOUT_STAGING:
        stage_order(apis.pickerman_facade, apis.fft, order_id, staging_location)
        wait_order_status_changed(order_id, "staged", apis.oms)
    """Order status verification"""
    order_status_tsc = apis.tsc.get_config_item_value(
        "ORDER_STATUS_AFTER_PICKING", return_format=TscReturnFormat.json
    )
    try:
        wait_order_status_changed(order_id, order_status_tsc, apis.oms)
    except Exception:
        pass  # we'll let the nicer logging/assertion below fail this test
    order_status = get_order_status(order_id, apis.oms)
    if order_status == order_status_tsc:
        print(
            blue(
                f"Final status is {order_status} for order {order_id}, retailer: {cfg.retailer}"
            )
        )
        print(cyan("Test case ISPS osr_flo__manual_picking is:"))
    else:
        assert False, red(
            f"Final Status {order_status_tsc} not found (have {order_status}), hence Test Case Failed"
        )
