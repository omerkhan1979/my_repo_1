from pytest import mark

from src.utils.console_printing import cyan, blue, yellow
from src.utils.picklist_helpers import put_away_from_store
from src.utils.place_order import prepare_and_place_order


@mark.rq
@mark.outbound
@mark.isps_picklist_flow
@mark.retailers("abs", "maf", "smu")
@mark.testrail("459549")
def test_isps_picklist_flow(
    cfg,
    apis,
    location_code_tom,
    cancel_all_draft_orders,
    close_all_open_picklists,
    stage_by_in_1_minutes_1_min_cutoff,
):
    cutoff, order_id = prepare_and_place_order(
        cfg,
        apis,
        stage_by_in_1_minutes_1_min_cutoff,
        flo_items=1,
        add_stock_for_flo_items=False,
    )
    print(f"Cutoff: {cutoff} for {order_id}")
    user_id = apis.ims.config.user_id

    # Triggering picklist:
    trigger_picklist = apis.oms.trigger_picklist_creation(
        cutoff, picklist_type="PRELIM"
    )
    verification_trigger_picklist = len(trigger_picklist)
    assert verification_trigger_picklist > 0
    find_picklist = apis.isps.find_picklists_by_cutoff_and_status(cutoff, "SPLIT")[0]
    picklist_code = find_picklist["code"]  # {pick-list-code}
    print(
        blue(
            f"\nPicklist is created, picklist ID is {picklist_code}. "
            f"\nYour picklist in TOM UI with cutoff-datetime in UTC: {cutoff}"
        )
    )

    get_picklist = apis.isps.get_picklist_by_code(picklist_code)
    assert picklist_code == get_picklist["code"]
    picklist_status_after_creating = get_picklist["status"]
    assert picklist_status_after_creating == "SPLIT"
    print(
        yellow("The picklist status after creation is:"),
        blue(picklist_status_after_creating),
    )

    workorders = apis.isps.get_workorders_for_picklist(picklist_code)
    work_order_code = workorders[0]["code"]  # {work-order-code}
    wo_status_after_creating = apis.isps.get_workorders_status(work_order_code)
    assert apis.isps.get_workorders_status(work_order_code) == "NEW"
    print(
        yellow("The workorder status after creation is:"),
        blue(wo_status_after_creating),
    )
    wo_items = apis.isps.get_workorder_items(work_order_code)
    work_order_item_code = wo_items[0]["code"]  # {work-order-item-code}

    # Assign order by user
    workorders_assign = apis.isps.workorders_assign(work_order_code, user_id)
    assign_validation = workorders_assign["result"][0]["updated"]
    assert assign_validation is True
    check_workorders_status_after_assign = apis.isps.get_workorders_status(
        work_order_code
    )
    assert apis.isps.get_workorders_status(work_order_code) == "PICKING"
    check_picklist_status_after_assign = apis.isps.get_picklist_by_code(picklist_code)[
        "status"
    ]
    assert check_picklist_status_after_assign == "PROGRESS"
    print(
        yellow("The picklist status after assign is:"),
        blue(check_picklist_status_after_assign),
    )
    print(
        yellow("The workorder status after assign is:"),
        blue(check_workorders_status_after_assign),
    )

    # Start picking:
    decision_for_workorder_item = apis.isps.put_workorder_changes_to_picking(
        work_order_code, work_order_item_code
    )
    product_id = decision_for_workorder_item["product-id"]
    wo_items_after_picking = apis.isps.get_workorder_items(work_order_code)
    assert (
        wo_items_after_picking[0]["asked-qty"]
        == decision_for_workorder_item["asked-qty"]
    )
    assert (
        wo_items_after_picking[0]["picked-qty"]
        == decision_for_workorder_item["picked-qty"]
    )
    assert (
        wo_items_after_picking[0]["product-id"]
        == decision_for_workorder_item["product-id"]
    )
    assert (
        wo_items_after_picking[0]["reason-code"]
        == decision_for_workorder_item["reason-code"]
    )
    assert apis.isps.get_picklist_by_code(picklist_code)["status"] == "PROGRESS"
    assert apis.isps.get_workorders_status(work_order_code) == "PICKING"

    # Finish picking
    apis.isps.put_workorder_changes(work_order_code, "COMPLETED")
    assert apis.isps.get_picklist_by_code(picklist_code)["status"] == "PROGRESS"
    assert apis.isps.get_workorders_status(work_order_code) == "COMPLETED"
    print(
        yellow("The picklist status after finishing picking:"),
        blue(apis.isps.get_picklist_by_code(picklist_code)["status"]),
    )
    print(
        yellow("The workorder status after finishing picking:"),
        blue(apis.isps.get_workorders_status(work_order_code)),
    )

    # Put away form store:
    item_qty = decision_for_workorder_item["picked-qty"]
    put_away_from_store_verification = put_away_from_store(
        apis.ims,
        apis.ops_api,
        product_id,
        location_code_tom,
        item_qty,
        "ST",
    )
    assert put_away_from_store_verification["quantity"] == item_qty
    assert put_away_from_store_verification["product"] == product_id
    assert put_away_from_store_verification["reason-code"] == "ST"
    print(blue(f"The put away from store for item  {product_id} has been done"))

    # Manual close picklist:
    apis.isps.post_picklist_close(picklist_code)
    assert apis.isps.get_picklist_by_code(picklist_code)["status"] == "COMPLETE"
    assert apis.isps.get_workorders_status(work_order_code) == "COMPLETED"

    print(
        yellow("The picklist status after close is:"),
        blue(apis.isps.get_picklist_by_code(picklist_code)["status"]),
    )
    print(
        yellow("The workorder status after close is:"),
        blue(apis.isps.get_workorders_status(work_order_code)),
    )

    print(cyan("Test case Batch/FLO/ISPS - isps_picklist_flow:"))
