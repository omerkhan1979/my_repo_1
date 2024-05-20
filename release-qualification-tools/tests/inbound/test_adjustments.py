from time import time

from pprint import pprint
from pytest import mark

from src.utils.assortment import Product
from src.utils.ims import wait_for_item_adjustment_from_ims
from src.utils.console_printing import cyan
from src.api.collections import InitializedApis
from scripts.steps.orderflow.setup import prepare_orderflow_data


@mark.smoke
@mark.inbound
@mark.inbound_smoke
@mark.adjustments
@mark.testrail("49606")
def test_adjustments(
    retailer, distiller, ims, location_code_tom, apis: InitializedApis
):

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

    time_past = str(int(round(time() * 1000)))

    ims.shelf_adjust("01K", products[0].tom_id, 10, "IB")

    adjustments_response = wait_for_item_adjustment_from_ims(
        ims, time_past, None, location_code_tom
    )
    pprint(adjustments_response)

    adjustment_qty = adjustments_response["quantity"]

    assert adjustment_qty == 10
    print(cyan("Test case adjustments is:"))
