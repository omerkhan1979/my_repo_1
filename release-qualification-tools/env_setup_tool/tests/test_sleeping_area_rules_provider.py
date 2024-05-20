import os
import sys
from unittest.mock import patch

import pytest
import requests_mock

from env_setup_tool.src import config_types
from env_setup_tool.src.config_types import ConfigType
from src.config.config import Config, get_token
from env_setup_tool.src.config_providers.sleeping_area_rules_provider import (
    SleepingAreaRulesProvider,
)

# poetry run pytest env_setup_tool/tests/test_sleeping_area_rules_provider.py -s

project_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_root_dir)


@pytest.fixture
@patch.dict(os.environ, {"SERVICE_WORKER_TOKEN": "ondemand_dummy_worker_token"})
def sleeping_area_rules_prereq():
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
            cfg = Config(
                retailer="retailer",
                env="ode",
                location_code_tom="9999",
                token=get_token("retailer", "ode"),
                skip_location_check=True,
            )
            sleeping_area_rules_provider = SleepingAreaRulesProvider(cfg)
            return sleeping_area_rules_provider


def test_sleeping_area_rules_apply(sleeping_area_rules_prereq):
    with patch.object(
        sleeping_area_rules_prereq.service,
        "upsert_rule_sleeping_area",
        return_value=True,
    ) as mock_upsert_rule_sleeping_area:
        rule_config = config_types.Config(
            path="sleeping-area-rules-mock.yaml",
            data={
                "rules": [
                    {
                        "rule": {
                            "priority": 10,
                            "rule": '#and [#eq[#arg[:temperature-zone],["frozen"]], #or [#eq [#arg [:location-info :item-type], "REG"], #eq[#arg[:storage-zone], "manual"]]]',
                            "sleeping-area": "B",
                            "store-id": "9999",
                            "update-note": "B for frozen REG or manual zone products",
                        }
                    },
                    {
                        "rule": {
                            "priority": 20,
                            "rule": '#and[#insec[#arg[:temperature-zone] ["chilled"]] #or[ #and[ #eq[#arg[:location-info :item-type] "REG"] #eq[#arg[:feature-attributes :is-hazardous], true]] #eq[#arg[:storage-zone] "manual"] #and[ #eq[#arg[:storage-zone] "osr"] #eq[#arg[:feature-attributes :is-hazardous], true ]]]]',
                            "sleeping-area": "C",
                            "store-id": "9999",
                            "update-note": "C for chilled hazardous products or manual zone products",
                        }
                    },
                ]
            },
        )

        res = sleeping_area_rules_prereq.apply(rule_config)
        assert res[ConfigType.SleepingAreaRules.value] is True
        assert mock_upsert_rule_sleeping_area.call_count == 2
        mock_upsert_rule_sleeping_area.assert_called()
