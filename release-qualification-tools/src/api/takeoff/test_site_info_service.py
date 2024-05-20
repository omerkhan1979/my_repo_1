# Run with: poetry run pytest src/api/takeoff/test_site_info_service.py -s -vv
from unittest.mock import MagicMock, patch
from urllib.parse import urljoin

import pytest
import requests_mock
from _pytest.fixtures import FixtureRequest
from requests_mock.exceptions import NoMockAddress
import unittest

from src.api.takeoff.site_info_service import (
    SiteInfoSvc,
    SiteInfoSitePayload,
    SiteInfoSiteQuery,
    SiteInfoSiteResponse,
    Location,
    SiteInfoRetailerPayload,
    SiteInfoRetailerResponse,
    SiteInfoRetailerQuery,
)

BASE_DOMAIN = "fake-url.com"
BASE_URL = f"https://ode.ode-api.{BASE_DOMAIN}"
TOKEN_URL = urljoin(BASE_URL, "auth/token")
SITES_URL = urljoin(BASE_URL, "sites")
RETAILER_URL = urljoin(BASE_URL, "retailers")


@pytest.fixture(scope="class")
def site_service_fixture(request: FixtureRequest) -> None:
    with requests_mock.Mocker() as m:
        m.post(
            TOKEN_URL,
            status_code=200,
            json={"access_token": "test_token"},
        )
        request.cls.service = SiteInfoSvc(
            base_domain=BASE_DOMAIN, clientid="fake-id", clientsecret="fake-secret"
        )


