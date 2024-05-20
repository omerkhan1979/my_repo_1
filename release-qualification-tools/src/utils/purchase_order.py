import json
import datetime
import os
from random import randint
import random
from typing import Optional, TypedDict

from google.auth.credentials import Credentials
from src.api.takeoff.decanting import Decanting
from src.api.takeoff.distiller import Distiller
from src.api.takeoff.rint import CommonPurchaseOrderCreate, POItemCreate

from src.api.third_party.gcp import upload_file_to_google_bucket
from src.api.third_party.sftp_interaction import upload_via_sftp
from src.config.config import Config
from src.config.constants import MANUAL_SLEEPING_AREAS
from src.utils.assortment import Product, find_products_by_criteria
from src.utils.console_printing import green, done, blue, bold
from src.utils.os_helpers import get_cwd, delete_file
from src.utils.sftp_helpers import (
    get_modified_wh_invoice_file,
    get_po_id_from_wh_invoice_file,
    get_modified_dsd_file,
    get_po_id_from_dsd_invoice_file,
)


def make_purchase_order_from_products(
    location_code_retailer: str, products: list[Product]
) -> CommonPurchaseOrderCreate:
    assert len(products) >= 1, "Must provide at least one product in a PO"
    # block below work for creating an item list for Purchase order.
    products_data: list[POItemCreate] = []
    for p in products:
        products_data.append(
            POItemCreate(
                tom_id=p.tom_id,
                product_name=p.name,
                ship_unit_description="BOX",
                product_quantity_in_ship_unit=randint(1, 5),
                ship_unit_quantity=4.0,
                purchase_price=5,
            )
        )

    # generate data for Purchase order with item list
    po_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(
        random.randint(1000, 2000)
    )
    delivery_date = datetime.datetime.now().strftime("%Y-%m-%d")
    return CommonPurchaseOrderCreate(
        purchase_order_id=po_id,
        mfc_id=location_code_retailer,
        delivery_date=delivery_date,
        supplier_id="111000",
        supplier_name="DC",
        supplier_type="DC",
        supplier_account="",
        items=products_data,
    )


POFile = TypedDict("POFile", {"file_name": str, "file_path": str, "po_id": str})


def generate_purchase_order_file_common(
    location_code_tom: str, products: list[Product]
) -> POFile:
    """
    Create a "common" PO json and store it in a file for use in some FTP/Storage
    bucket interaction.
    """
    po = make_purchase_order_from_products(location_code_tom, products)
    po_id = po.purchase_order_id

    # compose a filename and file path
    file_name = "PO_" + location_code_tom + "_inbound_" + po_id + ".json"
    file_path = "/tmp/" + file_name
    json_dump = po.to_json()
    # create a file with composed filename and Purchase order data
    with open(file_path, "w") as file:
        file.write(json_dump)
    return {"file_name": file_name, "file_path": file_path, "po_id": po_id}


def generate_purchase_order_gr_file(products: list[Product]):
    # block below work for creating an item list for Purchase order.
    products_data = []

    po_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    for p in products:
        products_data.append(
            {
                "MATDOC_ITM": "0001",
                "MATERIAL": "20103822",
                "PLANT": "2833",
                "VENDOR": "D060",
                "ENTRY_QNT": "6.000",
                "ENTRY_UOM": "EA",
                "PO_NUMBER": po_id,
                "PO_ITEM": "00020",
            }
        )

    # generate data for Purchase order with item list
    dataset = {
        "MAT_DOC": po_id,
        "DOC_YEAR": "2022",
        "DOC_DATE": "20220828",
        "ENTRY_TIME": "062958",
        "REF_DOC_NO": po_id,
        "ITEMS": products_data,
    }

    # compose a filename and file path
    file_name = "GR_" + po_id + "_1" + ".json"
    file_path = "/tmp/" + file_name
    json_dump = json.dumps(dataset)
    # create a file with composed filename and Purchase order data
    with open(file_path, "w") as file:
        file.write(json_dump)
    return {"file_name": file_name, "file_path": file_path, "po_id": po_id}


def get_po_file_and_id_from_user():
    path_to_po = input(
        blue(
            "Please provide absolute path to Purchase Order file from your local machine:"
        )
    )
    file_name = path_to_po.split("/")[-1]
    po_id = input(blue("Please provide PO id so that script can find it: "))

    return file_name, path_to_po, po_id


class PreparedProducts(TypedDict):
    ambient_osr_products: list[Product]
    chilled_osr_products: list[Product]
    osr_products_with_exp_date: list[Product]
    chemical_osr_products: list[Product]
    manual_products: list[Product]


