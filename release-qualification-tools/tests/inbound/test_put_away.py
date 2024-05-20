from pytest import mark
from src.utils.addresses import get_addresses_v2
from src.utils.console_printing import blue
from src.utils.purchase_order import create_po
from src.utils.assortment import Product
from src.api.collections import InitializedApis
from scripts.steps.orderflow.setup import prepare_orderflow_data
from src.utils.decanting import wait_for_po_from_decanting


@mark.rq
@mark.smoke
@mark.darkstore
@mark.inbound
@mark.inbound_smoke
@mark.put_away_tma_po
@mark.retailers(
    "wings",
    "maf",
    "abs",
    "winter",
    "smu",
    "pinemelon",
    "tienda",
)
@mark.testrail("716383")
def test_put_away_tma_po(
    location_code_gold: str,
    location_code_tom: str,
    apis: InitializedApis,
    login_gcp_project,
    cfg,
    retailer,
):
    credentials = login_gcp_project
    location_gold = int(location_code_gold)

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

    po_id = create_po(
        decanting_service=apis.decanting,
        config=cfg,
        location_code_gold=location_gold,
        products=products,
        po_provided_by_user=False,
        credentials=credentials,
    )
    decanting_response = wait_for_po_from_decanting(
        decanting_service=apis.decanting,
        po_id=po_id,
        location_code_gold=location_gold,
    )
    # Just to make sure the wait's type is not None.
    assert decanting_response

    manual_product = decanting_response.products[0].product
    po_id = decanting_response.purchase_order

    decanting_tasks = apis.decanting.get_decanting_tasks_by_product(
        int(location_code_gold), manual_product
    )
    po_found = False
    for task in decanting_tasks["tasks"]:
        if task["purchase_order"] == po_id:
            po_found = True
            break
    assert po_found

    shelf_id = get_addresses_v2(ims=apis.ims_admin)[0]
    stock_before = apis.ims_admin.shelves_balance_products(
        location_code_tom, manual_product
    )
    qty_total_before = 0
    if stock_before["success"]:
        for item in stock_before["success"]:
            if item["address"] == shelf_id:
                qty_total_before = item["qty-total"]
                print(f"shelf balance for {shelf_id} before put-away-TMA: {item}")
                break
            else:
                qty_total_before = 0

    qty_to_adjust = 1
    put_away_action = apis.mobile.putaway(
        shelf_id, manual_product, qty_to_adjust, po_id
    )
    print("Put_away_TMA_operation response:", put_away_action)

    stock_after = apis.ims_admin.shelves_balance_products(
        location_code_tom, manual_product
    )
    qty_total_after = None
    assert stock_after[
        "success"
    ], "Did not find any stock after completing 'put away TMA'"
    for item in stock_after["success"]:
        if item["address"] == shelf_id:
            qty_total_after = item["qty-total"]
            print(f"shelf balance for {shelf_id} after put-away-TMA: {item}")
            break

    print(
        blue(
            f"The stock for item  {manual_product} has been increased by {qty_total_after - qty_total_before} pcs on "
            f"the shelf {shelf_id}, PO {po_id}"
        )
    )

    assert qty_total_after - qty_total_before == qty_to_adjust


@mark.rq
@mark.smoke
@mark.darkstore
@mark.inbound
@mark.inbound_smoke
@mark.put_away_tma_without_po
@mark.retailers(
    "wings",
    "maf",
    "abs",
    "winter",
    "smu",
    "pinemelon",
    "tienda",
)
@mark.testrail("716384")
def test_put_away_tma_without_po(
    location_code_retailer: str,
    location_code_tom: str,
    retailer: str,
    apis: InitializedApis,
):
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

    prepared_product: Product = products[0]
    product_id = prepared_product.tom_id
    shelf_id = get_addresses_v2(ims=apis.ims_admin)[0]
    stock_before = apis.ims_admin.shelves_balance_products(
        location_code_tom, product_id
    )
    qty_total_before = 0
    if stock_before["success"]:
        for item in stock_before["success"]:
            if item["address"] == shelf_id:
                qty_total_before = item["qty-total"]
                print(f"shelf balance for {shelf_id} before put-away-TMA: {item}")
                break
            else:
                qty_total_before = 0

    qty_to_adjust = 1
    put_away_action = apis.mobile.putaway(shelf_id, product_id, qty_to_adjust)
    print("Put_away_TMA_operation response:", put_away_action)

    stock_after = apis.ims_admin.shelves_balance_products(location_code_tom, product_id)
    qty_total_after = None
    assert stock_after[
        "success"
    ], "Did not find any stock after completing 'put away TMA'"
    for item in stock_after["success"]:
        if item["address"] == shelf_id:
            qty_total_after = item["qty-total"]
            print(f"shelf blance for {shelf_id} after put-away-TMA: {item}")
            break

    print(
        blue(
            f"The stock for item  {manual_product} has been increased by {qty_total_after - qty_total_before} pcs on "
            f"the shelf {shelf_id}, DSD PO "
        )
    )

    assert qty_total_after - qty_total_before == qty_to_adjust
