import datetime
from time import sleep

from src.utils.os_helpers import give_file_body


def get_modified_wh_invoice_file(retailer, project_root_dir, multiple_mfc):
    body = give_file_body(f"{project_root_dir}/data/wh_invoice_{retailer}.txt")
    props = body.split(",")
    document_id_part1 = datetime.datetime.now().strftime("%H%M%S")
    date_now = datetime.datetime.now()
    date_tomorrow = date_now + datetime.timedelta(days=1)
    issued_date = date_now.strftime("%Y-%m-%d-%H.%M.%S.%f")
    delivery_date = date_tomorrow.strftime("%Y-%m-%d-%H.%M.%S.%f")
    props[1] = f"1_{document_id_part1}"
    props[2] = issued_date
    props[3] = delivery_date
    wh_invoice_body = ",".join(props)
    document_id_divided = f"1{document_id_part1}"

    if multiple_mfc:
        sleep(1)  # In order to have different PO_id for multiple MFC
        document_id_part2 = datetime.datetime.now().strftime("%H%M%S")
        props[1] = f"1_{document_id_part2}"
        props[0] = "608"
        wh_invoice_body2 = ",".join(props)
        wh_invoice_body_multiple = wh_invoice_body + "\n" + wh_invoice_body2
        print(wh_invoice_body_multiple)
        document_id_divided2 = f"1{document_id_part2}"
    else:
        document_id_divided2 = None
        wh_invoice_body_multiple = None

    return (
        wh_invoice_body,
        document_id_divided,
        wh_invoice_body_multiple,
        document_id_divided2,
    )


def get_po_id_from_wh_invoice_file(
    wh_invoice_body, document_id_divided, document_id_divided2=None, multiple_mfc=False
) -> tuple[str, str]:
    props = wh_invoice_body.split(",")
    delivery_date = props[3]
    delivery_date_divided = delivery_date.split("-")
    po_id_divided = (
        delivery_date_divided[0][2:]
        + delivery_date_divided[1]
        + delivery_date_divided[2]
    )
    po_id1 = po_id_divided + document_id_divided
    if multiple_mfc:
        po_id2 = po_id_divided + document_id_divided2
    else:
        po_id2 = None
    return po_id1, po_id2


def get_modified_dsd_file(retailer, project_root_dir, location_code_retailer, product):
    body = give_file_body(f"{project_root_dir}/data/dsd_invoice_{retailer}.txt")
    props = body.split(",")
    document_id_part1 = datetime.datetime.now().strftime("%H%M%S")
    date_now = datetime.datetime.now()
    date_tomorrow = date_now + datetime.timedelta(days=1)
    issued_date = date_now.strftime("%Y-%m-%d-%H.%M.%S.%f")
    delivery_date = date_tomorrow.strftime("%Y-%m-%d-%H.%M.%S.%f")
    props[0] = location_code_retailer
    props[1] = f"1_{document_id_part1}"
    props[2] = issued_date
    props[3] = delivery_date
    props[4] = product[0].tom_id
    props[5] = product[0].ecom_id
    props[6] = str(product[0].name)
    dsd_invoice_body = ",".join(props)
    document_id_divided = f"1{document_id_part1}"

    return dsd_invoice_body, document_id_divided


def get_po_id_from_dsd_invoice_file(wh_invoice_body, document_id_divided) -> int:
    props = wh_invoice_body.split(",")
    delivery_date = props[3]
    delivery_date_divided = delivery_date.split("-")
    po_id_divided = (
        delivery_date_divided[0][2:]
        + delivery_date_divided[1]
        + delivery_date_divided[2]
    )
    po_id = po_id_divided + document_id_divided

    return po_id
