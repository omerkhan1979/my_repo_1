from scripts.steps.product_catalog_upload import (
    check_revision_max_updated,
    input_path_to_im_file,
)
from src.api.takeoff.distiller import Distiller, get_revision_max
from src.api.third_party.gcp import upload_file_to_google_bucket, login_to_gcp
from src.api.third_party.sftp_interaction import upload_via_sftp

from src.config.config import Config, get_config
from src.utils.console_printing import red
from tests.conftest import location_code_tom

*config, day, hour = get_config()
cfg = Config(*config)
distiller = Distiller(cfg)

bucket_retailers = ["maf", "wings"]
sftp_retailers = ["winter", "abs"]

if cfg.retailer in bucket_retailers:
    # Obtaining revision-max before product_catalog file was uploaded
    revision_max_old = get_revision_max(
        distiller=distiller, location_code_tom=str(location_code_tom)
    )

    # Obtain product_catalog filepath from user
    filepath, filename = input_path_to_im_file()

    # Logging to google cloud project
    credentials = login_to_gcp()

    # Uploading product_catalog file to google cloud project
    upload_file_to_google_bucket(
        project_id=cfg.google_project_id,
        credentials=credentials,
        integration_etl_bucket_name=cfg.integration_etl_bucket_name,
        source_filename=filename,
        source_filepath=filepath,
    )

    # Checking that revision-max was updated after product_catalog file uploaded
    check_revision_max_updated(
        distiller=distiller,
        revision_max_old=revision_max_old,
        location_code_tom=str(location_code_tom),
    )

elif cfg.retailer in sftp_retailers:
    # Obtaining revision-max before product_catalog file was uploaded
    revision_max_old = get_revision_max(
        distiller=distiller, location_code_tom=str(location_code_tom)
    )

    # Obtain product_catalog filepath from user
    filepath, filename = input_path_to_im_file()

    # Uploading product_catalog file to sftp
    upload_via_sftp(config=cfg, source_filename=filename, source_filepath=filepath)

    # Checking that revision-max was updated after product_catalog file uploaded
    check_revision_max_updated(
        distiller=distiller,
        revision_max_old=revision_max_old,
        location_code_tom=str(location_code_tom),
    )

else:
    print(red("Not supported retailer, exiting..."))
