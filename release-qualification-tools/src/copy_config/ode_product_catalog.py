import datetime
import json
import os
import sys
import tempfile
import time
import typer


project_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_root_dir)


from src.api.takeoff.distiller import Distiller, get_revision_max
from src.api.takeoff.tsc import TSC, TscReturnFormat
from src.api.third_party.gcp import upload_file_to_google_bucket, login_to_gcp
from src.config.config import Config
from src.config.constants import ODE_RETAILER

app = typer.Typer()


def _upload(
    cfg: Config, location_code_tom: str, filepath: str, distiller: Distiller
) -> bool:
    # Obtaining revision-max before product_catalog file was uploaded
    revision_max_old = get_revision_max(
        distiller=distiller, location_code_tom=location_code_tom
    )

    # Logging to google cloud project
    credentials = login_to_gcp(interactive=False)

    # Uploading product_catalog file to google cloud project
    upload_file_to_google_bucket(
        project_id=cfg.google_project_id,
        credentials=credentials,
        integration_etl_bucket_name=cfg.integration_etl_bucket_name,
        source_filename=os.path.basename(filepath),
        source_filepath=filepath,
    )

    for _ in range(30):
        if (
            get_revision_max(distiller=distiller, location_code_tom=location_code_tom)
            > revision_max_old
        ):
            return True
        print("Waiting for revision to update")
        time.sleep(5)
    return False


@app.command()
def upload_default_product_catalog(
    location_code_tom: str, new_tom_ids: bool, fail_if_not_processed: bool = True
):
    """Upload a default product catalog to ODE"""
    # NOTE: new_tom_ids is true if "FEATURE__SET_NEW_TOM_ID__TURN_ON" is set in Distiller's env
    # this corresponds with the key "RETURN_NEW_TOM_IDS_ONLY" in TSC
    # I'm not super clear on how important this is here, but we have the info if needed
    # for wakefern and maf (as of time of writing) these values are set to True
    token = os.environ.get("SERVICE_WORKER_TOKEN")
    if not token:
        raise RuntimeError(
            "This is only valid for running with rq-tools container in ODE context"
        )
    cfg = Config(ODE_RETAILER, "ode", location_code_tom, token)

    distiller = Distiller(cfg)
    tsc = TSC(cfg)
    location_code = tsc.get_location_code("location-code-retailer")
    tsc_new_ids = tsc.get_config_item_value(
        "RETURN_NEW_TOM_IDS_ONLY", return_format=TscReturnFormat.json
    )

    print(
        f"About to upload product catalog for Location: {location_code_tom}, FEATURE__SET_NEW_TOM_ID__TURN_ON: {new_tom_ids}, location-code-retailer: {location_code}, RETURN_NEW_TOM_IDS_ONLY: {tsc_new_ids}"
    )

    # this logic is WRONG, but it's what we've been doing
    # TODO: is there a better way to choose format?
    kind = "v6"
    prefix = "Takeoff_product_catalog_"
    if not tsc_new_ids:
        kind = "v5custom"
        prefix = "MFC_itemmaster_"

    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    suffix = f"_{now}.json"

    with tempfile.NamedTemporaryFile(
        prefix=prefix, suffix=suffix, delete=False, mode="w"
    ) as fp:
        with open(os.path.join(project_root_dir, "data", f"{kind}.json")) as pcfp:
            template_data = json.load(pcfp)
        for entry in template_data:
            if kind == "v6":
                entry["mfc-id"] = location_code
            else:
                for loc in entry.get("location-info", []):
                    loc["store-id"] = location_code
        # add our date into the first product name
        template_data[0]["name"] = f"Yummy {now}"
        json.dump(template_data, fp, indent=2)
        fp.close()

        if not _upload(cfg, location_code_tom, fp.name, distiller):
            print("WARNING: File was not processed")
            if fail_if_not_processed:
                sys.exit(1)


if __name__ == "__main__":
    app()
