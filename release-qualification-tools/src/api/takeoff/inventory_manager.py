import requests

from src.api.takeoff.base_api_takeoff import BaseApiTakeoff
from src.api.takeoff.tsc import TSC
from src.config.config import Config
from src.utils.http import handle_response
from src.utils.config import make_inventorymanager_url


class InventoryManager(BaseApiTakeoff):
    def __init__(self, my_config: Config):
        self.config = my_config
        self.default_headers = {
            "X-Token": self.config.token,
        }
        self.base_url = make_inventorymanager_url(my_config.env)

    # TODO PROD-11507: Need to implement changes in base_api_takeoff file to resolve the default_headers return structure
    def inventory_snapshot(self, tsc: TSC) -> dict:
        print(self.base_url)
        location_code_retailer = tsc.get_location_code("location-code-retailer")

        url = (
            self.base_url
            + f"/sites/{self.config.retailer}_{location_code_retailer}/inventorySnapshot"
        )

        response = requests.get(url=url, headers=self.default_headers)
        return handle_response(response, 200, 201)
