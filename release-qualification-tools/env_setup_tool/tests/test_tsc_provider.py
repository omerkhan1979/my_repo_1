import os
import sys
from unittest.mock import patch, Mock

import pytest
import requests_mock

from src.api.takeoff.ops_api import OpsApi
from src.api.takeoff.tsc import TSC
from src.config.config import Config, get_token
from env_setup_tool.src import config_types
from env_setup_tool.src.config_providers.tsc_provider import TscProvider
from env_setup_tool.src.config_types import CompositeConfig, TSCConfigType
from env_setup_tool.src.feature_file import FeatureFile

project_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_root_dir)


@pytest.fixture
@patch.dict(os.environ, {"SERVICE_WORKER_TOKEN": "ondemand_dummy_worker_token"})
def tsc_prereq():
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
            tsc_provider = TscProvider(cfg)
            return tsc_provider


def test_apply_config_with_invalid_key(tsc_prereq):
    with patch.object(
        tsc_prereq, "apply_tote_types", return_value=True
    ) as mock_apply_tote_types:
        key = "invalid_key"
        subconfig_data = CompositeConfig(
            configs={
                "tote_types": config_types.Config(
                    path="tsc-tote-types-isps.yaml",
                    data={"barcode-format-name": "test"},
                )
            }
        )
        with patch(
            "env_setup_tool.src.config_types.TSCConfigType.get_tsc_config_type",
            return_value="invalid_tsc_type",
        ):
            res = tsc_prereq.apply(subconfig_data, key)
            assert len(res) == 1

            for k, v in res.items():
                assert v is False
            mock_apply_tote_types.assert_not_called()


def test_tote_types_apply(tsc_prereq):
    with patch.object(
        tsc_prereq.service, "post_tote_type", return_value=True
    ) as mock_tsc_post_tote_type:
        key = "tote_types"
        subconfig_data = CompositeConfig(
            configs={
                "tote_types": config_types.Config(
                    path="tsc-tote-types-isps.yaml",
                    data=[{"barcode-format-name": "test"}],
                )
            }
        )
        with patch(
            "src.api.takeoff.tsc.TSC.get_tote_location_types",
            return_value=[{"tote-kind-name": "storage"}],
        ):
            res = tsc_prereq.apply(subconfig_data, key)
            assert len(res) == 1
            for k, v in res.items():
                assert k == "tsc.tote_types"
                assert v is True
            mock_tsc_post_tote_type.assert_called()


def test_flow_racks_apply(tsc_prereq):
    with patch.object(
        tsc_prereq.service, "put_flow_racks", return_value=True
    ) as mock_tsc_put_flow_racks:
        subconfig_data = CompositeConfig(
            configs={
                "flow_racks": config_types.Config(
                    path="tsc-flow-racks-isps.yaml",
                    data={
                        "location-code-tom": "9999",
                        "flow-racks": {
                            "1": "R9L2P01",
                            "2": "R11L2P01",
                        },
                    },
                )
            }
        )
        with patch(
            "src.api.takeoff.tsc.TSC.get_flow_racks",
            return_value={
                "location-code-tom": "9999",
                "flow-racks": {
                    "1": "R12L2P01",
                },
            },
        ):
            res = tsc_prereq.apply(subconfig_data)
            assert len(res) == 1
            for k, v in res.items():
                assert k == "tsc.flow_racks"
                assert v is True
            mock_tsc_put_flow_racks.assert_called()


def test_put_flow_racks_apply_is_not_called_if_configs_are_the_same(tsc_prereq):
    with patch.object(
        tsc_prereq.service, "put_flow_racks", return_value=True
    ) as mock_tsc_put_flow_racks:
        subconfig_data = CompositeConfig(
            configs={
                "flow_racks": config_types.Config(
                    path="tsc-flow-racks-isps.yaml",
                    data={
                        "location-code-tom": "9999",
                        "flow-racks": {
                            "1": "R9L2P01",
                            "2": "R11L2P01",
                        },
                    },
                )
            }
        )
        with patch(
            "src.api.takeoff.tsc.TSC.get_flow_racks",
            return_value={
                "location-code-tom": "9999",
                "flow-racks": {
                    "1": "R9L2P01",
                    "2": "R11L2P01",
                },
            },
        ):
            res = tsc_prereq.apply(subconfig_data, "flow_racks")
            assert len(res) == 1
            for k, v in res.items():
                assert k == "tsc.flow_racks"
                assert v is True
            mock_tsc_put_flow_racks.assert_not_called()


