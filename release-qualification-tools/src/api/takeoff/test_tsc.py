from unittest.mock import patch
import pytest
import requests_mock
import unittest

from src.api.takeoff.tsc import TSC
from src.config.config import Config
from src.utils.config import get_url_builder
from src.utils.locations import locations_endpoint


@pytest.fixture(scope="class")
def tsc_fixture(request):
    url_builder = get_url_builder("api/", "service-catalog")
    request_url = url_builder(
        retailer="fake",
        env="qai",
        rel=locations_endpoint,
    )
    with patch(
        "src.config.config.is_location_code_tom_valid",
        return_value="9999",
    ):
        with requests_mock.Mocker() as n:
            n.get(
                "https://fake-qai.tom.takeoff.com/",
                status_code=200,
                json={},
            )
            with requests_mock.Mocker() as m:
                m.get(request_url, status_code=200, json={})
                cfg = Config("fake", "qai", "9999", "anything", "")
                request.cls.tsc = TSC(cfg)


@pytest.mark.usefixtures("gcp_config_mocks", "tsc_fixture")
class TestTsc(unittest.TestCase):
    # ---------Locations---------

    def test_get_locations(self):
        with requests_mock.Mocker() as p:
            p.get(
                "https://service-catalog-fake-qai.tom.takeoff.com/api/"
                + locations_endpoint,
                status_code=200,
                json=[
                    {
                        "location-id": 9999,
                    }
                ],
            )
            assert self.tsc.get_locations() == [{"location-id": 9999}]

    def test_get_location_code(self):
        with requests_mock.Mocker() as p:
            p.get(
                "https://service-catalog-fake-qai.tom.takeoff.com/api/"
                + locations_endpoint,
                status_code=200,
                json=[
                    {
                        "location-code-tom": "9999",
                        "location-id": 9999,
                        "location_code_type": "MFC",
                        "location-code-retailer": "OK",
                    }
                ],
            )
            assert self.tsc.get_location_code("location-code-retailer", "9999") == "OK"

    def test_get_spoke_id_for_mfc_tom_location(self):
        with requests_mock.Mocker() as p:
            p.get(
                "https://service-catalog-fake-qai.tom.takeoff.com/api/"
                + locations_endpoint,
                status_code=200,
                json=[
                    {
                        "location-code-tom": "9999",
                        "location-id": 9999,
                        "location_code_type": "MFC",
                        "location-code-retailer": "OK",
                        "mfc-ref-code": "11W",
                    }
                ],
            )
            self.tsc.get_spoke_id_for_mfc_tom_location() == ""

    def test_get_all_spokes_for_mfc_tom(self) -> list:
        with requests_mock.Mocker() as p:
            p.get(
                "https://service-catalog-fake-qai.tom.takeoff.com/api/"
                + locations_endpoint,
                status_code=200,
                json=[
                    {
                        "location-code-tom": "9999",
                        "location-id": 9999,
                        "location-type": "MFC",
                        "location-code-retailer": "OK",
                        "mfc-ref-code": "11W",
                    }
                ],
            )
            self.tsc.get_all_spokes_for_mfc_tom() == ""

    def test_get_config_items(self):
        with requests_mock.Mocker() as p:
            p.get(
                "https://service-catalog-fake-qai.tom.takeoff.com/api/"
                + TSC.config_items_endpoint,
                status_code=200,
                json=[
                    {
                        "location-code-tom": "9999",
                        "location-id": 9999,
                        "location_code_type": "MFC",
                        "location-code-retailer": "OK",
                        "mfc-ref-code": "11W",
                    }
                ],
            )
            assert self.tsc.get_config_items() == [
                {
                    "name": "HELLO",
                    "value": "TAKEOFF",
                }
            ]

    def test_put_config_items(self):
        with requests_mock.Mocker() as p:
            p.put(
                "https://service-catalog-fake-qai.tom.takeoff.com/api/"
                + TSC.put_config_items_endpoint,
                status_code=201,
                json=[
                    {
                        "name": "HELLO",
                        "value": "TAKEOFF",
                    }
                ],
            )
            assert self.tsc.put_config_items(
                [{"name": "HELLO", "value": "TAKEOFF"}], [201, 200]
            ) == [
                {
                    "name": "HELLO",
                    "value": "TAKEOFF",
                }
            ]

    def test_get_config_item_value(self):
        with requests_mock.Mocker() as p:
            p.get(
                "https://service-catalog-fake-qai.tom.takeoff.com/api/"
                + TSC.config_items_endpoint,
                status_code=200,
                json=[
                    {
                        "name": "HELLO",
                        "value": "TAKEOFF",
                    }
                ],
            )
            assert self.tsc.get_config_item_value("HELLO1") is None
