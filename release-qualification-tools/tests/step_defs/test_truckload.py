from pytest_bdd import scenarios, when

from src.api.collections import InitializedApis
from src.api.takeoff.tsc import TscReturnFormat


scenarios("../features/truck_load.feature")


@when("user performs Truck Load")
def truckload(apis: InitializedApis):
    order_status_after_picking = apis.tsc.get_config_item_value(
        "ORDER_STATUS_AFTER_PICKING", return_format=TscReturnFormat.json
    )
    """ Getting the route details for the retailers"""
    route_code = apis.tsc.get_routes()["routes"][0]["route-code"]
    print(f"Route code: {route_code}")
    truckload_orders = apis.mobile.get_truckload_orders(
        route_code, order_status_after_picking
    )
    truck_load_session_status = "served"
    print(
        f"Get all the order_ids which are in status '{order_status_after_picking}' and validate if the orders are '{truck_load_session_status}' or not "
    )
    order_ids = [data["order_id"] for data in truckload_orders]

    print(f"Truckload order ids: {order_ids}")
    assert order_ids, "Need at least on truckload order"
    for order_id in order_ids:
        order_status = apis.mobile.post_truckload([order_id], truck_load_session_status)
        assert (
            order_status == truck_load_session_status
        ), f"Truckload status for order {order_id} is {order_status}, expected '{truck_load_session_status}'."
