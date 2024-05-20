from pytest import mark
from src.api.takeoff.distiller import Distiller
from src.api.takeoff.ims import IMS
from src.utils.assortment import Product
from src.utils.console_printing import cyan
from src.api.collections import InitializedApis
from scripts.steps.orderflow.setup import prepare_orderflow_data


@mark.smoke
@mark.inbound
@mark.inbound_smoke
@mark.shelf_adjust
@mark.testrail("184996")
def test_shelf_adjust(retailer, distiller: Distiller, ims: IMS, apis: InitializedApis):

    osr_product = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        retailer,
        picklist_weighted_qty=0,
        osr_products_qty=1,
        manual_non_weighted_qty=0,
        manual_weighted_qty=0,
    )
    products: list[Product] = osr_product["all_products"]
    product = products[0]

    quantity_init = 0
    shelf_state_init = ims.v2_snapshot(
        products=[product.tom_id], addresses=["01K"], include_zeros=True
    )
    for address in shelf_state_init["addresses"]:
        if address["address"] == "01K":
            quantity_init = address["quantity"]

    ims.shelf_adjust("01K", product.tom_id, 10, "IB")

    shelf_state_post = ims.v2_snapshot(
        products=[product.tom_id], addresses=["01K"], include_zeros=True
    )
    for address in shelf_state_post["addresses"]:
        if address["address"] == "01K":
            quantity_post = address["quantity"]

    assert (quantity_post - quantity_init) == 10
    print(cyan("Test case shelf_adjust is:"))
