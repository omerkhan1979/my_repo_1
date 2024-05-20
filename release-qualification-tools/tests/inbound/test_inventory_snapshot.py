import pytest
from pytest import mark
import random

from src.api.collections import InitializedApis
from src.config.config import Config
from src.utils.console_printing import blue, cyan


@mark.rq
@mark.inbound
@mark.darkstore
@mark.inventory_snapshot_match
@mark.retailers(
    "wings",
    "maf",
    "abs",
    "winter",
    "smu",
    "pinemelon",
    "tienda",
)
@mark.testrail("30309")
def test_inventory_snapshot_match(
    apis: InitializedApis,
    location_code_tom,
    location_code_retailer,
    cfg: Config,
):
    if cfg.env == "ode" and cfg.retailer == "abs":
        pytest.skip("This test does not work in ODE for abs")
        return

    snapshot_rint = apis.rint.get_shelves_snapshot_v4(location_code_retailer)
    product = random.choice(snapshot_rint["data"])
    product_id = product["takeoff-item-id"]
    qty_total_rint = product["quantity-on-hands"]

    snapshot_ims = apis.ims.shelves_snapshot(location_code_tom)
    qty_total_ims = 0
    for item in snapshot_ims["success"]:
        if item["product-id"] == product_id:
            qty_total_ims += item["qty-total"]

    print(
        blue(
            f"\nQuantity-on-hands in RINT snapshot is {qty_total_rint}pcs and qty-total in IMS snapshot is {qty_total_ims}pcs for item {product_id}."
        )
    )
    print(cyan("Test case inventory_snapshot_match is:"))

    assert qty_total_ims == qty_total_rint


"""NOTE: As a change of Inventory Manager endpoint from RINT to INVENTORY MANAGER due to deprecation of inventory api from RINT,
so we had created a separate test script specific for the new endpoint. We are keeping the RINT endpoint for some time,
and we will deprecate the above test script and testcase"""


@mark.rq
@mark.inbound
@mark.darkstore
@mark.inventory_snapshot_ims
@mark.retailers("abs", "winter")
@mark.testrail("716381")
def test_inventory_snapshot_match_ims(
    apis: InitializedApis,
    location_code_tom,
    cfg: Config,
):
    if cfg.env == "ode":
        pytest.skip("This test will not work in ODE until INBOUND-3838 is addressed")
        return

    snapshot_im = apis.im.inventory_snapshot(apis.tsc)
    product = random.choice(snapshot_im["data"])
    product_id = product["tom_id"]
    qty_total_im = product["quantity_on_hand"]

    snapshot_ims_shelve = apis.ims.shelves_snapshot(location_code_tom)
    qty_total_ims_shelve = 0
    for item in snapshot_ims_shelve["success"]:
        if item["product-id"] == product_id:
            qty_total_ims_shelve += item["qty-total"]

    print(
        blue(
            f"\nQuantity-on-hands in InventoryManager snapshot is {qty_total_im}pcs and qty-total in IMS snapshot is {qty_total_ims_shelve}pcs for item {product_id}."
        )
    )
    print(cyan("Test case inventory_snapshot_match is:"))

    assert qty_total_ims_shelve == qty_total_im
