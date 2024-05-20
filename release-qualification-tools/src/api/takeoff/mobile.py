"""
Class to interact with Mobile API. It was created for TOMA  - Takeoff Mobile App':
  Swagger doc: https://nonprod.mobile.tom.takeoff.com/
"""

from typing import Optional
import requests
from src.config.config import Config
from src.config.constants import BASE_DOMAIN, ODE_RETAILER

from src.utils.http import handle_response


def get_target_retailer(retailer, env):
    if ODE_RETAILER and env != "prod":
        return ODE_RETAILER
    else:
        return retailer


class Mobile:
    url_builder: str
    target_retailer: str

    def __init__(self, my_config: Config):
        self.config = my_config
        if self.config.env == "prod":
            self.url_builder = "https://prod.mobile.tom.takeoff.com"
        elif self.config.env == "ode":
            self.url_builder = f"https://ode.mobile.{BASE_DOMAIN}"
        else:
            self.url_builder = "https://nonprod.mobile.tom.takeoff.com"

        self.target_retailer = get_target_retailer(
            self.config.retailer, self.config.env
        )

        self.default_headers = {
            "X-Token": self.config.token,
            "accept": "application/json",
            "content-type": "application/json",
            "X-Env-Type": self.config.env,
            "X-Retailer-Id": self.target_retailer,
        }

    def assign_fulfillment_task(self) -> dict:
        url = (
            self.url_builder
            + f"/api/retailers/{self.target_retailer}/mfcs/{self.config.location_code_tom}/fulfillmentTasks:assign"
        )

        response = requests.post(url=url, headers=self.default_headers)
        return handle_response(response, 200)

    def get_totes_fulfillment(
        self,
        fulfillment_task_id,
    ) -> dict:
        url = (
            self.url_builder
            + f"/api/retailers/{self.target_retailer}/mfcs/{self.config.location_code_tom}/fulfillmentTasks/{fulfillment_task_id}/totes"
        )

        response = handle_response(
            requests.get(url=url, headers=self.default_headers), 200
        )
        return response["fulfillment_task"]["totes_to_collect"][0]["tote"]

    def clear_session(
        self,
        fulfillment_task_id,
        re_enqueue: bool = False,
    ) -> bool:
        url = (
            self.url_builder
            + f"/api/retailers/{self.target_retailer}/mfcs/{self.config.location_code_tom}/fulfillmentTasks/{fulfillment_task_id}:clearSession"
        )
        body = {"re_enqueue": re_enqueue}

        response = requests.put(
            url=url,
            headers=self.default_headers,
            json=body,
        )
        return response.status_code == 200

    def get_truckload_orders(self, route_id: str, order_status: str):
        url = (
            self.url_builder
            + f"/api/retailers/{self.target_retailer}/mfcs/{self.config.location_code_tom}/truckLoad/orders?route_id={route_id}&order_status_after_picking={order_status}"
        )
        response = requests.get(url=url, headers=self.default_headers)
        return handle_response(response, 200)

    def post_truckload(
        self,
        order_ids: list,
        order_status: str,
    ):
        url = (
            self.url_builder
            + f"/api/retailers/{self.target_retailer}/mfcs/{self.config.location_code_tom}/truckLoad:complete"
        )

        json_body = {"truck_load_session_status": order_status, "order_ids": order_ids}
        response = requests.post(url=url, headers=self.default_headers, json=json_body)
        if response.status_code == 200:
            result = response.json()
            status = result.get("orders", [{}])[0].get("status")
            return status
        else:
            response.raise_for_status()

    def putaway(
        self,
        shelf_id: str,
        product_id: str,
        qty: int,
        po: Optional[str] = None,
    ):
        url = (
            self.url_builder
            + f"/api/retailers/{self.target_retailer}/mfcs/{self.config.location_code_tom}/putaway"
        )
        body = {"shelf_id": shelf_id, "product_id": product_id, "quantity": qty}
        if po:
            body["po"] = po

        response = requests.post(
            url=url,
            json=body,
            headers=self.default_headers,
        )
        return handle_response(response, 200)

    def get_staging_locations(
        self,
        fulfillment_task_id: str,
    ):
        url = (
            self.url_builder
            + f"/api/retailers/{self.target_retailer}/mfcs/{self.config.location_code_tom}/fulfillmentTasks/{fulfillment_task_id}/stagingLocations"
        )

        response = requests.get(url=url, headers=self.default_headers)
        return handle_response(response, 200)

    def post_register_staging_location(
        self,
        fulfillment_task_id: str,
        location: str,
    ):
        url = (
            self.url_builder
            + f"/api/retailers/{self.target_retailer}/mfcs/{self.config.location_code_tom}/fulfillmentTasks/{fulfillment_task_id}/stagingLocations:register"
        )
        body = {
            "staging_location": location,
        }

        response = requests.post(
            url=url,
            json=body,
            headers=self.default_headers,
        )
        return handle_response(response, 200)

    def post_fulfillmenttask(self, action: dict, **kwargs):
        url = (
            self.url_builder
            + f"/api/retailers/{self.target_retailer}/fulfillmentTasks/actions:batchCreate"
        )
        """
        the json body will look something like below, its better to process and pass the action from the calling method rather than adding condition here in this method
        {"actions":[{"email":"operatorbigy@takeoff.com","id":"dc7dd5c2-6058-4feb-8adc-83db5ad27efe:493137971477918","mfc_id":"0124","type":"fulfillment.staging.taskStaged","user_id":"FQ2IIcUeKhSDeTTTYvijW23fay43","order_id":"493137971477918","order_part_id":0,"work_task_id":0,"action":{"type":"fulfillment.staging.taskStaged","addressId":"0124H010011A","toteBarcodes":["99890683074937"],"id":"dc7dd5c2-6058-4feb-8adc-83db5ad27efe:493137971477918","workTaskId":0,"orderId":"493137971477918","orderPartId":0,"mfcId":"0124","retailerId":"blueberry","appVersion":"1.10.21","deviceId":"takeoff-mobile","deviceTimestamp":"2023-07-13T16:03:01.879Z","email":"operatorbigy@takeoff.com","environmentTypeId":"qai","userId":"FQ2IIcUeKhSDeTTTYvijW23fay43"}},{"email":"operatorbigy@takeoff.com","id":"0cd36fe2-adc8-4931-ae64-bb952d74aa91:493137971477918","mfc_id":"0124","type":"fulfillment.staging.taskCompleted","user_id":"FQ2IIcUeKhSDeTTTYvijW23fay43","order_id":"493137971477918","order_part_id":0,"work_task_id":0,"action":{"type":"fulfillment.staging.taskCompleted","id":"0cd36fe2-adc8-4931-ae64-bb952d74aa91:493137971477918","workTaskId":0,"orderId":"493137971477918","orderPartId":0,"mfcId":"0124","retailerId":"blueberry","appVersion":"1.10.21","deviceId":"takeoff-mobile","deviceTimestamp":"2023-07-13T16:03:01.903Z","email":"operatorbigy@takeoff.com","environmentTypeId":"qai","userId":"FQ2IIcUeKhSDeTTTYvijW23fay43"}}]}"""
        body = action

        response = requests.post(
            url=url,
            json=body,
            headers=self.default_headers,
        )
        return handle_response(response, 200)

    def put_pack(self, fulfillment_task_id: str):
        url = (
            self.url_builder
            + f"/api/retailers/{self.target_retailer}/mfcs/{self.config.location_code_tom}/fulfillmentTasks/{fulfillment_task_id}:pack"
        )
        body = {"bag_count": 0, "device_identifier": "takeoff-mobile"}

        response = requests.put(
            url=url,
            json=body,
            headers=self.default_headers,
        )
        return handle_response(response, 200)
