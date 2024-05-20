"""
Class to interact with Integration aka RInt service.
Most of inward and outward communications with retailers' systems -
placing/updating customer orders, exchange inventory and assortment data -
happen through RInt
"""

from datetime import datetime
from typing import List, Optional, cast

import exrex
import requests
from pytest import fail
from pprint import pprint

from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin, LetterCase, config

from src.api.takeoff.base_api_takeoff import BaseApiTakeoff
from src.utils.console_printing import done, yellow
from src.utils.http import handle_response
from src.utils.config import get_url_builder

kebabConfig = config(letter_case=LetterCase.KEBAB)


@dataclass
class POItemCreate(DataClassJsonMixin):
    tom_id: str = field(metadata=kebabConfig)
    product_name: str = field(metadata=kebabConfig)
    ship_unit_description: str = field(metadata=kebabConfig)
    product_quantity_in_ship_unit: int = field(metadata=kebabConfig)
    ship_unit_quantity: float = field(metadata=kebabConfig)
    purchase_price: int = field(metadata=kebabConfig)


@dataclass
class CommonPurchaseOrderCreate(DataClassJsonMixin):
    purchase_order_id: str = field(metadata=kebabConfig)
    mfc_id: str = field(metadata=kebabConfig)
    delivery_date: str = field(metadata=kebabConfig)
    supplier_id: str = field(metadata=kebabConfig)
    supplier_name: str = field(metadata=kebabConfig)
    supplier_type: str = field(metadata=kebabConfig)
    supplier_account: Optional[str] = field(metadata=kebabConfig)
    items: list[POItemCreate] = field(metadata=kebabConfig)


@dataclass
class POItemGet(DataClassJsonMixin):
    tom_id: str = field(metadata=kebabConfig)
    product_quantity_in_ship_unit: int = field(metadata=kebabConfig)
    ship_unit_quantity: float = field(metadata=kebabConfig)
    received_quantity: int = field(metadata=kebabConfig)


@dataclass
class CommonPurchaseOrderGet(DataClassJsonMixin):
    purchase_order_id: str = field(metadata=kebabConfig)
    mfc_id: str = field(metadata=kebabConfig)
    delivery_date: str = field(metadata=kebabConfig)
    supplier_id: str = field(metadata=kebabConfig)
    supplier_name: str = field(metadata=kebabConfig)
    supplier_type: str = field(metadata=kebabConfig)
    update_time: str = field(metadata=kebabConfig)
    close_time: str = field(metadata=kebabConfig)
    ordered_total_quantity: int = field(metadata=kebabConfig)
    status: str = field(metadata=kebabConfig)
    items: list[POItemGet] = field(metadata=kebabConfig)
    supplier_account: Optional[str] = field(metadata=kebabConfig, default=None)


@dataclass
class CreateResponseWarning(DataClassJsonMixin):
    type: str = field(metadata=kebabConfig)
    description: str = field(metadata=kebabConfig)


@dataclass
class RINTCreateResponseData(DataClassJsonMixin):
    success: bool = field(metadata=kebabConfig)
    warnings: List[CreateResponseWarning] = field(metadata=kebabConfig)


@dataclass
class CreateCOResponse(DataClassJsonMixin):
    data: RINTCreateResponseData = field(metadata=kebabConfig)


@dataclass
class CreatePOResponse(DataClassJsonMixin):
    data: RINTCreateResponseData = field(metadata=kebabConfig)


@dataclass
class GetPOResponse(DataClassJsonMixin):
    data: CommonPurchaseOrderGet = field(metadata=kebabConfig)


