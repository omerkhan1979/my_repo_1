from pytest import fixture
from unittest.mock import patch


@fixture(scope="class")
def gcp_config_mocks():
    with (
        patch("src.config.config.get_gcp_project_id", return_value="fake-project"),
        patch("src.config.config.get_firebase_key", return_value="fake-key"),
    ):
        yield
