import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import requests_mock

from env_setup_tool.src import config_types
from env_setup_tool.src.config_providers.site_info_provider import SiteInfoProvider
from env_setup_tool.src.config_types import CompositeConfig
from src.api.takeoff.site_info_service import (
    SiteInfoRetailerResponse,
    SiteInfoRetailerPayload,
)
from src.config.config import Config, get_token

project_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_root_dir)


@pytest.fixture
@patch.dict(
    os.environ,
    {
        "SERVICE_WORKER_TOKEN": "ondemand_dummy_worker_token",
        "AUTH_ODE_USER_ID": "dummy_user_id",
        "AUTH_ODE_USER_SECRET": "dummy-secret",
    },
)
def site_info_prereq() -> SiteInfoProvider:
    with requests_mock.Mocker() as n:
        n.get(
            "https://ode.ode-api.tom.takeoff.com/",
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
                "src.api.takeoff.site_info_service.MultiTenantBaseApi._MultiTenantBaseApi__get_token",
                return_value="mock_token",
            ):
                cfg = Config(
                    retailer="retailer",
                    env="ode",
                    location_code_tom="9999",
                    token=get_token("retailer", "ode"),
                    skip_location_check=True,
                )
                site_info_provider = SiteInfoProvider(cfg)
                return site_info_provider


def test_retailer_apply(site_info_prereq: SiteInfoProvider) -> None:
    retailer_payload = {
        "id": "ret1idrandom",
        "name": "Takeoff Retailer",
        "code": "retailer",
        "deployed_region": "us-central1",
        "create_by": "rqt@takeoff.com",
        "update_by": "rqt@takeoff.com",
        "create_time": "2024-01-01T07:15:50Z",
        "update_time": "2024-01-01T07:15:50Z",
    }

    key = "retailer"
    subconfig_data = CompositeConfig(
        configs={
            "retailer": config_types.Config(
                path=Path("site-info-retailer.yaml"),
                data={
                    "name": "Takeoff Retailer",
                    "code": "retailer",
                    "deployed_region": "us-central1",
                },
            )
        }
    )
    with patch(
        "src.api.takeoff.site_info_service.SiteInfoSvc.get_retailers",
        return_value=[],
    ), patch(
        "env_setup_tool.src.config_providers.site_info_provider.create_firebase_document",
        return_value=True,
    ) as mock_create_firestore_doc, patch(
        "src.api.takeoff.site_info_service.SiteInfoSvc.create_retailer",
        return_value=SiteInfoRetailerResponse.from_dict(retailer_payload),  # type: ignore
    ) as mock_site_info_post_retailer:
        res = site_info_prereq.apply(subconfig_data, key)
        assert len(res) == 1
        for k, v in res.items():
            assert k == "site_info.retailer"
            assert v is True
        mock_site_info_post_retailer.assert_called_once()
        mock_site_info_post_retailer.assert_called_with(
            SiteInfoRetailerPayload.from_dict(  # type: ignore
                {
                    "name": "Takeoff Retailer",
                    "code": "retailer",
                    "deployed_region": "us-central1",
                }
            )
        )
        mock_create_firestore_doc.assert_called_once()


def test_retailer_apply_skip_if_exist(site_info_prereq: SiteInfoProvider) -> None:
    retailer_payload = {
        "id": "ret1idrandom",
        "name": "Test Retailer One",
        "code": "olz123",
        "deployed_region": "us-west2-a",
        "create_by": "rqt@takeoff.com",
        "update_by": "rqt@takeoff.com",
        "create_time": "2024-01-01T07:15:50Z",
        "update_time": "2024-01-01T07:15:50Z",
    }

    get_retailer_payload = [
        {
            "id": "ret1idrandom",
            "name": "Test Retailer One",
            "code": "olz123",
            "deployed_region": "us-west2-a",
            "create_by": "rqt@takeoff.com",
            "update_by": "rqt@takeoff.com",
            "create_time": "2024-01-01T07:15:50Z",
            "update_time": "2024-01-01T07:15:50Z",
        },
        {
            "id": "ret2idrandom",
            "name": "Test Retailer",
            "code": "retailer",
            "deployed_region": "us-west2-a",
            "create_by": "rqt@takeoff.com",
            "update_by": "rqt@takeoff.com",
            "create_time": "2024-01-02T07:15:50Z",
            "update_time": "2024-01-02T07:15:50Z",
        },
    ]

    key = "retailer"
    subconfig_data = CompositeConfig(
        configs={
            "retailer": config_types.Config(
                path=Path("site-info-retailer.yaml"),
                data={
                    "name": "Takeoff Retailer",
                    "code": "retailer",
                    "deployed_region": "us-central1",
                },
            )
        }
    )
    with patch(
        "src.api.takeoff.site_info_service.SiteInfoSvc.get_retailers",
        return_value=[SiteInfoRetailerResponse(**d) for d in get_retailer_payload],
    ), patch(
        "env_setup_tool.src.config_providers.site_info_provider.create_firebase_document",
        return_value=True,
    ) as mock_create_firestore_doc, patch(
        "src.api.takeoff.site_info_service.SiteInfoSvc.create_retailer",
        return_value=SiteInfoRetailerResponse.from_dict(retailer_payload),  # type: ignore
    ) as mock_site_info_post_retailer:
        res = site_info_prereq.apply(subconfig_data, key)
        assert len(res) == 1
        for k, v in res.items():
            assert k == "site_info.retailer"
            assert v is True
        mock_site_info_post_retailer.assert_not_called()
        mock_create_firestore_doc.assert_called_once()
