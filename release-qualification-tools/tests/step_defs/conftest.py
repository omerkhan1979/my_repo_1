from pprint import pprint
import pytest
from scripts.steps.orderflow.setup import prepare_orderflow_data
from src.api.takeoff.decanting import Decanting
from src.api.takeoff.tsc import TscReturnFormat
from src.api.collections import InitializedApis
from src.utils.assortment import Product
from src.utils.decanting import wait_for_po_product_decanted_quanity
from src.utils.purchase_order import create_po
from src.utils.user import AuthServiceUser
from src.utils.console_printing import red, blue
from src.utils.cmd_line import run_env_setup_tool
from src.utils.helpers import wait_order_status_changed, get_order_status
from src.utils.order_picking import (
    consolidate_order,
    stage_order,
)
from src.utils.place_order import place_order, products_to_lineitems
from src.utils.order_timings import (
    MFCRelativeFutureTime,
)
from pytest_bdd import given, then, when, parsers
from src.utils.picklist_helpers import transition_order_to_picked
from src.utils.decanting import (
    wait_for_po_from_decanting,
    wait_for_po_update_after_decanting,
)


@given(parsers.parse("{config} feature is set in env"))
def apply_feature(config: str) -> None:
    run_env_setup_tool(feature=config)


@given(
    parsers.parse(
        'products from "{osr:d}" "{manual:d}" "{flo:d}" "{manual_weighted:d}" are available in the environment'
    ),
    target_fixture="products",
)
def get_products(
    osr: int,
    manual: int,
    flo: int,
    manual_weighted: int,
    apis: InitializedApis,
    retailer: str,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
) -> dict:
    adjust_flo_stock = True
    if flo > 0:
        adjust_flo_stock = False

    orderflow_test_data = prepare_orderflow_data(
        ims=apis.ims,
        distiller=apis.distiller,
        tsc=apis.tsc,
        retailer=retailer,
        picklist_non_weighted_qty=flo,
        osr_products_qty=osr,
        manual_non_weighted_qty=manual,
        manual_weighted_qty=manual_weighted,
        stage_by_data=stage_by_in_1_minutes_1_min_cutoff,
    )
    return {"order_flow_data": orderflow_test_data, "flo_stock": adjust_flo_stock}


@when(
    parsers.parse('order is created with type "{service_type}"'),
    target_fixture="orderid",
)
def create_order_service_type(
    apis: InitializedApis,
    retailer: str,
    service_type: str,
    products: dict,
) -> str:
    order_id = place_order(
        rint=apis.rint,
        retailer=retailer,
        products=products["order_flow_data"]["all_products"],
        store_id=products["order_flow_data"]["store_id"],
        spoke_id=products["order_flow_data"]["spoke_id"],
        stage_by_datetime=products["order_flow_data"]["stage_by_datetime"],
        service_window_start=products["order_flow_data"]["service_window_start"],
        route_id=products["order_flow_data"]["route_id"],
        ims=apis.ims_admin,
        oms=apis.oms,
        add_flo_stock=products["flo_stock"],
        ecom_service_type=service_type,
    )
    return order_id


@when(
    parsers.parse('order is created with zero stock and with type "{service_type}"'),
    target_fixture="orderid_zero_stock_products",
)
def create_order_with_zero_stock(
    apis: InitializedApis,
    retailer,
    service_type: str,
    products: dict,
    location_code_retailer: str,
) -> dict:
    products_list: list[Product] = products["order_flow_data"]["all_products"]
    for product in products_list:
        apis.ims.zero_stock_for_products_or_addresses([product.tom_id])
        tom_ids = [product.tom_id for product in products_list]
        product_stock = apis.ims.v2_snapshot([product.tom_id])
        pprint(product_stock)
    lineitems = products_to_lineitems(
        retailer, products["order_flow_data"]["all_products"]
    )
    order_id = apis.rint.create_customer_order(
        spoke_id=products["order_flow_data"]["spoke_id"],
        stage_by_datetime=products["order_flow_data"]["stage_by_datetime"],
        service_window_start=products["order_flow_data"]["service_window_start"],
        lineitems=lineitems,
        store_id=location_code_retailer,
        ecom_service_type=service_type,
    )
    return {"orderid": order_id, "product_zero_stock": tom_ids}


