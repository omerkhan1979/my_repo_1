"""
Class tom interact with decanting service - backend service for inbound operations.
Name is misleading - the service is used not only for decanting but also for put away

Swagger: https://ds-qai.abs.takeofftech.io

Confluence (there are a lot of docs):
https://takeofftech.atlassian.net/wiki/spaces/ARCH/pages/1702954398/Decanting+Service
"""

from datetime import datetime, timedelta
from random import randint
from sys import exit
from typing import cast

import exrex
import requests

from src.api.takeoff.base_api_takeoff import BaseApiTakeoff
from src.utils.assortment import Product
from src.utils.console_printing import bold, red
from src.utils.http import handle_response
from src.utils.config import get_url_builder

from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin, LetterCase, config

kebabConfig = config(letter_case=LetterCase.KEBAB)


@dataclass
class ToteInitValue(DataClassJsonMixin):
    dc_id: str


@dataclass
class ToteInitResponse(DataClassJsonMixin):
    success: bool
    value: ToteInitValue


@dataclass
class DecantingLoginResult(DataClassJsonMixin):
    user_id: str = field(metadata=kebabConfig)


@dataclass
class DecantingLoginResponse(DataClassJsonMixin):
    result: DecantingLoginResult


@dataclass
class DecantingOperationResponse(DataClassJsonMixin):
    success: bool


@dataclass
class ToteSection(DataClassJsonMixin):
    product: str
    amount: int
    po: str
    expiration_date: str = field(metadata=kebabConfig)
    reason_code: str = field(metadata=kebabConfig)


@dataclass
class DSDReceiveResponse(DataClassJsonMixin):
    # NOTE: This schema is very incomplete
    purchase_order: str


@dataclass
class TaskListProduct(DataClassJsonMixin):
    product: str
    qty_decanted: int
    qty: int


@dataclass
class TaskListItem(DataClassJsonMixin):
    purchase_order: str
    products: list[TaskListProduct]
    status: str
    pending_product_count: int


@dataclass
class TaskListResponse(DataClassJsonMixin):
    data: list[TaskListItem]


def tote_sections_to_dict(sections: dict[str, ToteSection]) -> dict:
    """
    Converts the sections dictionary into a generic dict mainly for JSONificiation.
    """
    return {k: v.to_dict() for k, v in sections.items()}


