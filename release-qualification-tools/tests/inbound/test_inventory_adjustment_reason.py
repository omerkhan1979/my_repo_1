import datetime
from pprint import pprint
from time import sleep
from pytest import mark

from google.cloud.logging_v2 import DESCENDING
from google.cloud import logging
from scripts.steps.orderflow.setup import prepare_orderflow_data
from src.utils.addresses import get_addresses_v2
from src.utils.assortment import Product
from src.utils.console_printing import cyan, waiting
from src.api.collections import InitializedApis

""""Removed test from RQ as this functionality is supported on staging environments (DEV, QAI, UAT),
    NOT for PROD for the time being.  Leave test for perhaps future reusing"""


@mark.rq
@mark.inbound
@mark.inventory_adjustment_reason_code
@mark.retailers("winter")
@mark.testrail("294010")
def test_winter_inventory_adjustment_reason_code(
    cfg,
    retailer,
    env,
    location_code_retailer,
    apis: InitializedApis,
):
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

    start_date = (datetime.datetime.utcnow() - datetime.timedelta(minutes=1)).strftime(
        "%Y-%m-%dT%H:%M:%S.%fZ"
    )
    apis.ims_admin.shelf_adjust(shelf_id, product_id, 10, "CC")
    apis.ims_admin.shelf_adjust(shelf_id, product_id, -1, "DA")
    apis.ims_admin.shelf_adjust(shelf_id, product_id, -2, "EX")
    apis.ims_admin.shelf_adjust(shelf_id, product_id, -3, "TH")
    for _ in range(60):
        rint_inventory_movements = apis.rint.get_inventory_movements(
            location_code_retailer, start_date
        )
        if len(rint_inventory_movements["data"]) >= 4:
            break
        else:
            sleep(1)
    pprint(rint_inventory_movements)
    assert len(rint_inventory_movements["data"]) >= 4

    # just to be safe, be sure to check all kinda are actually seen
    seen = set()
    for movement in rint_inventory_movements["data"]:
        if movement["takeoff-item-id"] == product_id and movement["quantity"] == 10:
            seen.add(movement["reason"])
            assert movement["reason"] == "1"
        if movement["takeoff-item-id"] == product_id and movement["quantity"] == 1:
            seen.add(movement["reason"])
            assert movement["reason"] == "4_6"
        if movement["takeoff-item-id"] == product_id and movement["quantity"] == 2:
            seen.add(movement["reason"])
            assert movement["reason"] == "4_2"
        if movement["takeoff-item-id"] == product_id and movement["quantity"] == 3:
            seen.add(movement["reason"])
            assert movement["reason"] == "4_11"
    assert set(["1", "4_6", "4_2", "4_11"]) == seen
    # Check inventory-adjustment after creation of adjustment with valid Winter reason in logs integration-api-op :
    logging_client = logging.Client(project=cfg.google_project_id)
    logger_name = "rint-core.http.client"
    message = "apimdev.wakefern.com/RASCOL/V1/LTOInventory_U_Row"
    pod = "integration-api-op-"
    product_upc = f"0{product_id[:-1]}"

    print(waiting("this next part will take a few minutes..."))
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
