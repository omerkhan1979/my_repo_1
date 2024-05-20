from src.api.takeoff.decanting import Decanting
from src.api.collections import InitializedApis
from pytest_bdd import scenarios, given, then, parsers, when
from src.api.takeoff.distiller import Distiller
from src.utils.addresses import get_addresses_v2
from src.utils.console_printing import cyan
from src.utils.decanting import wait_for_po_from_decanting
from src.utils.distiller import wait_for_po_from_purchase_order_by_id
from src.utils.purchase_order import (
    upload_sftp_po_single_mfc,
    upload_sftp_po_multiple_mfc,
    upload_sftp_po_dsd_file,
    make_purchase_order_from_products,
)
from scripts.steps.orderflow.setup import prepare_orderflow_data
from src.utils.assortment import Product

scenarios("../features/purchase_order.feature")


@given("the retailer MFC site is enabled in the environment", target_fixture="mfc_code")
def get_MFC_code(apis: InitializedApis):
    mfc_code = apis.tsc.get_location_code("location-code-gold")

    return mfc_code


@then("get the current list of Purchase Orders", target_fixture="view_po_response")
def get_POs(mfc_code: str, decanting: Decanting):
    view_po_response = decanting.get_decanting_tasks_for_view_po(mfc_code)
    return view_po_response


@then(parsers.parse('check at least one Purchase Order is in "{status}" status'))
def check_po_status(view_po_response, status: str):
    found = False
    for po in view_po_response["tasks"]:
        if po["status"] == status:
            found = True
            break
    assert found, f"No Purchase Order found in '{status}' status"


@given("purchase order is created", target_fixture="po_data")
def create_po(location_code_retailer: str, apis: InitializedApis, retailer):
    manual_products = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        retailer,
        picklist_weighted_qty=0,
        osr_products_qty=0,
        manual_non_weighted_qty=1,
        manual_weighted_qty=0,
    )
    products: list[Product] = manual_products["all_products"]
    po = make_purchase_order_from_products(location_code_retailer, products)
    apis.rint.create_purchase_order(po)

    manual_product = po.items[0].tom_id
    po_id = po.purchase_order_id

    return {"manual_product": manual_product, "po_id": po_id, "po": po}


@when("the Purchase Order is filled by decanting the product")
def add_product_decanting(
    apis: InitializedApis,
    po_data: dict,
    decanting: Decanting,
    location_code_retailer: str,
    location_code_tom: str,
):
    po_id = po_data["po_id"]
    product = po_data["manual_product"]
    rint_po = apis.rint.get_purchase_order(location_code_retailer, po_id)
    assert rint_po.data.status == "created", "The PO should be marked as created"
    assert (
        rint_po.data.items[0].received_quantity == 0
    ), "The PO should not reflect any received inventory"

    # When the inventory is put away against that purchase order
    address = get_addresses_v2(apis.ims, 1)[0]
    quantity = 1

    decanting.put_away_operation(location_code_tom, address, product, quantity, po_id)

    # And the retailer gets the purchase order
    rint_po = apis.rint.get_purchase_order(location_code_retailer, po_id)

    # Then the response is ...
    assert rint_po.data.status == "started", "The PO should be started"
    assert (
        rint_po.data.items[0].received_quantity == 1
    ), "The PO should reflect the quantity received"

    # When the purchase order is closed
    decanting.close_purchase_order(po_id)


@then('close the Purchase Order and verify that the status is "completed"')
def verify_completed_status(
    apis: InitializedApis, po_data: dict, location_code_retailer: str
):
    po_id = po_data["po_id"]
    rint_po = apis.rint.get_purchase_order(location_code_retailer, po_id)
    assert rint_po.data.status == "completed", "The PO should be complete"
    assert (
        rint_po.data.items[0].received_quantity == 1
    ), "The PO should still report the quantity received"


@then("verify the Purchase Order response for the price of the product")
def verify_purchase_price(po_data: dict):
    po = po_data["po"]
    assert po.items[0].purchase_price == 5
    print(cyan("Test case create_po_and_check_price is:"))


