import os
from pytest_bdd import scenarios, given, then, when, parsers
from scripts.steps.product_catalog_upload import (
    check_revision_max_updated,
)
from src.api.takeoff.distiller import get_revision_max
from src.api.third_party.gcp import (
    upload_file_to_google_bucket,
    login_to_gcp,
)
from src.utils.product_catalog_helpers import (
    give_modified_product_catalog_from_pc_version,
)
from src.api.third_party.sftp_interaction import delete_sftp_file, upload_via_sftp
from datetime import datetime
from src.utils.os_helpers import get_cwd, delete_file
import json

scenarios("../features/product_catalog_upload.feature")
project_root_dir = get_cwd()


@given(
    parsers.parse("product catalog version {pc_version} is available to upload"),
    target_fixture="pc_version_filepath",
)
def product_catalog_available(pc_version: str) -> str:
    filename = f"{pc_version}.json"
    filepath = f"{project_root_dir}/data/{filename}"
    if os.path.exists(filepath):
        print("Product catalog version formats are available")
        return filepath
    else:
        print("Product catalog version formats are not available")
        exit(0)


@when(
    parsers.parse("product catalog file with version {pc_version} is uploaded via GCP"),
    target_fixture="revision_max_old_gcp",
)
def upload_pc_via_gcp(
    cfg, distiller, location_code_tom, pc_version_filepath: str, pc_version: str
):
    revision_max_old_gcp = get_revision_max(
        distiller=distiller, location_code_tom=location_code_tom
    )
    print(revision_max_old_gcp)
    product_catalog_body = give_modified_product_catalog_from_pc_version(
        pc_version, location_code_tom, pc_version_filepath
    )
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"takeoff_product_catalog_{now}.json"
    filepath = f"{project_root_dir}/data/{filename}"

    pc = json.dumps(product_catalog_body, indent="")
    with open(filepath, "w+") as product_catalog:
        product_catalog.write(pc)

    credentials = login_to_gcp(interactive=False)
    upload_file_to_google_bucket(
        project_id=cfg.google_project_id,
        credentials=credentials,
        integration_etl_bucket_name=cfg.integration_etl_bucket_name,
        source_filename=filename,
        source_filepath=filepath,
    )

    delete_file(filepath)
    return revision_max_old_gcp


@when(
    parsers.parse(
        "product catalog file with version {pc_version} is uploaded via SFTP"
    ),
    target_fixture="revision_max_old_sftp",
)
def upload_pc_via_sftp(
    distiller, cfg, location_code_tom, pc_version_filepath: str, pc_version: str
):
    revision_max_old_sftp = get_revision_max(
        distiller=distiller, location_code_tom=location_code_tom
    )
    print(revision_max_old_sftp)
    product_catalog_body = give_modified_product_catalog_from_pc_version(
        pc_version, location_code_tom, pc_version_filepath
    )

    now_datetime = datetime.now()
    now = now_datetime.strftime("%Y%m%d%H%M%S")
    now_date = now_datetime.strftime("%Y%m%d")
    now_year = now_datetime.strftime("%Y")
    filename = f"Takeoff_product_catalog_{now}.json"
    filepath = f"{project_root_dir}/data/{filename}"
    remote_file_path = f"/inbound/processed/{now_year}/{now_date}"

    pc = json.dumps(product_catalog_body, indent="")
    with open(filepath, "w+") as product_catalog:
        product_catalog.write(pc)

    login_to_gcp(interactive=False)

    try:
        upload_via_sftp(cfg, filename, filepath)
        delete_file(filepath)
        return revision_max_old_sftp

    finally:
        if cfg.env != "ode":
            assert delete_sftp_file(cfg, filename, remote_file_path)
        else:
            try:
                delete_sftp_file(cfg, filename, remote_file_path)
            except Exception as err:
                print(
                    f"Failed to check/delete sftp file {remote_file_path}/{filename}: {err}"
                )


@then("verify that the product catalog revision value is updated")
def verify_revision_value_updated(
    distiller, location_code_tom, revision_max_old_sftp: int, revision_max_old_gcp: int
):
    assert check_revision_max_updated(
        distiller, revision_max_old_gcp, location_code_tom
    )

    assert check_revision_max_updated(
        distiller, revision_max_old_sftp, location_code_tom
    )
