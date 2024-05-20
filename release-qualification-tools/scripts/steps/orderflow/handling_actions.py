from time import sleep
from src.api.takeoff.ims import IMS
from src.api.takeoff.isps import ISPS
from src.utils.assortment import Product, get_product_from_list_by_tom_id
from src.utils.barcode import create_barcode_page
from src.utils.console_printing import blue, bold, red, waiting, link
from src.utils.order_status import check_status_change_interactively
from src.utils.picklist_helpers import (
    force_picklist_creation,
    get_picklist_name_in_tma,
)
from src.utils.totes import generate_target_tote
from src.api.takeoff.oms import OMS
from src.api.takeoff.pickerman_facade import PickermanFacade


def handle_putaway_from_store(
    ims: IMS, addresses_and_barcodes: dict, picklist_tom_ids: list[str]
):
    print(
        blue(
            "Use TMA application ('Put Away From Store') to put away picklist products to dynamic shelves!"
        )
    )
    print(blue("Addresses and product barcodes: "))

    barcode_data = []

    for address, barcode in addresses_and_barcodes.items():
        print(bold(address))
        print(bold(barcode))
        barcode_data.append(address)
        barcode_data.append(barcode)
    input(blue("Press ENTER to open barcode sheet"))
    create_barcode_page(barcode_data)

    input(blue("Press Enter once you finish putaway from store: "))
    picklist_product_stock = ims.v2_snapshot(picklist_tom_ids)["addresses"]
    _continue = "no"
    while len(picklist_product_stock) < len(picklist_tom_ids) and _continue != "yes":
        _continue = input(
            red(
                "Can't find picklist products on dynamic addresses! \
                              \nMake sure you have put them away or type 'yes' to continue anyway: "
            )
        )
        picklist_product_stock = ims.v2_snapshot(picklist_tom_ids)["addresses"]


def handle_picklist(
    oms: OMS,
    ims: IMS,
    isps: ISPS,
    cutoff: str,
    picklist_products: list[Product],
    addresses_and_barcodes: dict,
    in_store_picking_url,
):
    barcode_data = []
    force_picklist_creation(oms=oms, cutoff=cutoff, picklist_type="PRELIM")
    print(waiting("Waiting 60 seconds for picklist to get created..."))
    picklist = isps.find_picklists_by_cutoff_and_status(cutoff, "SPLIT")[0]

    picklist_code = picklist["code"]
    print(
        blue(
            f"\nPicklist created, picklist ID is {picklist_code}. Your Picklist in TMA application under In-Store picking is:"
        )
    )
    print(get_picklist_name_in_tma(cutoff, "PRELIM"))
    store_pick_url = link(in_store_picking_url)
    print(
        blue(
            f"\nYour picklist in TOM UI: {store_pick_url} "
            f"\nwith cutoff-datetime in UTC: {cutoff}"
        )
    )
    print(
        blue(
            "Picklist might contain these products (for many reasons, difficult to tell for sure): "
        )
    )
    for product in picklist_products:
        print(bold(f"{product.name, product.tom_id}"))

    print(blue("\nBarcodes for picklist products: \n"))
    for product in picklist_products:
        print(bold(product.barcode))
        barcode_data.append(product.barcode)

    input(blue("Press ENTER to open barcode sheet"))
    create_barcode_page(barcode_data)

    input(
        blue(
            "PICK YOUR PICKLIST IN TMA Application! PRESS ENTER WHEN YOU FINISH PICKING: "
        )
    )
    isps.check_if_picklist_status_change_happened(picklist_code, ("PROGRESS",))
    isps.check_if_picklist_items_picked(picklist_code)

    handle_putaway_from_store(
        ims=ims,
        addresses_and_barcodes=addresses_and_barcodes,
        picklist_tom_ids=[p.tom_id for p in picklist_products],
    )

    input(
        blue(f"\nMARK PICKLIST AS COMPLETE HERE: {link(in_store_picking_url)}")
        + blue("\n Press Enter once done: ")
    )
    isps.check_if_picklist_status_change_happened(
        picklist_code, ("COMPLETE", "INCOMPLETE")
    )


def handle_manual_picking(products: list[Product], reservations: list):
    print(blue("Continue picking. Here's your barcode data:"))
    manual_tote = generate_target_tote()
    print(blue("\nAddresses, products, and tote: "))
    barcode_data = []
    for item in reservations:
        address = item["picking-address"]
        print(bold(address))
        barcode_data.append(address)
        product_barcode = get_product_from_list_by_tom_id(
            products, item["product-id"]
        ).barcode
        print(bold(product_barcode))
        barcode_data.append(product_barcode)

    print(bold(manual_tote))
    barcode_data.append(manual_tote)
    if barcode_data:
        input(blue("Press ENTER to open barcode sheet"))
        create_barcode_page(barcode_data)


def handle_consolidation(ims: IMS, order_id: str):
    print(blue("Scan OSR totes: "))
    totes_from_ramp = ims.get_ramp_state_for_order(order_id)
    for tote in totes_from_ramp:
        print(bold(tote))
    input(blue("Press ENTER to open barcode sheet: "))
    create_barcode_page(totes_from_ramp)


def handle_staging(oms: OMS, fftracker, order_id: str, staging_location: str):
    print(bold("Stage the order. Staging location: "))
    sleep(1)

    order_totes = fftracker.order_totes(order_id).get("data", [{}])[0].get("totes")
    if not order_totes:
        print(bold("No totes found in ff-tracker... Maybe you were too fast"))
    barcode_data = []
    print(bold("Staging location and totes to scan: "))
    for tote in order_totes:
        print(bold(tote))
        barcode_data.append(tote)

    print(bold(staging_location))
    barcode_data.append(staging_location)
    input(blue("Press ENTER to open barcode sheet: "))
    create_barcode_page(barcode_data)

    input(blue("\nPress Enter once done: "))
    check_status_change_interactively(oms, order_id, "staged")


def handle_truck_load(
    facade: PickermanFacade,
    retailer,
    oms: OMS,
    order_id: str,
    order_status: str,
    route_id: str,
    spoke_id: str,
) -> object:
    print(
        bold(
            "Now you can perform 'Truck Load' in TMA Application! Open Truck Load menu"
        )
    )
    print(blue("Route and totes to scan for truck load: "))
    barcode_data = []
    totes = facade.get_totes_for_route(order_status, route_id)
    for tote in totes:
        print(bold(tote))
        barcode_data.append(tote)
    print(bold(route_id))
    barcode_data.append(route_id)

    input(blue("Press ENTER to open barcode sheet"))
    create_barcode_page(barcode_data)
    input("Press Enter once done: ")

    truck_load_status = "served"
    check_status_change_interactively(oms, order_id, truck_load_status)