def prepare_products_for_po(
    distiller: Distiller,
    location_code_retailer,
    retailer,
    ambient_osr_count,
    chilled_osr_count,
    req_exp_date_osr_count,
    chemical_osr_count,
    manual_count,
) -> PreparedProducts:
    ambient_osr_products = find_products_by_criteria(
        distiller=distiller,
        location_code_retailer=location_code_retailer,
        retailer=retailer,
        required_count=ambient_osr_count,
        temp_zones=["ambient"],
        sleeping_areas=["K"],
        req_exp_date=[False, None],
        chemical=[False, None],
    )

    chilled_osr_products = find_products_by_criteria(
        distiller=distiller,
        location_code_retailer=location_code_retailer,
        retailer=retailer,
        required_count=chilled_osr_count,
        temp_zones=["chilled"],
        sleeping_areas=["K"],
        req_exp_date=[False, None],
        chemical=[False, None],
    )
    osr_products_with_exp_date = find_products_by_criteria(
        distiller=distiller,
        location_code_retailer=location_code_retailer,
        retailer=retailer,
        required_count=req_exp_date_osr_count,
        req_exp_date=[True],
        chemical=[False, None],
        sleeping_areas=["K"],
    )
    chemical_osr_products = find_products_by_criteria(
        distiller=distiller,
        location_code_retailer=location_code_retailer,
        retailer=retailer,
        required_count=chemical_osr_count,
        req_exp_date=[False, None],
        chemical=[True],
        sleeping_areas=["K"],
    )
    manual_products = find_products_by_criteria(
        distiller=distiller,
        location_code_retailer=location_code_retailer,
        retailer=retailer,
        required_count=manual_count,
        sleeping_areas=MANUAL_SLEEPING_AREAS,
    )

    return {
        "ambient_osr_products": ambient_osr_products,
        "chilled_osr_products": chilled_osr_products,
        "osr_products_with_exp_date": osr_products_with_exp_date,
        "chemical_osr_products": chemical_osr_products,
        "manual_products": manual_products,
    }


# TODO: This should _always_ just go thru rint. Special cases should just test
# the special case part (e.g. integration processes sftp properly and thats
# that)
def create_po(
    decanting_service: Decanting,
    config: Config,
    location_code_gold: int,  # needs to be retrieved from tsc
    products: list[Product],
    po_provided_by_user=False,
    credentials: Optional[Credentials] = None,
) -> str:
    if config.retailer in ["maf", "wings", "smu"]:
        assert credentials, "Google Credentials are required for file based PO creation"
        generated_file = generate_purchase_order_file_common(
            location_code_tom=config.location_code_tom, products=products
        )
        upload_file_to_google_bucket(
            # TODO: This should be input not lookup.
            project_id=config.google_project_id,
            credentials=credentials,
            integration_etl_bucket_name=config.integration_etl_bucket_name,
            source_filename=generated_file["file_name"],
            source_filepath=generated_file["file_path"],
        )
        # remove file locally after uploading to GCP
        os.remove(generated_file["file_path"])
        print(
            green(
                done(
                    f"!!Generated {generated_file['file_name']} is removed/cleaned after upload to bucket!!\n"
                )
            )
        )
        return generated_file["po_id"]

    elif config.retailer in ["abs", "winter", "tienda"]:
        if po_provided_by_user:
            if config.retailer == "winter":
                file_name, file_path, po_id = get_po_file_and_id_from_user()
                upload_via_sftp(
                    config=config, source_filename=file_name, source_filepath=file_path
                )
                return po_id
            else:
                po_id = input(blue("Please provide PO id so that script can find it: "))
            return po_id

    # TODO: Switch to rint.
    print(bold("Posting PO to decanting service..."))

    return decanting_service.v2_add_purchase_order(location_code_gold, products)


def upload_sftp_po_single_mfc(retailer, cfg: Config):
    project_root_dir = get_cwd()
    wh_invoice_body, document_id_divided, _, _ = get_modified_wh_invoice_file(
        retailer, project_root_dir, multiple_mfc=False
    )
    po_id, _ = get_po_id_from_wh_invoice_file(wh_invoice_body, document_id_divided)
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    filename = f"wh_invoice_{now}.txt"
    filepath = f"{project_root_dir}/data/{filename}"
    with open(filepath, "w+") as wh_invoice:
        wh_invoice.write(wh_invoice_body)

    upload_via_sftp(cfg, filename, filepath)

    delete_file(filepath)
    print(
        green(done(f"!!Generated file {filename} is removed/cleaned after upload!!\n"))
    )
    return po_id


def upload_sftp_po_multiple_mfc(retailer, cfg: Config) -> tuple[str, str]:
    project_root_dir = get_cwd()
    (
        _,
        document_id_divided,
        wh_invoice_body_multiple,
        document_id_divided2,
    ) = get_modified_wh_invoice_file(retailer, project_root_dir, multiple_mfc=True)

    po_id1, po_id2 = get_po_id_from_wh_invoice_file(
        wh_invoice_body_multiple,
        document_id_divided,
        document_id_divided2,
        multiple_mfc=True,
    )

    assert wh_invoice_body_multiple, "Invoice body is required for upload via sftp"
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    filename = f"wh_invoice_{now}.txt"
    filepath = f"{project_root_dir}/data/{filename}"
    with open(filepath, "w+") as wh_invoice:
        wh_invoice.write(wh_invoice_body_multiple)

    upload_via_sftp(cfg, filename, filepath)

    delete_file(filepath)
    print(
        green(done(f"!!Generated file {filename} is removed/cleaned after upload!!\n"))
    )
    return po_id1, po_id2


def upload_sftp_po_dsd_file(
    retailer, cfg: Config, location_code_retailer, product
) -> int:
    project_root_dir = get_cwd()
    dsd_invoice_body, document_id_divided = get_modified_dsd_file(
        retailer, project_root_dir, location_code_retailer, product
    )
    po_id = get_po_id_from_dsd_invoice_file(dsd_invoice_body, document_id_divided)
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    filename = f"dsd_invoice_{now}.txt"
    filepath = f"{project_root_dir}/data/{filename}"
    with open(filepath, "w+") as dsd_file:
        dsd_file.write(dsd_invoice_body)

    print(f"INVOICE BODY:\n{dsd_invoice_body}\n")
    upload_via_sftp(cfg, filename, filepath)

    delete_file(filepath)
    print(
        green(done(f"!!Generated file {filename} is removed/cleaned after upload!!\n"))
    )
    return po_id
