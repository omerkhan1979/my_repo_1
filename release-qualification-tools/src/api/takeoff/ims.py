"""
Class to interact with IMS API. IMS API exists in 2 'implementations':

 - IMS API V1 is a so-called 'command-server'. Mostly, single endpoint 'message/{}' is used.,
   It can be used to perform different actions. Action is specified by path param.
   Swagger doc: https://ims-api-qai.maf.takeofftech.io/api/v1/command-server/index.html#!/

   Endpoint request body has a unified form, which contains an array of 'command arguments'
   (see example in the code below)

   IMS commands description and examples can be found here:
   https://takeofftech.atlassian.net/wiki/spaces/takeoff/pages/733806613/IMS+info

   Additionally, V1 has other 'standalone' endpoints (for example, to retrieve all adjustments for purchase orders)

- IMS API V2 - set of REST-full endpoints. Some endpoints are new functionality (addresses management -
  https://takeofftech.atlassian.net/wiki/spaces/INV/pages/2610038687/Known+Address+Infrastructure),
  some are improved V1 commands, that can be used for the same operations (such as inventory snapshot)
  Swagger doc: https://ims-api-qai.maf.takeofftech.io/api/v2
"""

from typing import TypedDict, cast, Iterator
import requests

from time import time
from src.api.takeoff.base_api_takeoff import BaseApiTakeoff
from src.utils.console_printing import blue, yellow
from src.utils.helpers import get_params_from_kwargs
from src.utils.http import handle_response
from src.utils.config import get_url_builder

IMSAddress = TypedDict(
    "IMSAddress",
    {
        "active": bool,
        "address": str,
        "aisle": str,
        "area": str,
        "bay": str,
        "dynamic": bool,
        "location-id": str,
        "overstock": bool,
        "pickable": bool,
        "shelf": str,
        "stack": str,
        "temp-zone": str,
        "type": str,
    },
)


