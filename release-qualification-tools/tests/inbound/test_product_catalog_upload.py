from datetime import datetime

from pytest import mark
from scripts.steps.product_catalog_upload import (
    check_revision_max_updated,
)
from src.api.takeoff.distiller import Distiller, get_revision_max
from src.api.third_party.gcp import (
    upload_file_to_google_bucket,
    login_to_gcp,
)
from src.api.third_party.sftp_interaction import delete_sftp_file, upload_via_sftp

from src.config.constants import (
    ABS_ENCRYPTION_VECTOR,
    ABS_ENCRYPTION_KEY,
)
from src.config.config import Config
from src.utils.encryption import pack_and_encrypt
from src.utils.product_catalog_helpers import (
    give_modified_product_catalog_from_template,
)
from src.utils.console_printing import cyan
from src.utils.os_helpers import get_cwd, delete_file


@mark.rq
@mark.smoke
@mark.inbound
@mark.inbound_smoke
@mark.common_product_catalog_upload
@mark.retailers("maf", "wings", "smu", "pinemelon", "tienda")
@mark.testrail("140975")
def test_common_product_catalog_upload(
    distiller: Distiller, retailer, cfg: Config, location_code_tom
):
    revision_max_old = get_revision_max(
        distiller=distiller, location_code_tom=location_code_tom
    )
    project_root_dir = get_cwd()

    product_catalog_body = give_modified_product_catalog_from_template(
        retailer, project_root_dir
    )

    now = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"takeoff_product_catalog_{now}.json"
    filepath = f"{project_root_dir}/data/{filename}"

    with open(filepath, "w+") as product_catalog:
        product_catalog.write(product_catalog_body)

    credentials = login_to_gcp(interactive=False)

    upload_file_to_google_bucket(
        project_id=cfg.google_project_id,
        credentials=credentials,
        integration_etl_bucket_name=cfg.integration_etl_bucket_name,
        source_filename=filename,
        source_filepath=filepath,
    )

    delete_file(filepath)

    assert check_revision_max_updated(distiller, revision_max_old, location_code_tom)
    print(cyan("Test case product_catalog_upload is:"))


@mark.rq
@mark.inbound
@mark.abs_product_catalog_upload
@mark.retailers("abs")
@mark.testrail("313757")
def test_abs_product_catalog_upload(distiller, retailer, cfg, location_code_tom):
    revision_max_old = get_revision_max(
        distiller=distiller, location_code_tom=location_code_tom
    )
    project_root_dir = get_cwd()

    product_catalog_body = give_modified_product_catalog_from_template(
        retailer, project_root_dir
    )

    date, time = (
        datetime.now().strftime("%Y%m%d"),
        datetime.now().strftime("%H%M%S"),
    )
    filename = f"abs_takeoff_item_master_delta_{location_code_tom}_{date}_{time}"
    filepath = f"{project_root_dir}/data/{filename}"

    product_catalog_body_encrypted = pack_and_encrypt(
        product_catalog_body, ABS_ENCRYPTION_VECTOR, ABS_ENCRYPTION_KEY
    )

    with open(filepath, "wb") as product_catalog:
        product_catalog.write(product_catalog_body_encrypted)

    upload_via_sftp(cfg, filename, filepath)

    delete_file(filepath)

    assert check_revision_max_updated(distiller, revision_max_old, location_code_tom)
    print(cyan("Test case abs_product_catalog_upload is:"))


# Commented out because winter Product Catalog has not been upsated to use json
# files yet. See: PROD-10478
@mark.rq
@mark.inbound
@mark.product_catalog_upload_sftp
@mark.retailers("winter")
@mark.testrail("606852")
def test_product_catalog_upload_sftp(distiller, retailer, cfg, location_code_tom):
    revision_max_old = get_revision_max(
        distiller=distiller, location_code_tom=location_code_tom
    )
    project_root_dir = get_cwd()

    product_catalog_body = give_modified_product_catalog_from_template(
        retailer, project_root_dir
    )

    now_datetime = datetime.now()
    now = now_datetime.strftime("%Y%m%d%H%M%S")
    now_date = now_datetime.strftime("%Y%m%d")
    now_year = now_datetime.strftime("%Y")
    filename = f"Takeoff_product_catalog_{now}.json"
    filepath = f"{project_root_dir}/data/{filename}"
    remote_file_path = f"/inbound/processed/{now_year}/{now_date}"

    with open(filepath, "w+") as product_catalog:
        product_catalog.write(product_catalog_body)

    login_to_gcp(interactive=False)

    try:
        upload_via_sftp(cfg, filename, filepath)

        delete_file(filepath)

        assert check_revision_max_updated(
            distiller, revision_max_old, location_code_tom
        )
        print(cyan("Test case product_catalog_upload is:"))
    finally:
        # TODO: remove this if != ode stuff after fixing PROD-12391
        if cfg.env != "ode":
            assert delete_sftp_file(cfg, filename, remote_file_path)
        else:
            try:
                delete_sftp_file(cfg, filename, remote_file_path)
            except Exception as err:
                print(
                    f"Failed to check/delete sftp file {remote_file_path}/{filename}: {err}"
                )
