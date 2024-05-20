from datetime import datetime
from typing import Optional
from src.api.takeoff.ims import IMS
from src.config.config import Config

from src.utils.console_printing import done
from src.utils.totes import generate_target_tote
from src.api.takeoff.pickerman_facade import PickermanFacade
from src.api.takeoff.mobile import Mobile
from src.api.takeoff.ff_tracker import FFTracker


def generate_picking_decision_record(
    order_id: str,
    tom_id: str,
    amount: int,
    barcodes: list,
    address: str,
    totes: list,
    weight: list,
):
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    record = {
        "amount": amount,
        "picking_address": address,
        "item_id": tom_id,
        "created_time": now,
        "type": 0,
        "weights": weight,
        "origin_decision": None,
        "id": order_id + ":" + now,
        "barcodes": barcodes,
        "line_number": 0,
        "tote_ids": totes,
        "ws_number": "test",
        "lot_id": 0,
    }
    return record


def tma_assign_available_order_and_send_decisions(
    facade: PickermanFacade,
    mobile: Mobile,
    desired_order_id: str,
    user_id: Optional[str] = None,
    email: Optional[str] = None,
):
    while True:
        order = mobile.assign_fulfillment_task()
        order_id = order["order_id"]
        if order_id == desired_order_id or not order:
            break
        else:
            print(f"Got order '{order_id}' not matching desired: '{desired_order_id}'")
            mobile.clear_session(order["id"], re_enqueue=False)
    order_items = order["steps"]
    totes = [generate_target_tote()]
    decision_records = []
    weight = []
    for i in order_items:
        record = generate_picking_decision_record(
            order_id,
            i["product_id"],
            i["requested"],
            [i["product_id"]],  # not actual barcodes - here not neccesary
            i["address_id"],
            totes,
            weight,
        )
        decision_records.append(record)
    facade.post_manual_picking_item_decision(
        order_id, decision_records, user_id=user_id, email=email
    )
    print(done(f"Picking decisions for order {order_id} have been sent!"))
    return order["id"]


def process_unassigned_orders(
    facade: PickermanFacade, user_id: Optional[str] = None, email: Optional[str] = None
):
    print("\nProcessing unassigned orders (if any)...")
    order_id = assign_available_order_and_send_decisions(
        facade, user_id=user_id, email=email, no_wait=True
    )
    while order_id:
        order_id = assign_available_order_and_send_decisions(
            facade, user_id=user_id, email=email, no_wait=True
        )


def assign_available_order_and_send_decisions_all_available(
    facade: PickermanFacade,
    desired_order_id: str,
    user_id: Optional[str] = None,
    email: Optional[str] = None,
) -> str:
    """Just like assign_available_order_and_send_decisions but will run until the
    desired_order_id is processed"""
    order_processed = assign_available_order_and_send_decisions(
        facade, user_id=user_id, email=email
    )
    while order_processed != desired_order_id:
        order_processed = assign_available_order_and_send_decisions(
            facade, user_id=user_id, email=email
        )
    return order_processed


def assign_available_order_and_send_decisions(
    facade: PickermanFacade,
    user_id: Optional[str] = None,
    email: Optional[str] = None,
    no_wait: bool = False,
) -> str:
    if no_wait:
        order = facade.assign_no_wait()
    else:
        order = facade.assign()
    order_id = order["session_id"]
    order_items = order["session"]["items"]
    totes = [generate_target_tote()]
    decision_records = []
    weight = []
    for i in order_items:
        record = generate_picking_decision_record(
            order_id,
            i["body_id"],
            i["amount"],
            [i["body_id"]],  # not actual barcodes - here not neccesary
            i["picking_address"],
            totes,
            weight,
        )
        decision_records.append(record)
    facade.post_manual_picking_item_decision(
        order_id, decision_records, user_id=user_id, email=email
    )
    print(done(f"Picking decisions for order {order_id} have been sent!"))

    return order_id


def consolidate_order(facade: PickermanFacade, order_id: str):
    totes = facade.get_all_order_totes_from_ramp_state(order_id)
    facade.consolidate(order_id, totes)
    print(done(f"Order {order_id} has been consolidated!"))


def clear_dispatch_lane_order(ims: IMS, order_id: str):
    ims.clear_ramp(order_id)


def stage_order(
    facade: PickermanFacade,
    fft: FFTracker,
    order_id: str,
    staging_address: str,
):
    totes = fft.order_totes(order_id)["data"][0]["totes"]
    facade.stage(order_id, staging_address, totes)
    print(
        done(
            f"Totes {totes} for order {order_id} have been staged to {staging_address}!"
        )
    )


def tma_stage_order(
    mobile: Mobile, cfg: Config, fulfillment: str, totes: str, order_id: str
):
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    staging_address = mobile.get_staging_locations(fulfillment)["staging_locations"][0][
        "staging_location_code"
    ]
    mobile.post_register_staging_location(fulfillment, staging_address)
    action = {
        "actions": [
            {
                "email": cfg.user,
                "id": fulfillment,
                "mfc_id": cfg.location_code_tom,
                "type": "fulfillment.staging.taskStaged",
                "user_id": cfg.user_id,
                "order_id": order_id,
                "order_part_id": 0,
                "work_task_id": 0,
                "action": {
                    "type": "fulfillment.staging.taskStaged",
                    "addressId": staging_address,
                    "toteBarcodes": [totes],
                    "id": fulfillment,
                    "workTaskId": 0,
                    "orderId": order_id,
                    "orderPartId": 0,
                    "mfcId": cfg.location_code_tom,
                    "retailerId": cfg.retailer,
                    "appVersion": "1.10.21",
                    "deviceId": "takeoff-mobile",
                    "deviceTimestamp": now,
                    "email": cfg.user,
                    "environmentTypeId": cfg.env,
                    "userId": cfg.user_id,
                },
            },
            {
                "email": cfg.user,
                "id": fulfillment,
                "mfc_id": cfg.location_code_tom,
                "type": "fulfillment.staging.taskCompleted",
                "user_id": cfg.user_id,
                "order_id": order_id,
                "order_part_id": 0,
                "work_task_id": 0,
                "action": {
                    "type": "fulfillment.staging.taskCompleted",
                    "id": fulfillment,
                    "workTaskId": 0,
                    "orderId": order_id,
                    "orderPartId": 0,
                    "mfcId": cfg.location_code_tom,
                    "retailerId": cfg.retailer,
                    "appVersion": "1.10.21",
                    "deviceId": "takeoff-mobile",
                    "deviceTimestamp": now,
                    "email": cfg.user,
                    "environmentTypeId": cfg.env,
                    "userId": cfg.user_id,
                },
            },
        ]
    }
    mobile.post_fulfillmenttask(action)
