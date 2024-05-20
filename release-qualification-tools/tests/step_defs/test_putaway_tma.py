from pytest_bdd import scenarios, when, then, parsers
from src.api.collections import InitializedApis
from src.utils.addresses import get_addresses_v2
from src.utils.console_printing import blue, green


scenarios("../features/put_away.feature")


@when(
    parsers.parse(
        'put away is performed with quantity = "{quantity:d}" in TMA with "{PO}"'
    ),
    target_fixture="putaway_action",
)
def put_away(
    po_data: dict,
    PO,
    quantity: int,
    apis: InitializedApis,
    location_code_gold,
    location_code_tom,
    products: dict,
):
    if PO == "TRUE":
        print(green("Execution starts : Put away with PO"))
        manual_product = po_data["manual_product"]
        po_id = po_data["po_id"]

        decanting_tasks = apis.decanting.get_decanting_tasks_by_product(
            int(location_code_gold), manual_product
        )

        po_found = any(
            task["purchase_order"] == po_id for task in decanting_tasks["tasks"]
        )
        if not po_found:
            pass

        shelf_id = get_addresses_v2(ims=apis.ims)[0]
        stock_before = apis.ims.shelves_balance_products(
            location_code_tom, manual_product
        )
        qty_total_before = 0
        if stock_before["success"]:
            for item in stock_before["success"]:
                if item["address"] == shelf_id:
                    qty_total_before = item["qty-total"]
                    print(f"shelf balance for {shelf_id} before put-away-TMA: {item}")
                    break
                else:
                    qty_total_before = 0
        qty_to_adjust = quantity
        put_away_action = apis.mobile.putaway(
            shelf_id, manual_product, qty_to_adjust, po_id
        )
        print(green(f"Put_away_TMA_operation response: {put_away_action}"))
    else:
        print(green("Execution starts : Put away without PO"))
        manual_product = products["order_flow_data"]["manual_products"]
        product_id = manual_product[0].tom_id
        shelf_id = get_addresses_v2(ims=apis.ims)[0]
        stock_before = apis.ims.shelves_balance_products(location_code_tom, product_id)
        qty_total_before = 0
        if stock_before["success"]:
            for item in stock_before["success"]:
                if item["address"] == shelf_id:
                    qty_total_before = item["qty-total"]
                    print(f"shelf balance for {shelf_id} before put-away-TMA: {item}")
                    break
                else:
                    qty_total_before = 0
        qty_to_adjust = quantity
        put_away_action = apis.mobile.putaway(shelf_id, product_id, qty_to_adjust)
        print(green(f"Put_away_TMA_operation response: {put_away_action}"))

    return {
        "shelf_id": shelf_id,
        "po_status": PO,
        "qty_total_before": qty_total_before,
    }


@then(parsers.parse('product quantity is increased by "{quantity:d}"'))
def verify_quantity(
    po_data: dict,
    apis: InitializedApis,
    putaway_action: dict,
    location_code_tom,
    products: dict,
):
    if putaway_action.get("po_status") == "TRUE":
        print(green("Validation with PO"))
        manual_product = po_data["manual_product"]
        po_id = po_data["po_id"]
        shelf_id = putaway_action.get("shelf_id")
        qty_total_before = putaway_action.get("qty_total_before")
        stock_after = apis.ims.shelves_balance_products(
            location_code_tom, manual_product
        )
        qty_total_after = None
        assert stock_after[
            "success"
        ], "Did not find any stock after completing 'put away TMA'"
        for item in stock_after["success"]:
            if item["address"] == shelf_id:
                qty_total_after = item["qty-total"]
                print(f"Shelf balance for {shelf_id} after put-away-TMA: {item}")
                break
        print(
            blue(
                f"The stock for item  {manual_product} has been increased by {qty_total_after - qty_total_before} pcs on "
                f"the shelf {shelf_id}, PO {po_id}"
            )
        )
    else:
        print(green("Validation without PO"))
        manual_product = products["order_flow_data"]["manual_products"]
        product_id = manual_product[0].tom_id
        shelf_id = putaway_action.get("shelf_id")
        qty_total_before = putaway_action.get("qty_total_before")
        stock_after = apis.ims.shelves_balance_products(location_code_tom, product_id)
        qty_total_after = None
        assert stock_after[
            "success"
        ], "Did not find any stock after completing 'put away TMA'"
        for item in stock_after["success"]:
            if item["address"] == shelf_id:
                qty_total_after = item["qty-total"]
                print(f"shelf balance for {shelf_id} after put-away-TMA: {item}")
                break

        print(
            blue(
                f"The stock for item  {manual_product} has been increased by {qty_total_after - qty_total_before}"
                f"pcs on "
                f"the shelf {shelf_id}, DSD PO "
            )
        )
