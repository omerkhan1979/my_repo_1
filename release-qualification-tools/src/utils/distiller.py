from src.api.takeoff.distiller import Distiller
from src.utils.waiters import wait


@wait
def wait_for_po_from_purchase_order_by_id(distiller: Distiller, create_common_po: int):
    try:
        response = distiller.get_purchase_order_by_id(create_common_po)
        if response.data:
            return response.data[0]
        else:
            return {}
    except IndexError:
        return {}
