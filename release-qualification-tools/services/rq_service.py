"""
you need to install fastapi and uvicorn library
To run this hit the command in pycharm terminal "uvicorn services.rq_service:app --reload --host=0.0.0.0 --port=8000"
a server will be started and then hit the url http://0.0.0.0:8000/docs in browser and start using like swagger
to stop the server click the terminal and then press Ctrl + C
"""

import uvicorn
import time
from exrex import getone
from scripts.steps.orderflow.setup import prepare_orderflow_data
from src.api.takeoff.ops_api import OpsApi
from src.config.constants import (
    MANUAL_SLEEPING_AREAS,
    MANUALLY_ENQUEUE_RETAILERS,
)
from src.utils.addresses import get_addresses_v2
from src.utils.barcode import weighted_barcode
from src.utils.helpers import wait_ramp_state_tote, wait_order_status_changed
from src.utils.place_order import place_order_for_rq_service
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from src.api.takeoff.distiller import Distiller
from src.api.takeoff.ims import IMS
from src.api.takeoff.oms import OMS
from src.api.takeoff.tsc import TSC
from src.api.takeoff.rint import RInt
from src.api.takeoff.mobile import Mobile
from src.config.config import get_config_fastapi, Config
from src.utils.assortment import (
    get_products_for_possible_areas,
    find_products_by_criteria,
)
from src.utils.ims import wait_for_item_adjustment_from_ims
from src.utils.assortment import Product
from src.utils.purchase_order import prepare_products_for_po
from src.utils.totes import generate_target_tote

app = FastAPI()


