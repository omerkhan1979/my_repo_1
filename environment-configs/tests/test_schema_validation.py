import os

import pytest

from validators.schema_validator import (
    validate_config,
    validate_referenced_configs,
    validate_feature_config_file,
)


@pytest.mark.parametrize(
    "filename",
    [
        "tests/data/feature_valid.yaml",
        "tests/data/valid_feature2.yaml",
    ],
)
def test_valid_feature_schema_validation(filename):
    root_dir = os.path.dirname(os.path.dirname(__file__))
    schema = os.path.join(root_dir, "schemas/feature-schema.json")
    result, message = validate_config(filename, schema)
    assert result, f"Validation failed for valid data in {filename}"


@pytest.mark.parametrize(
    "filename",
    [
        "tests/data/invalid_absent_required_field.yaml",
    ],
)
def test_invalid_feature_schema_validation(filename):
    schema = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "schemas/feature-schema.json"
    )
    valid, error = validate_config(filename, schema)
    assert not valid, f"Validation passed for invalid data in {filename}"


def test_product_catalog_doesnt_error():
    errors = validate_referenced_configs(
        "product_catalog", "features_data/templates/product-catalog.json", []
    )
    assert len(errors) == 0


def test_unrecognized_config_type():
    errors = validate_referenced_configs(
        "config_type", "features_data/templates/ims-addresses.yaml", []
    )
    assert len(errors) == 1


def test_file_path_doesnt_exist():
    errors = validate_referenced_configs(
        "sleeping_area_rules", "features_data/sleeping-area-file.yaml", []
    )
    assert len(errors) == 1


def test_validate_feature_config_file_happy_path():
    errors = validate_feature_config_file("tests/data/valid_feature2.yaml")
    assert len(errors) == 0


def test_validate_feature_config_unknown_path():
    errors = validate_feature_config_file(
        "tests/data/feature-invalid-config-paths.yaml"
    )
    assert len(errors) == 2

def test_fulfillment_profiles_doesnt_error():
    errors = validate_referenced_configs(
        "fulfillment_profiles", "features_data/templates/fulfillment-profiles.yaml", []
    )
    assert len(errors) == 0