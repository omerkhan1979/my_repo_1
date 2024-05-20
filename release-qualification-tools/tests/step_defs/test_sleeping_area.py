from scripts.steps.product_catalog_upload import (
    check_revision_max_updated,
)
from src.api.takeoff.distiller import get_revision_max
from src.api.collections import InitializedApis
from pytest_bdd import scenarios, when, then, parsers, given
from src.utils.os_helpers import get_cwd, delete_file
from src.utils.assortment import Product
from datetime import datetime
import random
import json
from src.utils.product_catalog_helpers import (
    give_modified_product_catalog_from_pc_version,
)

from src.api.third_party.gcp import (
    upload_file_to_google_bucket,
    login_to_gcp,
)

scenarios("../features/validate_sleeping_area_rules.feature")


@given(
    parsers.parse('the product catalog with "{temp_zone}" item'),
    target_fixture="product_catalog",
)
def create_new_product_catalog(
    temp_zone: str, location_code_tom: str, apis: InitializedApis
):
    project_root_dir = get_cwd()
    filename = "v6.json"
    filepath = f"{project_root_dir}/data/{filename}"
    product_catalog_body = give_modified_product_catalog_from_pc_version(
        "v6", location_code_tom, filepath, temp_zone
    )
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    new_product_catalog_filename = f"takeoff_product_catalog_{now}.json"
    new_product_catalog_filepath = (
        f"{project_root_dir}/data/{new_product_catalog_filename}"
    )
    pc = json.dumps(product_catalog_body, indent="")
    with open(new_product_catalog_filepath, "w+") as product_catalog:
        product_catalog.write(pc)

    revision = get_revision_max(
        distiller=apis.distiller, location_code_tom=location_code_tom
    )
    return {
        "filename": new_product_catalog_filename,
        "filepath": new_product_catalog_filepath,
        "tom-id": str(product_catalog_body["tom-id"]),
        "revision": revision,
    }


@given(
    parsers.parse('sleeping area rule with "{sleeping_area}" and "{temp_zone}"'),
    target_fixture="sleeping_area_rules",
)
def create_new_sleeping_area_rule(
    sleeping_area: str, temp_zone: str, location_code_tom: str, apis: InitializedApis
):
    priority = random.randint(1, 9)
    sleeping_area_rule = {
        "rule": {
            "store-id": location_code_tom,
            "sleeping-area": f"{sleeping_area}",
            "priority": priority,
            "rule": f'#and[#insec[#arg[:temperature-zone],["{temp_zone}"]], #and[#eq[#arg[:feature-attributes :is-chemical], false], #eq[#arg[:feature-attributes :food-safety], "food"]]]',
            "update-note": "Added new product with sleeping area H",
        }
    }
    apis.distiller.upsert_rule_sleeping_area(sleeping_area_rule)
    return {"sleeping_area": sleeping_area, "priority": priority}


@when("product catalog is uploaded")
def upload_new_product_catalog(
    cfg, product_catalog: dict, apis: InitializedApis, location_code_tom: str
):
    credentials = login_to_gcp(interactive=False)
    upload_file_to_google_bucket(
        project_id=cfg.google_project_id,
        credentials=credentials,
        integration_etl_bucket_name=cfg.integration_etl_bucket_name,
        source_filename=product_catalog["filename"],
        source_filepath=product_catalog["filepath"],
    )

    delete_file(product_catalog["filepath"])
    check_revision_max_updated(
        apis.distiller, product_catalog["revision"], location_code_tom
    )


@then("product should fall under sleeping area rule")
def validate_products_sleeping_area(
    apis: InitializedApis,
    sleeping_area_rules: dict,
    product_catalog: dict,
    location_code_tom: str,
):
    products: list[Product] = apis.distiller.get_products_by_tom_ids(
        [product_catalog["tom-id"]]
    )
    assert sleeping_area_rules["sleeping_area"] == products[0].sleeping_area

    delete_sleeping_area_rule = {
        "store_id": location_code_tom,
        "sleeping_area": sleeping_area_rules["sleeping_area"],
        "priority": sleeping_area_rules["priority"],
    }
    apis.distiller.delete_sleeping_area(delete_sleeping_area_rule)