@when("order is consolidated and staged")
def order_consolidated_and_staged(
    apis: InitializedApis,
    staging_location: str,
    operator_user: AuthServiceUser,
    orderid: str,
) -> None:
    transition_order_to_picked(apis, orderid, operator_user)
    """Order consolidation"""
    consolidate_order(apis.pickerman_facade, orderid)
    wait_order_status_changed(orderid, "packed", apis.oms)
    """Order staging"""
    if apis.tsc.get_config_item_value(
        "STAGING_CONFIGURATION_ENABLED", return_format=TscReturnFormat.json
    ):
        stage_order(
            apis.pickerman_facade,
            apis.fft,
            orderid,
            staging_location,
        )
        wait_order_status_changed(orderid, "staged", apis.oms)


@then("order status matches ORDER_STATUS_AFTER_PICKING config in TSC")
def order_status_after_picking(
    apis: InitializedApis, retailer: str, orderid: str
) -> None:
    """Order status verification"""
    order_status_tsc = apis.tsc.get_config_item_value(
        "ORDER_STATUS_AFTER_PICKING", return_format=TscReturnFormat.json
    )
    wait_order_status_changed(orderid, order_status_tsc, apis.oms)
    order_status = get_order_status(orderid, apis.oms)

    if order_status == order_status_tsc:
        print(
            blue(
                f"Final status is {order_status} for order {orderid}, retailer: {retailer}"
            )
        )
    else:
        assert False, red(
            f"Final Status {order_status_tsc} not found (have {order_status}), hence Test Case Failed"
        )


@then(parsers.parse('order is in "{status}" status'))
def order_status(apis: InitializedApis, orderid: str, status: str) -> None:
    assert wait_order_status_changed(orderid, status, apis.oms)


@then("verify that decanting operation is successful")
def verify_decanting_success(decanting_result_data: dict) -> None:
    assert decanting_result_data["decanting_result"].success


@then(parsers.parse('decanting status is "{status}"'))
def verify_post_decanting_status(
    decanting: Decanting,
    location_code_gold,
    po_data: dict,
    decanting_result_data: dict,
    status: str,
) -> None:
    expected_final_status = status
    location_gold = int(location_code_gold)

    if expected_final_status == "in_progress":
        if "products" in po_data.keys():
            po1_update = wait_for_po_update_after_decanting(
                decanting_service=decanting,
                po_id=po_data["po1"].purchase_order_id,
                location_code_gold=location_gold,
            )

            po2_update = wait_for_po_update_after_decanting(
                decanting_service=decanting,
                po_id=po_data["po2"].purchase_order_id,
                location_code_gold=location_gold,
            )

            assert po1_update
            assert po1_update.status == "in_progress"
            assert po1_update.pending_product_count == 0

            assert po2_update
            assert po2_update.status == "in_progress"
            assert po2_update.pending_product_count == 0

        else:
            po_information_post_decanting = wait_for_po_product_decanted_quanity(
                decanting_service=decanting,
                po_id=po_data["po_id"],
                location_code_gold=location_gold,
                product_id=po_data["product_id"],
                qty=decanting_result_data["product_info"].qty_decanted + 1,
            )
            assert po_information_post_decanting
            assert po_information_post_decanting.status == expected_final_status
    else:
        decanting.close_purchase_order(po_data["po_id"])
        po_information_after_closing = wait_for_po_from_decanting(
            decanting_service=decanting,
            po_id=po_data["po_id"],
            location_code_gold=location_gold,
        )
        assert po_information_after_closing
        assert po_information_after_closing.status == expected_final_status


@given("purchase order is created", target_fixture="po_data")
def create_purchase_order(
    login_gcp_project, apis: InitializedApis, location_code_gold: str, retailer, cfg
) -> dict:
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
    credentials = login_gcp_project
    location_gold = int(location_code_gold)
    products: list[Product] = manual_products["all_products"]
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
    manual_product = decanting_response.products[0].product
    po_id = decanting_response.purchase_order

    return {"manual_product": manual_product, "po_id": po_id}


@given(parsers.parse("TOM location code {MFC_Type}"), target_fixture="location")
def create_sftp_po_mfc(location_code_tom: str, MFC_Type) -> str:
    MFC_Type = MFC_Type.strip('"')
    if location_code_tom != MFC_Type:
        pytest.skip(
            red(
                "Test might be run ONLY for WF0001 because wh_invoice_winter template includes "
                "data relevant to WF0001"
            )
        )
    return location_code_tom
