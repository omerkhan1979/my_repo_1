from pprint import pprint
import datetime
from time import time, sleep

from pytest import mark

from src.utils.addresses import get_addresses_v2
from src.utils.assortment import Product
from src.utils.console_printing import cyan
from src.utils.ims import wait_for_item_adjustment_from_ims
from src.api.collections import InitializedApis
from scripts.steps.orderflow.setup import prepare_orderflow_data


@mark.rq
@mark.inbound
@mark.inventory_adjustment_abs_ex
@mark.retailers("abs")
@mark.testrail("51779")
def test_inventory_adjustment(
    retailer, env, location_code_tom, location_code_retailer, apis: InitializedApis
):
    shelf_id = get_addresses_v2(ims=apis.ims_admin)[0]

    orderflow_test_data = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        retailer,
        picklist_weighted_qty=0,
        osr_products_qty=1,
        manual_non_weighted_qty=0,
        manual_weighted_qty=0,
    )
    products: list[Product] = orderflow_test_data["all_products"]
    product_id = products[0].tom_id
    time_past = str(int(round(time() * 1000)))
    start_date = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    apis.ims_admin.shelf_adjust(shelf_id, product_id, 10, "CC")
    adjustments_response = wait_for_item_adjustment_from_ims(
        apis.ims_admin, time_past, None, location_code_tom
    )
    assert adjustments_response["quantity"] == 10
    apis.ims_admin.shelf_adjust(shelf_id, product_id, -5, "EX")
    # NOTE: ODE-Winter's config has an external code mapping if we use EX it'll be EX in abs-qai but "4_2" in ODE
    expected_code = "4_2" if env == "ode" else "EX"
    # validate adjustment via rint.get_inventory_movements:
    for _ in range(5):
        rint_inventory_movements = apis.rint.get_inventory_movements(
            location_code_retailer, start_date
        )
        pprint(rint_inventory_movements)
        # Iterate through the movements to find the one with the desired characteristics
        actual_movement = None
        for movement in rint_inventory_movements["data"]:
            if movement["operation"] == "dec" and movement["reason"] == expected_code:
                actual_movement = movement
                break
        else:  # no break
            sleep(5)
            continue
        break
    # Validate the quantity
    assert (
        actual_movement is not None
    ), "No movement with the specified characteristics found"
    actual_quantity = actual_movement["quantity"]
    expected_quantity = 10 - actual_quantity

    assert (
        actual_quantity == expected_quantity
    ), f"Expected {expected_quantity} but got {actual_quantity}"
    assert (
        actual_movement["operation"] == "dec"
    ), "Expected operation 'dec' after the movement"
    assert (
        actual_movement["reason"] == expected_code
    ), f"Expected reason {expected_code} after the movement"
    print(cyan("Test case inventory_adjustment_abs_ex is:"))
