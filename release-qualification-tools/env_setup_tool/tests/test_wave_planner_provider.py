import os
from unittest.mock import patch

import pytest
import requests_mock

from env_setup_tool.src import config_types
from env_setup_tool.src.config_providers.wave_planner_provider import (
    WavePlannerProvider,
)
from env_setup_tool.src.config_types import ConfigType
from src.config.config import Config, get_token


# poetry run pytest env_setup_tool/tests/test_sleeping_area_rules_provider.py -s


@pytest.fixture
@patch.dict(os.environ, {"SERVICE_WORKER_TOKEN": "ondemand_dummy_worker_token"})
def wave_plans_prereq():
    with requests_mock.Mocker() as n:
        n.get(
            "https://retailer-ode.tom.takeoff.com/",
            status_code=200,
            json={},
        )
    with patch(
        "src.config.config.get_gcp_project_id",
        return_value="random-gcp-project-id",
    ):
        with patch(
            "src.config.config.get_firebase_key",
            return_value="FIREBASE_KEY",
        ):
            with patch(
                "src.api.takeoff.wave_planner.get_bearer",
                return_value="bearer_token",
            ):
                with patch(
                    "src.api.takeoff.wave_planner.get_or_create_user_token",
                    return_value="user_KEY",
                ):
                    cfg = Config(
                        retailer="retailer",
                        env="ode",
                        location_code_tom="9999",
                        token=get_token("retailer", "ode"),
                        skip_location_check=True,
                    )
                    wave_planner_provider = WavePlannerProvider(cfg)
                    return wave_planner_provider


def test_wave_plans_apply(wave_plans_prereq):
    with patch.object(
        wave_plans_prereq.service,
        "post_wave_plan",
        return_value=True,
    ) as mock_post_wave_plans:
        rule_config = config_types.Config(
            path="wave-plans-mock.yaml",
            data={
                "9999": [
                    {
                        "cutoff_time": "00:30",
                        "from_time": "01:00",
                        "to_time": "11:59",
                        "schedules": [],
                    },
                    {
                        "cutoff_time": "04:36",
                        "from_time": "12:00",
                        "to_time": "00:59",
                        "schedules": [],
                    },
                ]
            },
        )

        res = wave_plans_prereq.apply(rule_config)
        assert res[ConfigType.WAVE_PLANS.value] is True
        assert mock_post_wave_plans.call_count == 1
        mock_post_wave_plans.assert_called()
