"""
Class to interact with Order management system API
Swagger: https://oms-qai.abs.takeofftech.io / https://oms-wings-uat.tom.takeoff.com
"""

import requests
from requests import HTTPError

from src.api.takeoff.base_api_takeoff import BaseApiTakeoff
from src.utils.console_printing import bold, red
from src.utils.http import handle_response
from src.utils.config import get_url_builder


class OMS(BaseApiTakeoff):
    url_builder = get_url_builder("", "oms")

    order_search_page = "https://{}/orders/details/?id={}"

    order_split_endpoint = "v3/order/split/{}"
    in_store_picking_picklist_endpoint = "support/picklist"
    v3_order_endpoint = "v3/order"
    start_picking_endpoint = "/v3/order/start-picking"
    update_order_status_endpoint = "/v3/order/{}/status"
    status_history_endpoint = "/v3/order/{}/statuses"

    def split_order(self, order_id: str) -> dict:
        """Moves order from status 'draft' to 'new' to make it ready for picking in the MFC"""
        print(
            bold(
                "NOTE: prefer using RINT’s 'update_ecom_order_status' for almost all cases"
            )
        )
        url = self.url_builder(rel=self.order_split_endpoint.format(order_id))

        response = requests.put(
            url=url,
            headers=self.default_headers,
        )
        return handle_response(response, 200, 201)

    def trigger_picklist_creation(self, cutoffs, picklist_type, store_id=None):
        """See usage in utils/picklist_helpers.py"""
        url = self.url_builder(rel=self.in_store_picking_picklist_endpoint)

        body = {
            "store-id": store_id or self.config.location_code_tom,
            "picklist-type": picklist_type,
            "cutoffs": [cutoffs],
        }

        response = requests.post(url=url, headers=self.default_headers, json=body)
        return handle_response(response, 200, 201)

    def get_orders(self, **kwargs):
        url = self.url_builder(rel=self.v3_order_endpoint)

        params = {"location-id": self.config.location_code_tom}

        if kwargs.get("order_id"):
            params["order-id"] = kwargs["order_id"]
        if kwargs.get("is_split") is not None:
            # our devs' english :(
            params["splitted"] = str(kwargs["is_split"]).lower()
        if kwargs.get("cancelled") is not None:
            params["cancelled"] = str(kwargs["cancelled"]).lower()
        if kwargs.get("status"):
            params["status"] = kwargs["status"]
        if kwargs.get("page"):
            params["page"] = kwargs["page"]

        response = requests.get(url=url, headers=self.default_headers, params=params)
        return handle_response(response, 200)

    def get_order_status_history(self, order_id: str):
        url = self.url_builder(rel=self.status_history_endpoint.format(order_id))

        response = requests.get(
            url=url,
            headers=self.default_headers,
        )

        return handle_response(response, 200)

    def check_status_change(self, order_id: str, target_status: str):
        history = self.get_order_status_history(order_id)
        return any(change["status"] == target_status for change in history["statuses"])

    def get_order(self, order_id: str):
        url = self.url_builder(rel=self.v3_order_endpoint + f"/{order_id}")

        response = requests.get(
            url=url,
            headers=self.default_headers,
        )

        return handle_response(response, 200)

    def update_order_status(self, order_id: str, status: str):
        """Should be used for all status transitions except 'draft' -> 'new'"""
        url = self.url_builder(rel=self.update_order_status_endpoint.format(order_id))
        body = {
            "status": status,
            "user-id": "rq-tools",
            "force-update": True,  # propagtes order-status in TOM API, need to have that always True for now
        }
        response = requests.patch(url=url, headers=self.default_headers, json=body)
        return handle_response(response, 200)

    def start_picking(self, order_id: str):
        """Is used for enqueueing the order for MANUALLY_ENQUEUE_RETAILERs"""
        url = self.url_builder(rel=self.start_picking_endpoint)
        body = [order_id]
        response = requests.post(url=url, headers=self.default_headers, json=body)
        return handle_response(response, 200, 201)

    """Helper methods start here"""

    def cancel_all_draft_orders(self):
        first_page = self.get_orders(is_split=False, cancelled=False)
        print(f"Total draft order pages: {first_page['pager']['total-pages']}")
        order_ids = []
        for i in range(0, first_page["pager"]["total-pages"]):
            print(f"Collecting order ids from page {i + 1}")
            page = self.get_orders(is_split=False, page=i + 1, cancelled=False)
            for order in page["orders"]:
                order_ids.append(order["order-id"])

        # a safety measure, when picklists tests are run during release qualification.
        # sometimes we need to test if order split happens automatically as expected for the orders,
        # which were placed before newer version deploy, but split is scheduled for the time
        # when new version is already deployed (so-called 'organic split' test)
        # To test this case, orders might live in 'draft' status for 1-2 days; and if we run tests
        # in this period, we don't want to cancel orders that were placed for organic split tests.
        for o_id in order_ids:
            if "organic_split" not in o_id and "os" not in o_id:
                try:
                    self.update_order_status(o_id, "cancelled")
                except HTTPError as e:
                    print(red(f"Error cancelling order {o_id}: {e}"))
            else:
                (
                    print(
                        bold(
                            f"Draft order {o_id} is meant for organic split, keeping it"
                        )
                    )
                )
