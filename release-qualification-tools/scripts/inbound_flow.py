import sys
from src.api.takeoff.bifrost import Bifrost

from src.api.takeoff.decanting import Decanting
from src.api.takeoff.distiller import Distiller
from src.api.takeoff.ims import IMS
from src.api.takeoff.tsc import TSC
from src.api.third_party.gcp import login_to_gcp
from src.config.config import get_config, Config
from src.config.constants import (
    RETAILERS_WITH_PO_UPLOAD_TO_BUCKET,
)
from src.utils.console_printing import blue, red, waiting, bold, link
from scripts.steps.inbound_flow import (
    check_po_in_distiller,
    get_po_from_decanting_service,
    handle_decanting,
    handle_put_away,
    filter_products_by_sleeping_area,
    ask_user_for_products_numbers,
)
from src.utils.purchase_order import prepare_products_for_po, create_po

cfg = Config(*get_config())
distiller = Distiller(cfg)
decanting_service = Decanting(cfg)
ims = IMS(cfg)
tsc = TSC(cfg)
bifrost = Bifrost(cfg, tsc.get_location_code("location-code-gold"))

po_provided_by_user = False
osr_products = None
manual_products = None

location_code_retailer = tsc.get_location_code("location-code-retailer")
location_code_gold = int(tsc.get_location_code("location-code-gold"))

if cfg.retailer in [
    "winter",
]:
    po_provided_by_user_answer = input(
        blue(
            "1 - Provide PO id and/or file \n"
            "2 - Create PO directly in decanting service \n"
        )
    )
    while po_provided_by_user_answer not in ["1", "2"]:
        po_provided_by_user_answer = input(blue("Please type 1 or 2: "))
    if po_provided_by_user_answer == "1":
        po_provided_by_user = True
    elif po_provided_by_user_answer == "2":
        po_provided_by_user = False

if po_provided_by_user:
    products = []
    # TODO: is it correct to create po with empty list of products in this way?
else:
    prepared_products = prepare_products_for_po(
        distiller=distiller,
        retailer=cfg.retailer,
        location_code_retailer=location_code_retailer,
        **ask_user_for_products_numbers(),
    )

    osr_products = (
        prepared_products["ambient_osr_products"]
        + prepared_products["chilled_osr_products"]
        + prepared_products["osr_products_with_exp_date"]
        + prepared_products["chemical_osr_products"]
    )
    products = osr_products + prepared_products["manual_products"]

credentials = None
if cfg.retailer in RETAILERS_WITH_PO_UPLOAD_TO_BUCKET:
    # TODO: What happens when retailer not in the list during next step? (create_po with an empty
    # TODO: credentials and project id)
    credentials = login_to_gcp()

po_id = create_po(
    decanting_service=decanting_service,
    config=cfg,
    location_code_gold=location_code_gold,
    products=products,
    po_provided_by_user=po_provided_by_user,
    credentials=credentials,
)

if po_provided_by_user is None:
    print(blue(waiting("Waiting for Purchase order to be processed ...\n")))
    print(bold("Will check if PO appeared in Distiller..."))
    check_po_in_distiller(distiller=distiller, po_id=po_id)

print(waiting("Getting PO from decanting service..."))
purchase_order = get_po_from_decanting_service(
    decanting_service=decanting_service,
    po_id=po_id,
    location_code_gold=location_code_gold,
)
if purchase_order:
    print(input(blue("To begin decanting process press ENTER: ")))
else:
    print(red(f"Couldn't find po {po_id} in decanting service! Exiting..."))
    sys.exit(-1)

if po_provided_by_user:
    # list of ids required for distiller endpoint
    po_product_ids = [product["product"] for product in purchase_order["products"]]
    distiller_product_data = distiller.get_products_by_tom_ids(po_product_ids)
    purchase_order["products"] = dict(
        zip(po_product_ids, purchase_order["products"])
    )  # converting list of products in PO to dict

    osr_products = filter_products_by_sleeping_area(
        products=distiller_product_data, retailer=cfg.retailer, osr_products=True
    )
    manual_products = filter_products_by_sleeping_area(
        products=distiller_product_data, retailer=cfg.retailer, osr_products=False
    )

if osr_products:
    if bifrost.get_health_pass():
        handle_decanting(
            ims=ims,
            decanting_ui_url=cfg.decanting_ui_url,
            po_id=po_id,
            osr_products=osr_products,
        )
    else:
        quit(red("Bifrost is not healthy!"))
else:
    print(bold("No OSR products found in this PO"))

if manual_products:
    handle_put_away(ims=ims, po_id=po_id, manual_products=manual_products)
else:
    print(bold("No manual products in this PO"))

print("\nReceiving of this PO is finished. You may close the PO")
print(bold(link(f"https://{cfg.url}/decanting/")))
