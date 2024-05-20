import time

from pytest import mark, param
from src.api.takeoff.pickerman_facade import PickermanFacade
from src.utils.console_printing import cyan
from src.utils.helpers import wait_order_status_changed, get_order_status
from src.utils.order_picking import (
    assign_available_order_and_send_decisions_all_available,
    consolidate_order,
    stage_order,
)
from src.api.collections import InitializedApis
from src.utils.place_order import place_order
from scripts.steps.orderflow.setup import prepare_orderflow_data
from src.utils.order_timings import MFCRelativeFutureTime
from src.config.constants import MANUALLY_ENQUEUE_RETAILERS


@mark.smoke
@mark.outbound_smoke
@mark.retailers("abs")
@mark.parametrize(
    "product_type,flo,osr,manual,weighted_manual,expected_status",
    [
        ("OSR", 0, 1, 0, 0, "draft"),
        ("manual", 0, 0, 1, 0, "draft"),
        ("FLO", 1, 0, 0, 0, "draft"),
        ("OSR + manual", 0, 1, 1, 0, "draft"),
        ("OSR + FLO", 1, 1, 0, 0, "draft"),
        ("manual + FLO", 1, 0, 1, 0, "draft"),
        ("OSR + manual + FLO", 1, 1, 1, 0, "draft"),
    ],
)  # Can be extended later with weighted products
@mark.testrail("65006")
def test_order_status_draft_after_creation(
    cfg,
    product_type,
    expected_status,
    apis: InitializedApis,
    flo,
    osr,
    manual,
    weighted_manual,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
):
    orderflow_test_data = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        cfg.retailer,
        picklist_weighted_qty=flo,
        osr_products_qty=osr,
        manual_non_weighted_qty=manual,
        manual_weighted_qty=weighted_manual,
        stage_by_data=stage_by_in_1_minutes_1_min_cutoff,
    )
    order_id = place_order(
        rint=apis.rint,
        retailer=cfg.retailer,
        products=orderflow_test_data["all_products"],
        store_id=orderflow_test_data["store_id"],
        spoke_id=orderflow_test_data["spoke_id"],
        stage_by_datetime=orderflow_test_data["stage_by_datetime"],
        service_window_start=orderflow_test_data["service_window_start"],
        route_id=orderflow_test_data["route_id"],
        ims=apis.ims_admin,
        oms=apis.oms,
    )

    order_status = get_order_status(order_id, apis.oms)
    assert order_status == expected_status
    print(cyan(f"Test case {product_type} - order_status_draft_after_creation:"))


@mark.smoke
@mark.outbound_smoke
@mark.retailers("abs")
@mark.parametrize(
    "product_type,flo,osr,manual,weighted_manual,expected_status",
    [
        ("OSR", 0, 1, 0, 0, "queued"),
        ("manual", 0, 0, 1, 0, "queued"),
        ("FLO", 1, 0, 0, 0, "queued"),
        ("OSR + manual", 0, 1, 1, 0, "queued"),
        ("OSR + FLO", 1, 1, 0, 0, "queued"),
        ("manual + FLO", 1, 0, 1, 0, "queued"),
        ("OSR + manual + FLO", 1, 1, 1, 0, "queued"),
    ],
)
@mark.testrail("128001")
def test_order_status_new_queued_after_split(
    cfg,
    apis: InitializedApis,
    flo,
    osr,
    manual,
    weighted_manual,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
    product_type,
    expected_status,
):
    orderflow_test_data = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        cfg.retailer,
        picklist_weighted_qty=flo,
        osr_products_qty=osr,
        manual_non_weighted_qty=manual,
        manual_weighted_qty=weighted_manual,
        stage_by_data=stage_by_in_1_minutes_1_min_cutoff,
    )
    order_id = place_order(
        rint=apis.rint,
        retailer=cfg.retailer,
        products=orderflow_test_data["all_products"],
        store_id=orderflow_test_data["store_id"],
        spoke_id=orderflow_test_data["spoke_id"],
        stage_by_datetime=orderflow_test_data["stage_by_datetime"],
        service_window_start=orderflow_test_data["service_window_start"],
        route_id=orderflow_test_data["route_id"],
        ims=apis.ims_admin,
        oms=apis.oms,
    )
    # note that ABS is always "queued", other retailers are "new"
    wait_order_status_changed(order_id, expected_status, apis.oms)
    order_status = get_order_status(order_id, apis.oms)
    assert order_status == expected_status
    print(cyan(f"Test case {product_type} - order_status_new_queued_after_split:"))


