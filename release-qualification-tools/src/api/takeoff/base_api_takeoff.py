from functools import partial

from src.config.config import Config


class BaseApiTakeoff:
    url_builder = None

    def __init__(self, my_config: Config, url_builder=None):
        self.config = my_config

        self.url_builder = partial(
            url_builder or self.url_builder, my_config.retailer, my_config.env
        )

        self.default_headers = {
            "X-Token": my_config.token,
            "accept": "application/json",
            "content-type": "application/json",
        }

    def __repr__(self):
        return f'BaseApiTakeoff("{self.config}","{self.url_builder}","{self.default_headers}")'

    def __str__(self):
        return (
            f"BaseApiTakeoff {{config: {self.config}, url_builder: {self.url_builder}}}"
        )
