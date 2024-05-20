from pprint import pprint

from pytest import mark

from src.utils.console_printing import cyan, blue
from src.utils.helpers import wait_order_status_changed, wait_for_decisions
from src.utils.assortment import Product
from src.api.collections import InitializedApis
from src.utils.place_order import place_order
from scripts.steps.orderflow.setup import prepare_orderflow_data
from src.utils.order_timings import MFCRelativeFutureTime
from src.utils.order_picking import clear_dispatch_lane_order


@mark.rq
@mark.multi_temp_osr_picking
@mark.retailers("maf")
@mark.testrail("142994")
def test_multi_temp_osr_picking(
    retailer,
    location_code_retailer,
    apis: InitializedApis,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
):
    ambient_order_data = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        retailer,
        picklist_weighted_qty=0,
        osr_products_qty=1,
        manual_non_weighted_qty=0,
        manual_weighted_qty=0,
        stage_by_data=stage_by_in_1_minutes_1_min_cutoff,
        temp_zone=["ambient"],
    )

    chilled_order_data = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        retailer,
        picklist_weighted_qty=0,
        osr_products_qty=1,
        manual_non_weighted_qty=0,
        manual_weighted_qty=0,
        stage_by_data=stage_by_in_1_minutes_1_min_cutoff,
        temp_zone=["chilled"],
    )
    ambient_product: list[Product] = ambient_order_data["all_products"]
    chilled_product: list[Product] = chilled_order_data["all_products"]
    multi_temp_zone = ambient_product + chilled_product

    order_id = place_order(
        rint=apis.rint,
        retailer=retailer,
        products=multi_temp_zone,
        store_id=chilled_order_data["store_id"],
        spoke_id=chilled_order_data["spoke_id"],
        stage_by_datetime=chilled_order_data["stage_by_datetime"],
        service_window_start=chilled_order_data["service_window_start"],
        route_id=chilled_order_data["route_id"],
        ims=apis.ims_admin,
        oms=apis.oms,
    )

    wait_order_status_changed(order_id, "queued", apis.oms)
    wait_for_decisions(apis.fft, order_id)
    response_from_get_order = apis.oms.get_order(order_id)["response"]["line-items"]
    pprint(response_from_get_order)
    # verify that all decisions have "Chilled" zone (since only Chilled target totes were send for picking):
    verify_tote_ambient_item = response_from_get_order[0]["tom-items"][0]["decision"][
        0
    ]["zone"]
    verify_tote_chilled_item = response_from_get_order[1]["tom-items"][0]["decision"][
        0
    ]["zone"]
    assert verify_tote_ambient_item == verify_tote_chilled_item == "chilled"

    print(cyan("Test case test_maf_multi_temp_osr_picking is:"))

    print(blue(f"\nClearing dispatch lane(s) if needed for order: {order_id}\n"))
    clear_dispatch_lane_order(apis.ims, order_id)
