from src.config.config import Config, get_config
from src.api.takeoff.ops_api import OpsApi

cfg = Config(*get_config())
ops_api = OpsApi(cfg)
ops_api.clear_manual_picking_q()