def test_post_new_location(tsc_prereq):
    with patch.object(
        tsc_prereq.service, "set_location_availability", return_value=True
    ) as mock_set_location_availability, patch.object(
        OpsApi, "initialize_picking_queue", return_value=True
    ):
        subconfig_data = CompositeConfig(
            configs={
                "locations": config_types.Config(
                    path="tsc-locations-test.yaml",
                    data=[
                        {
                            "location-code-gold": "99",
                            "location-code-retailer": "9999",
                            "location-code-tom": "9999",
                            "location-id": 1,
                            "location-type": "mfc",
                            "mfc-ref-code": "9999",
                        }
                    ],
                )
            }
        )
        with patch(
            "src.api.takeoff.tsc.TSC.get_tom_code_locations",
            return_value=[
                {
                    "location-code-gold": "88",
                    "location-code-retailer": "8888",
                    "location-code-tom": "8888",
                    "location-id": 1,
                    "location-type": "mfc",
                    "mfc-ref-code": "8888",
                }
            ],
        ):
            with patch(
                "src.api.takeoff.tsc.TSC.post_mfc_location",
                return_value={
                    "location-code-gold": "99",
                    "location-code-retailer": "9999",
                    "location-code-tom": "9999",
                    "location-id": 1,
                    "location-type": "mfc",
                    "mfc-ref-code": "9999",
                },
            ):
                tsc_prereq.apply(subconfig_data, "locations")
                tsc_prereq.service.post_mfc_location.assert_called_once()
                mock_set_location_availability.assert_called_once()


def test_update_existing_location(tsc_prereq):
    with patch.object(
        tsc_prereq.service, "set_location_availability", return_value=True
    ) as mock_set_location_availability, patch.object(
        tsc_prereq.service, "update_location", return_value=True
    ) as mock_update_location, patch.object(
        tsc_prereq.service, "post_mfc_location", return_value=True
    ) as mock_post_mfc_location, patch.object(
        TSC,
        "get_tom_code_locations",
        return_value=[
            {
                "location-code-gold": "99",
                "location-code-retailer": "9999",
                "location-code-tom": "9999",
                "location-id": 1,
                "location-type": "mfc",
                "mfc-ref-code": "9999",
                "location-service-info": {"desctext": "another text"},
            }
        ],
    ):
        subconfig_data = CompositeConfig(
            configs={
                "locations": config_types.Config(
                    path="tsc-locations-test.yaml",
                    data=[
                        {
                            "location-code-gold": "99",
                            "location-code-retailer": "9999",
                            "location-code-tom": "9999",
                            "location-id": 1,
                            "location-type": "mfc",
                            "mfc-ref-code": "9999",
                            "location-service-info": {"desctext": "some text"},
                        }
                    ],
                )
            }
        )
        tsc_prereq.apply(subconfig_data, "locations")
        mock_post_mfc_location.assert_not_called()
        mock_update_location.assert_called_once()
        mock_set_location_availability.assert_not_called()


def test_post_new_spoke(tsc_prereq):
    with patch.object(
        tsc_prereq.service, "update_location_spoke", return_value=True
    ), patch.object(
        tsc_prereq.service, "create_location_spoke", return_value=True
    ) as mock_create_location_spoke:
        subconfig_data = CompositeConfig(
            configs={
                "spokes": config_types.Config(
                    path="tsc-totes-test.yaml",
                    data=[
                        {
                            "location-code-gold": "11",
                            "location-code-retailer": "1111",
                            "location-code-tom": "1111",
                            "location-id": 5,
                            "location-type": "spoke",
                            "mfc-ref-code": "9999",
                        }
                    ],
                )
            }
        )
        with patch(
            "src.api.takeoff.tsc.TSC.get_tom_code_locations",
            return_value=[
                {
                    "location-code-gold": "99",
                    "location-code-retailer": "9999",
                    "location-code-tom": "9999",
                    "location-id": 1,
                    "location-type": "mfc",
                    "mfc-ref-code": "9999",
                }
            ],
        ):
            with patch(
                "src.api.takeoff.tsc.TSC.get_locations",
                return_value=[
                    {
                        "location-code-gold": "99",
                        "location-code-retailer": "9999",
                        "location-code-tom": "9999",
                        "location-id": 1,
                        "location-type": "mfc",
                        "mfc-ref-code": "9999",
                    }
                ],
            ):
                tsc_prereq.apply(subconfig_data, "spokes")
                mock_create_location_spoke.assert_called_once()