@when("purchase order is created with SFTP", target_fixture="po_id")
def create_po_SFTP(retailer: str, cfg):
    po_id = upload_sftp_po_single_mfc(retailer, cfg)
    return po_id


@then("verify that the Purchase Order appears in the distiller")
def verify_PO_dist(distiller: Distiller, po_id):
    purchase_orders_response = wait_for_po_from_purchase_order_by_id(
        distiller=distiller, create_common_po=po_id
    )
    print(purchase_orders_response)
    assert purchase_orders_response["purchase-order-id"] == po_id


@then(
    "verify the Purchase order response to ensure purchase order is present in the response"
)
def verify_po_response(decanting: Decanting, location_code_gold: str, po_id):
    decanting_response = wait_for_po_from_decanting(
        decanting_service=decanting,
        po_id=po_id,
        location_code_gold=int(location_code_gold),
    )
    print(decanting_response)
    assert decanting_response.purchase_order == po_id

    print(cyan("TC test_create_sftp_po_single_mfc is:"))


@when(
    parsers.parse("purchase order is created for multiple POs {PO_ID}"),
    target_fixture="po_id",
)
def create_pos_SFTP(retailer, cfg, PO_ID):
    po_id = [po_id.strip('"') for po_id in PO_ID.split(",")]
    po_id[0], po_id[1] = upload_sftp_po_multiple_mfc(retailer, cfg)
    return {"po_id[0]": po_id[0], "po_id[1]": po_id[1]}


@when("a Purchase Order DSD file is created and processed", target_fixture="po_id")
def create_PO_DSD(retailer, cfg, products, location_code_retailer: str):
    product = [
        product
        for product in products["order_flow_data"]["osr_products"]
        if product.temp_zone == "ambient"
    ]
    po_id = upload_sftp_po_dsd_file(retailer, cfg, location_code_retailer, product)
    return {"po_id[0]": po_id}


@then("verify that the Purchase Orders are present in the Distiller service")
def verify_PO_distiller(distiller: Distiller, po_id):
    po_id[0] = po_id["po_id[0]"]
    if po_id[0]:
        purchase_orders_response_1 = wait_for_po_from_purchase_order_by_id(
            distiller=distiller, create_common_po=po_id[0]
        )
        assert purchase_orders_response_1["purchase-order-id"] == po_id[0]
    elif po_id[0] & po_id[1]:
        purchase_orders_response_1 = wait_for_po_from_purchase_order_by_id(
            distiller=distiller, create_common_po=po_id[0]
        )
        purchase_orders_response_2 = wait_for_po_from_purchase_order_by_id(
            distiller=distiller, create_common_po=po_id[1]
        )
        assert purchase_orders_response_1["purchase-order-id"] == po_id[0]
        assert purchase_orders_response_2["purchase-order-id"] == po_id[1]
    else:
        raise ValueError("Invalid number of PO IDs provided")


@then(
    "verify that the Purchase Orders are present in the response from the Decanting service"
)
def verify_PO_decanting(decanting: Decanting, location_code_gold: str, po_id):
    if po_id[0]:
        decanting_response_1 = wait_for_po_from_decanting(
            decanting_service=decanting,
            po_id=po_id[0],
            location_code_gold=int(location_code_gold),
        )
        assert decanting_response_1.purchase_order == po_id[0]
    elif po_id[0] & po_id[1]:
        decanting_response_1 = wait_for_po_from_decanting(
            decanting_service=decanting,
            po_id=po_id[0],
            location_code_gold=int(location_code_gold),
        )
        decanting_response_2 = wait_for_po_from_decanting(
            decanting_service=decanting, po_id=po_id[1], location_code_gold=2502
        )
        assert decanting_response_1.purchase_order == po_id[0]
        assert decanting_response_2.purchase_order == po_id[1]
    else:
        raise ValueError("Invalid number of PO IDs provided")
