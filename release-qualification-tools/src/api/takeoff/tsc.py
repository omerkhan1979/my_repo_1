from enum import Enum
import functools
from random import choice
import requests
from typing import Optional, Tuple

from src.api.takeoff.base_api_takeoff import BaseApiTakeoff
from src.utils.config import get_url_builder
from src.utils.locations import locations_endpoint
from src.config.constants import RETAILERS_WITH_NO_SPOKES_IN_SYSTEM
from src.utils.console_printing import yellow
from src.utils.http import handle_response

TSC_CATEGORIES_ENV = (
    "decanting-ui",
    "features",
    "inbound",
    "inventory",
    "outbound",
    "rint-api",
    "rint-etl",
    "rint-gold",
    "rint-sinfonietta",
    "user-management",
)

TSC_CATEGORIES_MFC = (
    "osr",
    "pickerman",
    "decanting",
    "isps",
    "fulfillment-orchestrator",
    "planogram",
    "ecom",
    "takeoff-mobile",
)


class TscReturnFormat(Enum):
    edn = "edn"
    json = "json"


class TSC(BaseApiTakeoff):
    url_builder = get_url_builder("api/", "service-catalog")
    config_items_endpoint = "v1/configuration/config-items"
    put_config_items_endpoint = "v1/configuration/config-items/values"
    routes_endpoint = "v1/routes"
    mfc_location_endpoint = "v1/location/mfc"  # used to create MFC definition
    flow_racks_endpoint = "v1/flow-racks"  # used for both get/put
    tote_location_types_endpoint = "v1/tote/location/types"
    tote_type_endpoint = "v1/tote/type"  # Create a new tote-type definition
    staging_locations = "v1/staging-locations"
    location_endpoint = "v1/location"
    # used to set default staging location
    staging_locations_default = staging_locations + "/default"
    put_profile = "v1/profile/apply"  # added for future usage if needed
    apply_profile_endpoint = "v1/profile/apply"
    # get list of staging configurations for MFC.
    staging_configurations_endpoint = "v1/staging-configurations"
    _cached_config_items = None

    # ---------Profile---------

    def apply_profile(self, location_code_tom: str | None = None):
        """Apply profile on a newly created location
        Args:
            location_code_tom (str): The TOM code of an MFC to sync.

        Returns:
            dict: result of the apply profile
        """
        url = self.url_builder(rel=self.apply_profile_endpoint)

        response = requests.put(
            url=url,
            headers=self.default_headers,
            json={
                "tom-code": location_code_tom or self.config.location_code_tom,
                "profile-name": "default_staging_mfc_profile",
            },
        )
        return handle_response(response, 200, 207)

    # ---------Locations---------

    def get_locations(self) -> list[dict]:
        """Returns a list of details of locations
        could be [] or [{}] or [{},...]

        Returns:
            list[dict]: list of details of locations or empty list
        """
        url = self.url_builder(rel=locations_endpoint)

        response = requests.get(
            url=url,
            headers=self.default_headers,
        )
        return handle_response(response, 200)

    def get_location(self, location_id: int) -> dict:
        url = self.url_builder(rel=f"{self.location_endpoint}/{location_id}")

        response = requests.get(
            url=url,
            headers=self.default_headers,
        )
        return handle_response(response, 200)

    def get_location_id_by_code_tom(self, location_code_tom: str = None) -> int:
        return self.get_location_details(location_code_tom)["location-id"]

    def update_location(self, mfc_id: int, location_details: dict) -> dict:
        """Updates a location with come changes

        Args:
            mfc_id (int): unique id of the location
            location_details (dict): updated content

        Returns:
            dict: returns from the update
        """
        url = self.url_builder(rel=f"{self.location_endpoint}/{mfc_id}")
        response = requests.patch(
            url=url, headers=self.default_headers, json=location_details
        )
        return handle_response(response, 200)

    def update_location_spoke(
        self, mfc_id: int, spoke_id: int, location_details: dict
    ) -> dict:
        """Updates a location with come changes

        Args:
            mfc_id (int): unique id of the location
            spoke_id (int): unique id of the spoke
            location_details (dict): updated content

        Returns:
            dict: returns from the update
        """
        url = self.url_builder(
            rel=f"{self.location_endpoint}/{mfc_id}/spoke/{spoke_id}"
        )
        response = requests.patch(
            url=url, headers=self.default_headers, json=location_details
        )
        return handle_response(response, 200)

    def create_location_spoke(self, mfc_id: int, spoke_details: dict) -> dict:
        """Creates a spoke for a mfc

        Args:
            mfc_id (int): unique id of the location
            spoke_details (dict): updated content

        Returns:
            dict: returns from the update
        """
        url = self.url_builder(rel=f"{self.location_endpoint}/{mfc_id}/spoke")
        body = spoke_details
        body["enabled?"] = True
        response = requests.post(url=url, headers=self.default_headers, json=body)
        return handle_response(response, 200)

    def get_tom_code_locations(self, enabled="true") -> list[dict]:
        """Returns a list of locations

        Returns:
            json: list of locations
        """
        url = self.url_builder(rel=locations_endpoint)

        response = requests.get(
            url=url, headers=self.default_headers, params={"enabled": enabled}
        )
        return handle_response(response, 200)

    def get_enabled_mfc_locations(self, enabled="true") -> list[dict]:
        """Returns a list of all enabled MFC locations

        Returns:
            json: list of locations
        """
        locations_list = self.get_tom_code_locations(enabled)
        mfc_locations = list(
            filter(
                (lambda location: (location["location-type"] == "mfc")),
                locations_list,
            )
        )
        return mfc_locations

    def get_location_details(self, location_tom_code: str = None) -> dict:
        """Call the locations endpoint and get data for the passed in location

        Args:
            location_tom_code (str, optional): location to gain details about. Defaults to None.

        Returns:
            dict: details of location or details of all locations
        """
        locations = self.get_locations()
        if locations is None or len(locations) == 0:
            return None
        if not location_tom_code:
            location_tom_code = self.config.location_code_tom
        selected_location_data = list(
            filter(
                lambda location: location["location-code-tom"] == location_tom_code,
                locations,
            )
        )
        return selected_location_data[0] if selected_location_data else None

    @functools.cache
    def get_location_code(
        self, location_code_type: str, location_tom_code: str = None
    ) -> dict | str:
        """Returns details of the location code and its type

        Args:
            location_code_type (str): mfc/spoke
            location_tom_code (str, optional): If not provided, returns the details of the first found of the selected type. Defaults to None.

        Returns:
            dict | str: details of location found or str of the value of the location_tom_code
        """
        selected_location_data = self.get_location_details(location_tom_code)
        if selected_location_data and location_code_type:
            location_code_retailer = selected_location_data[location_code_type]
            return location_code_retailer

        return selected_location_data

    def get_spoke_id_for_mfc_tom_location(self) -> str:
        """If the mfc has a spoke that spoke is returned,
        otherwise the location code is returned

        Returns:
            str: location-code-retailer or spoke_id or None if not locations
        """
        spoke_id = None
        if self.config.retailer in RETAILERS_WITH_NO_SPOKES_IN_SYSTEM:
            print(
                f"No spokes for {self.config.retailer}!"
                "Using mfc location code as spoke id."
            )
            return self.get_location_code("location-code-retailer")

        locations = self.get_locations()
        if locations:
            all_spokes_for_mfc = list(
                filter(
                    lambda location: location["mfc-ref-code"]
                    == self.config.location_code_tom
                    and location["location-type"] == "spoke",
                    locations,
                )
            )
        try:
            spoke_id: str = choice(all_spokes_for_mfc)["location-code-retailer"]
        except IndexError:
            print(
                yellow(
                    "No spokes found for location-code-tom "
                    f"{self.config.location_code_tom}! Will use MFC"
                )
            )
            return self.config.location_code_tom
        return spoke_id

    def get_mfc_timezone(self, location_tom_code: str) -> Tuple[str, str]:
        """Given a location, return the timezone for it's MFC (input can
        be spoke or mfc location code). Raise ValueError if a location
        cannot be found."""

        details = self.get_location_details(location_tom_code)
        if not details:
            # we maybe were passed a retailer location code vs a tom code...
            print(f"Getting timezone from {location_tom_code} found no locations..")
            for loc in self.get_locations():
                if loc.get("location-code-retailer") == location_tom_code:
                    tom_code = loc.get("location-code-tom")
                    print(f"... using {tom_code} instead")
                    details = self.get_location_details(tom_code)
                    break
            else:
                raise ValueError(f"No details for {location_tom_code}")

        if details["location-type"] == "mfc":
            return details["timezone"], location_tom_code
        else:
            return (
                self.get_location_details(details["mfc-ref-code"])["timezone"],
                details["mfc-ref-code"],
            )

    def get_all_spokes_for_mfc_tom(self, location_code_tom=None) -> list:
        locations = self.get_locations()
        all_spokes_for_mfc = []
        if locations:
            all_spokes_for_mfc = list(
                filter(
                    (
                        lambda location: (
                            location["mfc-ref-code"] == location_code_tom
                            or self.config.location_code_tom
                        )
                        and (location["location-type"] == "spoke")
                    ),
                    locations,
                )
            )
        return all_spokes_for_mfc

    def set_location_availability(self, location_code: int, error_codes=None):
        if error_codes is None:
            error_codes = [200]
        url = self.url_builder(
            rel=f"{self.location_endpoint}/{location_code}/availability"
        )
        response = requests.put(
            url=url,
            headers=self.default_headers,
            params={"enabled?": "true"},
        )
        return handle_response(response, *error_codes)

    def post_mfc_location(self, body, error_codes=None):
        if error_codes is None:
            error_codes = [200]
        url = self.url_builder(rel=self.mfc_location_endpoint)
        response = requests.post(
            url=url,
            headers=self.default_headers,
            json=body,
        )
        return handle_response(response, *error_codes)

    # ------Configurations Items--------------

    def get_config_items(
        self,
        force: bool = False,
        level: str = "env",
        location_tom_code: Optional[str] = None,
        return_format: TscReturnFormat = TscReturnFormat.edn,
    ) -> list[dict]:
        """Returns config-items from cache if any or forces request to TSC if
        force == True
        """
        if self._cached_config_items and not force:
            return self._cached_config_items
        url = self.url_builder(rel=self.config_items_endpoint)

        params = {"level": level} if level else {}
        params["value-format"] = return_format.value

        if location_tom_code:
            params["location-codes"] = location_tom_code
        response = requests.get(
            url=url,
            headers=self.default_headers,
            params=params,
        )

        self._cached_config_items = handle_response(response, 200)
        return self._cached_config_items

    def put_config_items(self, payload: list, error_codes=None):
        """Puts a list of config items onto the endpint

        Args:
            payload (list): config items
            error_codes (list, optional): possible error codes. Defaults to None.

        Returns:
            Any: response
        """
        if error_codes is None:
            error_codes = [201]
        url = self.url_builder(rel=self.put_config_items_endpoint)
        response = requests.put(
            url=url,
            headers=self.default_headers,
            json=payload,
        )

        return handle_response(response, *error_codes)

    def get_config_item_value(
        self,
        param_name: str,
        force: bool = False,
        env: Optional[str] = None,
        return_format: TscReturnFormat = TscReturnFormat.json,
    ):
        """Searches for param value in cached config-items if force == False or
        requests for a new one otherwise

        Args:
            param_name (str): item we want to retrieve
            force (bool, optional): force tsc to update. Defaults to False.
            env (str, optional): at what level. Defaults to None.

        Returns:
            Any: value of the config_item if it exists
        """
        config_item = self.get_config_item(
            param_name, force=force, level=env, return_format=return_format
        )
        if config_item:
            return config_item["value"]
        return None

    def get_config_item(
        self,
        param_name: str,
        force: bool = False,
        level: Optional[str] = None,
        return_format: TscReturnFormat = TscReturnFormat.json,
    ) -> dict:
        """Searches for param in cached config-items if force == False or
        requests for a new one otherwise

        Args:
            param_name (str): item we want to retrieve
            force (bool, optional): force tsc to update. Defaults to False.
            env (str, optional): level of config. Defaults to None.

        Returns:
            dict: contents of the config item
        """
        config_items = self.get_config_items(
            force=force, level=level, return_format=return_format
        )
        for config_item in config_items:
            if config_item["name"] == param_name:
                return config_item

    def express_orders_enabled(self) -> bool:
        date_validation_enabled = (
            self.get_config_item_value(
                "RINT_API__FEATURE__VALIDATION__STAGE_BY_DATETIME_VALIDATION__TURN_ON"
            )
            == "true"
        )
        late_orders_enabled = (
            self.get_config_item_value("AUTO_SPLIT_FOR_LATE_ORDERS_ENABLED") == "true"
        )
        return late_orders_enabled and not date_validation_enabled

    # --------Flow Racks-------------

    def get_flow_racks(self, location_code_tom=None):
        url = self.url_builder(rel=self.flow_racks_endpoint)

        response = requests.get(
            url=url,
            headers=self.default_headers,
            params={"mfc-tom-code": location_code_tom or self.config.location_code_tom},
        )
        return handle_response(response, 200)

    def put_flow_racks(self, flow_racks: dict, error_codes=None):
        if error_codes is None:
            error_codes = [201]
        """Creates or updates flow-racks config associated with MFC

        Args:
            location_code_tom (str): mfc doe
            flow_racks (dict): flow rack details

        Returns:
            json,bytes: result of the put
        """
        url = self.url_builder(rel=self.flow_racks_endpoint)

        response = requests.put(url=url, headers=self.default_headers, json=flow_racks)
        return handle_response(response, *error_codes)

    # ------Staging-Configurations-------

    def get_staging_configurations(
        self, location_code_tom: Optional[str] = None
    ) -> dict:
        """Responds with a list of staging configurations for MFC

        Args:
            location_code_tom (str): mfc code

        Returns:
            dict: list of staging configuration
        """
        url = self.url_builder(rel=self.staging_configurations_endpoint)

        response = requests.get(
            url=url,
            headers=self.default_headers,
            params={"mfc-tom-code": location_code_tom or self.config.location_code_tom},
        )
        return handle_response(response, 200)

    def post_staging_configurations(self, body, error_codes=None):
        """Responds with a message about successful inserting or error

        Args:
            body (_type_):New Staging Configuration

        """
        if error_codes is None:
            error_codes = [201]
        url = self.url_builder(rel=self.staging_configurations_endpoint)

        response = requests.post(
            url=url,
            headers=self.default_headers,
            json=body,
        )
        return handle_response(response, *error_codes)

    # ------Staging-locations-------

    def put_default_staging_location(
        self, default_staging_location: str, location_code_tom=None, error_codes=None
    ) -> dict:
        if error_codes is None:
            error_codes = [201]
        url = self.url_builder(rel=self.staging_locations_default)
        response = requests.put(
            url=url,
            headers=self.default_headers,
            params={
                "mfc-tom-code": location_code_tom or self.config.location_code_tom,
                "default-staging-location": default_staging_location,
            },
        )
        return handle_response(response, *error_codes)

    def get_staging_locations(self, location_code_tom=None) -> dict:
        url = self.url_builder(rel=self.staging_locations)

        response = requests.get(
            url=url,
            headers=self.default_headers,
            params={"mfc-tom-code": location_code_tom or self.config.location_code_tom},
        )
        return handle_response(response, 200)

    def post_staging_location(self, json_body, error_codes=None) -> dict:
        if error_codes is None:
            error_codes = [201]
        url = self.url_builder(rel=self.staging_locations)

        response = requests.post(url=url, headers=self.default_headers, json=json_body)
        return handle_response(response, *error_codes)

    # ----------Tote------------

    def get_tote_location_types(self, location_code_tom=None) -> list:
        """Responds with a list of tote types filtered by TOM code.

        Args:
            location_code_tom (str): tom code used for filter

        Returns:
            list: Response of Tote types
        """
        url = self.url_builder(rel=self.tote_location_types_endpoint)

        response = requests.get(
            url=url,
            headers=self.default_headers,
            params={"tom-code": location_code_tom or self.config.location_code_tom},
        )
        return handle_response(response, 200)

    def patch_tote_type(
        self, tote_type_id: int, body: dict, error_codes: list = None
    ) -> dict:
        """Updates an existing tote type

        Args:
            tote_type_id (int): unique id of tote type
            body (dict): tote_type details
            error_codes (list, optional): list of error codes. Defaults to None.

        Returns:
            dict: results after the patch update
        """
        if error_codes is None:
            error_codes = [200]
        url = self.url_builder(rel=f"{self.tote_type_endpoint}/{tote_type_id}")

        response = requests.patch(
            url=url,
            headers=self.default_headers,
            json=body,
        )
        return handle_response(response, *error_codes)

    def post_tote_type(self, body: dict, error_codes: list = None) -> dict:
        """Creates a new tote_type

        Args:
            body (dict): tote_type details
            error_codes (list, optional): list of errors that are acceptable. Defaults to None.

        Returns:
            dict: results of the create
        """
        if error_codes is None:
            error_codes = [201]
        url = self.url_builder(rel=self.tote_type_endpoint)

        response = requests.post(
            url=url,
            headers=self.default_headers,
            json=body,
        )
        return handle_response(response, *error_codes)

    # ------Routes-----------

    def get_routes(self, location_code_tom=None):
        url = self.url_builder(rel=self.routes_endpoint)
        response = requests.get(
            url=url,
            headers=self.default_headers,
            params={"mfc-tom-code": location_code_tom or self.config.location_code_tom},
        )
        return handle_response(response, 200)

    def post_route(self, json_body, error_codes=None):
        """Route code is not unique, but pair mfc-tom-code + route-code is
        unique.

        Args:
            location_code (str): mfc
            route_code (str): route

        Returns:
            json, bytes: response body of the result of the request
        """
        if error_codes is None:
            error_codes = [201]
        url = self.url_builder(rel=self.routes_endpoint)
        response = requests.post(
            url=url,
            headers=self.default_headers,
            json=json_body,
        )
        return handle_response(response, *error_codes)

    def get_default_or_first_staging_location(self):
        staging_locations = self.get_staging_locations()
        default_location = get_default_staging_location_code(staging_locations)
        if default_location:
            return default_location
        else:
            return staging_locations["staging-locations"][0].get(
                "staging-location-code"
            )

    def delete_route(self, mfc_id: int, route_code: str):
        url = self.url_builder(rel=f"{self.routes_endpoint}/{route_code}/mfc/{mfc_id}")
        response = requests.delete(url=url, headers=self.default_headers)
        return handle_response(response, 200)

    def delete_flow_racks(self, mfc_id: int):
        url = self.url_builder(rel=f"{self.flow_racks_endpoint}/mfc/{mfc_id}")
        response = requests.delete(url=url, headers=self.default_headers)
        return handle_response(response, 200)


def get_default_staging_location_code(staging_locations_dict):
    for d in staging_locations_dict["staging-locations"]:
        if d.get("default"):
            return d.get("staging-location-code", "")
    return ""
