from dataclasses import asdict
from unittest.mock import patch

import requests
import requests_mock
import pytest

from src.api.takeoff.wave_planner import (
    FireTriggersSuccessResponse,
    GenerateTriggersSuccessResponse,
    GetTriggersSuccessResponse,
    GetWavePlanSuccessResponse,
    WavePlanner,
)
from src.config.config import Config
from src.utils.locations import locations_endpoint


@pytest.mark.usefixtures("gcp_config_mocks")
@requests_mock.Mocker(kw="mock")
def test_get_wave_plan(**kwargs):
    path_url = (
        "https://wave-planner.nonprod.outbound.tom.takeoff.com//"
        + WavePlanner.retailer_mfc_waveplan_endpoint.format("1111", "1")
    )
    wave_plan_dict = {
        "id": "791e58c6-c45f-4e18-bdf0-010c5cec9dce",
        "retailer_id": "MAF",
        "mfc_id": "D02",
        "timezone": "Asia/Dubai",
        "created_at": "2016-11-01T20:44:39Z",
        "created_time": "2016-11-01T20:44:39Z",
        "created_by": "dsaAddgG",
        "waves": [
            {
                "id": "791e58c6-c45f-4e18-bdf0-110c5cec9dce",
                "cutoff_time": "14:00",
                "from_time": "16:00",
                "to_time": "18:00",
                "schedules": [
                    {
                        "id": "791e58c7-c45f-4e18-bdf0-110c5cec9dce",
                        "schedule_type": "prelim_picklist",
                        "schedule_time": "12:00",
                    }
                ],
            }
        ],
    }
    wave_plan_success = GetWavePlanSuccessResponse.from_dict(wave_plan_dict)

    kwargs["mock"].get(
        path_url,
        status_code=200,
        json=wave_plan_dict,
    )
    kwargs["mock"].get(
        "https://service-catalog-fake-qai.tom.takeoff.com/api/" + locations_endpoint,
        status_code=200,
        json=[
            {
                "location-id": 9999,
            }
        ],
    )
    with patch(
        "src.config.config.is_location_code_tom_valid",
        return_value="9999",
    ):
        with patch(
            "src.api.takeoff.wave_planner.get_bearer",
            return_value="9999",
        ):
            with patch(
                "src.api.takeoff.wave_planner.WavePlanner.get_or_create_wave_planner_user_token",
                return_value="fake-token",
            ):
                cfg = Config("fake", "qai", "9999", "anything", "", "")
                WavePlanner(cfg)
                assert (
                    GetWavePlanSuccessResponse.from_json(requests.get(path_url).text)
                    == wave_plan_success
                )
                assert "created_at" not in asdict(wave_plan_success).items()
                assert wave_plan_success.created_time == "2016-11-01T20:44:39Z"


@pytest.mark.usefixtures("gcp_config_mocks")
@requests_mock.Mocker(kw="mock")
def test_post_wave_plan(**kwargs):
    path_url = (
        "https://wave-planner.nonprod.outbound.tom.takeoff.com//"
        + WavePlanner.retailer_mfc_waveplan_endpoint.format("1111", "1")
    )
    wave_plan_dict = {
        "retailer_id": "MAF",
        "mfc_id": "D02",
        "timezone": "Asia/Dubai",
        "created_time": "2016-11-01T20:44:39Z",
        "created_by": "dsaAddgG",
        "id": "plan1",
        "waves": [
            {
                "cutoff_time": "14:00",
                "from_time": "16:00",
                "to_time": "18:00",
                "id": "wave1",
                "schedules": [
                    {
                        "id": "schedule1",
                        "schedule_type": "prelim_picklist",
                        "schedule_time": "12:00",
                    }
                ],
            }
        ],
    }
    wave_plan_success = GetWavePlanSuccessResponse.from_dict(wave_plan_dict)

    kwargs["mock"].post(
        path_url,
        status_code=200,
        json=wave_plan_dict,
    )
    kwargs["mock"].get(
        "https://service-catalog-fake-qai.tom.takeoff.com/api/" + locations_endpoint,
        status_code=200,
        json=[
            {
                "location-id": 9999,
            }
        ],
    )
    with patch(
        "src.config.config.is_location_code_tom_valid",
        return_value="9999",
    ):
        with patch(
            "src.api.takeoff.wave_planner.get_bearer",
            return_value="9999",
        ):
            with patch(
                "src.api.takeoff.wave_planner.WavePlanner.get_or_create_wave_planner_user_token",
                return_value="fake-token",
            ):
                cfg = Config("fake", "qai", "9999", "anything", "", "")
                WavePlanner(cfg)
                assert (
                    GetWavePlanSuccessResponse.from_json(requests.post(path_url).text)
                    == wave_plan_success
                )
                assert wave_plan_success.created_time == "2016-11-01T20:44:39Z"


