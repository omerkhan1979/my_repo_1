import os
import sys
from unittest.mock import patch

import pytest
import requests_mock

from src.config.config import Config, get_token
from env_setup_tool.src import config_types
from env_setup_tool.src.config_providers.ims_provider import ImsProvider
from env_setup_tool.src.config_types import CompositeConfig

project_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_root_dir)


@pytest.fixture
@patch.dict(os.environ, {"SERVICE_WORKER_TOKEN": "ondemand_dummy_worker_token"})
def ims_prereq():
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
            ims_provider = ImsProvider(cfg)
            return ims_provider


def test_apply_all(ims_prereq):
    with patch.object(
        ims_prereq.service, "v2_create_addresses", return_value=True
    ) as mock_address_create, patch.object(
        ims_prereq.service, "v2_update_address_attributes", return_value=True
    ) as mock_address_update, patch.object(
        ims_prereq.service, "replace_reason_codes", return_value=True
    ) as mock_reason_codes_update:
        subconfig_data = CompositeConfig(
            configs={
                "addresses": config_types.Config(
                    path="ims-addresses.yaml",
                    data=[
                        {
                            "address": "01A000521W",
                            "shelf": "1",
                            "aisle": "0",
                            "dynamic": False,
                            "temp-zone": "ambient",
                            "active": True,
                            "location-id": "9999",
                            "stack": "W",
                            "bay": "05",
                            "area": "A",
                            "pickable": True,
                            "overstock": False,
                        },
                        {
                            "address": "0190D166020I",
                            "shelf": "0",
                            "aisle": "16",
                            "dynamic": True,
                            "temp-zone": "frozen",
                            "active": True,
                            "location-id": "9999",
                            "stack": "I",
                            "bay": "602",
                            "area": "D",
                            "pickable": True,
                            "overstock": False,
                        },
                    ],
                ),
                "reason_codes": config_types.Config(
                    path="ims-reason-codes.yaml",
                    data=[
                        {
                            "description": "Charitable donation",
                            "sort-order": 20,
                            "name": "Charity",
                            "can-remove": "true",
                            "parent-code": "",
                            "internal-only": "false",
                            "external-code": "4_8",
                            "can-add": "false",
                            "code": "CD",
                            "movement-type": "adjustment",
                        }
                    ],
                ),
            }
        )
        with patch(
            "src.api.takeoff.ims.IMS.v2_get_addresses",
            return_value={},
        ):
            res = ims_prereq.apply(subconfig_data)
            assert len(res) == 2

            assert "ims.addresses" in res
            assert res["ims.addresses"] is True
            assert "ims.reason_codes" in res
            assert res["ims.reason_codes"] is True
            assert mock_address_create.call_count == 1
            assert mock_address_update.call_count == 2
            assert mock_reason_codes_update.call_count == 1
            # Verify Create arguments correct, list of dicts with dashes not underscores
            assert mock_address_create.call_args.args == (
                [
                    {
                        "address": "01A000521W",
                        "location-id": "9999",
                        "area": "A",
                        "temp-zone": "ambient",
                        "aisle": "0",
                        "bay": "05",
                        "shelf": "1",
                        "stack": "W",
                    },
                    {
                        "address": "0190D166020I",
                        "location-id": "9999",
                        "area": "D",
                        "temp-zone": "frozen",
                        "aisle": "16",
                        "bay": "602",
                        "shelf": "0",
                        "stack": "I",
                    },
                ],
            )
            # Verify update parameters correct (underlined kwargs)
            _, _, kwargs_test = mock_address_update.mock_calls[0]
            assert kwargs_test == {
                "address": "01A000521W",
                "location_code": "9999",
                "dynamic": False,
                "overstock": False,
                "pickable": True,
                "active": True,
                "temp_zone": "ambient",
            }
            _, _, kwargs_test = mock_address_update.mock_calls[1]
            assert kwargs_test == {
                "address": "0190D166020I",
                "location_code": "9999",
                "dynamic": True,
                "overstock": False,
                "pickable": True,
                "active": True,
                "temp_zone": "frozen",
            }


