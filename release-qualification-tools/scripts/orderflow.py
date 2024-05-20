from datetime import datetime, timedelta
from time import sleep

from scripts.steps.orderflow.handling_actions import (
    handle_picklist,
    handle_manual_picking,
    handle_consolidation,
    handle_staging,
    handle_truck_load,
)
from scripts.steps.orderflow.setup import prepare_orderflow_data
from scripts.steps.orderflow.user_interaction import (
    verify_products_ids,
    input_product_counts,
    ask_if_user_needs_truck_load,
    ask_if_user_has_mobile_app,
)
from src.api.takeoff.bifrost import Bifrost
from src.api.takeoff.distiller import Distiller
from src.api.takeoff.ff_tracker import FFTracker
from src.api.takeoff.ims import IMS
from src.api.takeoff.isps import ISPS
from src.api.takeoff.oms import OMS
from src.api.takeoff.ops_api import OpsApi
from src.api.takeoff.pickerman_facade import PickermanFacade
from src.api.takeoff.rint import RInt
from src.api.takeoff.osr_replicator import OSRR
from src.api.takeoff.tsc import TSC
from src.config.config import get_config, Config
from src.config.constants import (
    MANUALLY_ENQUEUE_RETAILERS,
    RETAILERS_WITHOUT_STAGING,
)
from src.utils.console_printing import (
    blue,
    red,
    done,
    waiting,
    link,
    bold,
    green,
)
from src.utils.order_picking import (
    assign_available_order_and_send_decisions,
    clear_dispatch_lane_order,
    consolidate_order,
    stage_order,
)
from src.utils.order_status import check_status_change_interactively

from src.utils.place_order import place_order

*config, day, hour = get_config()
cfg = Config(*config)
distiller = Distiller(cfg)
facade = PickermanFacade(cfg)
fft = FFTracker(cfg)
ims = IMS(cfg)
isps = ISPS(cfg)
oms = OMS(cfg)
ops = OpsApi(cfg)
rint = RInt(cfg)
tsc = TSC(cfg)
osr_replicator = OSRR(cfg)
bifrost = Bifrost(cfg, tsc.get_location_code("location-code-gold"))

user_products = None

if cfg.user_tom_ids:
    # If custom tom_ids were provided by user in argv:
    user_products = verify_products_ids(
        distiller=distiller, retailer=cfg.retailer, tom_ids=cfg.user_tom_ids
    )
    test_data = prepare_orderflow_data(
        ims=ims,
        distiller=distiller,
        tsc=tsc,
        retailer=cfg.retailer,
        user_products=user_products,
    )
else:
    (
        picklist_non_weighted_qty,
        picklist_weighted_qty,
        picklist_total_qty,
        osr_products_qty,
        manual_non_weighted_qty,
        manual_weighted_qty,
        manual_total_qty,
    ) = input_product_counts(retailer=cfg.retailer)
    test_data = prepare_orderflow_data(
        ims=ims,
        distiller=distiller,
        tsc=tsc,
        retailer=cfg.retailer,
        picklist_non_weighted_qty=picklist_non_weighted_qty,
        picklist_weighted_qty=picklist_weighted_qty,
        osr_products_qty=osr_products_qty,
        manual_non_weighted_qty=manual_non_weighted_qty,
        manual_weighted_qty=manual_weighted_qty,
    )

# need to clear queue, so that in manual picking, the order we will place is the 1st
ops.clear_manual_picking_q()

spoke_id, include_truck_load = ask_if_user_needs_truck_load(
    cfg.retailer, test_data["spoke_id"], test_data["store_id"]
)

express_order = (
    tsc.express_orders_enabled()
    and input(blue("Do you want order to be EXPRESS? (y/n): ")) == "y"
)
if express_order:
    """express orders should be enabled on ENV. Check tsc.express_orders_enabled for more information"""
    ecom_service_type = "EXPRESS"
    stage_by_datetime = (datetime.utcnow() + timedelta(hours=3)).strftime(
        "%Y-%m-%dT%H:%M:00Z"
    )
    service_window_start = (datetime.utcnow() + timedelta(hours=3, minutes=1)).strftime(
        "%Y-%m-%dT%H:%M:00Z"
    )
else:
    ecom_service_type = "DELIVERY"
    stage_by_datetime = test_data["stage_by_datetime"]
    service_window_start = test_data["service_window_start"]