@pytest.mark.usefixtures("site_service_fixture")
class TestSiteSvc(unittest.TestCase):
    # ---------Site---------

    def test_create_site(self) -> None:
        site_post_response = SiteInfoSiteResponse.from_dict(  # type:ignore
            {
                "id": "123",
                "name": "site123 name",
                "deployed_region": "us-central1",
                "retailer_site_id": "rsite123 name",
                "retailer_id": "test-retailer-id",
                "status": "draft",
                "timezone": "Europe/Berlin",
                "location": {"lat": 54.25, "long": 13.134},
                "create_by": "xyx@takeoff.com",
                "update_by": "joe.d@takeoff.com",
                "create_time": "2022-12-12T12:16:38Z",
                "update_time": "2022-12-12T12:16:38Z",
            }
        )
        with requests_mock.Mocker() as p:
            p.post(
                SITES_URL,
                request_headers={
                    "accept": "application/json; version=1",
                    "content-type": "application/json",
                    "X-Correlation-ID": "corid-test",
                    "Authorization": "Bearer test_token",
                    "retailer_id": "test-retailer-id",
                },
                status_code=200,
                json=site_post_response.to_dict(),
            )
            test_site = SiteInfoSitePayload(
                name="site123 name",
                retailer_site_id="rsite123 name",
                location=Location(lat=54.25, long=13.134),
            )
            try:
                returndata = self.service.create_site(  # type: ignore
                    retailer_id="test-retailer-id",
                    site=test_site,
                    correlation_id="corid-test",
                )
            except NoMockAddress as e:
                raise Exception(
                    f"{e} -- (This Exception can also be caused by a HEADER mismatch!)"
                )

            assert returndata == site_post_response

    def test_get_sites(self) -> None:
        def getsite(id: str) -> SiteInfoRetailerResponse:
            return SiteInfoSiteResponse.from_dict(  # type:ignore
                {
                    "id": f"{id}",
                    "name": f"site{id} name",
                    "deployed_region": "us-central1",
                    "retailer_site_id": f"rsite{id} name",
                    "retailer_id": "test-retailer-id",
                    "status": "draft",
                    "timezone": "Europe/Berlin",
                    "location": {"lat": 54.25, "long": 13.134},
                    "create_by": "xyx@takeoff.com",
                    "update_by": "joe.d@takeoff.com",
                    "create_time": "2022-12-12T12:16:38Z",
                    "update_time": "2022-12-12T12:16:38Z",
                }
            )

        site_query1 = SiteInfoSiteQuery.from_dict(  # type:ignore
            {}
        )
        site_post_data1 = [getsite(x) for x in ["123", "456", "789"]]
        site_post_response1 = {
            "sites": [siteresp.to_dict() for siteresp in site_post_data1]  # type:ignore
        }
        site_query2 = SiteInfoSiteQuery.from_dict(  # type:ignore
            {
                "retailer_id": "retailer123",
            }
        )
        site_post_data2 = [getsite(x) for x in ["123"]]
        site_post_response2 = {
            "sites": [siteresp.to_dict() for siteresp in site_post_data2]  # type:ignore
        }

        with requests_mock.Mocker() as g:
            g.get(
                SITES_URL,
                request_headers={
                    "accept": "application/json; version=1",
                    "content-type": "application/json",
                    "X-Correlation-ID": "corid-test",
                    "Authorization": "Bearer test_token",
                },
                status_code=200,
                json=site_post_response1,
            )
            returndata1 = self.service.get_sites(  # type: ignore
                site_params=site_query1,
                correlation_id="corid-test",
            )
            assert returndata1 == site_post_data1

        with requests_mock.Mocker() as g:
            g.get(
                SITES_URL + "?retailer_id=retailer123",
                request_headers={
                    "accept": "application/json; version=1",
                    "content-type": "application/json",
                    "X-Correlation-ID": "corid-test",
                    "Authorization": "Bearer test_token",
                },
                status_code=200,
                json=site_post_response2,
            )
            returndata2 = self.service.get_sites(  # type: ignore
                site_params=site_query2,
                correlation_id="corid-test",
            )
            assert returndata2 == site_post_data2

    @patch("src.api.takeoff.site_info_service.requests.post")
    def test_activate_site(self, post: MagicMock) -> None:
        site_response_dict = {
            "id": "123456",
            "name": "Test name",
            "deployed_region": "us-central1",
            "retailer_site_id": "rsite123456name",
            "retailer_id": "test-retailer-id",
            "status": "draft",
            "timezone": "Europe/Berlin",
            "location": {"lat": 54.25, "long": 13.134},
            "create_by": "xyx@takeoff.com",
            "update_by": "joe.d@takeoff.com",
            "create_time": "2022-12-12T12:16:38Z",
            "update_time": "2022-12-12T12:16:38Z",
            "etag": "8698369506e3196a6421024c9e2334bd0efdd6a5cc41ef704b8333e19e00e6ca",
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = site_response_dict
        post.return_value = mock_response
        with patch("src.utils.http.handle_response", return_value=site_response_dict):
            response = self.service.site_activate(  # type: ignore
                etag="8698369506e3196a6421024c9e2334bd0efdd6a5cc41ef704b8333e19e00e6ca",
                site_id="123456",
                retailer_id="rsite123456name",
            )

            assert isinstance(response, SiteInfoSiteResponse)
            assert response.id == "123456"
            assert response.name == "Test name"
            assert response.deployed_region == "us-central1"
            expected_headers = self.service.headers(correlation_id=None)  # type: ignore
            expected_headers["If-Match"] = (
                "8698369506e3196a6421024c9e2334bd0efdd6a5cc41ef704b8333e19e00e6ca"
            )
            expected_headers["retailer_id"] = "rsite123456name"

            post.assert_called_once_with(
                url=f"{SITES_URL}/123456:active",
                headers=expected_headers,
            )

    # ---------Retailer---------

    @patch("src.api.takeoff.site_info_service.requests.post")
    def test_create_retailer(self, post: MagicMock) -> None:
        retailer_payload_dict = {
            "name": "Test Retailer",
            "code": "olz123",
            "deployed_region": "us-west2-a",
        }
        retailer_payload = SiteInfoRetailerPayload.from_dict(  # type:ignore
            retailer_payload_dict
        )
        retailer_response_dict = {
            "id": "retailer123",
            "name": "Test Retailer",
            "deployed_region": "us-west2-a",
            "code": "olz123",
            "create_by": "rqt@takeoff.com",
            "update_by": "rqt@takeoff.com",
            "create_time": "2024-01-01T07:15:50Z",
            "update_time": "2024-01-01T07:15:50Z",
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = retailer_response_dict
        post.return_value = mock_response
        with patch(
            "src.utils.http.handle_response", return_value=retailer_response_dict
        ):
            response = self.service.create_retailer(retailer_payload)  # type: ignore

            assert isinstance(response, SiteInfoRetailerResponse)
            assert response.id == "retailer123"
            assert response.name == "Test Retailer"
            assert response.deployed_region == "us-west2-a"
            post.assert_called_once_with(
                RETAILER_URL,  # type: ignore
                headers=self.service.headers(correlation_id=None),  # type: ignore
                data=retailer_payload.to_json(),
            )

    @patch("src.api.takeoff.site_info_service.requests.get")
    def test_get_retailer(self, get: MagicMock) -> None:
        retailers_dict = [
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
                "name": "Test Retailer Two",
                "code": "qwe456",
                "deployed_region": "us-west2-a",
                "create_by": "rqt@takeoff.com",
                "update_by": "rqt@takeoff.com",
                "create_time": "2024-01-01T07:15:50Z",
                "update_time": "2024-01-01T07:15:50Z",
            },
        ]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"retailers": retailers_dict}
        get.return_value = mock_response

        query = SiteInfoRetailerQuery(code="olz123")
        with patch(
            "src.utils.http.handle_response",
            return_value={"retailers:": retailers_dict},
        ):
            response = self.service.get_retailers(correlation_id="rqt", parameters=query)  # type: ignore

            get.assert_called_once_with(
                RETAILER_URL,  # type: ignore
                headers=self.service.headers(correlation_id=None),  # type: ignore
                params=query.to_dict(),  # type: ignore
            )
            for item in response:
                assert isinstance(item, SiteInfoRetailerResponse)
            assert response[0].name == "Test Retailer One"
            assert response[0].deployed_region == "us-west2-a"
            assert response[0].id == "ret1idrandom"
