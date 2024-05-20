import datetime
from pytest_bdd import scenarios, given, when, parsers
from src.api.takeoff.decanting import ToteSection
from src.utils.totes import generate_storage_tote
from src.utils.console_printing import yellow, blue
from src.utils.assortment import Product
from src.utils.decanting import (
    wait_for_po_from_decanting,
)
from src.api.collections import InitializedApis
from scripts.steps.orderflow.setup import prepare_orderflow_data

scenarios("../features/decanting_without_po_dsd.feature")


@given(
    parsers.parse('DSD item is decanted to OSR sleeping area "{number_of_items:d}"'),
    target_fixture="po_data",
)
def dsd_decanting(
    retailer: str,
    location_code_gold,
    apis: InitializedApis,
):
    assert apis.bifrost.get_health_pass()
    location_gold = int(location_code_gold)
    tote = generate_storage_tote()
    user_id = apis.decanting.login_to_decanting().result.user_id
    dc_id = apis.decanting.initialize_tote_for_decanting(
        location_gold, tote, user_id
    ).value.dc_id

    ambient_osr_product = prepare_orderflow_data(
        apis.ims_admin,
        apis.distiller,
        apis.tsc,
        retailer,
        picklist_weighted_qty=0,
        osr_products_qty=1,
        manual_non_weighted_qty=0,
        manual_weighted_qty=0,
        temp_zone=["ambient"],
    )

    products: list[Product] = ambient_osr_product["all_products"]

    prepared_product = products[0]
    print(yellow(prepared_product))

    product_id = prepared_product.tom_id
    print(yellow("Product id:"), blue(product_id))

    user_id = apis.decanting.login_to_decanting().result.user_id
    po_id = apis.decanting.create_dsd_task(location_gold, product_id).purchase_order

    expiration_date = (datetime.date.today() + datetime.timedelta(5)).strftime(
        "%Y%m%d%H%M%S"
    )

    return {
        "product_id": product_id,
        "po_id": po_id,
        "po_user_id": user_id,
        "exp_date": expiration_date,
        "tote": tote,
        "dc_id": dc_id,
    }


@when(
    parsers.parse('decanting operation is performed with "{number_of_items:d}"'),
    target_fixture="decanting_result_data",
)
def perform_decanting(
    apis: InitializedApis,
    location_code_gold,
    po_data: dict,
    number_of_items,
):
    po_information_before_decanting = wait_for_po_from_decanting(
        decanting_service=apis.decanting,
        po_id=po_data["po_id"],
        location_code_gold=int(location_code_gold),
    )
    assert po_information_before_decanting
    starting_dsd_product_info = next(
        product
        for product in po_information_before_decanting.products
        if product.product == po_data["product_id"]
    )

    decanting_operation_result = apis.decanting.decanting_operation(
        mfc=int(location_code_gold),
        user_id=po_data["po_user_id"],
        sections={
            "section_1": ToteSection(
                product=po_data["product_id"],
                amount=1,
                po=po_data["po_id"],
                expiration_date=po_data["exp_date"],
                reason_code="IB",
            )
        },
        licenceplate=po_data["tote"],
        dc_id=po_data["dc_id"],
    )
    return {
        "decanting_result": decanting_operation_result,
        "product_info": starting_dsd_product_info,
        "number_of_items": number_of_items,
    }
