"""
Class to interact with pickerman facade - newer backed for takeoff android app
that is used in MFCs. (Legacy service is ops-api)

"""

from datetime import datetime
from typing import List, Optional

import requests

from src.api.takeoff.base_api_takeoff import BaseApiTakeoff
from src.config.constants import DEFAULT_USER
from src.utils.http import handle_response
from src.utils.waiters import wait
from src.utils.config import get_url_builder


class PickermanFacade(BaseApiTakeoff):
    url_builder = get_url_builder("api/", "pickerman-facade")

    truck_load_orders_endpoint = "v1/truck/load-orders"
    truck_unload_orders_endpoint = "v1/truck/unload-orders"
    manual_picking_item_decision_endpoint = "v1/manual-picking/item-decisions"
    consolidation_ramp_state_url = (
        "v1/consolidation/ramp-state/{location_code_tom}/{order_id}/"
    )
    consolidate_url = "v4/consolidation/consolidate"
    stage_url = "v2/staging/stage"
    get_order_by_tote_endpoint = "v1/order/order-by-tote/{}"

    def get_order_by_tote(self, tote_id: str):
        url = self.url_builder(self.get_order_by_tote_endpoint.format(tote_id))
        response = requests.get(url=url, headers=self.default_headers)
        handle_response(response, 200)

        order_id = response.json()["order-id"]
        return order_id

    def post_manual_picking_item_decision(
        self,
        order_id: str,
        records: list,
        user_id: Optional[str] = None,
        email: Optional[str] = None,
    ):
        url = self.url_builder(rel=self.manual_picking_item_decision_endpoint)

        body = {
            "clear_items": [],
            "device_serial_number": "Test",
            "is_processed": False,
            "location_id": self.config.location_code_tom,
            "records": records,
            "build_version": "21-11-15.93-CUSTOMER-QAI",
            "order_id": order_id,
            "created_timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "processed_timestamp": None,
            "processing_error": None,
            "bags_qty": 0,
        }
        if user_id and email:
            body["user"] = {"id": user_id, "email": email}
        else:
            body["user"] = DEFAULT_USER
        response = requests.post(
            url=url,
            headers=self.default_headers,
            json=body,
        )
        return handle_response(response, 200)

    @wait
    def assign(self):
        url = self.url_builder(
            rel=f"v1/queue/{self.config.location_code_tom}/orders/assign"
        )
        response = requests.post(url=url, headers=self.default_headers)
        return handle_response(response, 201, print_details=False, raise_error=False)

    def assign_no_wait(self):
        url = self.url_builder(
            rel=f"v1/queue/{self.config.location_code_tom}/orders/assign"
        )
        response = requests.post(url=url, headers=self.default_headers)
        return handle_response(response, 201, print_details=False, raise_error=False)

    def consolidation_ramp_state(self, order_id: str):
        url = self.url_builder(
            self.consolidation_ramp_state_url.format(
                location_code_tom=self.config.location_code_tom, order_id=order_id
            )
        )
        response = requests.get(url=url, headers=self.default_headers)
        return handle_response(response, 200)

    def consolidate(self, order_id: str, totes: List):
        url = self.url_builder(rel=self.consolidate_url)
        body = {
            "location-id": self.config.location_code_tom,
            "order-id": order_id,
            "totes": totes,
            "bags-qty": 0,
            "device-serial-number": "rq-tools",
            "skip-decisions-check": True,
            "skip-status-update": False,
        }
        response = requests.post(url=url, headers=self.default_headers, json=body)
        return handle_response(response, 200)

    def stage(self, order_id: str, staging_address: str, totes: List):
        url = self.url_builder(rel="v2/staging/stage")
        body = {
            "location-id": self.config.location_code_tom,
            "order-id": order_id,
            "staging-address": staging_address,
            "totes": totes,
            "device-serial-number": "rq-tools",
            "skip-status-update": False,
        }
        response = requests.post(url=url, headers=self.default_headers, json=body)
        return handle_response(response, 200)

    """Helper methods start here"""

    def get_totes_for_route(self, order_status: str, route: str) -> list:
        url = self.url_builder(rel=self.truck_load_orders_endpoint)
        response = requests.get(
            url=url,
            headers=self.default_headers,
            params={
                "location-id": self.config.location_code_tom,
                "status": order_status,
            },
        )
        response.raise_for_status()

        totes = [
            tote
            for response_item in response.json()
            if route == response_item["route-id"]
            for tote in response_item["totes"]
        ]
        return totes

    def get_totes_for_route_unload(self, order_status: str, spoke_id) -> list:
        url = self.url_builder(rel=self.truck_unload_orders_endpoint)
        response = requests.get(
            url=url,
            headers=self.default_headers,
            params={"service-location-id": spoke_id, "status": order_status},
        )
        handle_response(response, 200)

        totes = [
            tote for response_item in response.json() for tote in response_item["totes"]
        ]
        return totes

    def get_all_order_totes_from_ramp_state(self, order_id: str):
        data = self.consolidation_ramp_state(order_id)
        all_totes = list(data.values())
        return [
            tote
            for totes_from_single_ramp in all_totes
            for tote in totes_from_single_ramp
        ]
