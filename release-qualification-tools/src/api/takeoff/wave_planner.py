"""
Class to interact with Wave Planner API.
This is a specification for Wave Planner service:
https://wave-planner.nonprod.outbound.tom.takeoff.com/
"""

from dataclasses import asdict, dataclass, field
import json
from datetime import datetime, timedelta
import pytz
from dataclasses_json import DataClassJsonMixin, dataclass_json
import requests
from typing import Optional, TypeAlias

from src.api.third_party.gcp import get_bearer
from src.api.takeoff.auth_service import AuthService

from src.config.config import Config
from src.config.constants import OUTBOUND_DOMAIN, ODE_RETAILER, BASE_DOMAIN
from src.utils.http import handle_response
from src.utils.user import get_or_create_user_token

UserId: TypeAlias = str
CutoffTime: TypeAlias = str
FromTime: TypeAlias = str
ToTime: TypeAlias = str


@dataclass
class ScheduleResponse(DataClassJsonMixin):
    """Schedule Response"""

    schedule_time: str
    id: str
    schedule_type: str


@dataclass
class WaveResponse(DataClassJsonMixin):
    """Wave Response"""

    cutoff_time: CutoffTime
    from_time: FromTime
    to_time: ToTime
    schedules: list[ScheduleResponse]
    id: str


@dataclass
class GetWavePlanSuccessResponse(DataClassJsonMixin):
    """Class for Get Wave Plan Success Response"""

    retailer_id: str
    mfc_id: str
    timezone: str
    created_by: UserId
    # below seem to be an optional fields
    created_time: Optional[str]
    id: str
    waves: list[WaveResponse] = field(default_factory=list)


@dataclass_json
@dataclass
class CreateWaveRequest:
    """Create Wave Request"""

    cutoff_time: CutoffTime
    from_time: FromTime
    to_time: ToTime
    prelim_picklist_schedule_time: str
    delta_picklist_schedule_time: str


@dataclass_json
@dataclass
class CreateWavePlanRequestBody:
    """Create Wave Plan Request Body"""

    waves: list[CreateWaveRequest] = field(default_factory=list)


@dataclass_json
@dataclass
class CreateWavePlanSuccessResponse(CreateWavePlanRequestBody):
    """Create Wave Plan Success Response"""

    id: str = None
    retailer_id: str = None
    mfc_id: str = None
    created_by: UserId = None
    created_at: str = None


@dataclass_json
@dataclass
class GenerateTriggersSuccessResponse:
    """Generate Triggers Success Response"""

    generated_triggers: str


@dataclass_json
@dataclass
class BaseTriggerResponse:
    """Fire Trigger Response"""

    retailer_id: str
    mfc_id: str
    schedule_id: str
    cutoff_datetime: str
    trigger_at: str
    fired_at: str
    created_at: str = None


@dataclass_json
@dataclass
class FireTriggerResponse(BaseTriggerResponse):
    """Fire Trigger Response"""

    schedule_type: str = None


@dataclass_json
@dataclass
class TriggerResponse(BaseTriggerResponse):
    """Trigger Response"""

    wave_id: str = None
    wave_plan_id: str = None
    cutoff_time: str = None


@dataclass_json
@dataclass
class PlanSaveError:
    """Plan Save Error"""

    cutoff_time: str
    error_fields: list
    error: str


@dataclass_json
@dataclass
class CreateWavePlanNonSuccessResponse:
    """Create Wave Plan Non Success Response"""

    errors: list[PlanSaveError] = field(default_factory=list)


@dataclass_json
@dataclass
class FireTriggersSuccessResponse:
    """Fire Triggers Success Response"""

    triggers: list[FireTriggerResponse] = field(default_factory=list)


@dataclass_json
@dataclass
class GetTriggersSuccessResponse:
    """Fire Triggers Success Response"""

    triggers: list[TriggerResponse] = field(default_factory=list)


