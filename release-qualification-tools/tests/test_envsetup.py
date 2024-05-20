#!/usr/bin/env python3
import yaml
from pytest import mark


@mark.odeenvsetup
def test_get_environment_variables(garden_file):
    with open(garden_file) as file:
        data = yaml.safe_load(file)

    env_vars = {
        "FIREBASE_KEY": "AIzaSyB21EBh0L4R0enU_1vqODNkrTgjoBQWn0M",
        "GOOGLE_PROJECTS_ID": data.get("google_project_id"),
        "BASE_DOMAIN": data.get("env_domain"),
        "ODE_RETAILER": data.get("retailer_name"),
        "INTEGRATION_ETL_BUCKET_NAME": data.get("integration_etl_bucket_name"),
        "IAP_CLIENT_ID": data.get("outbound", {}).get("iap_client_id"),
    }

    env_str = ""
    for key, value in env_vars.items():
        env_str += f"{key}={value} "

    # Return the environment variables string
    return env_str.strip()
