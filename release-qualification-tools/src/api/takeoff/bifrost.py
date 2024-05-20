"""
Class to interact with bifrost service
Swagger: https://bifrost-%{location_code_gold}-${env}-${customer}.{base-domain}/
"""

import requests

from src.config.config import Config
from src.utils.http import handle_response
from src.utils.config import make_bifrost_url


class Bifrost:
    health_endpoint = "/health"

    def __init__(self, my_config: Config, location_gold: str):
        self.base_url = make_bifrost_url(
            my_config.retailer, my_config.env, location_gold
        )

    def get_health(self) -> dict:
        """Checks the health for the bifrost service

        Returns:
            dict: data structure of health metrics
        """
        url = self.base_url + self.health_endpoint
        response = requests.get(
            url=url,
        )
        return handle_response(response, 200)

    def get_health_pass(self) -> bool:
        """Returns true if bifrost is healthy

        Returns:
            boolean: true if healthy false other wise
        """
        status = self.get_health().get("status")
        return True if status and status == "pass" else False