def test_new_addresses(ims_prereq):
    with patch.object(
        ims_prereq.service, "v2_create_addresses", return_value=True
    ) as mock_address_create, patch.object(
        ims_prereq.service, "v2_update_address_attributes", return_value=True
    ) as mock_address_update:
        key = "addresses"
        subconfig_data = CompositeConfig(
            configs={
                "addresses": config_types.Config(
                    path="ims-addresses.yaml",
                    data=[
                        {
                            "address": "01A000521W",
                            "shelf": "1",
                            "aisle": "0",
                            "dynamic": False,
                            "temp-zone": "ambient",
                            "active": True,
                            "location-id": "9999",
                            "stack": "W",
                            "bay": "05",
                            "area": "A",
                            "pickable": True,
                            "overstock": False,
                        },
                        {
                            "address": "0190D166020I",
                            "shelf": "0",
                            "aisle": "16",
                            "dynamic": True,
                            "temp-zone": "frozen",
                            "active": True,
                            "location-id": "9999",
                            "stack": "I",
                            "bay": "602",
                            "area": "D",
                            "pickable": True,
                            "overstock": False,
                        },
                    ],
                )
            }
        )
        with patch(
            "src.api.takeoff.ims.IMS.v2_get_addresses",
            return_value={},
        ):
            res = ims_prereq.apply(subconfig_data, key)
            assert len(res) == 1
            for k, v in res.items():
                assert k == "ims.addresses"
                assert v is True
            assert mock_address_create.call_count == 1
            assert mock_address_update.call_count == 2
            # Verify Create arguments correct, list of dicts with dashes not underscores
            assert mock_address_create.call_args.args == (
                [
                    {
                        "address": "01A000521W",
                        "location-id": "9999",
                        "area": "A",
                        "temp-zone": "ambient",
                        "aisle": "0",
                        "bay": "05",
                        "shelf": "1",
                        "stack": "W",
                    },
                    {
                        "address": "0190D166020I",
                        "location-id": "9999",
                        "area": "D",
                        "temp-zone": "frozen",
                        "aisle": "16",
                        "bay": "602",
                        "shelf": "0",
                        "stack": "I",
                    },
                ],
            )
            # Verify update parameters correct (underlined kwargs)
            _, _, kwargs_test = mock_address_update.mock_calls[0]
            assert kwargs_test == {
                "address": "01A000521W",
                "location_code": "9999",
                "dynamic": False,
                "overstock": False,
                "pickable": True,
                "active": True,
                "temp_zone": "ambient",
            }
            _, _, kwargs_test = mock_address_update.mock_calls[1]
            assert kwargs_test == {
                "address": "0190D166020I",
                "location_code": "9999",
                "dynamic": True,
                "overstock": False,
                "pickable": True,
                "active": True,
                "temp_zone": "frozen",
            }


def test_update_addresses(ims_prereq):
    with patch.object(
        ims_prereq.service, "v2_create_addresses", return_value=True
    ) as mock_address_create, patch.object(
        ims_prereq.service, "v2_update_address_attributes", return_value=True
    ) as mock_address_update:
        key = "addresses"
        subconfig_data = CompositeConfig(
            configs={
                "addresses": config_types.Config(
                    path="ims-addresses.yaml",
                    data=[
                        {
                            "address": "01A000521W",
                            "shelf": "1",
                            "aisle": "0",
                            "dynamic": False,
                            "temp-zone": "ambient",
                            "active": True,
                            "location-id": "9999",
                            "stack": "W",
                            "bay": "05",
                            "area": "A",
                            "pickable": True,
                            "overstock": False,
                        },
                        {
                            "address": "0190D166020I",
                            "shelf": "0",
                            "aisle": "16",
                            "dynamic": True,
                            "temp-zone": "frozen",
                            "active": True,
                            "location-id": "9999",
                            "stack": "I",
                            "bay": "602",
                            "area": "D",
                            "pickable": True,
                            "overstock": False,
                        },
                    ],
                )
            }
        )
        with patch(
            "src.api.takeoff.ims.IMS.v2_get_addresses",
            return_value=[
                {
                    "address": "01A000521W",
                    "shelf": "1",
                    "aisle": "0",
                    "dynamic": False,
                    "temp-zone": "ambient",
                    "active": True,
                    "location-id": "9999",
                    "stack": "W",
                    "bay": "05",
                    "area": "A",
                    "pickable": True,
                    "overstock": True,
                },
                {
                    "address": "0190D166020I",
                    "shelf": "0",
                    "aisle": "16",
                    "dynamic": True,
                    "temp-zone": "frozen",
                    "active": True,
                    "location-id": "9999",
                    "stack": "I",
                    "bay": "602",
                    "area": "D",
                    "pickable": True,
                    "overstock": False,
                },
            ],
        ):
            res = ims_prereq.apply(subconfig_data, key)
            assert len(res) == 1
            for k, v in res.items():
                assert k == "ims.addresses"
                assert v is True
            assert mock_address_create.call_count == 0
            assert mock_address_update.call_count == 1
