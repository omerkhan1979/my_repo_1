import datetime
from pytest import mark
from src.api.takeoff.bifrost import Bifrost
from src.api.takeoff.decanting import Decanting, ToteSection
from src.api.takeoff.distiller import Distiller

from src.utils.decanting import (
    wait_for_po_from_decanting,
    wait_for_po_product_decanted_quanity,
)
from src.utils.purchase_order import prepare_products_for_po
from src.utils.totes import generate_storage_tote
from src.utils.console_printing import yellow, blue


@mark.rq
@mark.smoke
@mark.inbound
@mark.inbound_smoke
@mark.decanting
@mark.decanting_dsd
@mark.retailers("maf", "wings", "smu", "abs", "tienda")
@mark.parametrize("number_of_items", [(1)])
@mark.testrail("538874")
def test_decanting_dsd(
    decanting: Decanting,
    retailer: str,
    distiller: Distiller,
    location_code_retailer,
    number_of_items,
    location_code_gold,
    bifrost: Bifrost,
):
    assert bifrost.get_health_pass()
    location_gold = int(location_code_gold)
    tote = generate_storage_tote()
    user_id = decanting.login_to_decanting().result.user_id
    dc_id = decanting.initialize_tote_for_decanting(
        location_gold, tote, user_id
    ).value.dc_id

    products = prepare_products_for_po(
        distiller=distiller,
        retailer=retailer,
        location_code_retailer=location_code_retailer,
        ambient_osr_count=number_of_items,
        chilled_osr_count=0,
        req_exp_date_osr_count=False,
        chemical_osr_count=0,
        manual_count=0,
    )["ambient_osr_products"]

    prepared_product = products[0]
    print(yellow(prepared_product))

    product_id = prepared_product.tom_id
    print(yellow("Product id:"), blue(product_id))

    user_id = decanting.login_to_decanting().result.user_id
    po_id = decanting.create_dsd_task(location_gold, product_id).purchase_order

    expiration_date = (datetime.date.today() + datetime.timedelta(5)).strftime(
        "%Y%m%d%H%M%S"
    )

    po_information_before_decanting = wait_for_po_from_decanting(
        decanting_service=decanting,
        po_id=po_id,
        location_code_gold=location_gold,
    )

    assert po_information_before_decanting
    starting_dsd_product_info = next(
        product
        for product in po_information_before_decanting.products
        if product.product == product_id
    )

    decanting_operation_result = decanting.decanting_operation(
        mfc=location_gold,
        user_id=user_id,
        sections={
            "section_1": ToteSection(
                product=product_id,
                amount=1,
                po=po_id,
                expiration_date=expiration_date,
                reason_code="IB",
            )
        },
        licenceplate=tote,
        dc_id=dc_id,
    )

    assert decanting_operation_result.success

    po_information_post_decanting = wait_for_po_product_decanted_quanity(
        decanting_service=decanting,
        po_id=po_id,
        location_code_gold=location_gold,
        product_id=product_id,
        qty=starting_dsd_product_info.qty_decanted + 1,
    )

    assert po_information_post_decanting
    assert po_information_post_decanting.status == "in_progress"
