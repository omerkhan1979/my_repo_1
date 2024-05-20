from src.api.collections import InitializedApis
from pytest_bdd import scenarios, when

from src.api.takeoff.tsc import TscReturnFormat
from src.config.config import Config
from src.utils.helpers import wait_order_status_changed
from src.utils.order_picking import (
    tma_assign_available_order_and_send_decisions,
    tma_stage_order,
)

scenarios("../features/manual_fulfillment_tma.feature")


@when("order is consolidated and staged with tma")
def consolidate_stage_tma(
    cfg: Config,
    apis: InitializedApis,
    orderid: str,
):
    wait_order_status_changed(orderid, "queued", apis.oms)
    """assign order to the picker using fulfillment task assign endpoints"""
    fulfillment_id = tma_assign_available_order_and_send_decisions(
        apis.pickerman_facade, apis.mobile, orderid, user_id=cfg.user_id, email=cfg.user
    )
    print("fulfillment id", fulfillment_id)
    wait_order_status_changed(orderid, "picked", apis.oms)
    tote = apis.mobile.get_totes_fulfillment(fulfillment_id)

    apis.mobile.put_pack(fulfillment_id)

    wait_order_status_changed(orderid, "packed", apis.oms)

    """Order staging"""
    if apis.tsc.get_config_item_value(
        "STAGING_CONFIGURATION_ENABLED", return_format=TscReturnFormat.json
    ):
        tma_stage_order(apis.mobile, cfg, fulfillment_id, tote, orderid)
        wait_order_status_changed(orderid, "staged", apis.oms)
