# Here is recommended to place helper functions that is hard to be categorized yet.
# Project structure is about to change

from src.api.third_party.gcp import pubsub_puller
from src.config.config import Config
from src.config.constants import (
    ETL_ENTITIES_SUBSCRIPTION,
    INV_MOV_SUBSCRIPTION,
    CO_STATUS_HISTORY_SUBSCRIPTION,
)
from src.utils.waiters import wait
from src.api.takeoff.oms import OMS


def get_params_from_kwargs(param_names: list, **kwargs) -> dict:
    """Returns dict of params populated from kwargs by given param_names"""
    params = {}
    for param_name in param_names:
        # It is possible to pass different param names expected on kwargs and to populate body
        # e.g. given param_names = [ ["order_by", "order-by"] ] means, that
        # we will look kwargs for param = "order_by" but put this value into "order-by"

        if isinstance(param_name, list):
            param_name_kwarg = param_name[0]
            param_name_body = param_name[1]
        else:
            param_name_kwarg = param_name_body = param_name

        if kwargs.get(param_name_kwarg) is not None:
            params.update({param_name_body: kwargs.get(param_name_kwarg)})
    return params


def get_order_status(order_id, oms: OMS) -> str:
    return oms.get_order(order_id)["response"]["status"]


@wait
def wait_ramp_state_tote(order_id, ims) -> list:
    return ims.get_ramp_state_for_order(order_id)


@wait
def wait_order_status_changed(order_id, expected_status, oms: OMS) -> bool:
    # TODO: consider to rework to use more plain waiters structure
    result = oms.check_status_change(order_id, expected_status)
    if result:
        print(
            f"wait_order_status_changed succeeded with status of {expected_status} for {order_id}"
        )
    return result


@wait
def wait_for_decisions(fft, order_id):
    return len(fft.order_totes(order_id)["data"]) > 0


@wait
def wait_for_pubsub_message_after_inv_mov(cfg: Config):
    subscription_name = INV_MOV_SUBSCRIPTION[cfg.env]
    message = pubsub_puller(cfg.google_project_id, subscription_name)
    return message


@wait
def wait_for_pubsub_message_after_co_update(cfg: Config):
    subscription_name = CO_STATUS_HISTORY_SUBSCRIPTION[cfg.env]
    message = pubsub_puller(cfg.google_project_id, subscription_name)
    return message


@wait
def wait_for_pubsub_message_after_sftp_upload(cfg: Config):
    subscription_name = ETL_ENTITIES_SUBSCRIPTION[cfg.env]
    message = pubsub_puller(cfg.google_project_id, subscription_name, 3)
    return message


def remove_fields(d: list | dict, list_of_keys_to_remove: list) -> dict:
    """Returns a modified dict with the specified keys removed.

    Args:
        d (dict): original dictionary
        list_of_keys_to_remove (list): fields to remove

    Returns:
        dict: modified dict
    """
    if not isinstance(d, (dict, list)):
        return d
    if isinstance(d, list):
        return [v for v in (remove_fields(v, list_of_keys_to_remove) for v in d) if v]
    return {
        k: v
        for k, v in (
            (k, remove_fields(v, list_of_keys_to_remove)) for k, v in d.items()
        )
        if k not in list_of_keys_to_remove
    }
