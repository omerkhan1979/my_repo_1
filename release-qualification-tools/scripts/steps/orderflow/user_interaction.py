from sys import exit

from src.config.constants import (
    RETAILERS_WITH_ISPS,
    RETAILERS_WITHOUT_MANUAL_ZONE,
    RETAILERS_WITH_TRUCK_LOAD,
)
from src.utils.assortment import transform_list_of_jsons_to_list_of_products
from src.utils.console_printing import yellow, red, blue, cyan, bold


def verify_products_ids(distiller, retailer, tom_ids):
    data = distiller.get_products_by_tom_ids(tom_ids)
    products = transform_list_of_jsons_to_list_of_products(data, retailer)
    # Excluding found products from set of entered products by user
    not_found_products = set(tom_ids) - set(p.tom_id for p in products)
    if len(not_found_products):
        print(
            yellow(
                f"Not found products data for {not_found_products}, these products will be skipped"
            )
        )
    if products:
        return products
    else:
        print(red("Couldn't find valid products among provided tom ids! Exiting..."))
        exit()


def input_product_counts(retailer) -> tuple:
    if retailer in RETAILERS_WITH_ISPS:
        picklist_non_weighted_qty = int(
            input(
                blue(
                    "How many NON-WEIGHTED products you want in picklist? Type 0 if you don't want any: "
                )
            )
        )
        picklist_weighted_qty = int(
            input(
                blue(
                    "How many WEIGHTED products you want in picklist? Type 0 if you don't want any: "
                )
            )
        )
    else:
        picklist_non_weighted_qty = 0
        picklist_weighted_qty = 0
    picklist_total_qty = picklist_non_weighted_qty + picklist_weighted_qty

    osr_products_qty = int(
        input(
            blue(
                "!!!REMINDER: you can switch Manual Mode ON/OFF in the OSR replicator service"
                "\nHow many products you want to be picked from OSR? Type 0 if you don't want any: "
            )
        )
    )

    if retailer not in RETAILERS_WITHOUT_MANUAL_ZONE:
        manual_non_weighted_qty = int(
            input(
                blue(
                    "How many NON-WEIGHTED manual products you want? Type 0 if you don't want any: "
                )
            )
        )
        manual_weighted_qty = int(
            input(
                blue(
                    "How many WEIGHTED manual products you want? Type 0 if you don't want any: "
                )
            )
        )
    else:
        manual_non_weighted_qty = 0
        manual_weighted_qty = 0
    manual_total_qty = manual_non_weighted_qty + manual_weighted_qty
    products = (
        picklist_non_weighted_qty,
        picklist_weighted_qty,
        picklist_total_qty,
        osr_products_qty,
        manual_non_weighted_qty,
        manual_weighted_qty,
        manual_total_qty,
    )

    if not sum(products):
        # Continue while non-zero product quantity provided
        print(
            red(
                "Zero products quantity provided. Please provide non-zero values or interrupt."
            )
        )
        products = input_product_counts(retailer=retailer)
    return products


def ask_if_user_needs_truck_load(retailer, spoke_id: str, store_id: str) -> tuple:
    include_truck_load = False
    if retailer in RETAILERS_WITH_TRUCK_LOAD:
        include_truck_load = input(blue("Do you want to include Truck Load? (y/n): "))
        if "y" in include_truck_load:
            include_truck_load = True
            print(blue("\nTruck load flow selected! Order will be placed for spoke"))
            print(cyan(f"\nSpoke id is {spoke_id}"))
        else:
            spoke_id = spoke_id if retailer == "winter" else store_id
            print(blue("\n No Truck load flow!"))
    return spoke_id, include_truck_load


def ask_if_user_has_mobile_app():
    answer = input(
        blue(
            "\nWill you use Takeoff Application(TMA) on Android phone?"
            "\nIf no, further interactions will be substituted by corresponding API calls (y/n): "
        )
    )
    if "y" in answer:
        return True
    else:
        print(
            bold(
                "No TMA! All Pickerman interactions will be substituted by corresponding API calls"
            )
        )
        return False
