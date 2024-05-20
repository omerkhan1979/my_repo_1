import datetime

from pytest import mark, param
from src.api.takeoff.bifrost import Bifrost
from src.api.takeoff.decanting import Decanting, ToteSection
from src.api.takeoff.distiller import Distiller
from src.api.takeoff.rint import RInt

from src.api.third_party.gcp import login_to_gcp
from src.config.config import Config
from src.utils.decanting import (
    wait_for_po_from_decanting,
    compose_decanting_operation_body_for_decanting_task,
    wait_for_po_update_after_decanting,
)
from src.utils.purchase_order import (
    prepare_products_for_po,
    create_po,
    make_purchase_order_from_products,
)
from src.utils.totes import generate_storage_tote
from src.utils.console_printing import cyan


expiration_date = (datetime.date.today() + datetime.timedelta(5)).strftime(
    "%Y%m%d%H%M%S"
)


@mark.rq
@mark.smoke
@mark.inbound
@mark.darkstore
@mark.inbound_smoke
@mark.decanting
@mark.decanting_po
@mark.decanting_without_date
@mark.retailers(
    "maf",
    "winter",
    "wings",
    "abs",
    "smu",
    "tienda",
)
@mark.parametrize(
    "number_of_items, expiration_date",
    [
        param(4, None, marks=mark.testrail("538876")),
        param(8, None, marks=mark.testrail("538877")),
    ],
)
def test_decanting_without_date(
    decanting: Decanting,
    location_code_gold: str,
    retailer: str,
    distiller: Distiller,
    location_code_retailer: str,
    cfg: Config,
    number_of_items,
    expiration_date: str,
    bifrost: Bifrost,
):
    assert bifrost.get_health_pass()
    location_gold = int(location_code_gold)
    tote = generate_storage_tote()
    user_id = decanting.login_to_decanting().result.user_id
    dc_id = decanting.initialize_tote_for_decanting(
        location_gold, tote, user_id
    ).value.dc_id

    credentials = None
    if retailer in ["maf", "wings", "smu"]:
        credentials = login_to_gcp(interactive=False)

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

    po_information_init = wait_for_po_from_decanting(
        decanting_service=decanting,
        po_id=po_id,
        location_code_gold=location_gold,
    )

    decanting_operation = compose_decanting_operation_body_for_decanting_task(
        po_information_init,
        expiration_date=expiration_date,
    )

    decanting_operation_result = decanting.decanting_operation(
        user_id=user_id,
        mfc=location_gold,
        sections=decanting_operation,
        licenceplate=tote,
        dc_id=dc_id,
    )

    assert decanting_operation_result.success

    po_information_post_decanting = wait_for_po_update_after_decanting(
        decanting_service=decanting,
        po_id=po_id,
        location_code_gold=location_gold,
    )

    assert po_information_post_decanting, "Must have found a purchase order"
    assert po_information_post_decanting.status == "in_progress"
    assert po_information_post_decanting.pending_product_count == 0

    expected_final_status = "in_progress"

    decanting.close_purchase_order(po_id)
    expected_final_status = "completed"

    po_information_after_closing = wait_for_po_from_decanting(
        decanting_service=decanting,
        po_id=po_id,
        location_code_gold=location_gold,
    )

    assert po_information_after_closing, "Must have found a purchase order"
    assert po_information_after_closing.status == expected_final_status
    print(cyan("Test case decanting without expiration date is:"))