class Decanting(BaseApiTakeoff):
    url_builder = get_url_builder("/api", "ds")

    decanting_task_endpoint = "decanting/tasks"
    decanting_task_list_endpoint = "decanting/task-list"
    add_purchase_order_endpoint = "v2/purchase-order/add"
    decanting_tasks_by_product_endpoint = "decanting/tasks-by-product"
    put_away_operation_endpoint = "put-away/operation"
    initialize_decanting_tote = "decanting/init"
    record_login_to_decanting = "record-decanting-ui-login"
    decanting_operation_endpoint = "decanting/operation"
    close_po = "purchase-order/close"
    decanting_dsd_task_endpoint = "decanting/dsd/receive"

    def get_decanting_tasks(self, location_code_gold: int, return_all):
        # required location-code-gold, which is int; retrieved from tsc
        """Retrieve decanting tasks (decanting task = purchase order) for given MFC"""
        url = self.url_builder(rel=self.decanting_task_endpoint)
        response = requests.get(
            url=url,
            headers={"X-Token": self.config.token},
            params={
                "mfc": location_code_gold,
                "all": return_all,
            },
        )
        return TaskListResponse.from_json(
            cast(str, handle_response(response, 200, json=False))
        )

    def get_decanting_task_list(self, mfc: int, po_id: str) -> TaskListResponse:
        """
        Get decanting tasks (purchase orders) matching the criteria;
        Filters are sent in post request
        """

        url = self.url_builder(rel=self.decanting_task_list_endpoint)
        body = {
            "filter": {"mfc": mfc, "purchase_order": po_id},
            "opts": {"skip": 0, "limit": 25},
        }

        response = requests.post(url=url, headers=self.default_headers, json=body)

        return TaskListResponse.from_json(
            cast(str, handle_response(response, 200, 201, json=False))
        )

    def get_decanting_tasks_for_view_po(self, location_code_tom):
        url = self.url_builder(rel=self.decanting_task_endpoint)
        response = requests.get(
            url=url,
            headers=self.default_headers,
            params={
                "mfc": location_code_tom,
                "all": "true",
            },
        )
        return handle_response(response, 200)

    def get_decanting_tasks_by_product(self, location_code_gold: int, product: str):
        # required location-code-gold, which is int; retrieved from tsc
        url = self.url_builder(rel=self.decanting_tasks_by_product_endpoint)
        response = requests.get(
            url=url,
            headers={"X-Token": self.config.token},
            params={
                "mfc": location_code_gold,
                "product": product,
            },
        )
        return handle_response(response, 200)

    def put_away_operation(
        self,
        location_code_tom: str,
        shelf_id: str,
        product: str,
        quantity: int,
        po_id: str,
    ):
        url = self.url_builder(rel=self.put_away_operation_endpoint)
        body = {
            "location_id": location_code_tom,
            "shelf_id": shelf_id,
            "product_id": product,
            "quantity": quantity,
            "po": po_id,
        }

        response = requests.post(url=url, headers=self.default_headers, json=body)

        return handle_response(response, 200, 201)

    def initialize_tote_for_decanting(
        self, location_code_gold: int, tote, user_id
    ) -> ToteInitResponse:
        url = self.url_builder(rel=self.initialize_decanting_tote)

        body = {"user-id": user_id, "user-name": "rq-tool"}

        response = requests.post(
            url=url,
            headers={"X-Token": self.config.token},
            params={"mfc": location_code_gold, "licenceplate": tote},
            json=body,
        )

        return ToteInitResponse.from_json(
            cast(str, handle_response(response, 200, json=False))
        )

    def close_purchase_order(self, po_id):
        url = self.url_builder(rel=self.close_po)
        body = {"order-id": po_id}

        response = requests.post(
            url=url, headers={"X-Token": self.config.token}, json=body
        )

        return handle_response(response, 200)

    def decanting_operation(
        self,
        mfc: int,
        sections: dict[str, ToteSection],
        licenceplate: str,
        dc_id: str,
        user_id: str,
    ) -> DecantingOperationResponse:
        url = self.url_builder(rel=self.decanting_operation_endpoint)

        user = {"id": user_id, "name": "rq-tool"}
        body = {
            "dc_id": dc_id,
            "mfc": mfc,
            "licenceplate": licenceplate,
            "user": user,
            "tote_size": len(sections),
            "sections": tote_sections_to_dict(sections),
        }

        response = requests.post(
            url=url,
            headers={"X-Token": self.config.token},
            params={"mfc": mfc},
            json=body,
        )

        return DecantingOperationResponse.from_json(
            cast(str, handle_response(response, 200, json=False))
        )

    def login_to_decanting(self) -> DecantingLoginResponse:
        url = self.url_builder(rel=self.record_login_to_decanting)

        response = requests.post(url=url, headers={"X-Token": self.config.token})

        return DecantingLoginResponse.from_json(
            cast(str, handle_response(response, 200, json=False))
        )

    def v2_add_purchase_order(
        self, location_code_gold: int, products: list[Product], **kwargs
    ):
        url = self.url_builder(rel=self.add_purchase_order_endpoint)
        po_id = exrex.getone("[0-9]{14}")

        body = {
            "purchase-order-id": po_id,
            "mfc-id": location_code_gold,
            "delivery-date": kwargs.get(
                "delivery_date",
                (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            ),
            "issued-date-ts": kwargs.get(
                "issued_date_ts", datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            ),
            "supplier-id": kwargs.get("supplier_id", "47895"),
            "supplier-name": kwargs.get("supplier_name", "Takeoff Test Supplier"),
            "supplier-type": kwargs.get("supplier_type", "DC"),
            "supplier-account": kwargs.get("supplier_account", "DC"),
            "items": [],
        }

        items = []

        for product in products:  # see the docstring for format description
            item = {
                "tom-id": product.tom_id,
                "product-name": product.name,
                "corp-id": "RETAIL_12",
                "ship-unit-description": "box",
                "product-quantity-in-ship-unit": randint(1, 5),
                "ship-unit-quantity": 3.00,
                "purchase-price": 500,
            }
            items.append(item)

        if items:
            body["items"] = items
        else:
            print(red("Attempt to create PO with no items! Exiting..."))
            exit()

        response = requests.post(url=url, headers=self.default_headers, json=body)
        handle_response(response, 200, 201)

        print(bold(f"Created PO {po_id}"))

        return po_id

    def create_dsd_task(
        self,
        location_code_gold: int,
        product: str,
    ) -> DSDReceiveResponse:
        url = self.url_builder(rel=self.decanting_dsd_task_endpoint)
        body = {"mfc-id": location_code_gold, "product-id": product, "qty": 1}
        response = requests.post(url=url, headers=self.default_headers, json=body)

        return DSDReceiveResponse.from_json(
            cast(str, handle_response(response, 200, json=False))
        )