@mark.smoke
@mark.outbound_smoke
@mark.retailers("abs")
@mark.parametrize(
    "product_type,flo,osr,manual,weighted_manual,expected_status",
    [
        ("OSR", 0, 1, 0, 0, "queued"),
        ("manual", 0, 0, 1, 0, "queued"),
        ("OSR + manual", 0, 1, 1, 0, "queued"),
    ],
)
@mark.testrail("128658")
def test_order_status_queued_after_assign(
    cfg,
    apis: InitializedApis,
    flo,
    osr,
    manual,
    weighted_manual,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
    pickerman_facade: PickermanFacade,
    product_type,
    expected_status,
):
    orderflow_test_data = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        cfg.retailer,
        picklist_weighted_qty=flo,
        osr_products_qty=osr,
        manual_non_weighted_qty=manual,
        manual_weighted_qty=weighted_manual,
        stage_by_data=stage_by_in_1_minutes_1_min_cutoff,
    )
    order_id = place_order(
        rint=apis.rint,
        retailer=cfg.retailer,
        products=orderflow_test_data["all_products"],
        store_id=orderflow_test_data["store_id"],
        spoke_id=orderflow_test_data["spoke_id"],
        stage_by_datetime=orderflow_test_data["stage_by_datetime"],
        service_window_start=orderflow_test_data["service_window_start"],
        route_id=orderflow_test_data["route_id"],
        ims=apis.ims_admin,
        oms=apis.oms,
    )
    order_status = get_order_status(order_id, apis.oms)
    # check the pre-condition is valid
    assert (
        order_status == expected_status
    ), f"pre-condition expectation of {expected_status} failed"
    result = pickerman_facade.assign()
    print(f"Result of calling pickerman_facade.assign(): {result}")
    # As bad a sleeps are, we want to let a moment pass to be sure status doesn't change
    time.sleep(10)
    # capture the value again, shouldn't have changed
    order_status = get_order_status(order_id, apis.oms)
    assert order_status == expected_status
    print(cyan(f"Test case {product_type} - order_status_queued_after_assign:"))


@mark.smoke
@mark.outbound_smoke
@mark.retailers("abs")
@mark.parametrize(
    "product_type,flo,osr,manual,weighted_manual,expected_status",
    [
        param("OSR", 0, 1, 0, 0, "picked", marks=mark.testrail("166248")),
        param("manual", 0, 0, 1, 0, "picked", marks=mark.testrail("166239")),
        param("FLO", 1, 0, 0, 0, "picked"),
        param("OSR + manual", 0, 1, 1, 0, "picked", marks=mark.testrail("166251")),
        param("OSR + FLO", 1, 1, 0, 0, "picked"),
        param("manual + FLO", 1, 0, 1, 0, "picked"),
        param("OSR + manual + FLO", 1, 1, 1, 0, "picked"),
    ],
)  # Can be extended later with weighted products
def test_order_status_picked_after_picking(
    cfg,
    apis: InitializedApis,
    flo,
    osr,
    manual,
    weighted_manual,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
    pickerman_facade: PickermanFacade,
    product_type,
    expected_status,
):
    orderflow_test_data = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        cfg.retailer,
        picklist_weighted_qty=flo,
        osr_products_qty=osr,
        manual_non_weighted_qty=manual,
        manual_weighted_qty=weighted_manual,
        stage_by_data=stage_by_in_1_minutes_1_min_cutoff,
    )
    order_id = place_order(
        rint=apis.rint,
        retailer=cfg.retailer,
        products=orderflow_test_data["all_products"],
        store_id=orderflow_test_data["store_id"],
        spoke_id=orderflow_test_data["spoke_id"],
        stage_by_datetime=orderflow_test_data["stage_by_datetime"],
        service_window_start=orderflow_test_data["service_window_start"],
        route_id=orderflow_test_data["route_id"],
        ims=apis.ims_admin,
        oms=apis.oms,
    )
    wait_order_status_changed(order_id, "new", apis.oms)
    if cfg.retailer in MANUALLY_ENQUEUE_RETAILERS:
        apis.oms.start_picking(order_id)
    wait_order_status_changed(order_id, "queued", apis.oms)

    order_assigned = assign_available_order_and_send_decisions_all_available(
        pickerman_facade,
        order_id,
        user_id=pickerman_facade.config.user_id,
        email=pickerman_facade.config.user,
    )
    assert (
        order_assigned == order_id
    ), f"Assigned {order_assigned} but we are using order {order_id}"
    wait_order_status_changed(order_id, expected_status, apis.oms)
    order_status = get_order_status(order_id, apis.oms)
    assert order_status == expected_status
    print(cyan(f"Test case {product_type} - order_status_picked_after_picking:"))


