from typing import Optional
from src.config.config import Config
from src.config.constants import BASE_DOMAIN, ODE_RETAILER


class outbound_baseApi:
    url_builder: Optional[str] = None

    def __init__(self, my_config: Config):
        self.config = my_config
        retailer_id = self.config.retailer
        if self.config.env == "prod":
            self.url_builder = "https://prod.outbound-backend.tom.takeoff.com/"
        elif self.config.env == "ode":
            self.url_builder = f"https://ode.outbound-backend.{BASE_DOMAIN}/"
            retailer_id = ODE_RETAILER
        else:
            self.url_builder = "https://nonprod.outbound-backend.tom.takeoff.com/"

        self.default_headers = {
            "X-Token": self.config.token,
            "accept": "application/json",
            "content-type": "application/json",
            "X-Env-Type": self.config.env,
            "X-Retailer-Id": retailer_id,
        }