class WavePlanner:
    # wave plan for site
    retailer_mfc_waveplan_endpoint = "/v1/retailers/{}/mfcs/{}/wavePlan"
    triggers_endpoint = "/v1/triggers"
    generate_trigger_endpoint = f"{triggers_endpoint}:generate"
    fire_trigger_endpoint = f"{triggers_endpoint}:fire"
    base_url: str

    def __init__(self, my_config: Config, url_builder=None):
        self.my_config = my_config
        if url_builder:
            self.base_url = url_builder
        elif my_config.env == "ode":
            self.base_url = f"https://wave-planner.ode.outbound.{BASE_DOMAIN}"
        elif my_config.env == "uat":
            self.base_url = f"https://wave-planner.uat.{OUTBOUND_DOMAIN}"
        else:
            self.base_url = f"https://wave-planner.nonprod.{OUTBOUND_DOMAIN}"

        # a hack to work around issues of deleted users
        self.wave_planner_user_token = self.get_or_create_wave_planner_user_token()
        # TODO : Need to implement changes in base_api_takeoff file to resolve the default_headers and remove self.default_headers from here
        self.default_headers = {
            "X-Token": self.wave_planner_user_token,
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": get_bearer(my_config.env),
        }
        self.default_headers["X-Env-Type"] = my_config.env
        self.retailer = ODE_RETAILER
        self.mfc_id = my_config.location_code_tom

    def __repr__(self):
        return f'WavePlanner("{self.mfc_id}","{self.base_url}","{self.retailer}","{self.default_headers}")'

    def get_or_create_wave_planner_user_token(self) -> str:
        """A helper function to work around OUTBOUND-6685 - if
        we delete the user that created a waveplan, the system does not work well
        This method checks for the user and if it exists it uses it, but if
        not it will create `wave_plan_test_user`. The id token is returned"""
        auth_service = AuthService(self.my_config)
        return get_or_create_user_token(
            auth_service,
            self.my_config.retailer,
            self.my_config.env,
            self.my_config.location_code_tom,
            "wave_planner_test_user@takeoff.com",
            role="mfc-manager",
        )

    def get_wave_plan(
        self, retailer_id: str = None, mfc_id: str = None
    ) -> GetWavePlanSuccessResponse:
        """Retrieves waves and schedules for site
        Args:
            retailer_id (str): Id of retailer
            mfc_id (str): id of mfc

        Returns:
            GetWavePlanSuccessResponse: contents of a success wave creation
        """
        retailer_id = ODE_RETAILER or retailer_id or self.retailer

        if not mfc_id:
            mfc_id = self.mfc_id

        url = self.base_url + self.retailer_mfc_waveplan_endpoint.format(
            retailer_id, mfc_id
        )

        response = requests.get(
            url=url,
            headers=self.default_headers,
        )
        if response.status_code == 200 and not response.text:
            return GetWavePlanSuccessResponse.from_json(
                json.dumps(handle_response(response, 200))
            )
        return None

    def post_wave_plan(
        self, retailer_id: str, mfc_id: str, waves: CreateWavePlanRequestBody
    ) -> CreateWavePlanSuccessResponse:
        """Creates a wave plan for site
        Args:
            retailer_id (str): Id of retailer
            mfc_id (str): id of mfc

        Returns:
            GetWavePlanSuccessResponse: contents of a success wave creation
        """
        retailer_id = ODE_RETAILER or retailer_id or self.retailer

        if not mfc_id:
            mfc_id = self.mfc_id

        url = self.base_url + self.retailer_mfc_waveplan_endpoint.format(
            retailer_id, mfc_id
        )
        response = requests.post(
            url=url, headers=self.default_headers, json=asdict(waves)
        )
        return handle_response(response, 200, 201)

    def post_generate_trigger(self) -> GenerateTriggersSuccessResponse:
        """Creates a trigger

        Returns:
            GenerateTriggersSuccessResponse: contents of a generate trigger call
        """
        url = self.base_url + self.generate_trigger_endpoint

        response = requests.post(
            url=url,
            headers=self.default_headers,
        )
        return handle_response(response, 200, 201)

    def post_fire_trigger(self) -> FireTriggersSuccessResponse:
        """Creates a fire trigger

        Returns:
            FireTriggersSuccessResponse: contents of a fire trigger call
        """
        url = self.base_url + self.fire_trigger_endpoint

        response = requests.post(
            url=url,
            headers=self.default_headers,
        )
        return handle_response(response, 200, 201)

    def get_triggers(self, retailer_id: str, mfc_id: str) -> GetTriggersSuccessResponse:
        url = self.base_url + self.triggers_endpoint
        response = requests.get(
            url=url,
            headers=self.default_headers,
            params={
                "mfcId": mfc_id or self.mfc_id,
                "retailerId": ODE_RETAILER or retailer_id or self.retailer,
            },
        )
        return handle_response(response, 200)

    def create_test_wave_plan(
        self,
        retailer_id: str,
        mfc_id: str,
        timezone: str,  # time zone of given mfc_id
        first_cutoff_minutes: int = 1,
        next_cutoff_minutes: int = 60 * 2,
    ) -> CreateWavePlanSuccessResponse:
        """Helper for creating a wave plan that looks like follows:

        Cutoff                                 | From Time   | To Time
        -------------------------------------------------------------------
        Now + first_cutoff_minutes             | Cutoff + 1Hr   | Cutoff + 12 Hr
        Now + 2 hours + first_cutoff_minutes   | Cutoff + 12 Hr | Cutoff + 59 Min
        """
        now = datetime.now(pytz.timezone(timezone))
        cutoff = now + timedelta(minutes=first_cutoff_minutes)
        waves = [
            {
                "cutoff_time": cutoff.strftime("%H:%M"),
                "from_time": (cutoff + timedelta(hours=1)).strftime("%H:%M"),
                "to_time": (cutoff + timedelta(hours=12)).strftime("%H:%M"),
            },
            {
                "cutoff_time": (
                    cutoff + timedelta(minutes=next_cutoff_minutes)
                ).strftime("%H:%M"),
                "from_time": (cutoff + timedelta(hours=12, minutes=1)).strftime(
                    "%H:%M"
                ),
                "to_time": (cutoff + timedelta(minutes=59)).strftime("%H:%M"),
            },
        ]
        return self.post_wave_plan(
            retailer_id, mfc_id, CreateWavePlanRequestBody(waves)
        )
