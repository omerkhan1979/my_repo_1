import pytest
from pytest import mark
from src.api.takeoff.bifrost import Bifrost
from src.utils.addresses import get_addresses_v2
from src.utils.assortment import Product
from src.utils.decanting import wait_for_po_from_decanting
from src.utils.console_printing import error_print, cyan, red, green
from src.utils.distiller import wait_for_po_from_purchase_order_by_id
from src.utils.purchase_order import (
    upload_sftp_po_single_mfc,
    upload_sftp_po_multiple_mfc,
    upload_sftp_po_dsd_file,
    prepare_products_for_po,
    make_purchase_order_from_products,
    create_po,
)
from src.api.collections import InitializedApis
from scripts.steps.orderflow.setup import prepare_orderflow_data


@mark.rq
@mark.smoke
@mark.darkstore
@mark.inbound
@mark.inbound_smoke
@mark.retailers(
    "wings",
    "maf",
    "abs",
    "winter",
    "smu",
    "pinemelon",
    "tienda",
)
@mark.create_common_po
@mark.testrail("185252")
def test_retailer_visibility_into_po_lifecycle(
    location_code_tom: str,
    location_code_retailer: str,
    retailer,
    apis: InitializedApis,
):
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

    # NOTE: We don't have to "wait" for decanting service to get these POs.
    # They're available as soon as rint has replied to us.
    # Unfortunately rint doesn't return anything very "useful" for us.
    apis.rint.create_purchase_order(po)

    product = po.items[0].tom_id

    # When the retailer gets the purchase order
    rint_po = apis.rint.get_purchase_order(location_code_retailer, po.purchase_order_id)

    # Then the response is ...
    assert rint_po.data.status == "created", "The PO should be marked as created"
    assert (
        rint_po.data.items[0].received_quantity == 0
    ), "The PO should not reflect any received inventory"

    # When the inventory is put away against that purchase order
    address = get_addresses_v2(apis.ims_admin, 1)[0]
    quantity = 1

    apis.decanting.put_away_operation(
        location_code_tom, address, product, quantity, po.purchase_order_id
    )

    # And the retailer gets the purchase order
    rint_po = apis.rint.get_purchase_order(location_code_retailer, po.purchase_order_id)

    # Then the response is ...
    assert rint_po.data.status == "started", "The PO should be started"
    assert (
        rint_po.data.items[0].received_quantity == 1
    ), "The PO should reflect the quantity received"

    # When the purchase order is closed
    apis.decanting.close_purchase_order(po.purchase_order_id)

    # And the retailer gets the purchase order
    # Then the response is ...
    rint_po = apis.rint.get_purchase_order(location_code_retailer, po.purchase_order_id)
    assert rint_po.data.status == "completed", "The PO should be complete"
    assert (
        rint_po.data.items[0].received_quantity == 1
    ), "The PO should still report the quantity received"


@mark.rq
@mark.inbound
@mark.create_po_and_check_price
@mark.retailers("wings", "maf", "smu")
@mark.testrail("128649")
def test_create_po_and_check_price(
    login_gcp_project, apis: InitializedApis, retailer, cfg, location_code_gold: str
):
    credentials = login_gcp_project
    if not apis.bifrost.get_health_pass():
        error_print("Bifrost is unhealthy")
        raise SystemError("Cannot continue as bifrost is unhealthy")

    ambient_osr_products = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        retailer,
        picklist_weighted_qty=0,
        osr_products_qty=1,
        manual_non_weighted_qty=0,
        manual_weighted_qty=0,
        temp_zone=["ambient"],
    )

    products: list[Product] = ambient_osr_products["all_products"]

    po_id = create_po(
        decanting_service=apis.decanting,
        config=cfg,
        location_code_gold=int(location_code_gold),
        products=products,
        po_provided_by_user=False,
        credentials=credentials,
    )

    purchase_orders_response = wait_for_po_from_purchase_order_by_id(
        distiller=apis.distiller, create_common_po=po_id
    )
    print(purchase_orders_response)

    assert purchase_orders_response["items"][0]["purchase-price"] == 5
    print(cyan("Test case create_po_and_check_price is:"))


