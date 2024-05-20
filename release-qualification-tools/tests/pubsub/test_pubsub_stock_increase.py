from time import time

import pytest
from pytest import mark
from pprint import pprint
from src.config.config import Config

from src.utils.helpers import wait_for_pubsub_message_after_inv_mov
from src.utils.assortment import Product
from src.utils.ims import wait_for_item_adjustment_from_ims
from src.utils.console_printing import cyan, blue, yellow
from src.api.collections import InitializedApis
from scripts.steps.orderflow.setup import prepare_orderflow_data


@mark.rq
@mark.pubsub
@mark.inbound
@mark.pubsub_stock_increase
@mark.retailers("wings", "tienda")
@mark.testrail("61100")
def test_pubsub_stock_increase(
    cfg: Config, retailer, distiller, ims, location_code_tom, apis: InitializedApis
):
    # TODO: Fixing of this issue will be taken care with ticket PROD-11888, currently we did add this to skip the execution from ODE env.
    if cfg.env == "ode":
        pytest.skip(
            "We can skip this test from ODE for now, need to fix the script from failing"
        )

    orderflow_test_data = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        cfg.retailer,
        picklist_weighted_qty=0,
        osr_products_qty=1,
        manual_non_weighted_qty=0,
        manual_weighted_qty=0,
    )

    products: list[Product] = orderflow_test_data["all_products"]

    time_past = str(int(round(time() * 1000)))

    ims.shelf_adjust("01K", products[0].tom_id, 10, "IB")
    item = products[0].tom_id

    adjustments_response = wait_for_item_adjustment_from_ims(
        ims, time_past, None, location_code_tom
    )
    pprint(adjustments_response)
    product = products[0]
    shelf_state_post = ims.v2_snapshot(
        products=[product.tom_id], addresses=["01K"], include_zeros=True
    )
    for address in shelf_state_post["addresses"]:
        if address["address"] == "01K":
            quantity_after_increase = address["quantity"]
            print(blue(f"\nThe item {item} has increased in 10"))
            print(
                cyan(
                    f"\nQuantity after increasing {quantity_after_increase} of the item {item}"
                )
            )
            print(
                yellow(
                    f"\nNow test is searching the needed pubsub message for the item {item} with quantity after "
                    f"increasing {quantity_after_increase}"
                )
            )

    count = 0
    success = False
    while count < 10:
        payload = wait_for_pubsub_message_after_inv_mov(cfg)
        count += 1
        item_id = payload.get("takeoff-item-id")
        quantity_after = payload.get("quantity-after")
        if item_id == item:
            if quantity_after == quantity_after_increase:
                success = True
            pprint(payload)
            break
    assert success
    print(cyan("Test case pubsub_stock_increase is:"))
