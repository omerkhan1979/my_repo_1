from src.utils.http import handle_response
from urllib.parse import urljoin
import requests

from src import logger

log = logger.get_logger(__name__)


class MultiTenantBaseApi(object):
    def __init__(self, base_domain, clientid, clientsecret):
        self.base_url = f"https://ode.ode-api.{base_domain}"
        self.__token_url = urljoin(self.base_url, "auth/token")
        self.__clientid = clientid
        self.__clientsecret = clientsecret
        self.__auth_token = self.__get_token()

    def __get_token(self) -> str:
        token_req_payload = {"grant_type": "client_credentials"}
        response = requests.post(
            self.__token_url,
            data=token_req_payload,
            auth=(self.__clientid, self.__clientsecret),
            headers={
                "accept": "application/json; version=1",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            verify=False,
            allow_redirects=False,
        )
        return handle_response(response, 200).get("access_token")

    def headers(self, correlation_id=None):
        if not correlation_id:
            correlation_id = "rqt"
        return {
            "accept": "application/json; version=1",
            "content-type": "application/json",
            "X-Correlation-ID": correlation_id,
            "Authorization": "Bearer " + self.__auth_token,
        }

    def __repr__(self):
        return f'MultiTenantBaseApi("{self.base_url}","{self.__headers()}")'

    def __str__(self):
        return f"MultiTenantBaseApi {{base_url: {self.base_url}}}"