@mark.rq
@mark.inbound
@mark.create_po_sftp_single
@mark.retailers("winter")
@mark.testrail("156702")
def test_create_sftp_po_single_mfc(
    distiller, retailer, cfg, location_code_tom, decanting, location_code_gold
):
    if location_code_tom != "WF0001":
        pytest.skip(
            red(
                "Test might be run ONLY for WF0001 because wh_invoice_winter template includes "
                "data relevant to WF0001"
            )
        )

    po_id = upload_sftp_po_single_mfc(retailer, cfg)
    # Verify that PO appeared in Distiller PostgreSQL:
    purchase_orders_response = wait_for_po_from_purchase_order_by_id(
        distiller=distiller, create_common_po=po_id
    )
    print(purchase_orders_response)
    assert purchase_orders_response["purchase-order-id"] == po_id
    # Verify that PO is present in the response from Decanting service:
    decanting_response = wait_for_po_from_decanting(
        decanting_service=decanting,
        po_id=po_id,
        location_code_gold=int(location_code_gold),
    )
    print(decanting_response)
    assert decanting_response.purchase_order == po_id

    print(cyan("TC test_create_sftp_po_single_mfc is:"))


@mark.rq
@mark.inbound
@mark.create_po_sftp_multiple
@mark.retailers("winter")
@mark.testrail("60850")
# We are uploading one file with several purchase orders for two different MFCs: WF0001 and WF0608.
# The second MFC (WF0608) is hard coded to verify the creation PO.
def test_create_sftp_po_multiple_mfc(
    distiller, retailer, cfg, location_code_tom, decanting, location_code_gold: str
):
    if location_code_tom != "WF0001":
        pytest.skip(
            red(
                "Test might be run ONLY for WF0001 because wh_invoice_winter template includes "
                "data relevant to WF0001"
            )
        )
    po_id_142, po_id_608 = upload_sftp_po_multiple_mfc(retailer, cfg)
    # Verify that PO appeared in Distiller PostgreSQL:
    purchase_orders_response_142 = wait_for_po_from_purchase_order_by_id(
        distiller=distiller, create_common_po=po_id_142
    )
    purchase_orders_response_608 = wait_for_po_from_purchase_order_by_id(
        distiller=distiller, create_common_po=po_id_608
    )

    assert purchase_orders_response_142["purchase-order-id"] == po_id_142
    assert purchase_orders_response_608["purchase-order-id"] == po_id_608
    # Verify that PO is present in the response from Decanting service:
    decanting_response_142 = wait_for_po_from_decanting(
        decanting_service=decanting,
        po_id=po_id_142,
        location_code_gold=int(location_code_gold),
    )
    decanting_response_608 = wait_for_po_from_decanting(
        decanting_service=decanting, po_id=po_id_608, location_code_gold=2502
    )
    assert decanting_response_142.purchase_order == po_id_142
    assert decanting_response_608.purchase_order == po_id_608
    print(green(f"Po_id for WF0001 is {po_id_142}, for WF0608 is {po_id_608}"))
    print(cyan("TC test_create_sftp_po_multiple_mfc is:"))


@mark.rq
@mark.inbound
@mark.create_po_dsd_file_processed
@mark.retailers("winter")
@mark.testrail("128029")
def test_create_po_dsd_file_processed(
    distiller,
    retailer,
    cfg,
    decanting,
    location_code_gold,
    location_code_retailer,
    bifrost: Bifrost,
):
    # check if bifrost is healthy
    assert bifrost.get_health_pass()
    product = prepare_products_for_po(
        distiller=distiller,
        retailer=retailer,
        location_code_retailer=location_code_retailer,
        ambient_osr_count=1,
        chilled_osr_count=0,
        req_exp_date_osr_count=0,
        chemical_osr_count=0,
        manual_count=0,
    )["ambient_osr_products"]
    po_id = upload_sftp_po_dsd_file(retailer, cfg, location_code_retailer, product)
    # Verify that PO appeared in Distiller PostgreSQL:
    purchase_orders_response = wait_for_po_from_purchase_order_by_id(
        distiller=distiller, create_common_po=po_id
    )
    print(purchase_orders_response)
    assert purchase_orders_response["purchase-order-id"] == po_id
    # Verify that PO is present in the response from Decanting service:
    decanting_response = wait_for_po_from_decanting(
        decanting_service=decanting,
        po_id=po_id,
        location_code_gold=int(location_code_gold),
    )
    print(decanting_response)
    assert decanting_response.purchase_order == po_id

    print(cyan("TC test_create_po_dsd_file_processed is:"))