def takeoff_schema():
    openapi_schema = get_openapi(
        title="TakeOff RQ as service APIs",
        version="1.0",
        description="RQ as service for different channel",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = takeoff_schema


@app.get("/product-search")
async def product_search(retailer, env, location, ambient: int):
    cfg = Config(*get_config_fastapi(retailer, env, location))
    distiller = Distiller(cfg)
    products = prepare_products_for_po(
        distiller=distiller,
        retailer=retailer,
        location_code_retailer=location,
        ambient_osr_count=ambient,
        chilled_osr_count=0,
        req_exp_date_osr_count=False,
        chemical_osr_count=0,
        manual_count=0,
    )
    return products["ambient_osr_products"]


@app.get("/get-order-status", summary="Find status of the order")
async def get_order_status(retailer, env, location, order_id):
    cfg = Config(*get_config_fastapi(retailer, env, location))
    rint = RInt(cfg)

    response_from_get_order_rint = rint.get_customer_order_v4(location, order_id)
    order_status = response_from_get_order_rint["data"]["mfc-status"]
    return order_status


@app.get("/inventory-adjustments", summary="Inventory Adjustment")
async def inventory_adjustments(retailer="abs", env="qai", location="0068"):
    cfg = Config(*get_config_fastapi(retailer, env, location))
    ims = IMS(cfg)
    products: list[Product] = get_products_for_possible_areas(
        distiller=Distiller(cfg),
        retailer=retailer,
        possible_areas=["K"],
        required_count=1,
        is_weighted_options=[False],
    )

    time_past = str(int(round(time() * 1000)))

    ims.shelf_adjust("01K", products[0].tom_id, 10, "IB")

    adjustments_response = wait_for_item_adjustment_from_ims(
        ims, time_past, None, location
    )
    return adjustments_response


@app.get(
    "/create-order-sleeping-areas",
    summary="Generate order from different sleeping areas",
)
async def create_order_sleeping_areas(
    retailer, env, location, osr_products_types: int = 0, manual_products_types: int = 0
):
    cfg = Config(*get_config_fastapi(retailer, env, location))
    distiller = Distiller(cfg)
    ims = IMS(cfg)
    oms = OMS(cfg)
    rint = RInt(cfg)
    tsc = TSC(cfg)
    ops_api = OpsApi(cfg)

    ops_api.clear_manual_picking_q()

    test_data = prepare_orderflow_data(
        ims=ims,
        distiller=distiller,
        tsc=tsc,
        retailer=retailer,
        osr_products_qty=osr_products_types,
        manual_non_weighted_qty=manual_products_types,
    )

    products = test_data["all_products"]

    service_window_start = test_data["service_window_start"]

    order_id = place_order_for_rq_service(
        rint=rint,
        retailer=retailer,
        products=test_data["all_products"],
        order_id=getone("rqt[0-9]{13}"),
        store_id=test_data["store_id"],
        spoke_id=test_data["spoke_id"],
        stage_by_datetime=service_window_start,
        service_window_start=service_window_start,
        print_body=False,
        weight=None,
    )
    wait_order_status_changed(order_id, "queued", oms)
    response_from_get_order_rint = rint.get_customer_order_v4(location, order_id)
    order_id = response_from_get_order_rint["data"]["ecom-order-id"]
    totes = {"totes_for_manual_picking": [generate_target_tote()]}
    totes_from_ramp = {"totes_from_ramp": wait_ramp_state_tote(order_id, ims)}
    stage_location = {"stage_location": test_data["default_staging_location"]}
    return order_id, products, totes, totes_from_ramp, stage_location


@app.get(
    "/create-order-with-temp-zones",
    summary="Generate order with specifying temperature zones",
)
async def create_order_with_temp_zones(
    retailer,
    env,
    location,
    ambient_products_types: int = 0,
    chilled_products_types: int = 0,
    frozen_products_types: int = 0,
):
    cfg = Config(*get_config_fastapi(retailer, env, location))
    distiller = Distiller(cfg)
    ims = IMS(cfg)
    oms = OMS(cfg)
    rint = RInt(cfg)
    tsc = TSC(cfg)
    ops_api = OpsApi(cfg)

    ops_api.clear_manual_picking_q()

    location_code_retailer = tsc.get_location_code("location-code-retailer")

    test_data = prepare_orderflow_data(
        ims=ims,
        distiller=distiller,
        tsc=tsc,
        retailer=retailer,
        osr_products_qty=0,
    )

    all_products = []
    for p in range(ambient_products_types):
        ambient_product = find_products_by_criteria(
            distiller=distiller,
            location_code_retailer=location_code_retailer,
            retailer=retailer,
            required_count=1,
            temp_zones=["ambient"],
            sleeping_areas=MANUAL_SLEEPING_AREAS,
        )
        ambient_manual_address = get_addresses_v2(ims=ims)[0]
        ims.shelf_adjust(ambient_manual_address, ambient_product[0].tom_id, 10, "IB")
        all_products.append(ambient_product)

    for p in range(chilled_products_types):
        while True:
            chilled_product = find_products_by_criteria(
                distiller=distiller,
                location_code_retailer=location_code_retailer,
                retailer=retailer,
                required_count=1,
                temp_zones=["chilled"],
                sleeping_areas=MANUAL_SLEEPING_AREAS,
            )
            temp_of_product = chilled_product[0].temp_zone
            if temp_of_product == "chilled":
                break
        chilled_manual_adress = get_addresses_v2(ims=ims)[0]
        ims.shelf_adjust(chilled_manual_adress, chilled_product[0].tom_id, 10, "IB")
        all_products.append(chilled_product)

    for p in range(frozen_products_types):
        frozen_product = find_products_by_criteria(
            distiller=distiller,
            location_code_retailer=location_code_retailer,
            retailer=retailer,
            required_count=1,
            temp_zones=["frozen"],
            sleeping_areas=MANUAL_SLEEPING_AREAS,
        )
        frozen_manual_adress = get_addresses_v2(ims=ims)[0]
        ims.shelf_adjust(frozen_manual_adress, frozen_product[0].tom_id, 10, "IB")
        all_products.append(frozen_product)

    prods = []
    for products in all_products:
        prods.append(products[0])

    service_window_start = test_data["service_window_start"]

    order_id = place_order_for_rq_service(
        rint=rint,
        retailer=retailer,
        products=prods,
        order_id=getone("rqt[0-9]{13}"),
        store_id=test_data["store_id"],
        spoke_id=test_data["spoke_id"],
        stage_by_datetime=service_window_start,
        service_window_start=service_window_start,
        print_body=False,
        weight=None,
    )
    wait_order_status_changed(order_id, "queued", oms)
    order = {"order_id": order_id}
    products = {"Products from different temperature zones": prods}
    return order, products


@app.get(
    "/create-order-with-weighted-items",
    summary="Create an order with different weight types: "
    "within_expected_range, overweight,"
    "overweight_maf, underweight",
)
async def create_order_weighted_items(retailer, env, location, weight_type):
    cfg = Config(*get_config_fastapi(retailer, env, location))
    distiller = Distiller(cfg)
    ims = IMS(cfg)
    oms = OMS(cfg)
    rint = RInt(cfg)
    tsc = TSC(cfg)
    ops_api = OpsApi(cfg)
    ops_api.clear_manual_picking_q()
    test_data = prepare_orderflow_data(
        ims=ims,
        distiller=distiller,
        tsc=tsc,
        retailer=retailer,
        manual_weighted_qty=1,
    )

    products = test_data["all_products"][0]
    product_id = products.tom_id
    product = [product_id]
    product_data = {}
    average_weight = distiller.get_products_by_tom_ids(product)[0]["retail-item"][
        "weight"
    ]["weight"]
    zero_barcode = distiller.get_products_by_tom_ids(product)[0]["barcodes"][-1]
    match weight_type:
        case "within_expected_range":
            weight = average_weight
            barcode_for_exact_weight = weighted_barcode(zero_barcode, average_weight)
            product_data = {
                "tom_id": products.tom_id,
                "ecom_id": products.ecom_id,
                "average_weight": average_weight,
                "real_weight": weight,
                "barcode_for_exact_weight": barcode_for_exact_weight,
            }

        case "overweight":
            weight = average_weight * 1.3
            barcode_for_exact_weight = weighted_barcode(zero_barcode, weight)
            product_data = {
                "tom_id": products.tom_id,
                "ecom_id": products.ecom_id,
                "average_weight": average_weight,
                "real_weight": weight,
                "barcode_for_out_expected_range": barcode_for_exact_weight,
            }

        case "overweight_maf":
            weight = average_weight * 1.3
            barcode_for_exact_weight = weighted_barcode(zero_barcode, weight)
            product_data = {
                "tom_id": products.tom_id,
                "ecom_id": products.ecom_id,
                "average_weight": average_weight,
                "real_weight": weight,
                "barcode_for_overweight": barcode_for_exact_weight,
            }

        case "underweight":
            weight = average_weight * 0.7
            barcode_for_exact_weight = weighted_barcode(zero_barcode, weight)
            product_data = {
                "tom_id": products.tom_id,
                "ecom_id": products.ecom_id,
                "average_weight": average_weight,
                "real_weight": weight,
                "barcode_for_underweight": barcode_for_exact_weight,
            }

    service_window_start = test_data["service_window_start"]

    order_id = place_order_for_rq_service(
        rint=rint,
        retailer=retailer,
        products=test_data["all_products"],
        order_id=getone("rqt[0-9]{13}"),
        store_id=test_data["store_id"],
        spoke_id=test_data["spoke_id"],
        stage_by_datetime=service_window_start,
        service_window_start=service_window_start,
        print_body=False,
        weight=average_weight,
    )
    if cfg.retailer in MANUALLY_ENQUEUE_RETAILERS:
        oms.start_picking(order_id)
    wait_order_status_changed(order_id, "new" or "queued", oms)

    order_identification = {"order_id": order_id}
    totes = {"totes_for_manual_picking": [generate_target_tote()]}
    stage_location = {"stage_location": test_data["default_staging_location"]}

    return order_identification, product_data, totes, stage_location


@app.get("/get-truckload-orders", summary="Find the order for truck load")
async def get_truckload_orders(retailer, location, env, route_id, order_status):
    map = Mobile()
    truck_load = map.truckload_orders(retailer, location, env, route_id, order_status)
    return truck_load


@app.get("/clear-order-picking-session", summary="Clear active picking session order")
async def clear_picking_session(retailer, location, env, token):
    mobile = Mobile()

    fulfillment_task_id = mobile.assign_fulfillment_task(
        retailer, location, env, token
    )["id"]
    mobile.clear_session(retailer, location, env, fulfillment_task_id, token)
    success_message = "Your order picking session was successfully cleared"
    return success_message


@app.get("/get-tote-details", summary="Get tote detailsr")
async def get_tote_details(retailer, location, env, order_id):
    cfg = Config(*get_config_fastapi(retailer, env, location))
    oms = OMS(cfg)
    tote_details = oms.get_order(order_id)
    return tote_details


# UVicron guicron will be used when moving to production currently we are still building the endpoints
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
