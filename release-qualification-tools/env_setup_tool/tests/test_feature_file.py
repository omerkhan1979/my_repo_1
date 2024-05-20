from env_setup_tool.src.config_types import ConfigType, TSCConfigType, IMSConfigType
from env_setup_tool.src.feature_file import FeatureFile


def test_feature_file_yaml_loading():
    feature_file = FeatureFile.from_yaml("env_setup_tool/tests/test_data", "base.yaml")
    assert feature_file.key == "base_key"
    assert feature_file.title == "base_title"
    assert feature_file.description == "base_description"

    assert ConfigType.TSC.value in feature_file.configs
    tsc_composite = feature_file.configs[ConfigType.TSC.value]
    assert len(tsc_composite.configs) == 8
    assert tsc_composite.configs[TSCConfigType.LOCATIONS.value].data == {
        "locations-test": "test"
    }
    assert tsc_composite.configs[TSCConfigType.CONFIG_ITEMS.value].data == {
        "config-items-test": "test"
    }
    assert ConfigType.IMS.value in feature_file.configs
    ims_composite = feature_file.configs[ConfigType.IMS.value]
    assert len(ims_composite.configs) == 2
    assert feature_file.configs[ConfigType.IMS.value].configs[
        IMSConfigType.ADDRESSES.value
    ].data == {"addresses": "test"}

    assert ConfigType.SleepingAreaRules.value in feature_file.configs
