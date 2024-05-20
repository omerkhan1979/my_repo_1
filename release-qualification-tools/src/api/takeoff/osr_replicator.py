import requests

from src.api.takeoff.base_api_takeoff import BaseApiTakeoff
from src.utils.config import get_url_builder
from src.utils.http import handle_response
from src.config.constants import BASE_DOMAIN


class OSRR(BaseApiTakeoff):
    osrr_health_endpoint = "health"

    url_builder = get_url_builder(base=None, service_name="osr-emu")

    def get_osrr_health(self, cfg):
        url = self.get_osrr_url(config=cfg, rel=self.osrr_health_endpoint)
        response = requests.get(url=url)
        return handle_response(response, 200)

    def get_osrr_url(self, config, rel):
        location = config.location_code_tom
        retailer = config.retailer
        env = config.env
        if env != "prod":
            return f"https://osr-emu-{location}-{retailer}-{env}.{BASE_DOMAIN}/{rel}"
        else:
            return f"https://osr-emu-{location}-{retailer}-{env}.tom.takeoff.com/{rel}"
