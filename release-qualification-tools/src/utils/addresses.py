from random import sample, choice
from time import sleep

from exrex import getone
from pprint import pprint
from requests.models import HTTPError
from src.api.takeoff.ims import IMS

from src.utils.console_printing import error_print, red, yellow, blue


def generate_random_address(location_code_tom: str, dynamic=False) -> dict:
    temp_zone, area = choice([["ambient", "A"], ["chilled", "B"], ["frozen", "C"]])

    if dynamic:
        area = "D"

    prefix = getone(r"\d{4}") if dynamic else getone(r"\d{2}")
    aisle = getone(r"\d{2}")
    bay = getone(r"\d{3}")
    shelf = getone(r"\d{1}")
    stack = getone(r"[A-K]{1}")

    address_string = prefix + area + aisle + bay + shelf + stack

    address_data = {
        "address": address_string,
        "location-id": location_code_tom,
        "area": area,
        "temp-zone": temp_zone,
        "aisle": aisle,
        "bay": bay,
        "shelf": shelf,
        "stack": stack,
    }

    return address_data


def get_addresses_v2(ims: IMS, qty_of_addresses: int = 1, dynamic=False) -> list:
    """
    Function to find or create (if not found) given number of addresses in IMS.
    If addresses not found, it'll try to migrate addresses from 'balances' table
    and query them again.
    If still not enough addresses found it will generate address data and create them one by one
    """
    # function might be called with 0 qty_of_addresses, don't need to do anything in this case
    result = []
    if not qty_of_addresses:
        return result

    data = ims.v2_get_addresses(
        dynamic=[dynamic], active=[True], pickable=[True], oversrock=[False]
    )
    if (
        not data
    ):  # if ims not returned addresses by provided criteria - will try to migrate from snapshot
        try:
            ims.v2_migrate_addresses()
        except HTTPError:  # if migration fails, will create new addresses
            print(red("Error migrating addresses, will create new ones"))
        else:
            sleep(3)
            data = ims.v2_get_addresses(dynamic=[dynamic])
    else:
        result = [a["address"] for a in data if a["address"] != "01K"]

    try:
        # here 'sample' func raises ValueError when size of population (data) < qty_of_addresses
        result = [
            a["address"]
            for a in sample(data, qty_of_addresses)
            if a["address"] != "01K"
        ]  # excluding 01K
        if (
            len(result) < qty_of_addresses
        ):  # if size of data < qty_of_addresses after 01K exclusion, raise error manually to fallback to creation
            raise ValueError
    except ValueError:
        # Adding max_retries so we don't get stuck in an inifinite loop in the when condition below
        max_retries = 2 * qty_of_addresses
        try_count = 0
        found = len(result)
        print(
            yellow(f"Not enough addresses found! ({found}). Creating...")
        )  # generating and posting one by one
        while len(result) < qty_of_addresses and try_count < max_retries:
            address = generate_random_address(ims.config.location_code_tom, dynamic)
            try:
                print(blue("Creating address: "))
                pprint(address)
                response = ims.v2_create_addresses([address])
                # can't create addresses as dynamic initially, need to create first and then make dynamic
                if dynamic:
                    ims.v2_update_address_attributes(
                        address["address"], dynamic=dynamic
                    )
                pprint(response)
            except (
                HTTPError
            ) as e:  # not to fail test if single address creation fails (if generated duplicate)
                try_count += 1
                print(f"Error creating address: {e}")
            else:
                result.append(address["address"])
        if len(result) < qty_of_addresses:
            error_print("Failed to create the necessary quantity of addresses")
    return result