@pytest.mark.usefixtures("gcp_config_mocks")
@requests_mock.Mocker(kw="mock")
def test_post_generate_trigger(**kwargs):
    path_url = (
        "https://wave-planner.nonprod.outbound.tom.takeoff.com//"
        + WavePlanner.generate_trigger_endpoint
    )

    trigeers_dict = {
        "generated_triggers": "791e58c6-c45f-4e18-bdf0-010c5cec9dce",
    }
    generate_trigger = GenerateTriggersSuccessResponse.from_dict(trigeers_dict)

    kwargs["mock"].post(path_url, status_code=200, json=trigeers_dict)
    kwargs["mock"].get(
        "https://service-catalog-fake-qai.tom.takeoff.com/api/" + locations_endpoint,
        status_code=200,
        json=[
            {
                "location-id": 9999,
            }
        ],
    )
    with patch(
        "src.config.config.is_location_code_tom_valid",
        return_value="9999",
    ):
        with patch(
            "src.api.takeoff.wave_planner.get_bearer",
            return_value="9999",
        ):
            with patch(
                "src.api.takeoff.wave_planner.WavePlanner.get_or_create_wave_planner_user_token",
                return_value="fake-token",
            ):
                cfg = Config("fake", "qai", "9999", "anything", "", "")
                WavePlanner(cfg)
        assert requests.post(path_url).text == generate_trigger.to_json()


@pytest.mark.usefixtures("gcp_config_mocks")
@requests_mock.Mocker(kw="mock")
def test_post_fire_trigger(**kwargs):
    path_url = (
        "https://wave-planner.nonprod.outbound.tom.takeoff.com/"
        + WavePlanner.fire_trigger_endpoint
    )

    trigers_dict = {
        "triggers": [
            {
                "retailer_id": "MAF",
                "mfc_id": "D02",
                "schedule_id": "791e58c6-c45f-4e18-bdf0-110c5cec9dce",
                "schedule_type": "prelim_picklist",
                "cutoff_datetime": "2016-11-01T20:44:39Z",
                "trigger_at": "2016-11-01T20:44:39Z",
                "created_at": "2016-11-01T20:44:39Z",
                "fired_at": "2016-11-01T20:44:39Z",
            }
        ]
    }
    generate_trigger = FireTriggersSuccessResponse.from_dict(trigers_dict)

    kwargs["mock"].post(path_url, status_code=200, json=trigers_dict)
    kwargs["mock"].get(
        "https://service-catalog-fake-qai.tom.takeoff.com/api/" + locations_endpoint,
        status_code=200,
        json=[
            {
                "location-id": 9999,
            }
        ],
    )
    with patch(
        "src.config.config.is_location_code_tom_valid",
        return_value="9999",
    ):
        with patch(
            "src.api.takeoff.wave_planner.get_bearer",
            return_value="9999",
        ):
            with patch(
                "src.api.takeoff.wave_planner.WavePlanner.get_or_create_wave_planner_user_token",
                return_value="fake-token",
            ):
                cfg = Config("fake", "qai", "9999", "anything", "", "")
                WavePlanner(cfg)
        assert (
            FireTriggersSuccessResponse.from_json(requests.post(path_url).text)
            == generate_trigger
        )


@pytest.mark.usefixtures("gcp_config_mocks")
@requests_mock.Mocker(kw="mock")
def test_get_triggers(**kwargs):
    path_url = (
        "https://wave-planner.nonprod.outbound.tom.takeoff.com"
        + WavePlanner.triggers_endpoint
    )

    trigers_dict = {
        "triggers": [
            {
                "retailer_id": "MAF",
                "mfc_id": "D02",
                "wave_plan_id": "791e58c6-c45f-4e18-bdf0-010c5cec9dce",
                "wave_id": "791e58c6-c45f-4e18-bdf0-010c5cec9dce",
                "cutoff_time": "14:00",
                "schedule_id": "791e58c6-c45f-4e18-bdf0-010c5cec9dce",
                "schedule_time": "12:00",
                "trigger_at": "2016-11-01T20:44:39Z",
                "cutoff_datetime": "2016-11-01T19:44:39Z",
                "created_at": "2016-11-01T19:44:39Z",
                "fired_at": "2016-11-01T20:44:39Z",
            }
        ]
    }
    generate_trigger = GetTriggersSuccessResponse.from_dict(trigers_dict)

    kwargs["mock"].get(path_url, status_code=200, json=trigers_dict)
    kwargs["mock"].get(
        "https://service-catalog-fake-qai.tom.takeoff.com/api/" + locations_endpoint,
        status_code=200,
        json=[
            {
                "location-id": 9999,
            }
        ],
    )
    with patch(
        "src.config.config.is_location_code_tom_valid",
        return_value="9999",
    ):
        with patch(
            "src.api.takeoff.wave_planner.get_bearer",
            return_value="9999",
        ):
            with patch(
                "src.api.takeoff.wave_planner.WavePlanner.get_or_create_wave_planner_user_token",
                return_value="fake-token",
            ):
                cfg = Config("fake", "qai", "9999", "anything", "", "")
                WavePlanner(cfg)
        assert (
            GetTriggersSuccessResponse.from_json(requests.get(path_url).text)
            == generate_trigger
        )
