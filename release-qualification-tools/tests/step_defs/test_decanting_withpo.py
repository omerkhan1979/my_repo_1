import datetime
from pytest_bdd import scenarios, given, when, parsers
from src.api.takeoff.bifrost import Bifrost
from src.api.takeoff.decanting import Decanting, ToteSection
from src.api.takeoff.distiller import Distiller
from src.utils.totes import generate_storage_tote
from src.config.config import Config
from src.api.takeoff.rint import RInt
from src.api.third_party.gcp import login_to_gcp
from src.utils.decanting import (
    wait_for_po_from_decanting,
    compose_decanting_operation_body_for_decanting_task,
)
from src.utils.purchase_order import (
    prepare_products_for_po,
    create_po,
    make_purchase_order_from_products,
)

scenarios("../features/decanting.feature")
expiration_date = (datetime.date.today() + datetime.timedelta(5)).strftime(
    "%Y%m%d%H%M%S"
)


@given(
    parsers.parse(
        'Purchase Order is created with "{number_of_items:d}" and "{expiry_date_required}"'
    ),
    target_fixture="po_data",
)
def create_po_for_decanting(
    cfg: Config,
    decanting: Decanting,
    retailer: str,
    distiller: Distiller,
    location_code_retailer,
    location_code_gold,
    bifrost: Bifrost,
    number_of_items: int,
    expiry_date_required: bool,
):
    assert bifrost.get_health_pass()
    location_gold = int(location_code_gold)

    credentials = login_to_gcp(interactive=False)
    if expiry_date_required is True:
        products = prepare_products_for_po(
            distiller=distiller,
            retailer=retailer,
            location_code_retailer=location_code_retailer,
            ambient_osr_count=2,
            chilled_osr_count=0,
            req_exp_date_osr_count=number_of_items,
            chemical_osr_count=0,
            manual_count=0,
        )["osr_products_with_exp_date"]

        po_id = create_po(
            decanting_service=decanting,
            config=cfg,
            location_code_gold=location_gold,
            products=products,
            po_provided_by_user=False,
            credentials=credentials,
        )

    else:
        products = prepare_products_for_po(
            distiller=distiller,
            retailer=retailer,
            location_code_retailer=location_code_retailer,
            ambient_osr_count=number_of_items,
            chilled_osr_count=0,
            req_exp_date_osr_count=0,
            chemical_osr_count=0,
            manual_count=0,
        )["ambient_osr_products"]

        po_id = create_po(
            decanting_service=decanting,
            config=cfg,
            location_code_gold=location_gold,
            products=products,
            po_provided_by_user=False,
            credentials=credentials,
        )

    print(po_id, products)
    return {"po_id": po_id, "products": products}


@given(
    parsers.parse("Purchase Order is created with 2 items in rint"),
    target_fixture="po_data",
)
def create_po_for_decanting_in_rint(
    location_code_retailer: str,
    distiller: Distiller,
    retailer: str,
    rint: RInt,
):
    print(f"Location code retailer: {location_code_retailer}")

    products = prepare_products_for_po(
        distiller=distiller,
        retailer=retailer,
        location_code_retailer=location_code_retailer,
        ambient_osr_count=2,
        chilled_osr_count=0,
        req_exp_date_osr_count=0,
        chemical_osr_count=0,
        manual_count=0,
    )["ambient_osr_products"]

    po1 = make_purchase_order_from_products(str(location_code_retailer), [products[0]])
    rint.create_purchase_order(po1)
    po2 = make_purchase_order_from_products(str(location_code_retailer), [products[1]])
    rint.create_purchase_order(po2)
    return {"po1": po1, "po2": po2, "products": products}


@when(
    parsers.parse(
        'decanting is performed for products in the PO with "{expiry_date_required}"'
    ),
    target_fixture="decanting_result_data",
)
def perform_decanting_with_po(
    decanting: Decanting,
    po_data: dict,
    location_code_gold: str,
    expiry_date_required: bool,
):
    location_gold = int(location_code_gold)
    user_id = decanting.login_to_decanting().result.user_id
    tote = generate_storage_tote()
    dc_id = decanting.initialize_tote_for_decanting(
        location_gold, tote, user_id
    ).value.dc_id
    if expiry_date_required:
        exp_date = expiration_date
    else:
        exp_date = None

    po_information_init = wait_for_po_from_decanting(
        decanting_service=decanting,
        po_id=po_data["po_id"],
        location_code_gold=location_gold,
    )

    sections = compose_decanting_operation_body_for_decanting_task(
        po_information_init,
        expiration_date=exp_date,
    )

    decanting_operation_result = decanting.decanting_operation(
        user_id=user_id,
        mfc=location_gold,
        sections=sections,
        licenceplate=tote,
        dc_id=dc_id,
    )

    return {
        "decanting_result": decanting_operation_result,
    }


@when(
    parsers.parse("decanting is performed for 2 items for multiple purchase orders"),
    target_fixture="decanting_result_data",
)
def perform_decanting_multiple_pos(
    decanting: Decanting,
    po_data: dict,
    location_code_gold: int,
):
    tote = generate_storage_tote()
    user_id = decanting.login_to_decanting().result.user_id
    dc_id = decanting.initialize_tote_for_decanting(
        location_code_gold, tote, user_id
    ).value.dc_id

    decanting_operation_result = decanting.decanting_operation(
        user_id=user_id,
        mfc=location_code_gold,
        licenceplate=tote,
        dc_id=dc_id,
        sections={
            "section_1": ToteSection(
                product=po_data["products"][0].tom_id,
                po=po_data["po1"].purchase_order_id,
                amount=int(
                    po_data["po1"].items[0].product_quantity_in_ship_unit
                    * po_data["po1"].items[0].ship_unit_quantity,
                ),
                expiration_date=expiration_date,
                reason_code="IB",
            ),
            "section_2": ToteSection(
                product=po_data["products"][1].tom_id,
                po=po_data["po2"].purchase_order_id,
                amount=int(
                    po_data["po2"].items[0].product_quantity_in_ship_unit
                    * po_data["po2"].items[0].ship_unit_quantity,
                ),
                expiration_date=expiration_date,
                reason_code="IB",
            ),
        },
    )
    return {
        "decanting_result": decanting_operation_result,
    }
