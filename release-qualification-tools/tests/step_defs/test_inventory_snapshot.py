from src.api.collections import InitializedApis
from pytest_bdd import scenarios, given, then
from src.utils.console_printing import blue, cyan
import random

scenarios("../features/inventory_snapshot.feature")


@given(
    "inventory snapshot for a product is taken from rint",
    target_fixture="product_snapshot",
)
def inventory_snapshot_rint(
    apis: InitializedApis,
    location_code_retailer,
):
    snapshot_rint = apis.rint.get_shelves_snapshot_v4(location_code_retailer)
    product = random.choice(snapshot_rint["data"])
    product_id = product["takeoff-item-id"]
    qty_total_rint = product["quantity-on-hands"]

    return {"product_id": product_id, "qty_total_rint": qty_total_rint}


@given(
    "inventory snapshot for the same product is taken from IMS",
    target_fixture="product_snapshot_ims",
)
def inventory_snapshot_ims(
    apis: InitializedApis, location_code_tom: str, product_snapshot: dict
):
    snapshot_ims = apis.ims.shelves_snapshot(location_code_tom)
    qty_total_ims = 0
    for item in snapshot_ims["success"]:
        if item["product-id"] == product_snapshot["product_id"]:
            qty_total_ims += item["qty-total"]

    return qty_total_ims


@then("quantity in rint is equal the total the quantity in IMS")
def verify_qty_from_rint_ims(product_snapshot: dict, product_snapshot_ims: int):
    print(
        blue(
            f"\nQuantity-on-hands in RINT snapshot is {product_snapshot['qty_total_rint']}pcs and qty-total in IMS snapshot is {product_snapshot_ims}pcs for item {product_snapshot['product_id']}."
        )
    )
    print(cyan("Test case inventory_snapshot_match is:"))

    assert product_snapshot_ims == product_snapshot["qty_total_rint"]


@given(
    "inventory snapshot for a product is taken from inventory manager",
    target_fixture="product_snapshot",
)
def inventory_snapshot_im(
    apis: InitializedApis,
):
    snapshot_im = apis.im.inventory_snapshot(apis.tsc)
    product = random.choice(snapshot_im["data"])
    product_id = product["tom_id"]
    qty_total_im = product["quantity_on_hand"]
    return {"product_id": product_id, "qty_total_rint": qty_total_im}


@then("quantity on-hand in Inventory Manager is equal to Total Quantity in IMS")
def verify_qty_from_im_ims(product_snapshot: dict, product_snapshot_ims: int):
    print(
        blue(
            f"\nQuantity-on-hands in RINT snapshot is {product_snapshot['qty_total_rint']}pcs and qty-total in IMS snapshot is {product_snapshot_ims}pcs for item {product_snapshot['product_id']}."
        )
    )
    print(cyan("Test case inventory_snapshot_match is:"))

    assert product_snapshot_ims == product_snapshot["qty_total_rint"]
