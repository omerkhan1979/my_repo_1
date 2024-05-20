from src.api.takeoff.ims import IMS
from src.utils.waiters import wait


@wait
def wait_for_item_adjustment_from_ims(ims: IMS, time_past, time_now, location_code_tom):
    try:
        return ims.adjustments(time_past, time_now, location_code_tom)["success"][0]
    except IndexError:
        return {}
