from src.utils.service_catalog import modify_value


def test_modify_value_boolean():
    config_item = {
        "categories": ["pickerman", "isps"],
        "name": "ISPS_ENABLED",
        "value": "true",
        "location-code-tom": "0068",
        "value-type": "boolean",
    }
    expected_config_item = {
        "categories": ["pickerman", "isps"],
        "name": "ISPS_ENABLED",
        "value": True,
        "location-code-tom": "0068",
        "value-type": "boolean",
    }

    modify_item = modify_value(config_item)
    assert modify_item == expected_config_item
