from src.api.collections import InitializedApis


def update_order_lineitem_quantity(
    apis: InitializedApis,
    location_code_tom: str,
    orderid: str,
    quantity: int,
) -> None:
    order_details = apis.rint.get_customer_order_v4(location_code_tom, orderid)
    for i in order_details["data"]["line-items"]:
        i["requested-quantity"] = i["requested-quantity"] + quantity

    line_items = []
    mfc_id = order_details["data"]["mfc-id"]
    service_window_start = order_details["data"]["service-window-start"]
    ecom_order_status = order_details["data"]["ecom-order-status"]

    for i in order_details["data"]["line-items"]:
        item = {
            "requested-quantity": int(i["requested-quantity"]),
            "ecom-line-id": i["ecom-line-id"],
            "line-note": i["line-note"],
            "ecom-item-id": i["ecom-item-id"],
            "fulfillment-location": i["fulfillment-location"],
        }
        line_items.append(item)

    apis.rint.update_customer_order(
        orderid,
        mfc_id,
        line_items,
        service_window_start,
        ecom_order_status,
    )


def update_order_specific_fields(
    apis: InitializedApis,
    location_code_tom: str,
    orderid: str,
    field_name: str,
    field_value: str,
) -> None:
    order_details = apis.rint.get_customer_order_v4(location_code_tom, orderid)

    mfc_id = order_details["data"]["mfc-id"]
    service_window_start = order_details["data"]["service-window-start"]
    ecom_order_status = order_details["data"]["ecom-order-status"]

    line_items = []

    if field_name == "requested-quantity":
        for i in order_details["data"]["line-items"]:
            item = {
                field_name: int(field_value),
                "line-note": i["line-note"],
                "ecom-line-id": i["ecom-line-id"],
                "ecom-item-id": i["ecom-item-id"],
                "fulfillment-location": i["fulfillment-location"],
            }
            line_items.append(item)

    elif field_name == "line-note":
        for i in order_details["data"]["line-items"]:
            item = {
                field_name: field_value,
                "requested-quantity": int(i["requested-quantity"]),
                "ecom-line-id": i["ecom-line-id"],
                "ecom-item-id": i["ecom-item-id"],
                "fulfillment-location": i["fulfillment-location"],
            }
            line_items.append(item)

    apis.rint.update_customer_order(
        orderid,
        mfc_id,
        line_items,
        service_window_start,
        ecom_order_status,
        field_name,
        field_value,
    )


def remove_product_from_customer_order(
    apis: InitializedApis, location_code_tom: str, orderid: str
) -> dict:
    order_details = apis.rint.get_customer_order_v4(location_code_tom, orderid)

    mfc_id = order_details["data"]["mfc-id"]
    service_window_start = order_details["data"]["service-window-start"]
    ecom_order_status = order_details["data"]["ecom-order-status"]

    line_items = []

    for i in order_details["data"]["line-items"]:
        item = {
            "requested-quantity": int(i["requested-quantity"]),
            "ecom-line-id": i["ecom-line-id"],
            "ecom-item-id": i["ecom-item-id"],
            "fulfillment-location": i["fulfillment-location"],
        }
        line_items.append(item)

    product = line_items.pop(0)

    apis.rint.update_customer_order(
        orderid,
        mfc_id,
        line_items,
        service_window_start,
        ecom_order_status,
    )
    return product


def add_product_to_customer_order(
    apis: InitializedApis,
    location_code_tom: str,
    orderid: str,
    product: dict,
) -> None:
    order_details = apis.rint.get_customer_order_v4(location_code_tom, orderid)
    mfc_id = order_details["data"]["mfc-id"]
    service_window_start = order_details["data"]["service-window-start"]
    ecom_order_status = order_details["data"]["ecom-order-status"]

    line_items = []

    for i in order_details["data"]["line-items"]:
        item = {
            "requested-quantity": int(i["requested-quantity"]),
            "ecom-line-id": i["ecom-line-id"],
            "ecom-item-id": i["ecom-item-id"],
            "fulfillment-location": i["fulfillment-location"],
        }
        line_items.append(item)
    line_items.append(product)

    apis.rint.update_customer_order(
        orderid,
        mfc_id,
        line_items,
        service_window_start,
        ecom_order_status,
    )
