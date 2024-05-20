from src.api.collections import InitializedApis
from pytest_bdd import scenarios, then, when, parsers
from time import sleep, time
from src.utils.addresses import get_addresses_v2
from src.utils.assortment import Product
from src.utils.ims import wait_for_item_adjustment_from_ims
from src.utils.console_printing import cyan
from google.cloud.logging_v2 import DESCENDING
from google.cloud import logging
from pprint import pprint
import datetime
from src.api.takeoff.ims import IMS

scenarios("../features/inventory_adjustment.feature")


@when(
    parsers.parse('product is adjusted with "{qty:d}" quantity'),
    target_fixture="adjustments_response",
)
def product_adjusted_qty(
    apis: InitializedApis, qty: int, products: dict, location_code_tom: str
):
    shelf_id = get_addresses_v2(ims=apis.ims_admin)[0]
    products_list: list[Product] = products["order_flow_data"]["all_products"]
    product_id = products_list[0].tom_id
    time_past = str(int(round(time() * 1000)))
    apis.ims.shelf_adjust(shelf_id, product_id, qty, "CC")
    adjustments_response = wait_for_item_adjustment_from_ims(
        apis.ims, time_past, None, location_code_tom
    )
    return adjustments_response


@then(parsers.parse('check the product "{qty:d}" is increased after adjustment'))
def product_with_adjusted_qty(qty: int, adjustments_response: int):
    assert adjustments_response["quantity"] == qty


@when(
    parsers.parse(
        'product is adjusted with "{qty:d}" with reason code "{reason_code}"'
    ),
    target_fixture="product_details",
)
def adjust_product_qty_with_reason_code(
    qty: int,
    products: dict,
    reason_code: str,
    admin_ims: IMS,
):
    shelf_id = get_addresses_v2(ims=admin_ims)[0]
    products_list: list[Product] = products["order_flow_data"]["all_products"]
    product_id = products_list[0].tom_id
    start_date = (datetime.datetime.utcnow() - datetime.timedelta(minutes=1)).strftime(
        "%Y-%m-%dT%H:%M:%S.%fZ"
    )
    admin_ims.shelf_adjust(shelf_id, product_id, 10, "CC")
    admin_ims.shelf_adjust(shelf_id, product_id, qty, reason_code)
    return {"time_past": start_date, "product_id": product_id}


@then(
    parsers.parse(
        'check the product "{qty:d}" is increased after adjustment with reason code'
    )
)
def adjusted_product_qty(
    apis: InitializedApis,
    product_details: dict,
    location_code_retailer: str,
    cfg,
    env,
):
    for _ in range(60):
        rint_inventory_movements = apis.rint.get_inventory_movements(
            location_code_retailer, product_details["time_past"]
        )
        if len(rint_inventory_movements["data"]) >= 1:
            break
        else:
            sleep(1)
    pprint(rint_inventory_movements)
    assert len(rint_inventory_movements["data"]) >= 1

    for movement in rint_inventory_movements["data"]:
        if (
            movement["takeoff-item-id"] == product_details["product_id"]
            and movement["quantity"] == 10
        ):
            assert movement["reason"] == "1"
        if (
            movement["takeoff-item-id"] == product_details["product_id"]
            and movement["quantity"] == 1
        ):
            assert movement["reason"] == "4_6"
        if (
            movement["takeoff-item-id"] == product_details["product_id"]
            and movement["quantity"] == 2
        ):
            assert movement["reason"] == "4_2"
        if (
            movement["takeoff-item-id"] == product_details["product_id"]
            and movement["quantity"] == 3
        ):
            assert movement["reason"] == "4_11"

    # Check inventory-adjustment after creation of adjustment with valid Winter reason in logs integration-api-op :
    logging_client = logging.Client(project=cfg.google_project_id)
    logger_name = "rint-core.http.client"
    message = "apimdev.wakefern.com/RASCOL/V1/LTOInventory_U_Row"
    pod = "integration-api-op-"
    product_upc = f"0{product_details['product_id'][:-1]}"

    # can we poll here or will that not work?
    sleep(150)  # Need wait at least 2 mins to get log after adjustment
    FILLTER = (
        f"resource.labels.pod_name:{pod} AND resource.labels.namespace_name:{env} "
        f"AND {logger_name} AND {message}"
    )

    for entry in logging_client.list_entries(filter_=FILLTER, order_by=DESCENDING):
        body_sent_to_wakefern = entry.payload.get("structured-data").get("body")
        if (
            body_sent_to_wakefern.get("UPC_NUM") == product_upc
            and body_sent_to_wakefern.get("ADJ_QTY") == "10"
        ):
            print("CC:", entry.payload["structured-data"]["body"])
            assert (
                body_sent_to_wakefern.get("INV_ADJ_TYP_CD") == "01"
                and body_sent_to_wakefern.get("REASON_CD") == ""
            )
        if (
            body_sent_to_wakefern.get("UPC_NUM") == product_upc
            and body_sent_to_wakefern.get("ADJ_QTY") == "-1"
        ):
            print("DA:", entry.payload["structured-data"]["body"])
            assert (
                body_sent_to_wakefern.get("INV_ADJ_TYP_CD") == "04"
                and body_sent_to_wakefern.get("REASON_CD") == "06"
            )
        if (
            body_sent_to_wakefern.get("UPC_NUM") == product_upc
            and body_sent_to_wakefern.get("ADJ_QTY") == "-2"
        ):
            print("EX:", entry.payload["structured-data"]["body"])
            assert (
                body_sent_to_wakefern.get("INV_ADJ_TYP_CD") == "04"
                and body_sent_to_wakefern.get("REASON_CD") == "02"
            )
        if (
            body_sent_to_wakefern.get("UPC_NUM") == product_upc
            and body_sent_to_wakefern.get("ADJ_QTY") == "-3"
        ):
            assert not (
                body_sent_to_wakefern.get("REASON_CD") == "11"
                and body_sent_to_wakefern.get("INV_ADJ_TYP_CD") == "04"
            ), (
                "Adjustment with reasons '04_11 TH' must not be sent to Wakefern."
                "Reach out to #domain-integration-and-configuration"
            )

    print(cyan("Test case test_winter_inventory_adjustment_reason_code is:"))
