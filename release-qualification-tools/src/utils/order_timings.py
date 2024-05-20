from dataclasses import dataclass
from datetime import datetime, timedelta
import pytz

from src.api.takeoff.tsc import TSC


@dataclass
class MFCRelativeFutureTime:
    timezone: str
    location_code_spoke: str
    location_code_retailer: str
    location_code_tom: str
    timestamp: str
    time_format: str
    now: datetime
    minutes_offset: int


def get_retailer_future_event(
    tsc: TSC,
    minutes: int = 1,
    time_format: str = "%Y-%m-%dT%H:%M:%S%z",
) -> MFCRelativeFutureTime:
    location_tom_code = tsc.get_spoke_id_for_mfc_tom_location()
    location_code_retailer = tsc.get_location_code("location-code-retailer")
    timezone, mfc = tsc.get_mfc_timezone(location_tom_code)
    print(f"Retailer time zone: {timezone}")
    now = datetime.now(pytz.timezone(timezone))
    future_event = (now + timedelta(minutes=minutes)).strftime(time_format)
    return MFCRelativeFutureTime(
        timezone=timezone,
        location_code_spoke=location_tom_code,
        time_format=time_format,
        now=now,
        timestamp=future_event,
        minutes_offset=minutes,
        location_code_retailer=location_code_retailer,
        location_code_tom=mfc,
    )


def get_cutoff_lite_and_spoke_for_order(tsc: TSC) -> dict:
    spoke = tsc.get_spoke_id_for_mfc_tom_location()

    """service_window_start will be a stage_by_datetime + 1 minute"""
    stage_by_datetime = (datetime.utcnow() + timedelta(days=1)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    service_window_start = (datetime.utcnow() + timedelta(days=1, minutes=1)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    result = {
        "service_window_start": service_window_start,
        "stage_by_datetime": stage_by_datetime,
        "spoke_id": spoke,
    }

    return result


def order_slot_for_tomorrow(tsc: TSC) -> dict:
    return get_cutoff_lite_and_spoke_for_order(tsc=tsc)