if len(test_data["all_products"]) > 0:
    order_id = place_order(
        rint=rint,
        retailer=cfg.retailer,
        products=test_data["all_products"],
        ims=ims,
        oms=oms,
        store_id=test_data["store_id"],
        spoke_id=spoke_id,
        stage_by_datetime=stage_by_datetime,
        service_window_start=service_window_start,
        ecom_service_type=ecom_service_type,
    )
    assert order_id
else:
    quit(red("There are no products for this location. Order will not be placed!"))

print(done(f"Order placed! Order ID is {order_id}"))
print(waiting("Waiting 10 seconds..."))
sleep(10)

cutoff_time = oms.get_order(order_id)["response"]["cutoff-datetime"]

if test_data.get("picklist_products") and not express_order:
    handle_picklist(
        oms=oms,
        ims=ims,
        isps=isps,
        cutoff=cutoff_time,
        picklist_products=test_data["picklist_products"],
        addresses_and_barcodes=test_data["dynamic_addresses_and_picklist_barcodes"],
        in_store_picking_url=cfg.in_store_picking_url,
    )

order_status = oms.get_order(order_id)["response"]["status"]
if order_status == "draft" and not express_order:
    oms.split_order(order_id)

print(waiting("Making sure order is split..."))
sleep(8)

print(blue("Order should be accessible in TOM UI!"))
print(link(oms.order_search_page.format(cfg.url, order_id)))

print(
    green(
        "You can check OSR Replicator service and perform additional actions with OSR items via the link below:"
    )
)
print(link(osr_replicator.get_osrr_url(cfg, "picking")))

if cfg.retailer in MANUALLY_ENQUEUE_RETAILERS:
    input(blue("Please enqueue order. Press Enter once done: "))

if test_data.get("osr_products"):
    if bifrost.get_health_pass():
        check_status_change_interactively(oms, order_id, "queued")
        print(bold("OSR emulator should send picking decisions for OSR items. "))
        input(blue("Press Enter once you see decisions in TOM UI: "))
    else:
        quit(red("Bifrost is not healthy!"))

use_mobile_app = ask_if_user_has_mobile_app()

if use_mobile_app:
    input(
        blue(
            "Order should drop to Pickerman! ('MFC Picks'). Press Enter once you have taken it: "
        )
    )
    check_status_change_interactively(oms, order_id, "queued")

reservations_in_manual_zone = list(
    filter(
        lambda i: i["picking-address"] != "01K",
        ims.get_reserved_picking_path_for_order(order_id),
    )
)

if use_mobile_app and reservations_in_manual_zone:
    handle_manual_picking(
        products=test_data["all_products"], reservations=reservations_in_manual_zone
    )
elif not use_mobile_app:
    input(
        blue(
            "Press Enter to send picking decisions for order (pick order manual part)"
            "\n(Status will change to 'Picked'): "
        )
    )
    assign_available_order_and_send_decisions(facade=facade)


input(blue("Press Enter to check if order status changed to 'Picked': "))
check_status_change_interactively(oms, order_id, "picked")

input(blue("\nPress Enter once you reached consolidation screen: "))
if test_data.get("all_products"):
    if use_mobile_app:
        if not test_data.get("osr_products"):
            input(blue("\nYou order is consolidated! Tap NEXT button in the Pickerman"))
        else:
            handle_consolidation(ims=ims, order_id=order_id)
    else:
        input(
            blue(
                "Press Enter to consolidate order (pick OSR totes from ramp)"
                "\n(Status will change to 'Packed'): "
            )
        )
        consolidate_order(facade=facade, order_id=order_id)

input(blue("Press Enter to check if order status changed to 'Packed': "))
check_status_change_interactively(oms, order_id, "packed")

if cfg.retailer not in RETAILERS_WITHOUT_STAGING:
    if use_mobile_app:
        handle_staging(
            fftracker=fft,
            oms=oms,
            order_id=order_id,
            staging_location=test_data["staging_location"],
        )
    else:
        input(
            blue(
                "Press Enter to stage order (prepare it to leave MFC)"
                "\n(Status will change to 'Staged'):"
            )
        )
        stage_order(
            facade=facade,
            fft=fft,
            order_id=order_id,
            staging_address=test_data["staging_location"],
        )

sleep(5)
order_status = oms.get_order(order_id)["response"]["status"]
print(blue(f"\nFinal status is {order_status}!"))

if include_truck_load:
    route_id = oms.get_order(order_id)["response"]["route-number"]
    handle_truck_load(
        facade=facade,
        oms=oms,
        retailer=cfg.retailer,
        order_id=order_id,
        order_status=order_status,
        route_id=route_id,
        spoke_id=spoke_id,
    )

# Clear out dispatch lane if needed
clear_dispatch_lane_order(ims, order_id)
