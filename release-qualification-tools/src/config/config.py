import base64
import os
import sys
from typing import Optional
import pytz
import requests
import yaml
from functools import partial
from src.utils.http import handle_response
from src.config.constants import (
    CUSTOM_PRODUCTS_ARG_INDEX,
    FIREBASE_KEYS,
    GCP_PROJECT_IDS,
)
from src.utils.config import make_env_url, url_builder
from src.utils.console_printing import bold, yellow
from src.utils.locations import is_location_code_tom_valid
from datetime import datetime, timedelta
import argparse


class Config:
    def __init__(
        self,
        retailer,
        env: str,
        location_code_tom: str,
        token: str,
        user_role: str = "",
        user_id: str = "",
        user: str = "",
        password: str = "",
        user_products=None,
        disallow=True,
        skip_location_check=False,
    ):
        self.token = token
        self.retailer = retailer
        if disallow and env in ["prod"]:
            raise ValueError("Cannot be run on production environment")
        else:
            self.env = env
        self.user = user
        self.password = password
        if env == "ode":
            self.sftp_username = "integration-api-sftp"
            self.sftp_password = "integration-api-sftp"
        else:
            self.sftp_username = "k1705kch"
            self.sftp_password = "k1705kch"
        self.user_role = user_role
        self.user_id = user_id
        self.google_project_id = get_gcp_project_id(retailer, env)

        self.user_tom_ids = user_products if user_products else None

        self.url = make_env_url(self.retailer, self.env)

        self.in_store_picking_url = url_builder(
            "",
            "isps",
            self.retailer,
            self.env,
            rel="picking-service/",
        )
        self.decanting_ui_url = url_builder(
            "",
            "decanting-ui",
            self.retailer,
            self.env,
            rel=f"?locationId={location_code_tom}",
        )

        self.tom_ui_url = partial(
            url_builder,
            "",
            "",
            self.retailer,
            self.env,
        )

        if skip_location_check:
            self.location_code_tom = location_code_tom
        else:
            valid_code = is_location_code_tom_valid(
                retailer, env, token, location_code_tom
            )
            if valid_code is None:
                sys.exit(1)
            else:
                self.location_code_tom = valid_code

        self.firebase_key = get_firebase_key(retailer, env)
        if user and password:
            self.user_token = get_user_token(self.firebase_key, user, password)
        else:
            self.user_token = None

        self.integration_etl_bucket_name = (
            {
                "maf": {"qai": "tkf-maf-qai-integration-etl"},
            }
            .get(retailer, {})
            .get(
                env,
                os.environ.get("INTEGRATION_ETL_BUCKET_NAME"),
            )
        )

        if not self.integration_etl_bucket_name:
            self.integration_etl_bucket_name = f"tkf-{os.environ.get('ODE_RETAILER', self.retailer)}-{self.env}-integration-etl"

    def __repr__(self):
        return f'Config("{self.url}","{self.env}","{self.token}","{self.retailer}","{self.user_tom_ids}","{self.in_store_picking_url}","{self.decanting_ui_url}","{self.location_code_tom}","{self.firebase_key}","{self.user_token}",{self.integration_etl_bucket_name})'


def get_tom_ids_from_args(start_index) -> list:
    # to support passing tom ids from next arguments
    tom_ids = sys.argv[start_index:]
    if not len(tom_ids):
        # if tom ids are not passed (just p), user will be asked to enter tom ids
        tom_ids = input(
            bold("Enter tom-ids separated by comma, e.g 111222333,444555333: ")
        ).split(",")
    return tom_ids


def get_user_password_tom_ids_from_args(start_index):
    user: Optional[str] = None
    password: Optional[str] = None
    tom_ids = []
    try:
        # Reading additional arguments. They can be user/password for Firestore or list of tom_ids
        extra_param = sys.argv[start_index]
        if extra_param == "p":
            # In case for list of tom_ids
            tom_ids = get_tom_ids_from_args(start_index + 1)
        else:
            # In case of user/passwords was passed
            user = extra_param
            extra_param = sys.argv[start_index + 1]
            password = extra_param
            # If tom_ids section is also present:
            if len(sys.argv) > start_index + 2 and sys.argv[start_index + 2] == "p":
                tom_ids = get_tom_ids_from_args(start_index + 3)
    except IndexError:
        print(yellow("Index issue with args"))
    return user, password, tom_ids


