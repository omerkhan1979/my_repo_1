"""
Class to interact with in-store picking service;
Service is relevant for the following retailers: abs, maf
The purpose of the service is to manage lists of products that need to be brought from
store to the the MFC before order wave picking

Swagger: https://isps-abs-uat.tom.takeoff.com

Confluence:
 - https://takeofftech.atlassian.net/wiki/spaces/FUL/pages/1352926314/In-Store+Picking+Service,
 - https://takeofftech.atlassian.net/wiki/spaces/FUL/pages/3298263080/In-Store+Picking+ISPS+2.0
"""

from datetime import datetime
from time import sleep

import requests

from src.api.takeoff.base_api_takeoff import BaseApiTakeoff
from src.utils.console_printing import red, bold, waiting
from src.utils.helpers import get_params_from_kwargs
from src.utils.http import handle_response
from src.utils.config import get_url_builder


class ISPS(BaseApiTakeoff):
    url_builder = get_url_builder(base=None, service_name="isps")

    get_picklists_endpoint = "v3/picklists"
    get_workorders_endpoint = "v3/workorders"
    workorders_assign_endpoint = "v3/workorders/assign"

    def get_picklists(self, status: str, **kwargs) -> dict:
        """
        Retrieve picklists based on criteria provied;
        Possible statuses: INCOMPLETE, NEW, SPLIT, PROGRESS, COMPLETE
        Pass the search criteria via kwargs. See the function body
        to check relevant kwargs
        """
        url = self.url_builder(rel=self.get_picklists_endpoint)

        params = {
            "status": status,
            "mfc-id": kwargs.get("mfc_id") or self.config.location_code_tom,
        }

        # Filling params with criteria passed via kwargs
        param_names = [
            "complete_at_from",
            "zone",
            "complete_at_to",
            "type",
            "offset",
            "limit",
            "cutoff",
        ]
        params.update(get_params_from_kwargs(param_names, **kwargs))

        response = requests.get(url=url, params=params, headers=self.default_headers)

        return handle_response(response, 200)

    def get_picklist_by_code(self, picklist_code: str) -> dict:
        url = self.url_builder(rel=self.get_picklists_endpoint + f"/{picklist_code}")

        response = requests.get(url=url, headers=self.default_headers)
        return handle_response(response, 200)

    def post_picklist_close(self, picklist_code: str) -> dict:
        url = self.url_builder(
            rel=self.get_picklists_endpoint + f"/{picklist_code}/close"
        )

        response = requests.post(url=url, headers=self.default_headers)
        return handle_response(response, 200, 201)

    def get_picklist_items(self, picklist_code: str, offset=0, limit=1000) -> list:
        url = self.url_builder(
            rel=self.get_picklists_endpoint + f"/{picklist_code}/picklistitems"
        )
        response = requests.get(
            url=url,
            headers=self.default_headers,
            params={"offset": offset, "limit": limit},
        )
        return handle_response(response, 200)["picklistitems"]

    def update_picklist_status(self, picklist_code: str, target_status: str) -> dict:
        print(f"Updating picklist {picklist_code} with status {target_status}")
        url = self.url_builder(rel=self.get_picklists_endpoint + f"/{picklist_code}")
        body = {"status": target_status}

        response = requests.put(url=url, headers=self.default_headers, json=body)

        return handle_response(response, 200, 201)

    def get_workorders_for_picklist(self, picklist_code: str) -> list:
        url = self.url_builder(rel=self.get_workorders_endpoint)
        params = {"picklist-code": picklist_code}

        response = requests.get(url=url, headers=self.default_headers, params=params)
        return handle_response(response, 200)["workorders"]

    def get_workorders_status(self, workorder_code: str) -> list:
        url = self.url_builder(rel=self.get_workorders_endpoint + f"/{workorder_code}")

        response = requests.get(url=url, headers=self.default_headers)
        return handle_response(response, 200)["status"]

    def get_workorder_items(self, workorder_code: str) -> list:
        url = self.url_builder(rel=self.get_workorders_endpoint + f"/{workorder_code}")

        response = requests.get(url=url, headers=self.default_headers)
        return handle_response(response, 200)["work-order-items"]

    def put_workorder_changes(self, workorder_code: str, target_status: str) -> dict:
        print(f"Updating workorder {workorder_code} with status {target_status}")
        url = self.url_builder(rel=self.get_workorders_endpoint + f"/{workorder_code}")

        body = {
            "status": target_status,
            "finished": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        response = requests.put(url=url, headers=self.default_headers, json=body)

        return handle_response(response, 200, 201)

    def put_workorder_changes_to_picking(
        self,
        workorder_code: str,
        workorder_item_code: str,
        picked_qty: int,
        reason_code: str,
    ) -> dict:
        url = self.url_builder(
            rel=self.get_workorders_endpoint
            + f"/{workorder_code}/workorderitems/{workorder_item_code}"
        )
        body = {
            "picked-qty": picked_qty,
            "performed-at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "reason-code": reason_code,
        }
        response = requests.put(url=url, headers=self.default_headers, json=body)

        return handle_response(response, 200, 201)

    def workorders_assign(self, work_order_code: str, user_id: str):
        url = self.url_builder(rel=self.workorders_assign_endpoint)

        body = {
            "work-orders": [{"code": work_order_code}],
            "user-id": user_id,
            "session-id": "string",
        }
        response = requests.post(url=url, headers=self.default_headers, json=body)
        return handle_response(response, 200, print_details=False, raise_error=False)

    """Helper methods start here"""

    def find_picklists_by_cutoff_and_status(self, cutoff: str, status: str) -> list:
        # Finding newly created picklist, where "complete-at" equals cutoff for our order

        matching_picklists = []
        num_of_retries = 0
        while not matching_picklists and num_of_retries < 10:
            picklists = self.get_picklists(status=status, complete_at_from=cutoff)[
                "picklists"
            ]

            print(f"Found picklists: {picklists}")
            matching_picklists = list(
                filter(lambda p: p["complete-at"] == cutoff, picklists)
            )
            if matching_picklists:
                break
            num_of_retries += 1
            retry_after = 3 * num_of_retries
            print(
                bold(
                    f"Could not find picklist matching the criteria, retrying in {retry_after} secs..."
                )
            )
            sleep(retry_after)

        assert matching_picklists, f"No picklist for cutoff time {cutoff} found!"
        return matching_picklists

    def check_if_picklist_status_change_happened(
        self, picklist_code: str, target_statuses: tuple
    ):
        picklist = self.get_picklist_by_code(picklist_code)
        status = picklist["status"]

        _continue = "no"
        while status not in target_statuses and _continue != "yes":
            _continue = input(
                red(
                    f"Picklist status is not one of {target_statuses}! \
                \nPress Enter to check again or type 'yes' to continue anyway: "
                )
            )
            picklist = self.get_picklist_by_code(picklist_code)
            status = picklist["status"]

    def check_if_picklist_items_picked(self, picklist_code: str):
        picklist = self.get_picklist_by_code(picklist_code)
        picked = picklist["total-units-picked"] == picklist["total-units"]

        _continue = "no"
        while not picked and _continue != "yes":
            _continue = input(
                red(
                    f"Not all items in picklist are marked as Picked, \
                \nPicked {picklist['total-units-picked']}, total  {picklist['total-units']}, picked: {picked} \
                \nPress Enter to check again or type 'yes' to continue anyway: "
                )
            )
            picklist = self.get_picklist_by_code(picklist_code)
            picked = picklist["total-units-picked"] == picklist["total-units"]

    def find_all_open_picklists(self) -> list:
        picklist_codes = []
        for status in ["SPLIT", "PROGRESS"]:
            picklists = self.get_picklists(status)["picklists"]
            picklist_codes += [p["code"] for p in picklists]

        return picklist_codes

    def close_picklist(self, picklist_code: str):
        workorders = self.get_workorders_for_picklist(picklist_code)
        workorders_not_in_terinal_statuses = list(
            filter(lambda w: w["status"] not in ["COMPLETED", "INCOMPLETE"], workorders)
        )
        if workorders_not_in_terinal_statuses:
            for workorder in workorders_not_in_terinal_statuses:
                self.put_workorder_changes(workorder["code"], "INCOMPLETE")
            self.update_picklist_status(picklist_code, "INCOMPLETE")
        else:
            if "COMPLETE" in [w["status"] for w in workorders]:
                self.update_picklist_status(picklist_code, "COMPLETE")
            else:
                self.update_picklist_status(picklist_code, "INCOMPLETE")

    def close_all_open_picklists(self):
        print(waiting("Checking for open picklists and closing them..."))
        open_picklists = self.find_all_open_picklists()
        for pl in open_picklists:
            self.close_picklist(pl)
        print(bold("All picklists are closed!"))
