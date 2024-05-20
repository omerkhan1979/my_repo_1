from urllib.error import HTTPError
import requests
from typing import List, Dict, Any
from src.api.takeoff.outbound_baseapi import outbound_baseApi
from src.utils.console_printing import red, bold
from src.utils.http import handle_response


class OutboundBackend(outbound_baseApi):
    def order_search_outbound(self) -> dict:
        url = f"{self.url_builder}v1/orders:search"
        data = {
            "filters": {
                "statuses": ["draft", "queued"],
                "location_id": self.config.location_code_tom,
            },
            "page": 1,
            "limit": 100,
        }
        response = requests.post(url=url, headers=self.default_headers, json=data)
        return handle_response(response, 200)

    def bulk_action(self) -> None:
        url = f"{self.url_builder}v1/orders:bulkActions"

        order_data = self.order_search_outbound()
        # Extract 'order_id' and 'status' from the response and store in a list of dictionaries
        orders: List[Dict[str, Any]] = []
        for order in order_data["orders"]:
            order_info = {"order_id": order["order_id"], "status": order["status"]}
            orders.append(order_info)
        json_body = {"orders": orders, "action": "cancel"}

        # a safety measure, when picklists tests are run during release qualification.
        # sometimes we need to test if order split happens automatically as expected for the orders,
        # which were placed before newer version deploy, but split is scheduled for the time
        # when new version is already deployed (so-called 'organic split' test)
        # To test this case, orders might live in 'draft' status for 1-2 days; and if we run tests
        # in this period, we don't want to cancel orders that were placed for organic split tests.
        for o_id in orders:
            if "organic_split" not in o_id and "os" not in o_id:
                try:
                    response = requests.post(
                        url=url, headers=self.default_headers, json=json_body
                    )
                    return handle_response(response, 200)
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

    def order_details(self, order_id: str) -> dict:

        url = f"{self.url_builder}v1/orders/" + order_id + ":details"

        self.default_headers["locationID"] = self.config.location_code_tom
        response = requests.get(
            url=url,
            headers=self.default_headers,
        )

        return handle_response(response, 200)