def get_config() -> tuple:
    parser = argparse.ArgumentParser(
        description="CLI --r for retailer, --e for env , --l for location, --d for day (optional if not passed default will be set to 1), --h for hour (optional if not passed default will be set to 1)"
    )
    parser.add_argument("--r", type=str)
    parser.add_argument("--e", type=str)
    parser.add_argument("--l", type=str)
    parser.add_argument("--d", type=str, default=1, nargs="?")
    parser.add_argument("--h", type=str, default=1, nargs="?")
    parser.add_argument("--u", type=str, default="", nargs="?")
    parser.add_argument("--p", type=str, default="", nargs="?")
    args = parser.parse_args()

    if args.r:
        retailer = args.r
    else:
        retailer = input(bold("retailer (tienda, maf, ...): "))

    if args.e:
        env = args.e
    else:
        env = input(bold("env (qai, dev, ...): "))

    if args.l:
        location = args.l
    else:
        location = input(bold("location-code-tom (GJJ, ABS3116, ...): "))

    day = None
    if args.d:
        day = args.d

    hour = None
    if args.h:
        hour = args.h

    user = args.u
    password = args.p

    token = get_token(retailer, env)
    return (
        retailer,
        env,
        location,
        token,
        None,
        None,
        user,
        password,
        None,
        True,
        False,
        day,
        hour,
    )


def get_config_fastapi(retailer, env, location):
    _, _, tom_ids = get_user_password_tom_ids_from_args(CUSTOM_PRODUCTS_ARG_INDEX)

    token = get_token(retailer, env)

    return (
        retailer,
        env,
        location,
        token,
        tom_ids,
    )


def get_config_date(day, hour):
    now_utc = datetime.now().astimezone(pytz.utc)
    td = timedelta(days=int(day), hours=int(hour), minutes=0)
    my_date = now_utc + td
    date = my_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    return date


def get_token(retailer, env):
    current_path = os.path.dirname(__file__)
    path_to_file = os.path.join(
        current_path, f"shared-tokens/helm/env/{env}/{retailer}/values.yaml"
    )
    if os.path.exists(path_to_file):
        env_yaml = open(path_to_file)
        values = yaml.load(env_yaml, Loader=yaml.FullLoader)
        return base64.b64decode(values["retailer_specific"]["SERVICE_WORKER_TOKEN"])
    else:
        if os.environ.get("SERVICE_WORKER_TOKEN"):
            return os.environ.get("SERVICE_WORKER_TOKEN")
        else:
            raise RuntimeError(
                f"Need to have either '{path_to_file}' on the filesystem or 'SERVICE_WORKER_TOKEN' defined on the environment"
            )


def get_user_token(firebase_key, user, password) -> str:
    """Returns an id Token for a given user or raises RuntimeError if user and password are not supplied"""
    if not (user and password):
        raise RuntimeError(
            f"Get user token called with incomplete information User: '{user}' Pass: '{password}'"
        )
    response = requests.post(
        url=f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={firebase_key}",
        json={
            "email": f"{user}",
            "password": f"{password}",
            "returnSecureToken": True,
        },
    )
    response.raise_for_status()
    return response.json()["idToken"]


def delete_user(idtoken, firebase_key):
    response = requests.post(
        url=f"https://identitytoolkit.googleapis.com/v1/accounts:delete?key={firebase_key}",
        json={"idToken": f"{idtoken}"},
    )
    handle_response(response, 200)


def get_gcp_project_id(retailer: str, env: str) -> str:
    env_value = os.environ.get("GOOGLE_PROJECT_ID")
    if env_value and env_value != "prj-release-qual-tools-2c2c":
        return env_value
    return GCP_PROJECT_IDS[f"{retailer}-{env}"]


def get_firebase_key(retailer: str, env):
    """
    Get the retailer-auth firepace projects API key. You probably want to get
    this from `Config.firebase_key` in most cases and use this function only in
    exceptional circumstances.
    """
    env_value = os.environ.get("FIREBASE_KEY")
    if env_value:
        return env_value
    return FIREBASE_KEYS[f"{retailer}-{env}"]
