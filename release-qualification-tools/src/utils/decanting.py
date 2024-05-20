from typing import Optional
from src.utils.waiters import wait

from src.api.takeoff.decanting import TaskListItem, ToteSection, Decanting


@wait
def wait_for_po_from_decanting(
    decanting_service: Decanting, po_id: str, location_code_gold: int
) -> Optional[TaskListItem]:
    try:
        return decanting_service.get_decanting_task_list(
            location_code_gold, po_id
        ).data[0]
    except IndexError:
        return None


@wait
def wait_for_po_update_after_decanting(
    decanting_service: Decanting, po_id: str, location_code_gold: int
) -> Optional[TaskListItem]:
    response = decanting_service.get_decanting_task_list(location_code_gold, po_id)
    if response.data[0].status == "not_started":
        return None
    else:
        return response.data[0]


@wait
def wait_for_po_product_decanted_quanity(
    decanting_service: Decanting,
    po_id: str,
    location_code_gold: int,
    product_id: str,
    qty: int,
) -> Optional[TaskListItem]:
    """
    Waits for the given purchase order to have the given product decanted to the
    amount provided or more.
    """
    response = decanting_service.get_decanting_task_list(location_code_gold, po_id)
    product = next(
        product
        for product in response.data[0].products
        if product.product == product_id
    )

    if product.qty_decanted < qty:
        return None
    else:
        return response.data[0]


def compose_decanting_operation_body_for_decanting_task(
    decanting_response: TaskListItem,
    expiration_date: str,
) -> dict[str, ToteSection]:
    sections = dict()
    products = decanting_response.products
    for idx, product in enumerate(products):
        sections["section_" + str(idx + 1)] = ToteSection(
            product=product.product,
            amount=product.qty,
            po=decanting_response.purchase_order,
            expiration_date=expiration_date,
            reason_code="IB",
        )

    return sections
