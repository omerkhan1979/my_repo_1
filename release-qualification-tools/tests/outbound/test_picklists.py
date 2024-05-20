from pytest import mark
from src.config.config import Config
from src.utils.assortment import Product

from src.utils.console_printing import bold, cyan
from src.utils.picklist_helpers import (
    force_picklist_creation,
    get_picklist_name_in_tma,
)
from src.api.collections import InitializedApis
from src.utils.place_order import place_order
from scripts.steps.orderflow.setup import prepare_orderflow_data
from src.utils.order_timings import MFCRelativeFutureTime


@mark.outbound
@mark.isps1
@mark.retailers("maf", "smu", "abs")
@mark.parametrize("picklist_type", ("PRELIM", "DELTA"))
@mark.testrail("633684")
def test_picklist_has_correct_list_of_items(
    cancel_all_draft_orders,
    close_all_open_picklists,
    picklist_type,
    cfg: Config,
    apis: InitializedApis,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
):  # cfg is a fixture defined in conftest.py, passed automatically
    print("Draft orders")

    draft_flo_item = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        cfg.retailer,
        picklist_non_weighted_qty=1,
        osr_products_qty=0,
        manual_non_weighted_qty=0,
        manual_weighted_qty=0,
        stage_by_data=stage_by_in_1_minutes_1_min_cutoff,
    )
    draft_flo_order_id = place_order(
        rint=apis.rint,
        retailer=cfg.retailer,
        products=draft_flo_item["all_products"],
        store_id=draft_flo_item["store_id"],
        spoke_id=draft_flo_item["spoke_id"],
        stage_by_datetime=draft_flo_item["stage_by_datetime"],
        service_window_start=draft_flo_item["service_window_start"],
        route_id=draft_flo_item["route_id"],
        ims=apis.ims_admin,
        oms=apis.oms,
    )
    draft_order_with_mixed_flo_items = apis.oms.get_order(draft_flo_order_id)
    resulted_flo_tom_ids = [
        lineitem["takeoff-item-ids"][0]
        for lineitem in draft_order_with_mixed_flo_items["response"]["line-items"]
    ]

    draft_reg_item = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        cfg.retailer,
        picklist_non_weighted_qty=0,
        osr_products_qty=0,
        manual_non_weighted_qty=1,
        manual_weighted_qty=0,
        stage_by_data=stage_by_in_1_minutes_1_min_cutoff,
    )
    draft_reg_order_id = place_order(
        rint=apis.rint,
        retailer=cfg.retailer,
        products=draft_reg_item["all_products"],
        store_id=draft_reg_item["store_id"],
        spoke_id=draft_reg_item["spoke_id"],
        stage_by_datetime=draft_reg_item["stage_by_datetime"],
        service_window_start=draft_reg_item["service_window_start"],
        route_id=draft_reg_item["route_id"],
        ims=apis.ims_admin,
        oms=apis.oms,
    )
    draft_order_with_mixed_reg_items = apis.oms.get_order(draft_reg_order_id)

    resulted_reg_tom_ids = [
        lineitem["takeoff-item-ids"][0]
        for lineitem in draft_order_with_mixed_reg_items["response"]["line-items"]
    ]

    draft_flo_reg_item = draft_flo_item["all_products"] + draft_reg_item["all_products"]

    draft_order_with_mixed_flo_reg_items_order_id = place_order(
        rint=apis.rint,
        retailer=cfg.retailer,
        products=draft_flo_reg_item,
        store_id=draft_reg_item["store_id"],
        spoke_id=draft_reg_item["spoke_id"],
        stage_by_datetime=draft_reg_item["stage_by_datetime"],
        service_window_start=draft_reg_item["service_window_start"],
        route_id=draft_reg_item["route_id"],
        ims=apis.ims_admin,
        oms=apis.oms,
    )
    draft_order_with_reg_and_flo_items = apis.oms.get_order(
        draft_order_with_mixed_flo_reg_items_order_id
    )

    resulted_all_tom_ids = resulted_flo_tom_ids + resulted_reg_tom_ids

    assert sorted(
        [
            lineitem["takeoff-item-ids"][0]
            for lineitem in draft_order_with_reg_and_flo_items["response"]["line-items"]
        ]
    ) == sorted(resulted_all_tom_ids)
    apis.ims.zero_stock_for_products_or_addresses(resulted_all_tom_ids)

    cutoff = draft_order_with_reg_and_flo_items["response"]["cutoff-datetime"]

    force_picklist_creation(oms=apis.oms, cutoff=cutoff, picklist_type=picklist_type)
    picklist_code = apis.isps.find_picklists_by_cutoff_and_status(cutoff, "SPLIT")[0][
        "code"
    ]
    picklist_items = apis.isps.get_picklist_items(picklist_code)

    all_picklist_eligible_products = resulted_all_tom_ids

    if not cfg.retailer == "maf":
        assert len(all_picklist_eligible_products) == len(picklist_items)
        for item in picklist_items:
            # since place_order() places with 3 units of each tom-id by default
            assert item["qty"] == 6, "Items qty mismatch"

    # check if all needed items included in the picklist
    for p in all_picklist_eligible_products:
        item = list(filter(lambda i: i["product-id"] == p, picklist_items))
        assert item, f"{p} is not in the picklist!"
        print(f"Item {p} found!")

    print(
        bold(f"Picklist code: {picklist_code}, should have {len(picklist_items)} lines")
    )
    print(get_picklist_name_in_tma(cutoff, picklist_type))


