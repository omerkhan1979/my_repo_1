from scripts.steps.product_catalog_upload import (
    check_revision_max_updated,
)
from src.api.takeoff.distiller import Distiller, get_revision_max
from src.api.takeoff.ims import IMS
from src.api.third_party.gcp import (
    upload_file_to_google_bucket,
    login_to_gcp,
)
from src.api.third_party.sftp_interaction import upload_via_sftp
from src.config.config import Config, get_config
from src.utils.console_printing import blue, red
from src.utils.os_helpers import get_cwd
from tests.conftest import location_code_tom

*config, day, hour = get_config()
cfg = Config(*config)
project_root_dir = get_cwd()
distiller = Distiller(cfg)

file_registry = {
    "maf": "MFC_product_catalog_20220531131221.json",
    "wings": "MFC_product_catalog_20220531161503.json",
    "winter": "mfc_product_catalog_20220531163909.csv",
    "abs": "abs_takeoff_product_catalog_full_ABS3116_20220623_224447",
}

file_name = file_registry[cfg.retailer]
file_path = f"{project_root_dir}/data/MOD71_enabler/{file_name}"

revision_max_old = get_revision_max(
    distiller=distiller, location_code_tom=str(location_code_tom)
)

print(red("Please ensure that proper rules have been set on a environment"))
print("Uploading product_calalog preset for test item...")

if cfg.retailer in ("winter", "abs"):
    upload_via_sftp(cfg, file_name, file_path)
else:
    credentials = login_to_gcp(interactive=False)
    upload_file_to_google_bucket(
        project_id=cfg.google_project_id,
        credentials=credentials,
        integration_etl_bucket_name=cfg.integration_etl_bucket_name,
        source_filename=file_name,
        source_filepath=file_path,
    )
check_revision_max_updated(
    distiller=distiller,
    revision_max_old=revision_max_old,
    location_code_tom=str(location_code_tom),
)


print(blue("Adjusting test item for 10 pcs..."))
ims = IMS(cfg)
ims.shelf_adjust("01K", "4071505", 10, "IB")

print(blue("Test item has been made available for testing"))
