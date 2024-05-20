"""
Set of functions to help find appropriate location-code-tom for various use-cases
"""

from typing import Optional
import requests
from src.utils.console_printing import red, bold
from src.utils.config import get_url_builder
from src.utils.http import handle_response

locations_endpoint = "v1/locations"
new_loc_endpoint = "/locations"
default_headers = {
    "accept": "application/json",
    "content-type": "application/json",
}

# TODO this needs refactoring as all of this in using TSC (service-catalog) so
# there is no reason to pass the service-name as a parameter in these functions


def get_mfc_location_tom_codes(
    retailer, env: str, token: str, service_name: str
) -> tuple:
    """This function is called during Config generation, meaning that
    no instance of TSC class can be created.

    Args:
        retailer (_type_): which client
        env (str): which env
        token (str): used in headers
        service_name (str): endpoint to contact

    Returns:
        tuple: (location, details for that location)
    """
    url_builder = get_url_builder("api/", service_name)
    request_url = url_builder(
        retailer=retailer,
        env=env,
        rel=locations_endpoint,
    )
    response = requests.get(url=request_url, headers={"x-token": token})

    data = handle_response(response, 200)
    # Example of possible contents of data:
    # [] or
    # [
    #   {
    #     "timezone": "string",
    #     "location-type": "mfc",
    #     "mfc-ref-code": "string",
    #     "location-address": {
    #       ...
    #     },
    #     "location-pickup": {
    #       ....
    #     },
    #     "location-service-info": {
    #       ....
    #     },
    #     .....
    #   }
    # ]
    # or above multiple entries
    return tuple(
        location["location-code-tom"]
        for location in data
        if location["location-type"] == "mfc"
    )


def is_location_code_tom_valid(
    retailer: str, env: str, token: str, location_code_tom: str
) -> Optional[str]:
    """
    Function that returns location-code-tom provided by user
    if it has valid mfc location. Is not a part of TSC class, since
    Config object (as defined in config.py) is not created yet

    Args:
        retailer (str): name of client
        env (str): executing env
        token (str): for auth header
        location_code_tom (str): location to check if its valid

    Returns:
        str or None: returns same location if valid, None otherwise
    """

    mfc_location_tom_codes = get_mfc_location_tom_codes(
        retailer, env, token, "service-catalog"
    )

    if location_code_tom in mfc_location_tom_codes:
        return location_code_tom
    else:
        print(red("Couldn't find given location among available location-codes: "))
        suggest_mfc_location_tom_codes(retailer, env, token, "service-catalog")
        return None


def suggest_mfc_location_tom_codes(
    retailer: str, env: str, token: str, service_name: str
):
    """Prints out some locations that enabled for client

    Args:
        retailer (str): name of retailer
        env (str): env we are checking
        token (str): used for headers
        service_name (str): name of the service
    """
    locations = get_mfc_location_tom_codes(retailer, env, token, service_name)
    print(bold("Available MFC location-tom-codes: "))
    for location in locations:
        print(bold(f"- {location}"))


def get_location_without_token(
    retailer: str, env: str, service_name: str
) -> list[dict]:
    """Gets the locations enabled from service catalog without any token"""
    url_builder = get_url_builder("", service_name)
    request_url = url_builder(
        retailer=retailer,
        env=env,
        rel=new_loc_endpoint,
    )
    response = requests.get(
        url=request_url,
        headers=default_headers,
    )

    return handle_response(response, 200)