@mark.smoke
@mark.outbound_smoke
@mark.retailers("abs")
@mark.parametrize(
    "product_type,flo,osr,manual,weighted_manual,expected_status",
    [
        param("OSR", 0, 1, 0, 0, "packed", marks=mark.testrail("132374")),
        # param("manual", 0, 0, 1, 0, "packed", marks=mark.testrail("141419")),
        # param("OSR + manual", 0, 1, 1, 0, "packed", marks=mark.testrail("142981")),
    ],
)
def test_order_status_packed_after_consolidation(
    cfg,
    apis: InitializedApis,
    flo,
    osr,
    manual,
    weighted_manual,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
    pickerman_facade: PickermanFacade,
    product_type,
    expected_status,
):
    orderflow_test_data = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        cfg.retailer,
        picklist_weighted_qty=flo,
        osr_products_qty=osr,
        manual_non_weighted_qty=manual,
        manual_weighted_qty=weighted_manual,
        stage_by_data=stage_by_in_1_minutes_1_min_cutoff,
    )
    order_id = place_order(
        rint=apis.rint,
        retailer=cfg.retailer,
        products=orderflow_test_data["all_products"],
        store_id=orderflow_test_data["store_id"],
        spoke_id=orderflow_test_data["spoke_id"],
        stage_by_datetime=orderflow_test_data["stage_by_datetime"],
        service_window_start=orderflow_test_data["service_window_start"],
        route_id=orderflow_test_data["route_id"],
        ims=apis.ims_admin,
        oms=apis.oms,
    )
    wait_order_status_changed(order_id, "new", apis.oms)
    if cfg.retailer in MANUALLY_ENQUEUE_RETAILERS:
        apis.oms.start_picking(order_id)
    wait_order_status_changed(order_id, "queued", apis.oms)

    order_assigned = assign_available_order_and_send_decisions_all_available(
        pickerman_facade,
        order_id,
        user_id=pickerman_facade.config.user_id,
        email=pickerman_facade.config.user,
    )
    assert (
        order_assigned == order_id
    ), f"Assigned {order_assigned} but we are using order {order_id}"
    wait_order_status_changed(order_id, "picked", apis.oms)
    consolidate_order(pickerman_facade, order_id)
    wait_order_status_changed(order_id, expected_status, apis.oms)
    order_status = apis.oms.get_order(order_id)["response"]["status"]
    assert order_status == expected_status
    print(cyan(f"Test case {product_type} - order_status_packed_after_consolidation:"))


@mark.smoke
@mark.outbound_smoke
@mark.retailers("abs")
@mark.parametrize(
    "product_type,flo,osr,manual,weighted_manual,expected_status",
    [
        param("OSR", 0, 1, 0, 0, "ready", marks=mark.testrail("138966")),
        param("manual", 0, 0, 1, 0, "ready", marks=mark.testrail("66050")),
        ("OSR + manual", 0, 1, 1, 0, "ready"),
    ],
)
def test_order_status_ready_after_staging(
    cfg,
    apis: InitializedApis,
    flo,
    osr,
    manual,
    weighted_manual,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
    product_type,
    expected_status,
    staging_location,
):
    orderflow_test_data = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        cfg.retailer,
        picklist_weighted_qty=flo,
        osr_products_qty=osr,
        manual_non_weighted_qty=manual,
        manual_weighted_qty=weighted_manual,
        stage_by_data=stage_by_in_1_minutes_1_min_cutoff,
    )
    order_id = place_order(
        rint=apis.rint,
        retailer=cfg.retailer,
        products=orderflow_test_data["all_products"],
        store_id=orderflow_test_data["store_id"],
        spoke_id=orderflow_test_data["spoke_id"],
        stage_by_datetime=orderflow_test_data["stage_by_datetime"],
        service_window_start=orderflow_test_data["service_window_start"],
        route_id=orderflow_test_data["route_id"],
        ims=apis.ims_admin,
        oms=apis.oms,
    )
    wait_order_status_changed(order_id, "new", apis.oms)
    if cfg.retailer in MANUALLY_ENQUEUE_RETAILERS:
        apis.oms.start_picking(order_id)
    wait_order_status_changed(order_id, "queued", apis.oms)

    order_assigned = assign_available_order_and_send_decisions_all_available(
        apis.pickerman_facade,
        order_id,
        user_id=apis.pickerman_facade.config.user_id,
        email=apis.pickerman_facade.config.user,
    )
    assert (
        order_assigned == order_id
    ), f"Assigned {order_assigned} but we are using order {order_id}"
    wait_order_status_changed(order_id, "picked", apis.oms)
    consolidate_order(apis.pickerman_facade, order_id)
    wait_order_status_changed(order_id, "packed", apis.oms)
    stage_order(apis.pickerman_facade, apis.fft, order_id, staging_location)
    wait_order_status_changed(order_id, "ready", apis.oms)
    order_status = apis.oms.get_order(order_id)["response"]["status"]
    assert order_status == expected_status
    print(cyan(f"Test case {product_type} - order_status_ready_after_staging:"))
