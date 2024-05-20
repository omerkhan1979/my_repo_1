from pprint import pprint
from time import time
from pytest import mark
from src.utils.addresses import get_addresses_v2
from src.utils.assortment import Product
from src.utils.console_printing import cyan
from src.utils.ims import wait_for_item_adjustment_from_ims
from src.api.collections import InitializedApis
from scripts.steps.orderflow.setup import prepare_orderflow_data


@mark.rq
@mark.inbound
@mark.darkstore
@mark.inventory_adjustment
@mark.retailers(
    "wings",
    "maf",
    "abs",
    "winter",
    "smu",
    "pinemelon",
    "tienda",
)
@mark.testrail("49606")
def test_inventory_adjustment(retailer, location_code_tom, apis: InitializedApis):
    shelf_id = get_addresses_v2(ims=apis.ims_admin)[0]

    manual_product = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        retailer,
        picklist_weighted_qty=0,
        osr_products_qty=0,
        manual_non_weighted_qty=1,
        manual_weighted_qty=0,
    )

    products: list[Product] = manual_product["all_products"]
    product_id = products[0].tom_id
    time_past = str(int(round(time() * 1000)))
    apis.ims.shelf_adjust(shelf_id, product_id, 10, "CC")
    adjustments_response = wait_for_item_adjustment_from_ims(
        apis.ims, time_past, None, location_code_tom
    )
    assert adjustments_response["quantity"] == 10

    # Pickerman backend - scan valid address:
    shelves_balance_subset_scan = apis.ims.shelves_balance_subset(
        location_code_tom, shelf_id
    )
    # be sure that address already has product:
    product_id_present = False
    for item in shelves_balance_subset_scan["success"]:
        if item["product-id"] == product_id:
            product_id_present = True
            break
    assert product_id_present

    time_past = str(int(round(time() * 1000)))
    apis.ops_api.inventory_adjust(
        shelf_id, product_id, 5, "CC"
    )  # Pickerman backend - adjustment via Platform
    adjustment_verification = wait_for_item_adjustment_from_ims(
        apis.ims, time_past, None, location_code_tom
    )
    pprint(adjustment_verification)
    print(cyan("Test case inventory_adjustment is:"))
    assert adjustment_verification["quantity"] == 5
    assert adjustment_verification["product"] == product_id
    assert adjustment_verification["reason-code"] == "CC"
