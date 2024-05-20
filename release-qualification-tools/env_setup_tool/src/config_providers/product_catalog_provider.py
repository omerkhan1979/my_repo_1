import datetime
import json
import os
import tempfile
import time
from typing import Optional

from src.config.config import Config as GlobalConfig
from env_setup_tool.src.config_providers.config_providers import BaseConfigProvider
from env_setup_tool.src.config_types import Config, CompositeConfig, ConfigType
from src import logger
from src.api.takeoff.distiller import Distiller, get_revision_max
from src.api.third_party.gcp import upload_file_to_google_bucket, login_to_gcp

log = logger.get_logger(__name__)


class ProductCatalogProvider(BaseConfigProvider):
    def __init__(self, global_config: GlobalConfig):
        self.glb_config = global_config
        self.service = Distiller(global_config)
        self.config_name = ConfigType.PRODUCT_CATALOG.value

    def apply_composite_config(
        self, config_data: CompositeConfig, subconfig_key: Optional[str] = None
    ) -> dict[str, bool]:
        raise NotImplementedError("This provider only handles composite configurations")

    def apply_simple_config(self, config_data: Config) -> dict[str, bool]:
        """
        Uploads provided Product Catalog data.

        This method data from the provided file. The method changes the filename by adding timestamp in a format YYYYmmddHHmmss.

        Args:
        config (Config): An instance of Config containing the configurations to be applied,
                                       previously read from feature file
        """

        # get location_id from file content
        if not config_data.data:
            log.error("Empty product catalog file. Will not upload")
            return {ConfigType.PRODUCT_CATALOG.value: False}
        location_id = config_data.data[0].get("mfc-id")
        if location_id is None or location_id == "":
            log.error("Location id is empty. Cannot check revision")
            return {ConfigType.PRODUCT_CATALOG.value: False}
        # get revision # to check PC upload was successful at the end
        old_revision_max = get_revision_max(self.service, location_code_tom=location_id)

        # update file_name with a timestamp
        now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = "Takeoff_product_catalog_" + now
        log.info(f"File re-named to PCv6 supported name {file_name}")
        success = False
        with tempfile.NamedTemporaryFile(
            mode="w+", prefix=file_name, suffix=".json", delete=False
        ) as temp_file:
            json.dump(config_data.data, temp_file, indent=2)
            temp_file.close()

            credentials = login_to_gcp(interactive=False)
            upload_file_to_google_bucket(
                project_id=self.glb_config.google_project_id,
                credentials=credentials,
                integration_etl_bucket_name=self.glb_config.integration_etl_bucket_name,
                source_filename=os.path.basename(temp_file.name),
                source_filepath=temp_file.name,
            )

            for _ in range(30):
                if (
                    get_revision_max(
                        distiller=self.service,
                        location_code_tom=location_id,
                    )
                    > old_revision_max
                ):
                    log.info("Product Catalog uploaded successfully")
                    success = True
                    break
                log.info("Waiting for revision to update")
                time.sleep(5)
        if not success:
            log.info(
                "Revision wasn't updated. There could be several reasons for that: no new changes detected in a PC;"
                "or an issue occurred during PC processing, please check integration-etl logs for more details."
            )
        return {self.config_name: success}