class RInt(BaseApiTakeoff):
    url_builder = get_url_builder("api/", "rint-api")

    create_customer_order_endpoint = "v4/common/create-customer-order"
    update_co_ecom_status_endpoint = "v4/common/update-customer-order-ecom-status"
    get_customer_order_endpoint = "v4/common/get-customer-order"
    get_shelves_snapshot_endpoint = "v4/common/get-inventory-snapshot"
    get_inventory_movements_endpoint = "v4/common/get-inventory-movements"

    create_purchase_order_endpoint = "v4/common/create-purchase-order"
    get_purchase_order_endpoint = "v4/common/get-purchase-order"
    update_customer_order_endpoint = "v4/common/update-customer-order"

    def create_purchase_order(self, po: CommonPurchaseOrderCreate) -> CreatePOResponse:
        """
        Creates a purchase order.
        """
        url = self.url_builder(rel=self.create_purchase_order_endpoint)

        response = CreatePOResponse.from_json(
            cast(
                str,
                handle_response(
                    requests.post(
                        url=url,
                        headers=self.default_headers,
                        json=po.to_dict(),
                    ),
                    200,
                    json=False,
                ),
            )
        )

        # TODO: Gosh, if the status is 200 but we dont have success I will sure be sad.
        if response.data.success:
            print(done(f"PO {po.purchase_order_id} placed!"))

        warnings = response.data.warnings
        if warnings:
            print(yellow(f"Warnings: {warnings}"))

        return response

    def get_purchase_order(self, location_code_retailer: str, po: str) -> GetPOResponse:
        """
        Get a purchase order.
        """
        url = self.url_builder(rel=self.get_purchase_order_endpoint)

        response = GetPOResponse.from_json(
            cast(
                str,
                handle_response(
                    requests.post(
                        url=url,
                        headers=self.default_headers,
                        json={
                            "mfc-id": location_code_retailer,
                            "purchase-order-id": po,
                        },
                    ),
                    200,
                    json=False,
                ),
            )
        )

        return response

    def create_customer_order(self, lineitems, print_body=True, **kwargs) -> str:
        """
        If you call this directly, make sure you pass lineitems correctly!
        You can transform tom-ids to lineitems with 'tom_ids_tom_lineitems' function
        from utils/place_order.py
        """
        url = self.url_builder(rel=self.create_customer_order_endpoint)

        if kwargs.get("order_id"):
            order_id = kwargs["order_id"]
        else:
            order_id = exrex.getone("[0-9]{15}")

        try:
            body = {
                "mfc-id": kwargs["store_id"],
                "corp-order-id": order_id,
                "spoke-id": kwargs["spoke_id"],
                "stage-by-datetime": kwargs["stage_by_datetime"],
                "ecom-service-type": kwargs.get("ecom_service_type", "DELIVERY"),
                "shipping-label": [
                    "Python Test",
                    "2000-01-01T00:00.000Z-3000-01-01T00:00.000Z",
                ],
                "line-items": lineitems,
                "service-window-start": kwargs["service_window_start"],
                "ecom-order-status": kwargs.get("ecom_order_status")
                or (
                    "SUBMITTED"
                    if self.config.retailer
                    in [
                        "winter",
                        "abs",
                        "maf",
                    ]
                    else "CREATED"
                ),
                "ecom-order-id": order_id,
            }
            body["delivery-route"] = {}
            body["delivery-route"]["shift-number"] = kwargs.get("shift_number") or 1
            body["delivery-route"]["route-id"] = kwargs.get("route_id")
            body["delivery-route"]["stop-number"] = kwargs.get("stop_number") or 1
        except KeyError as e:
            fail(f"Missing required parameter in order body: {e}")

        if kwargs.get("order_note") is not None:
            body["order-note"] = kwargs["order_note"]
        if print_body:
            pprint(body)

        response = CreateCOResponse.from_json(
            cast(
                str,
                handle_response(
                    requests.post(
                        url=url,
                        headers=self.default_headers,
                        json=body,
                    ),
                    200,
                    201,
                    json=False,
                ),
            )
        )
        response_data = response.data

        if response_data.success:
            print(done(f"Order {order_id} placed!"))
        warnings = response_data.warnings
        if warnings:
            print(yellow(f"Warnings: {warnings}"))
        return order_id

    def create_customer_order_required_field(
        self, lineitems, print_body=True, **kwargs
    ) -> str:
        url = self.url_builder(rel=self.create_customer_order_endpoint)

        if kwargs.get("order_id"):
            order_id = kwargs["order_id"]
        else:
            order_id = exrex.getone("[0-9]{15}")

        try:
            body = {
                "mfc-id": kwargs["store_id"],
                "spoke-id": kwargs["spoke_id"],
                "stage-by-datetime": kwargs["stage_by_datetime"],
                "ecom-service-type": kwargs.get("ecom_service_type") or "DELIVERY",
                "line-items": lineitems,
                "service-window-start": kwargs["service_window_start"],
                "ecom-order-status": kwargs.get("ecom_order_status")
                or (
                    "SUBMITTED"
                    if self.config.retailer
                    in [
                        "winter",
                        "abs",
                        "maf",
                    ]
                    else "CREATED"
                ),
                "ecom-order-id": order_id,
            }
        except KeyError as e:
            fail(f"Missing required parameter in order body: {e}")

        if print_body:
            pprint(body)

        response = CreateCOResponse.from_json(
            cast(
                str,
                handle_response(
                    requests.post(
                        url=url,
                        headers=self.default_headers,
                        json=body,
                    ),
                    200,
                    201,
                    json=False,
                ),
            )
        )

        response_data = response.data

        if response.data.success:
            print(done(f"Order {order_id} placed!"))
        warnings = response_data.warnings
        if warnings:
            print(yellow(f"Warnings: {warnings}"))
        return order_id

    def update_co_ecom_status(
        self, location_code_retailer: str, order_id: str, target_status: str
    ):
        url = self.url_builder(rel=self.update_co_ecom_status_endpoint)

        body = {
            "mfc-id": location_code_retailer,
            "ecom-order-id": order_id,
            "ecom-order-status": target_status,
            "ecom-payment-status": "",
        }
        response = requests.post(url=url, json=body, headers=self.default_headers)
        print(yellow(f"Updating... \nThe response is:{response.json()}"))
        return handle_response(response, 200)

    def get_customer_order_v4(self, location_code_retailer: str, order_id: str):
        url = self.url_builder(rel=self.get_customer_order_endpoint)

        body = {"mfc-id": location_code_retailer, "ecom-order-id": order_id}
        response = requests.post(url=url, json=body, headers=self.default_headers)

        return handle_response(response, 200)

    def get_shelves_snapshot_v4(self, location_code_retailer: str):
        url = self.url_builder(rel=self.get_shelves_snapshot_endpoint)

        body = {"mfc-id": location_code_retailer}
        response = requests.post(url=url, json=body, headers=self.default_headers)
        return handle_response(response, 200)

    def get_inventory_movements(self, location_code_retailer: str, start_date: str):
        url = self.url_builder(rel=self.get_inventory_movements_endpoint)

        body = {
            "mfc-id": location_code_retailer,
            "start-date": start_date,
            "end-date": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "offset": 0,
            "limit": 10,
        }
        response = requests.post(url=url, json=body, headers=self.default_headers)

        return handle_response(response, 200)

    def update_customer_order(
        self,
        order_id: str,
        mfc_id: str,
        line_items: list,
        service_window_start: str,
        ecom_order_status: str,
        field_name: str = "order-note",
        field_value: str = "UO",
    ):
        url = self.url_builder(rel=self.update_customer_order_endpoint)

        body = {
            "mfc-id": mfc_id,
            "corp-order-id": order_id,
            "line-items": line_items,
            "service-window-start": service_window_start,
            "ecom-order-status": ecom_order_status,
            "ecom-order-id": order_id,
        }

        if field_name == "route-id":
            delivery_route = {
                "route-id": field_value,
            }
            body["delivery-route"] = delivery_route
        elif field_name == "order-note":
            body["order-note"] = field_value

        response = requests.post(url=url, json=body, headers=self.default_headers)
        return handle_response(response, 200)