@mark.isps2
@mark.retailers("maf", "abs")
@mark.parametrize("picklist_type", ("PRELIM", "DELTA"))
@mark.testrail("173235", "185123", "205471")
def test_weighted_items_not_grouped(
    cancel_all_draft_orders,
    close_all_open_picklists,
    picklist_type,
    cfg,
    apis: InitializedApis,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
):
    randon_weighted_products = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        cfg.retailer,
        picklist_weighted_qty=1,
        osr_products_qty=0,
        manual_non_weighted_qty=0,
        manual_weighted_qty=0,
        stage_by_data=stage_by_in_1_minutes_1_min_cutoff,
    )
    randon_weighted_products_order_id = place_order(
        rint=apis.rint,
        retailer=cfg.retailer,
        products=randon_weighted_products["all_products"],
        store_id=randon_weighted_products["store_id"],
        spoke_id=randon_weighted_products["spoke_id"],
        stage_by_datetime=randon_weighted_products["stage_by_datetime"],
        service_window_start=randon_weighted_products["service_window_start"],
        route_id=randon_weighted_products["route_id"],
        ims=apis.ims_admin,
        oms=apis.oms,
    )
    order_with_weighted_items = apis.oms.get_order(randon_weighted_products_order_id)[
        "response"
    ]
    order_1_tom_ids = [
        lineitem["takeoff-item-ids"][0]
        for lineitem in order_with_weighted_items["line-items"]
    ]

    randon_non_weighted_products = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        cfg.retailer,
        picklist_non_weighted_qty=1,
        osr_products_qty=0,
        manual_non_weighted_qty=0,
        manual_weighted_qty=0,
        stage_by_data=stage_by_in_1_minutes_1_min_cutoff,
    )

    all_weighted_non_weighted_products = (
        randon_weighted_products["all_products"]
        + randon_non_weighted_products["all_products"]
    )

    randon_non_weighted_products_order_id = place_order(
        rint=apis.rint,
        retailer=cfg.retailer,
        products=all_weighted_non_weighted_products,
        store_id=randon_non_weighted_products["store_id"],
        spoke_id=randon_non_weighted_products["spoke_id"],
        stage_by_datetime=randon_non_weighted_products["stage_by_datetime"],
        service_window_start=randon_non_weighted_products["service_window_start"],
        route_id=randon_non_weighted_products["route_id"],
        ims=apis.ims_admin,
        oms=apis.oms,
    )
    order_with_non_weighted_items = apis.oms.get_order(
        randon_non_weighted_products_order_id
    )["response"]

    order_2_tom_ids = [
        lineitem["takeoff-item-ids"][0]
        for lineitem in order_with_non_weighted_items["line-items"]
    ]

    all_tom_ids = order_1_tom_ids + order_2_tom_ids
    apis.ims.zero_stock_for_products_or_addresses(all_tom_ids)
    cutoff = order_with_weighted_items["cutoff-datetime"]
    force_picklist_creation(oms=apis.oms, cutoff=cutoff, picklist_type=picklist_type)

    picklist_code = apis.isps.find_picklists_by_cutoff_and_status(cutoff, "SPLIT")[0][
        "code"
    ]
    workorder_codes = [
        w["code"] for w in apis.isps.get_workorders_for_picklist(picklist_code)
    ]

    workorder_items = []

    for wo_code in workorder_codes:
        items = apis.isps.get_workorder_items(wo_code)
        for item in items:
            workorder_items.append(item)

    weighted_products: list[Product] = randon_weighted_products["all_products"]
    for product in weighted_products:
        product_occurances_in_workorder = list(
            filter(lambda i: i["product-id"] == product.tom_id, workorder_items)
        )

        print(
            "product_occurances_in_workorder items ::", product_occurances_in_workorder
        )

        # two orders, 1 weighted unit in each; each occurance should be a separate item in workorder
        assert len(product_occurances_in_workorder) == 2

    print(
        bold(
            f"Picklist code: {picklist_code}, should have {len(workorder_items)} lines"
        )
    )
    print(get_picklist_name_in_tma(cutoff, picklist_type))
    print(cyan("Test case isps is:"))