def test_update_existing_spoke(tsc_prereq):
    with patch.object(
        tsc_prereq.service, "update_location_spoke", return_value=True
    ) as mock_update_location_spoke, patch.object(
        tsc_prereq.service, "set_location_availability", return_value=True
    ), patch.object(
        tsc_prereq,
        "is_location_exist_and_enabled",
        return_value=[
            True,
            True,
            [
                {
                    "location-code-gold": "11",
                    "location-code-retailer": "1111",
                    "location-code-tom": "1111",
                    "location-id": 5,
                    "location-type": "spoke",
                    "mfc-ref-code": "9999",
                }
            ],
        ],
    ):
        subconfig_data = CompositeConfig(
            configs={
                "spokes": config_types.Config(
                    path="tsc-totes-test.yaml",
                    data=[
                        {
                            "location-code-gold": "11",
                            "location-code-retailer": "1111",
                            "location-code-tom": "1111",
                            "location-id": 5,
                            "location-type": "spoke",
                            "mfc-ref-code": "9999",
                        }
                    ],
                )
            }
        )
        with patch(
            "src.api.takeoff.tsc.TSC.get_tom_code_locations",
            return_value=[
                {
                    "location-code-gold": "99",
                    "location-code-retailer": "9999",
                    "location-code-tom": "9999",
                    "location-id": 1,
                    "location-type": "mfc",
                    "mfc-ref-code": "9999",
                }
            ],
        ):
            with patch(
                "src.api.takeoff.tsc.TSC.get_locations",
                return_value=[
                    {
                        "location-code-gold": "99",
                        "location-code-retailer": "9999",
                        "location-code-tom": "9999",
                        "location-id": 1,
                        "location-type": "mfc",
                        "mfc-ref-code": "9999",
                    },
                    {
                        "location-code-gold": "11",
                        "location-code-retailer": "1111",
                        "location-code-tom": "1111",
                        "location-id": 5,
                        "location-type": "spoke",
                        "mfc-ref-code": "9999",
                    },
                ],
            ):
                tsc_prereq.apply(subconfig_data, "spokes")
                mock_update_location_spoke.assert_called_once()


def test_post_staging_loc(tsc_prereq):
    with patch.object(
        tsc_prereq.service, "post_staging_location", return_value=True
    ) as mock_post_staging_location, patch.object(
        tsc_prereq.service, "put_default_staging_location", return_value=True
    ) as mock_put_default_staging_location:
        subconfig_data = CompositeConfig(
            configs={
                "staging_locations": config_types.Config(
                    path="tsc-staging-locations-test.yaml",
                    data=[
                        {
                            "default": False,
                            "mfc-tom-code": "9999",
                            "staging-location-code": "9999H010011B",
                        },
                        {
                            "default": False,
                            "mfc-tom-code": "9999",
                            "staging-location-code": "9999H010012B",
                        },
                    ],
                )
            }
        )
        tsc_prereq.apply(subconfig_data, "staging_locations")
        assert mock_post_staging_location.call_count == 2
        mock_put_default_staging_location.assert_not_called()


def test_post_default_staging_loc(tsc_prereq):
    with patch.object(
        tsc_prereq.service, "post_staging_location", return_value=True
    ) as mock_post_staging_location, patch.object(
        tsc_prereq.service, "put_default_staging_location", return_value=True
    ) as mock_put_default_staging_location:
        subconfig_data = CompositeConfig(
            configs={
                "staging_locations": config_types.Config(
                    path="tsc-staging-locations-test.yaml",
                    data=[
                        {
                            "default": True,
                            "mfc-tom-code": "9999",
                            "staging-location-code": "9999H010011B",
                        }
                    ],
                )
            }
        )
        tsc_prereq.apply(subconfig_data, "staging_locations")
        mock_post_staging_location.assert_called_once()
        mock_put_default_staging_location.assert_called_once()


