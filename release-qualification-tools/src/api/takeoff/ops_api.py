"""
Class to interact with ops-api service - legacy python backed for takeoff android app
that is used in MFCs. (Newer service if Pickerman facade)

"""

import requests

from src.api.takeoff.base_api_takeoff import BaseApiTakeoff
from src.utils.console_printing import waiting, done
from src.utils.http import handle_response
from src.utils.config import get_url_builder


class OpsApi(BaseApiTakeoff):
    url_builder = get_url_builder("", "ops-api")
    picking_queue_endpoint = "api/v1/picking-queue/{}"
    create_picking_queue_endpoint = picking_queue_endpoint + "/create_queue/"
    assign_endpoint = picking_queue_endpoint + "/assign/"
    cancel_order_session_endpoint = "api/v1/picking-queue/{}/cancel_order_sessions/"
    inventory_adjust_endpoint = "api/v1/inventory/adjust/"

    def __init__(self, my_config, url_builder=url_builder):
        super().__init__(my_config, url_builder)

        self.default_headers = {
            "X-Token": self.config.token,
            "X-Lang": "en",
            "Accept": "application/json",
        }

    def assign(self, location_id=None):
        url = self.url_builder(
            rel=self.assign_endpoint.format(
                location_id or self.config.location_code_tom
            )
        )

        response = requests.put(
            url=url,
            headers=self.default_headers,
        )
        return handle_response(response, 200, 201, 400)

    def initialize_picking_queue(self, location_code_tom: str, location_id=None):
        url = self.url_builder(
            rel=self.create_picking_queue_endpoint.format(
                location_id or self.config.location_code_tom
            )
        )

        json_body = {
            "queue_id": "",
            "location_id": location_code_tom,
            "location_name": "",
            "queue_size": "",
            "queue_size_approx_number": "0",
            "queue_type": "",
            "session_params": {"object": {}},
        }

        response = requests.post(url=url, headers=self.default_headers, json=json_body)
        return handle_response(response, 200, 201)

    def cancel_order_session(self, session_id):
        url = self.url_builder(
            rel=self.cancel_order_session_endpoint.format(session_id)
        )

        response = requests.delete(
            url=url,
            headers=self.default_headers,
        )
        return handle_response(response, 204, print_details=False, json=False)

    """Helper methods start here"""

    def clear_manual_picking_q(self):
        print(waiting("Clearing manual picking queue..."))
        order_in_q = self.assign().get("session_id")
        while order_in_q:
            self.cancel_order_session(order_in_q)
            print(f"order {order_in_q} removed")
            order_in_q = self.assign().get("session_id")
        print(done("Picking queue cleared!"))

    def inventory_adjust(
        self, address: str, product: str, qty: int, reason: str
    ) -> dict:
        url = self.url_builder(rel=self.inventory_adjust_endpoint)
        body = {
            "location_id": self.config.location_code_tom,
            "shelf_id": address,
            "product_id": product,
            "quantity": qty,
            "reason_code": reason,
        }

        response = requests.post(
            url=url,
            headers=self.default_headers,
            json=body,
        )
        print(
            f"Adjusted product {product} on address {address} at {self.config.location_code_tom} with qty {qty}"
        )
        return handle_response(response, 200, 201)
