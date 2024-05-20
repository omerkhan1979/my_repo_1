from unittest.mock import patch
import pytest
import os
import mock
import unittest
import requests_mock

from src.api.takeoff.tsc import TSC
from src.copy_config.copy_tsc import (
    CopyTsc,
    ConfigurationSet,
    config_to_yaml,
    config_from_yaml,
)
from src.utils.config import get_url_builder
from src.utils.locations import locations_endpoint
from src.copy_config.exception import CopyConfigErrorCodes, CopyConfigException
from src.utils.os_helpers import delete_file
from src.config.config import Config


def nop(iterable, *args, **kwargs):
    """
    replacement for tqdm that just passes back the iterable
    useful to silence `tqdm` in tests
    """
    return None


def no_location(iterable, *args, **kwargs):
    return {"location-id": 1234}


def no_int(iterable, *args, **kwargs):
    return 1234


def no_list_location(iterable, *args, **kwargs):
    """
    replacement for tqdm that just passes back the iterable
    useful to silence `tqdm` in tests
    """
    return [{"location-id": 1234}]


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
                cfg = Config(
                    "fake",
                    "qai",
                    "9999",
                    "anything",
                    "",
                    disallow=False,
                )
                request.cls.tsc = TSC(cfg)


@pytest.mark.usefixtures("gcp_config_mocks", "tsc_fixture")
@mock.patch("src.api.takeoff.tsc.TSC.get_location_id_by_code_tom", no_int)
@mock.patch("src.api.takeoff.tsc.TSC.set_location_availability", nop)
@mock.patch("src.api.takeoff.ops_api.OpsApi.initialize_picking_queue", nop)
class TestCopyTsc(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def capsys(self, capsys):
        self.capsys = capsys

    def test_get_target_config(self):
        c = CopyTsc()
        c.retailer = "abs"
        c.env_target = "dev"
        c.locations = {"9998"}
        with patch(
            "src.config.config.is_location_code_tom_valid",
            return_value="9998",
        ):
            tgt_config: Config = c.get_target_config(c.locations.pop())
            assert tgt_config is not None
            assert tgt_config.env == "dev"
            assert tgt_config.token is not None
            # the length of the token is at least 83 chars
            assert len(tgt_config.token) >= 83
            assert tgt_config.location_code_tom == "9998"

    @mock.patch("src.api.takeoff.tsc.TSC.create_location_spoke", nop)
    @mock.patch("src.api.takeoff.tsc.TSC.update_location_spoke", nop)
    def test_update_target_spoke_found(self):
        c = CopyTsc()
        c.retailer = "abs"
        c.env_target = "dev"
        c.locations = {"4444"}
        with patch(
            "src.config.config.is_location_code_tom_valid",
            return_value="4444",
        ):
            tsc_tgt = TSC(c.get_target_config("4444"))
            with patch(
                "src.api.takeoff.tsc.TSC.get_locations",
                return_value=[
                    {
                        "location-type": "spoke",
                        "mfc-ref-code": "4443",
                        "location-pickup": {"lat": 0, "lon": 0},
                        "location-name": "test1234",
                        "location-id": 1234,
                        "location-code-retailer": "test",
                        "location-code-tom": "test",
                        "location-code-gold": "test",
                    }
                ],
            ):
                c.update_target_spoke(
                    tsc_tgt,
                    4444,
                    {
                        "location-type": "spoke",
                        "mfc-ref-code": "4444",
                        "location-pickup": {"lat": 0, "lon": 0},
                        "location-id": 1234,
                        "location-code-tom": "test",
                    },
                )
            out, err = self.capsys.readouterr()
            assert err == ""
            assert out != ""

    def test_update_target_spoke_error(self):
        c = CopyTsc()
        c.retailer = "abs"
        c.env_target = "dev"
        c.locations = {"4444", "9998"}
        with patch(
            "src.config.config.is_location_code_tom_valid",
            return_value="4444",
        ):
            tsc_tgt = TSC(c.get_target_config("4444"))

            # Until PROD-12474 we're going to not raise here
            # with pytest.raises(CopyConfigException) as pytest_wrapped_e:
            c.update_target_spoke(
                tsc_tgt,
                4444,
                {
                    "location-type": "spoke",
                    "location-code-tom": "HELLO",
                    "mfc-ref-code": "4444",
                    "location-pickup": {"lat": 0, "lon": 0},
                    "location-id": 1234,
                },
            )
            out, err = self.capsys.readouterr()
            assert err != ""
            # Until PROD-12474 we're going to not raise here
            # assert (
            #    pytest_wrapped_e.value.code_exception
            #    == CopyConfigErrorCodes.SPOKE_CREATION_FAILED
            # )

    @mock.patch("src.api.takeoff.tsc.TSC.get_tom_code_locations", nop)
    @mock.patch("src.api.takeoff.tsc.TSC.put_config_items", nop)
    def test_update_target_location_error(self):
        c = CopyTsc()
        c.retailer = "abs"
        c.env_target = "dev"
        c.locations = {"4444", "9998"}
        with patch(
            "src.config.config.is_location_code_tom_valid",
            return_value="4444",
        ):
            tsc_tgt = TSC(c.get_target_config("4444"))
            with pytest.raises(CopyConfigException) as pytest_wrapped_e:
                c.update_target_location(
                    tsc_tgt,
                    [
                        {
                            "timezone": "string",
                            "location-type": "mfc",
                            "mfc-ref-code": "4444",
                            "location-address": {
                                "state": "string",
                                "iso-state": "string",
                                "city": "string",
                                "street": "string",
                                "zip-code": "string",
                            },
                            "location-pickup": {"lat": 0, "lon": 0},
                            "location-name": "string",
                            "location-contact-phone": "string",
                            "location-service-info": {
                                "phone": "string",
                                "desctext": "string",
                                "email": "string",
                            },
                            "location-id": 0,
                            "location-code-retailer": "string",
                            "location-code-tom": "string",
                            "location-code-gold": "string",
                        }
                    ],
                    len(c.locations),
                )
            out, err = self.capsys.readouterr()
            assert err != ""
            assert out != ""
            assert (
                pytest_wrapped_e.value.code_exception
                == CopyConfigErrorCodes.LOCATION_CREATION_FAILED
            )

    @mock.patch("src.copy_config.copy_tsc.apply_location_osr_values", nop)
    @mock.patch("src.api.takeoff.tsc.TSC.apply_profile", nop)
    @mock.patch("src.api.takeoff.tsc.TSC.post_mfc_location", no_location)
    @mock.patch("src.api.takeoff.tsc.TSC.set_location_availability", nop)
    def test_update_target_location(self):
        c = CopyTsc()
        c.retailer = "abs"
        c.env_target = "dev"
        c.locations = {"4444", "9998"}
        with patch(
            "src.config.config.is_location_code_tom_valid",
            return_value="4444",
        ):
            tsc_tgt = TSC(c.get_target_config("4444"))
            c.update_target_location(
                tsc_tgt,
                {
                    "timezone": "string",
                    "location-type": "mfc",
                    "mfc-ref-code": "99",
                    "location-id": 0,
                    "location-code-retailer": "string",
                    "location-code-tom": "string",
                    "location-code-gold": "string",
                },
                len(c.locations),
            )
        out, err = self.capsys.readouterr()
        assert err == ""
        assert '----Creating location "4444" for "abs"----' in out
        assert '----Successfully created location "4444" for "abs"----' in out
        assert '----Applying default profile on location "4444" for ' in out
        assert (
            '----Successfully applied default profile on location "4444" for "abs"----'
            in out
        )
        assert '----Applying default OSR values on location "4444" for "abs"----' in out
        assert (
            '----Successfully applied default OSR values on location "4444" for "abs"----'
            in out
        )
        assert '---Enabling mfc location "4444" for "abs"----' in out
        assert '----Completed updated of location "4444" for "abs"----' in out
        assert '----No spokes to update on "dev" for retailer ' in out

    def test_get_source_config(self):
        c = CopyTsc()
        c.retailer = "abs"
        c.env_source = "qai"
        c.env_target = "dev"
        c.locations = {"9999", "9998"}
        with patch(
            "src.config.config.is_location_code_tom_valid",
            return_value="9999",
        ):
            tgt_config: Config = c.get_source_config("9999")
            assert tgt_config is not None
            assert tgt_config.env == "qai"
            assert tgt_config.token is not None
            # the length of the token is at least 83 chars
            assert len(tgt_config.token) >= 83
            assert tgt_config.location_code_tom == "9999"

    @mock.patch("src.copy_config.copy_tsc.copy_file_from_repo")
    def test_config_to_from_yaml(self, mock_copy_file_from_repo):
        test_file = "tests/config-data/test.yaml"
        project_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        path = os.path.join(project_root_dir, test_file)
        mock_copy_file_from_repo.return_value = path

        try:
            config_set = ConfigurationSet(
                config_items=[{"name": "HELLLOTHRE", "value-type": "set"}],
                flow_racks=[{"location-id": 9999, "mfc-ref-code": "mfc"}],
                spokes=[{"name": "HELLO"}],
                tote_types=[{"key1": "9999"}],
                staging_config=[{"Hello": 1}],
                staging_locations=[{"Hello": 1}],
                src_routes=[{}],
                locations=[{"location-id": 9999, "mfc-ref-code": "mfc"}],
            )
            config_to_yaml(path, config_set)
            loaded_config = config_from_yaml(path)
            self.assertEqual(config_set, loaded_config)
        finally:
            delete_file(path)