def test_post_staging_config(tsc_prereq):
    with patch.object(
        tsc_prereq.service, "post_staging_configurations", return_value=True
    ) as mock_post_staging_configurations:
        subconfig_data = CompositeConfig(
            configs={
                "staging_config": config_types.Config(
                    path="tsc-staging-config.yaml",
                    data={
                        "mfc-tom-code": "9999",
                        "staging-configurations": [
                            {
                                "staging-location-code": "9999H010003B",
                                "mapped-routes": [{"type": "ROUTE", "code": "DDS"}],
                            }
                        ],
                    },
                )
            }
        )
        res = tsc_prereq.apply(subconfig_data)
        for k, v in res.items():
            assert k == "tsc.staging_config"
            assert v is True
        mock_post_staging_configurations.assert_called_once()


def test_post_routes(tsc_prereq):
    with patch.object(
        tsc_prereq.service, "post_route", return_value=True
    ) as mock_post_route:
        subconfig_data = CompositeConfig(
            configs={
                "routes": config_types.Config(
                    path="tsc-routes-config.yaml",
                    data=[
                        {"mfc-tom-code": "9999", "route-code": "AXL"},
                        {"mfc-tom-code": "9999", "route-code": "NUR"},
                    ],
                )
            }
        )
        res = tsc_prereq.apply(subconfig_data, "routes")
        for k, v in res.items():
            assert k == "tsc.routes"
            assert v is True
        assert mock_post_route.call_count == 2


def test_config_items(tsc_prereq):
    with patch.object(
        tsc_prereq.service, "put_config_items", return_value=True
    ) as mock_put_config_items:
        subconfig_data = CompositeConfig(
            configs={
                "config_items": config_types.Config(
                    path="tsc-config-items.yaml",
                    data=[
                        {
                            "categories": ["test-category"],
                            "name": "config_test",
                            "value": 0.84,
                            "location-code-tom": None,
                            "value-type": "numeric",
                        }
                    ],
                )
            }
        )
        res = tsc_prereq.apply(subconfig_data, "config_items")
        for k, v in res.items():
            assert k == "tsc.config_items"
            assert v is True
        mock_put_config_items.assert_called_once()


def test_config_order(tsc_prereq):
    manager = Mock()
    with patch.object(
        tsc_prereq, "apply_flow_racks", return_value={"tsc.flow_racks": True}
    ) as mock_flow_racks, patch.object(
        tsc_prereq, "apply_locations", return_value={"tsc.locations": True}
    ) as mock_apply_locations, patch.object(
        tsc_prereq, "apply_config_items", return_value={"tsc.config_items": True}
    ) as mock_apply_config_items, patch.object(
        tsc_prereq, "apply_spokes", return_value={"tsc.spokes": True}
    ) as mock_spokes, patch.object(
        tsc_prereq, "apply_tote_types", return_value={"tsc.tote_types": True}
    ) as mock_apply_tote_types, patch.object(
        tsc_prereq, "apply_staging_config", return_value={"tsc.staging_config": True}
    ) as mock_apply_staging_config, patch.object(
        tsc_prereq,
        "apply_staging_locations",
        return_value={"tsc.staging_locations": True},
    ) as mock_apply_staging_locations, patch.object(
        tsc_prereq, "apply_routes", return_value={"tsc.routes": True}
    ) as mock_apply_routes:
        # Attach the mocks to the manager
        manager.attach_mock(mock_apply_locations, "apply_locations")
        manager.attach_mock(mock_apply_config_items, "apply_config_items")
        manager.attach_mock(mock_flow_racks, "apply_flow_racks")
        manager.attach_mock(mock_spokes, "apply_spokes")
        manager.attach_mock(mock_apply_tote_types, "apply_tote_types")
        manager.attach_mock(mock_apply_staging_config, "apply_staging_config")
        manager.attach_mock(mock_apply_staging_locations, "apply_staging_locations")
        manager.attach_mock(mock_apply_routes, "apply_routes")

        ff_content = FeatureFile.from_yaml(
            "env_setup_tool/tests/test_data",
            "base.yaml",
        )

        tsc_prereq.apply(ff_content.configs.get("tsc"))

        actual_method_names = [
            m[0] for m in manager.mock_calls if "__bool__" not in str(m)
        ]
        print(actual_method_names)
        expected_method_names = ["apply_" + config.value for config in TSCConfigType]
        assert expected_method_names == actual_method_names
