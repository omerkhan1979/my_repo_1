from dataclasses import asdict
from time import time
from src.api.takeoff.decanting import Decanting

from src.utils.addresses import get_addresses_v2
from src.utils.assortment import Product, transform_list_of_jsons_to_list_of_products
from src.utils.barcode import create_barcode_page
from src.utils.console_printing import link, green, blue, bold, waiting
from src.utils.totes import generate_storage_tote
from src.utils.waiters import wait_for_data_interactively


def ask_user_for_products_numbers() -> dict:
    ambient_osr_count = int(
        input(
            blue(
                "How many AMBIENT OSR products you want in PO? Type 0 if you don't want any: "
            )
        )
    )
    chilled_osr_count = int(
        input(
            blue(
                "How many CHILLED OSR products you want in PO? Type 0 if you don't want any: "
            )
        )
    )
    osr_with_exp_date_count = int(
        input(
            blue(
                "How many OSR products WITH EXPIRATION DATE you want in PO? Type 0 if you don't want any: "
            )
        )
    )
    chemical_osr_count = int(
        input(
            blue(
                "How many CHEMICAL OSR products you want in PO? Type 0 if you don't want any: "
            )
        )
    )
    manual_count = int(
        input(
            blue(
                "How many MANUAL products you want in PO? Type 0 if you don't want any: "
            )
        )
    )

    return {
        "ambient_osr_count": ambient_osr_count,
        "chilled_osr_count": chilled_osr_count,
        "req_exp_date_osr_count": osr_with_exp_date_count,
        "chemical_osr_count": chemical_osr_count,
        "manual_count": manual_count,
    }


@wait_for_data_interactively
def check_po_in_distiller(distiller, po_id: str):
    return distiller.get_purchase_order_by_id(po_id)


@wait_for_data_interactively
def get_po_from_decanting_service(
    decanting_service: Decanting, po_id: str, location_code_gold: int
):
    try:
        result = decanting_service.get_decanting_task_list(location_code_gold, po_id)[
            "data"
        ][0]
        return result
    except IndexError:
        return {}


@wait_for_data_interactively
def wait_for_adjustment_for_po(ims, po_id: str, since=0, exclude_osr=False):
    adjustments = ims.adjustments_for_po(po_id)
    adjustment_since_session_started = [
        a for a in adjustments if a["timestamp"] > since
    ]
    if exclude_osr:
        result = [a for a in adjustment_since_session_started if a["address"] != "01K"]
    else:
        result = adjustment_since_session_started
    return result


def handle_decanting(ims, decanting_ui_url, po_id: str, osr_products: list[Product]):
    """osr-products is a tuple of lists of products"""

    print(link(decanting_ui_url))
    print(green(f"Don't forget to select PO id during decanting: {po_id}"))
    print(blue("Use data below to decant OSR products (products sorted by temp zone):"))

    sorted_osr_products = sorted(osr_products, key=lambda p: p.temp_zone)
    decanting_start_time = int(round(time() * 1000))
    for p in sorted_osr_products:
        for attribute, value in asdict(p).items():
            # those we don't care about for decanting
            if attribute not in [
                "sleeping_area",
                "ecom_id",
                "unit_of_measure",
                "is_weighted",
            ]:
                print(bold(f"{attribute}: {value}"))
        print("\n")

    print(bold(f"\nYour storage tote for decanting: {generate_storage_tote()}"))
    print(input(blue("Press ENTER once you are done with decanting")))
    print(
        waiting(
            "Now let's check new inventory adjustments against this PO (since this session started)"
        )
    )
    wait_for_adjustment_for_po(ims=ims, po_id=po_id, since=decanting_start_time)
    # trying to get adjustments for 1.5 minutes, then stop

    print(input(blue("Decanting finished. Press ENTER to proceed")))


def handle_put_away(ims, po_id: str, manual_products: list[Product]):
    print("Manual items detected.")
    print(input(blue("Press ENTER to start Put Away")))
    print(bold("Barcodes for product and shelves are coming up"))

    barcodes_data = []

    putaway_start_time = int(round(time() * 1000))
    for product in manual_products:
        barcodes_data.append(product.barcode)
        print(bold(f"tom-id: {product.tom_id}, barcode: {product.barcode}"))
        address = get_addresses_v2(ims=ims)[0]
        barcodes_data.append(address)
        print(bold(f"Suggested address: {address}"))

    create_barcode_page(barcodes_data)
    print(input(blue("Press ENTER when you are done with Put Away")))
    print(waiting("Checking inventory increments"))
    wait_for_adjustment_for_po(ims, po_id, since=putaway_start_time, exclude_osr=True)


def filter_products_by_sleeping_area(products, retailer, osr_products=False):
    if osr_products:
        products_jsons = [
            product for product in products if product["sleeping-area"] == "K"
        ]
    else:
        products_jsons = [
            product for product in products if product["sleeping-area"] != "K"
        ]
    return transform_list_of_jsons_to_list_of_products(products_jsons, retailer)
