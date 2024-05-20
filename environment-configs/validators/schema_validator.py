import json
import os
import sys
from pathlib import Path

import yaml
from jsonschema import validate, ValidationError


def validate_config(yaml_file_path, schema_file) -> (bool, str):
    with open(schema_file, "r") as f:
        schema = json.load(f)
    with open(yaml_file_path, "r") as file:
        data = yaml.safe_load(file)
    try:
        validate(instance=data, schema=schema)
        print(f"File {yaml_file_path} is valid")
        return True, None
    except ValidationError as e:
        return False, str(e)


# SCHEMA_LIST is a dictionary mapping each config type to its validation schema file.
SCHEMA_LIST = {
    "feature": "schemas/feature-schema.json",
    "sleeping_area_rules": "schemas/sleeping-area-rules.json",
    "tsc.locations": "schemas/tsc-locations-schema.json",
    "tsc.spokes": "schemas/tsc-locations-schema.json",
    "tsc.staging_config": "schemas/tsc-staging-config-schema.json",
    "tsc.flow_racks": "schemas/tsc-flow-racks-schema.json",
    "tsc.tote_types": "schemas/tsc-tote-types-schema.json",
    "tsc.routes": "schemas/tsc-routes-schema.json",
    "tsc.config_items": "schemas/tsc-config-items-schema.json",
    "tsc.staging_locations": "schemas/tsc-staging-locations-schema.json",
    "ims.addresses": "schemas/ims-addresses-schema.json",
    "ims.reason_codes": "schemas/ims-reason-codes-schema.json",
    "waves": "schemas/waves-schema.json",
    "site_info.sites": "schemas/site-info-sites-schema.json",
    "site_info.retailer": "schemas/site-info-retailer-schema.json",
    "fulfillment_profiles": "schemas/fulfilment-profiles-schema.json",
}

SKIP_VALIDATION = ["product_catalog"]


def validate_feature_config_file(file_path: str) -> list[str]:
    """
    Validates a feature configuration file against a schema and checks referenced config files.

    This function performs two main validations:
    1. Validates the feature configuration file itself against its schema.
    2. Validates each referenced under "configs" file, based on their type

    Args:
    - file_path (str): Path to the feature configuration file.

    Returns:
    - List[str]: A list of error messages encountered during validation. An empty list
      indicates successful validation with no errors found.
    """
    errors = []
    # first validate feature config file against schema
    is_feature_file_valid, err = validate_config(file_path, SCHEMA_LIST.get("feature"))
    if is_feature_file_valid:
        # continue with referenced config files
        with open(file_path, "r") as file:
            data = yaml.safe_load(file)
        for cfg_type, cfg_value in data["configs"].items():
            if "path" in cfg_value:  # simple config
                validate_referenced_configs(cfg_type, cfg_value.get("path"), errors)
            else:  # complex config
                for cfg_subtype, cfg_sub_value in cfg_value.items():
                    complex_cfg = f"{cfg_type}.{cfg_subtype}"
                    validate_referenced_configs(
                        complex_cfg, cfg_sub_value.get("path"), errors
                    )
    else:
        errors.append(err)
    return errors


def validate_referenced_configs(
    cfg_type: str, file_path: str, errors: list
) -> list[str]:
    if cfg_type in SKIP_VALIDATION:
        print(f"Skipping validation of {cfg_type} with file {file_path}")
        return errors
    elif cfg_type not in SCHEMA_LIST:
        errors.append(f"No schema found for config {cfg_type}")
        return errors
    elif not Path(file_path).exists():
        errors.append(f"Could not find file {file_path}")
        return errors
    else:
        is_valid, err = validate_config(file_path, SCHEMA_LIST.get(cfg_type))
        if not is_valid:
            errors.append(err)
    return errors


def main():
    files = [f for f in sys.argv[1:] if os.path.basename(f).startswith("feature") or os.path.basename(f) == "base.yaml"]
    validation_errors = {}

    for file in files:
        file_errors = validate_feature_config_file(file)
        if file_errors:
            validation_errors[file] = file_errors

    if validation_errors:
        for k, v in validation_errors.items():
            print("========================================================")
            print(f"Validation errors found in file {k}. See details below:")
            for error in v:
                print(error)
        exit(1)
    else:
        print("All files validated successfully.")
        exit(0)


if __name__ == "__main__":
    main()