class IMS(BaseApiTakeoff):
    url_builder = get_url_builder("api/", "ims-api")

    shelf_adjust_endpoint = "v1/command-server/message/shelf-adjust"
    adjustments_endpoint = "v1/command-server/message/adjustments"
    adjustments_for_po_endpoint = (
        "v1/command-server/system/adjustments-for-purchase-order"
    )
    get_reserved_picking_path_endpoint = (
        "v1/command-server/message/reserved-picking-path"
    )
    message_bulk_endpoint = "v1/command-server/message/bulk"
    migrate_addresses_endpoint = "v2/migrate-addresses"
    v2_get_addresses_endpoint = "v2/get-addresses"
    update_address_attributes_endpoint = "v2/update-address-attributes"
    v2_create_addresses_endpoint = "v2/create-addresses"
    v2_snapshot_endpoint = "v2/snapshot"
    get_ramp_state_for_order_endpoint = "v1/command-server/message/ramp-state"
    free_up_channel_endpoint = "v1/command-server/message/free-up-channel"
    shelves_balance_products_endpoint = (
        "v1/command-server/message/shelves-balance-products"
    )
    shelves_snapshot_endpoint = "v1/command-server/message/shelves-snapshot"
    shelves_balance_subset_endpoint = "v1/command-server/message/shelves-balance-subset"
    add_totes_account_endpoint = "v1/command-server/message/init-accounts"
    init_totes_endpoint = "v1/command-server/message/init"
    reason_code_replace_endpoint = "v2/reason-codes/replace"

    message_body = {"args": []}

    def shelf_adjust(
        self,
        address: str,
        product: str,
        qty: int,
        reason: str,
        location_id=None,
        comment=None,
        expiration_date="",
    ) -> dict:
        """
        IMS command to perform inventory adjustment (change the state
        of a stock keeping unit in the inventory management system

        address: can be '01K' (which indicates OSR, or manual/dynamic address ('01A010203B'/'1001D090807A'))
        product: TOM product id
        qty: ∆ - can be positive, negative or 0
        reason: only one from predefined set is allowed.
                Learn more: https://takeofftech.atlassian.net/wiki/spaces/ST/pages/1664876734/IMS+Reason+Code+Management
        location_id: location-code-tom
        comment: used when adjustment comes during order picking or decanting -
                 comment contains order-id or purchase order-id. ('ORDER=444333222;' 'PO=111222333')
        expiration_date: ISO timestamp or empty string, IRL is passed on decanting.


        """
        url = self.url_builder(rel=self.shelf_adjust_endpoint)

        args = [
            location_id or self.config.location_code_tom,
            address,
            product,
            qty,
            reason,
            expiration_date,
        ]
        if comment:
            args.append(comment)
        body = self.message_body
        body["args"] = args
        response = requests.post(
            url=url,
            headers=self.default_headers,
            json=body,
        )
        print(
            f"Adjusted product {product} on address {address} at {location_id or self.config.location_code_tom} with qty {qty}"
        )
        return handle_response(
            response, 200, 201
        )  # just says "Operation successful", usually we are not interested in

    def adjustments(
        self,
        from_timestamp: str,  # milliseconds
        to_timestamp: str,  # milliseconds
        location_id=None,
    ):  # location-code-tom
        """Command to retrieve inventory adjustments within a given time interval"""
        url = self.url_builder(rel=self.adjustments_endpoint)
        if to_timestamp is None:
            to_timestamp = str(int(round(time() * 1000)))

        body = self.message_body
        body["args"] = [
            location_id or self.config.location_code_tom,
            from_timestamp,
            to_timestamp,
        ]
        response = requests.post(
            url=url,
            headers=self.default_headers,
            json=body,
        )
        return handle_response(response, 200, 201)

    def adjustments_for_po(self, po_id):
        url = self.url_builder(rel=self.adjustments_for_po_endpoint)

        body = {
            "location-id": self.config.location_code_tom,
            "purchase-order-id": str(po_id),
        }

        response = requests.post(url=url, headers=self.default_headers, json=body)
        return handle_response(response, 200, 201)

    # Get all reservations for particular order id
    def get_reserved_picking_path_for_order(self, order_id: str) -> dict:
        url = self.url_builder(rel=self.get_reserved_picking_path_endpoint)

        body = self.message_body
        body["args"] = [self.config.location_code_tom, order_id]

        response = requests.post(
            url=url,
            headers=self.default_headers,
            json=body,
        )

        return handle_response(response, 200, 201)["success"]

    def message_bulk(self, body):
        """
        Multiple (could be same or different) IMS commands within a single http request
        Body example:
        [
            {
             "cmd": "shelf-adjust",
             "args": ["2833", "01K","PRODUCT1", 1, "CC", ""]
            },
            {
            "cmd": "shelves-snapshot",
            "args": ["2833"]
            }
        ]
        """
        url = self.url_builder(rel=self.message_bulk_endpoint)

        response = requests.post(
            url=url,
            headers=self.default_headers,
            json=body,
        )
        return handle_response(response, 200, 201)

    def free_up_channel(self, tote: str) -> requests.Response:
        url = self.url_builder(rel=self.free_up_channel_endpoint)

        body = IMS.message_body
        body["args"] = [self.config.location_code_tom, tote]

        return requests.post(
            url=url,
            headers=self.default_headers,
            json=body,
        )

    def add_totes_account(self, totes_account: str) -> dict:
        """
        Add an account for totes from an input string. This will be used for applying existing configuration
        where the account name is given and not to be interpolated.

        Args:
        totes_account (str): The string of the account to be added.
        """
        body = IMS.message_body
        body["args"] = [totes_account]
        response = requests.post(
            url=self.url_builder(rel=self.add_totes_account_endpoint),
            headers=self.default_headers,
            json=body,
        )
        return handle_response(response, 200, 201)

    def add_default_totes_account(
        self,
        location_code_tom: str = None,
        target: bool = True,
    ) -> dict:
        """
        Add a default account for totes to IMS for a location_code_tom.

        Args:
        location_code_tom (str): The retailer location code to use for the account. If not passed,
                                 default to location code from config.
        target (bool): If true, create target totes account, else create storage totes account.
        """
        account_name = self.get_totes_account_name(
            location_code_tom=location_code_tom, target=target
        )
        return self.add_totes_account(totes_account=account_name)

    def add_totes(self, totes: list[str], totes_account: str) -> dict:
        """
        Add totes to a given totes account that is passed in.

        Args:
        totes (list[str]): A list of tote ids to add for the account.
        totes_account (str): The totes will be added to the account represented by this string.
        """
        body = IMS.message_body
        body["args"] = [totes_account].append(totes)
        response = requests.post(
            url=self.url_builder(rel=self.init_totes_endpoint),
            headers=self.default_headers,
            json=body,
        )
        return handle_response(response, 200, 201)

    def add_default_account_totes(
        self, totes: list[str], location_code_tom: str = None, target: bool = True
    ) -> dict:
        """
        Add totes to a default account in IMS for a location_code_tom and target. Calls add_totes method.

        Args:
        totes (list[str]): A list of tote ids to add for the account.
        location_code_tom (str): The location code to generate the account to be used for adding totes. If not passed,
                                 default to location code from config.
        target (bool): If true, use target totes account, else use storage totes account.
        """
        account_name = self.get_totes_account_name(
            location_code_tom=location_code_tom, target=target
        )
        return self.add_totes(totes=totes, totes_account=account_name)

    """
    !!! V2 endpoints start here !!!
    """

    def v2_migrate_addresses(self):
        """
        Endpoint to trigger 'migration' of addresses from 'balances' table to new 'addresses' table.
        Addresses' attributes will be 'guessed' from the address string
        (e.g. 01A012345B... -> is non-dynamic address from 'ambient' temp zone, in aisle 1,
        bay 234, shelf 5 and stack B on withing the shelf)
        """

        url = self.url_builder(rel=self.migrate_addresses_endpoint)

        response = requests.post(url=url, headers=self.default_headers)

        return handle_response(response, 200, 201)

    # retrieve addresses from 'addresses' IMS table by given criteria
    def v2_get_addresses(self, **kwargs) -> list[IMSAddress]:
        url = self.url_builder(rel=self.v2_get_addresses_endpoint)

        body = {
            "location-id": kwargs.pop("location_ids", [self.config.location_code_tom])
        }
        if not isinstance(body["location-id"], list):
            raise TypeError("location_ids must be a list of location ids")
        if not body["location-id"]:
            body = {}

        param_names = [
            "limit",
            "shelves",
            "aisles",
            "offset",
            "dynamic",
            "active",
            "stacks",
            "area",
            "pickable",
            "overstock",
            # Params that have diff names in kwargs and in body:
            ["order_direction", "order-direction"],
            ["temp_zones", "temp-zones"],
            ["order_by", "order-by"],
        ]
        body.update(get_params_from_kwargs(param_names, **kwargs))

        response = requests.post(url=url, headers=self.default_headers, json=body)

        return cast(list[IMSAddress], handle_response(response, 200, 201))

    def v2_update_address_attributes(
        self,
        address: str,
        dynamic=False,
        overstock=False,
        pickable=True,
        active=True,
        location_code=None,
        temp_zone=None,
    ) -> dict:
        """
        Endpoint to update attributes of multiple addresses at once.
        Pass necessary attributes to update and their boolean values.
        E.g.:
        ims.v2_update_address_attributes("1001D020304D", dynamic=True)
        """

        url = self.url_builder(rel=self.update_address_attributes_endpoint)

        if location_code is None:
            location_code = self.config.location_code_tom
        body = [
            {
                "address": address,
                "location-id": location_code,
                "attributes": {
                    "pickable": pickable,
                    "overstock": overstock,
                    "dynamic": dynamic,
                    "active": active,
                },
            }
        ]

        if temp_zone is not None:
            body[0]["attributes"]["temp-zone"] = temp_zone

        response = requests.post(url=url, headers=self.default_headers, json=body)

        return handle_response(response, 200, 201)

    # create new address in 'addresses' IMS table
    def v2_create_addresses(self, addresses: list) -> list[dict]:
        url = self.url_builder(rel=self.v2_create_addresses_endpoint)

        def slice_iterator(lst: list[str], slen: int) -> Iterator[list[str]]:
            while lst:
                block, lst = lst[:slen], lst[slen:]
                yield block

        responses = []
        for slice in slice_iterator(addresses, 20):
            body = slice
            response = requests.post(url=url, headers=self.default_headers, json=body)
            responses.append(handle_response(response, 200, 201, print_details=False))

        return responses

    def v2_snapshot(
        self,
        products=None,  # list; tom-ids of products of interest
        addresses=None,  # list: addresses of interest
        include_zeros=False,
    ) -> dict:  # whether to include
        """
        V2 endpoint (replaces commands 'snapshot', 'snapshot-products', 'shelves-balance-subset').
        Better use this one to get inventory data!
        Get state of inventory fo particular product(s), address(es) or their intersection

        Return value looks like:
        {
          "total": 2,
          "location-id": "D02",
          "addresses": [
              {
              "address": "01K",
              "product-id": "20210223171408592",
              "quantity": 10,
              "reserved": 5,
              "available": 5,
              "last-update": "2021-08-25T21:23:18Z"
              },
              {
              "address": "01A002048A",
              "product-id": "20210315163942135",
              "quantity": 0,
              "reserved": 0,
              "available": 0,
              "last-update": "2021-05-26T13:59:53Z"
              }
            ]
        }
        """
        url = self.url_builder(self.v2_snapshot_endpoint)

        body = {
            "location-id": self.config.location_code_tom,
            "include-zeros": include_zeros,
        }

        if addresses:
            body["addresses"] = addresses
        if products:
            body["products"] = products

        response = requests.post(url=url, headers=self.default_headers, json=body)
        return handle_response(response, 200, 201)

    """Helper methods start here"""

    # Get totes that are currently assigned to dispatch lanes (sorting channels) for particular order
    def get_ramp_state_for_order(self, order_id: str) -> list:
        url = self.url_builder(rel=self.get_ramp_state_for_order_endpoint)

        body = IMS.message_body
        body["args"] = [self.config.location_code_tom]

        response = requests.post(
            url=url,
            headers=self.default_headers,
            json=body,
        )

        data = handle_response(response, 200)["success"]["orders"].get(
            f"z-{order_id}", []
        )
        return data

    # makes sure there's no stock of particular product(s) or on address(es)
    def zero_stock_for_products_or_addresses(self, products=None, addresses=None):
        if products or addresses:
            snapshot = self.v2_snapshot(products, addresses)["addresses"]

            # get inventory records where qty-available is > 0
            inventory_to_remove = list(
                filter(
                    lambda product: product["available"] > 0,
                    snapshot,
                )
            )

            bulk_adjust_body = []

            if inventory_to_remove:
                print(
                    yellow(
                        f"Will zero out inventory for following tom ids: {[i['product-id'] for i in inventory_to_remove]}"
                    )
                )

                for item in inventory_to_remove:
                    bulk_adjust_body.append(
                        {
                            "cmd": "shelf-adjust",
                            "args": [
                                self.config.location_code_tom,
                                item["address"],
                                item["product-id"],
                                -item["available"],
                                "CC",
                                "",
                            ],
                        }
                    )
                self.message_bulk(bulk_adjust_body)

            return snapshot
        else:
            return {}

    def shelves_balance_products(self, location_code_tom, product):
        url = self.url_builder(rel=self.shelves_balance_products_endpoint)

        body = self.message_body
        body["args"] = [location_code_tom, product]
        response = requests.post(
            url=url,
            headers=self.default_headers,
            json=body,
        )

        return handle_response(response, 200, 201)

    def shelves_snapshot(self, location_code_tom):
        url = self.url_builder(rel=self.shelves_snapshot_endpoint)

        body = self.message_body
        body["args"] = [location_code_tom]
        response = requests.post(
            url=url,
            headers=self.default_headers,
            json=body,
        )

        return handle_response(response, 200, 201)

    def shelves_balance_subset(self, location_code_tom, shelf_id):
        url = self.url_builder(rel=self.shelves_balance_subset_endpoint)

        body = self.message_body
        body["args"] = [location_code_tom, shelf_id]
        response = requests.post(
            url=url,
            headers=self.default_headers,
            json=body,
        )
        return handle_response(response, 200, 201)

    # Derived from usefull_scripts/blob/master/pythoniser.py
    def clear_ramp(self, order_id):
        totes_list = self.get_ramp_state_for_order(order_id)
        for tote in totes_list:
            free = self.free_up_channel(tote)
            if tote and free:
                print(blue(f"\nTote: {tote} {free.text}\n"))
            elif free.status_code == 412 and free.json()["error"].endswith(
                "is assigned, no relation to particular order"
            ):
                print(blue(f"\n{tote}: was already freed\n"))
            else:
                print(
                    blue(
                        f"\n{tote}: http status: {free.status_code}, text: {free.text}"
                    )
                )

    def get_totes_account_name(self, location_code_tom: str, target: bool) -> str:
        """
        Get a default totes account string from location_code_tom and target/storage args.

        Args:
        location_code_tom (str): Location code to use for account. If None, get code from config object.
        target (bool): If true, create account for target totes. If false, create account for storage totes.
        """
        if location_code_tom is None:
            location_code_tom = self.config.location_code_tom
        if target:
            return f"{location_code_tom}-default-target-tote-account"
        else:
            return f"{location_code_tom}-default-storage-tote-account"

    def replace_reason_codes(self, codes: list[dict]) -> dict:
        """Replace existing reason codes for inventory movements"""
        url = self.url_builder(rel=self.reason_code_replace_endpoint)
        response = requests.post(url=url, headers=self.default_headers, json=codes)
        return handle_response(response, 200, 201)
