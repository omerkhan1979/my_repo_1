from functools import partial
import requests

from src.api.takeoff.base_api_takeoff import BaseApiTakeoff
from src.utils.http import handle_response
from src.utils.config import get_url_builder
from src.config.config import get_token, Config


class AuthService(BaseApiTakeoff):
    url_builder = get_url_builder("api/", "as")

    users_endpoint = "v2/users"
    user_info_endpoint = "v2/users/{}"
    user_roles_endpoint = "v2/users/{}/roles"

    def __init__(self, my_config: Config, url_builder=None, use_user_token=False):
        self.config = my_config

        self.url_builder = partial(
            url_builder or self.url_builder, my_config.retailer, my_config.env
        )
        if use_user_token:
            token = my_config.token
        else:
            token = get_token(my_config.retailer, my_config.env)
        self.default_headers = {
            "X-Token": token,
            "accept": "application/json",
            "content-type": "application/json",
        }

    def get_users(self):
        url = self.url_builder(rel=self.users_endpoint)
        response = requests.get(url=url, headers=self.default_headers)
        return handle_response(response, 200)

    def get_user(self, user_id):
        url = self.url_builder(rel=self.user_info_endpoint.format(user_id))
        response = requests.get(url=url, headers=self.default_headers)
        return handle_response(response, 200)

    def update_user(self, user_id, body):
        url = self.url_builder(rel=self.user_info_endpoint.format(user_id))
        response = requests.put(url=url, headers=self.default_headers, json=body)
        return handle_response(response, 200)

    def create_user(self, email, password, display_name):
        url = self.url_builder(rel=self.users_endpoint)
        body = {
            "email": email,
            "password": password,
            "display-name": display_name,
        }
        response = requests.post(url=url, headers=self.default_headers, json=body)
        return handle_response(response, 201)

    def set_user_role(self, user_id, user_role, location_id):
        url = self.url_builder(rel=self.user_roles_endpoint.format(user_id))
        body = [
            {
                "role": user_role,
                "locations": [location_id or self.config.location_code_tom],
            }
        ]
        response = requests.put(url=url, headers=self.default_headers, json=body)
        return handle_response(response, 200)

    def get_user_id(self, user_email: str) -> str:
        """Will return a user-id or raise RuntimeError if no such user_email"""
        response_get_users = self.get_users()["data"]
        for user in response_get_users:
            if user["user-email"] == user_email:
                return user["user-id"]
        else:
            raise RuntimeError(f"Could not find user '{user_email}'")
