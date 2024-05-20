import requests

from src.api.takeoff.base_api_takeoff import BaseApiTakeoff
from src.utils.http import handle_response
from src.utils.config import get_url_builder


class FFTracker(BaseApiTakeoff):
    url_builder = get_url_builder("api/", "fulfillment-tracker")

    order_totes_endpoint = "v1/order-totes"

    def order_totes(self, order_id):
        url = self.url_builder(rel=self.order_totes_endpoint)
        params = {"order-id": order_id}
        response = requests.get(url=url, params=params, headers=self.default_headers)
        return handle_response(response, 200)