@mark.rq
@mark.retailers(
    "maf",
    "winter",
    "wings",
    "abs",
    "smu",
    "tienda",
)
@mark.decanting_po
def test_start_multiple_pos_with_one_tote(
    decanting: Decanting,
    cfg: Config,
    location_code_retailer: str,
    location_code_gold: str,
    distiller: Distiller,
    retailer: str,
    rint: RInt,
):
    """
    Attempts to prove that OSR decanting can start and record recieved amounts
    for multiple purchase orders when decanting them into different sections of _ONE_ tote.
    """
    print(f"Location code retailer: {location_code_retailer}")
    location_gold = int(location_code_gold)
    tote = generate_storage_tote()

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

    user_id = decanting.login_to_decanting().result.user_id
    dc_id = decanting.initialize_tote_for_decanting(
        location_gold, tote, user_id
    ).value.dc_id

    decanting_operation_result = decanting.decanting_operation(
        user_id=user_id,
        mfc=location_gold,
        licenceplate=tote,
        dc_id=dc_id,
        sections={
            "section_1": ToteSection(
                product=products[0].tom_id,
                po=po1.purchase_order_id,
                amount=int(
                    po1.items[0].product_quantity_in_ship_unit
                    * po1.items[0].ship_unit_quantity,
                ),
                expiration_date=expiration_date,
                reason_code="IB",
            ),
            "section_2": ToteSection(
                product=products[1].tom_id,
                po=po2.purchase_order_id,
                amount=int(
                    po2.items[0].product_quantity_in_ship_unit
                    * po2.items[0].ship_unit_quantity,
                ),
                expiration_date=expiration_date,
                reason_code="IB",
            ),
        },
    )

    assert decanting_operation_result.success

    po1_update = wait_for_po_update_after_decanting(
        decanting_service=decanting,
        po_id=po1.purchase_order_id,
        location_code_gold=location_gold,
    )

    po2_update = wait_for_po_update_after_decanting(
        decanting_service=decanting,
        po_id=po1.purchase_order_id,
        location_code_gold=location_gold,
    )

    assert po1_update
    assert po1_update.status == "in_progress"
    assert po1_update.pending_product_count == 0

    assert po2_update
    assert po2_update.status == "in_progress"
    assert po2_update.pending_product_count == 0


@mark.rq
@mark.smoke
@mark.inbound
@mark.darkstore
@mark.inbound_smoke
@mark.decanting
@mark.decanting_po
@mark.retailers(
    "maf",
    "winter",
    "wings",
    "abs",
    "smu",
    "tienda",
)
@mark.decanting_with_ex_date
@mark.parametrize(
    "number_of_items, expiration_date",
    [
        param(1, expiration_date, marks=mark.testrail("538878")),
        param(2, expiration_date, marks=mark.testrail("538875")),
    ],
)
def test_decanting_with_ex_date(
    decanting: Decanting,
    location_code_gold: str,
    retailer: str,
    distiller: Distiller,
    expiration_date: str,
    location_code_retailer: str,
    cfg: Config,
    number_of_items: int,
    bifrost: Bifrost,
):
    assert bifrost.get_health_pass()
    location_gold = int(location_code_gold)
    tote = generate_storage_tote()
    user_id = decanting.login_to_decanting().result.user_id
    dc_id = decanting.initialize_tote_for_decanting(
        location_gold, tote, user_id
    ).value.dc_id

    credentials = None
    if retailer in ["maf", "wings", "smu"]:
        credentials = login_to_gcp(interactive=False)

    products = prepare_products_for_po(
        distiller=distiller,
        retailer=retailer,
        location_code_retailer=location_code_retailer,
        ambient_osr_count=0,
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

    po_information_init = wait_for_po_from_decanting(
        decanting_service=decanting,
        po_id=po_id,
        location_code_gold=location_gold,
    )

    sections = compose_decanting_operation_body_for_decanting_task(
        po_information_init,
        expiration_date=expiration_date,
    )

    decanting_operation_result = decanting.decanting_operation(
        user_id=user_id,
        mfc=location_gold,
        sections=sections,
        licenceplate=tote,
        dc_id=dc_id,
    )

    assert decanting_operation_result.success

    po_information_post_decanting = wait_for_po_update_after_decanting(
        decanting_service=decanting,
        po_id=po_id,
        location_code_gold=location_gold,
    )

    assert po_information_post_decanting
    assert po_information_post_decanting.status == "in_progress"
    assert po_information_post_decanting.pending_product_count == 0

    expected_final_status = "in_progress"

    decanting.close_purchase_order(po_id)
    expected_final_status = "completed"

    po_information_after_closing = wait_for_po_from_decanting(
        decanting_service=decanting,
        po_id=po_id,
        location_code_gold=location_gold,
    )

    assert po_information_after_closing
    assert po_information_after_closing.status == expected_final_status
    print(cyan("Test case decanting with expiration date is:"))
