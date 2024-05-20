from pytest_bdd import scenarios, when, parsers
from src.utils.update_order import (
    update_order_lineitem_quantity,
)
from src.api.collections import InitializedApis
from src.utils.order_timings import MFCRelativeFutureTime
from src.utils.picklist_helpers import process_and_complete_picklist
from src.utils.user import AuthServiceUser
from tests.conftest import close_all_open_picklists

scenarios("../features/in-store-picking.feature")


@when(
    parsers.parse('user processes "{picklist_type}" picklist to completion'),
)
def process_picklist_to_completion(
    apis: InitializedApis,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
    operator_user: AuthServiceUser,
    orderid: str,
    picklist_type: str,
    location_code_tom: str,
) -> None:
    close_all_open_picklists,
    cutoff = apis.oms.get_order(orderid)["response"]["cutoff-datetime"]

    picking_type_list = (
        picklist_type.split(",") if picklist_type == "PRELIM,DELTA" else [picklist_type]
    )
    for pick_type in picking_type_list:
        if len(picking_type_list) == 2 and pick_type == "DELTA":
            update_order_lineitem_quantity(apis, location_code_tom, orderid, 2)
            process_and_complete_picklist(
                apis,
                cutoff,
                stage_by_in_1_minutes_1_min_cutoff,
                operator_user,
                pick_type,
            )
