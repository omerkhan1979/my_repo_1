from pprint import pprint
from pytest_bdd import scenarios, given, parsers, when
from src.utils.helpers import wait_order_status_changed, wait_for_decisions
from src.utils.place_order import products_to_lineitems_required_field
from src.utils.assortment import Product
from scripts.steps.orderflow.setup import prepare_orderflow_data
from src.api.collections import InitializedApis

scenarios("../features/pick_multi_temp_products.feature")


@given(
    parsers.parse("products available with {temp_zone} temp zones in the environment"),
    target_fixture="products",
)
def get_products_tempZones(apis: InitializedApis, retailer: str, temp_zone):
    temp_zones_list = [zone.strip() for zone in temp_zone.split(",")]

    osr_product_1 = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        retailer,
        picklist_weighted_qty=0,
        osr_products_qty=1,
        manual_non_weighted_qty=0,
        manual_weighted_qty=0,
        temp_zone=[temp_zones_list[0]],
    )

    osr_product_2 = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        retailer,
        picklist_weighted_qty=0,
        osr_products_qty=1,
        manual_non_weighted_qty=0,
        manual_weighted_qty=0,
        temp_zone=[temp_zones_list[1]],
    )
    osr_products: list[Product] = (
        osr_product_1["all_products"] + osr_product_2["all_products"]
    )

    return {"order_flow_data": osr_products}


@when("order is created", target_fixture="orderid")
def create_order(
    apis: InitializedApis,
    retailer: str,
    products: list,
    location_code_retailer,
    order_timeslot_and_spoke,
) -> str:
    tom_ids = ",".join(map(lambda product: product.tom_id, products["order_flow_data"]))
    apis.ims.shelf_adjust("01K", tom_ids, 10, "IB")
    service_window_start = order_timeslot_and_spoke["service_window_start"]
    stage_by_datetime = order_timeslot_and_spoke["stage_by_datetime"]
    spoke_id = order_timeslot_and_spoke["spoke_id"]
    lineitems = products_to_lineitems_required_field(
        retailer, products["order_flow_data"]
    )
    order_id = apis.rint.create_customer_order(
        print_body=False,
        service_window_start=service_window_start,
        stage_by_datetime=stage_by_datetime,
        store_id=location_code_retailer,
        spoke_id=spoke_id,
        lineitems=lineitems,
    )
    return order_id


@when("products are picked into the same tote")
def use_totes(apis: InitializedApis, orderid):
    wait_order_status_changed(orderid, "queued", apis.oms)
    wait_for_decisions(apis.fft, orderid)
    response_from_get_order = apis.oms.get_order(orderid)["response"]["line-items"]
    pprint(response_from_get_order)
    # verify that all decisions have "Chilled" zone (since only Chilled target totes were send for picking):
    verify_tote_ambient_item = response_from_get_order[0]["tom-items"][0]["decision"][
        0
    ]["zone"]
    verify_tote_chilled_item = response_from_get_order[1]["tom-items"][0]["decision"][
        0
    ]["zone"]
    assert verify_tote_ambient_item == verify_tote_chilled_item == "chilled"
