from src.utils.locations import suggest_mfc_location_tom_codes
from src.config.config import Config, get_config

# TODO: Subject to delete or update to provide some output

cfg = Config(*get_config())

suggest_mfc_location_tom_codes(cfg.retailer, cfg.env, cfg.token, "service-catalog")
