from urllib.parse import urljoin

import requests

from src import logger
from src.api.takeoff.multi_tenant_base_api import MultiTenantBaseApi
from src.utils.http import handle_response

from typing import Optional, Any
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config

log = logger.get_logger(__name__)


def ExcludeIfNone(value: Any) -> Any:
    return value is None


@dataclass_json
@dataclass
class Location:
    lat: float
    long: float


@dataclass_json
@dataclass
class Legacy:
    location_id: int
    location_code_gold: str
    location_code_tom: str


@dataclass_json
@dataclass
class SiteInfoSitePayload:
    name: str
    retailer_site_id: str
    location: Location
    legacy: Optional[Legacy] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )


@dataclass_json
@dataclass
class SiteInfoSiteQuery:
    page_size: Optional[int | None] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    page_token: Optional[int | None] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    # If None, show_deactivated acts as False
    show_deactivated: Optional[bool | None] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    retailer_id: Optional[str | None] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    location_id: Optional[int | None] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    location_code_tom: Optional[str | None] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    location_code_gold: Optional[str | None] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    retailer_site_id: Optional[str | None] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )


@dataclass_json
@dataclass
class SiteInfoSiteResponse:
    id: str
    name: str
    deployed_region: str
    retailer_site_id: str
    retailer_id: str
    status: str
    timezone: str
    location: Location
    create_by: str
    update_by: str
    create_time: str
    update_time: str
    etag: Optional[str] = field(default=None, metadata=config(exclude=ExcludeIfNone))
    legacy: Optional[Legacy] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    deactivated_by: Optional[str] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    deactivate_time: Optional[str] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )


@dataclass_json
@dataclass
class SiteInfoRetailerPayload:
    name: str
    code: str
    deployed_region: str


@dataclass_json
@dataclass
class SiteInfoRetailerResponse:
    id: str
    name: str
    deployed_region: str
    code: str
    create_by: str
    update_by: str
    create_time: str
    update_time: str


@dataclass_json
@dataclass
class SiteInfoRetailerQuery:
    page_token: Optional[int] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )
    code: Optional[str] = field(default=None, metadata=config(exclude=ExcludeIfNone))
    page_size: Optional[int] = field(default=25, metadata=config(exclude=ExcludeIfNone))
    show_deactivated: Optional[bool] = field(
        default=None, metadata=config(exclude=ExcludeIfNone)
    )


class SiteInfoSvc(MultiTenantBaseApi):

    def __init__(self, base_domain: str, clientid: str, clientsecret: str):
        super().__init__(
            base_domain=base_domain, clientid=clientid, clientsecret=clientsecret
        )
        self.__sites_url = urljoin(self.base_url, "sites")
        self.__retailer_url = urljoin(self.base_url, "retailers")

    def create_site(
        self,
        retailer_id: str,
        site: SiteInfoSitePayload,
        correlation_id: str | None = None,
    ) -> SiteInfoSiteResponse:
        """
        This method creates a new site in the Site Info Service.

        Args:
        retailer_id (str): The site will be created under this Retailer.
        site (SiteInfoSitePayload): A dataclass representing the information
                                    necessary to create a new site.
        correlation_id (str): A tag used to track calls through the system.

        Return:
        SiteInfoSiteResponse: A representation of all of the data known about a site.
                              The return represents the site just created.
        """

        headers = self.headers(correlation_id=correlation_id)
        headers["retailer_id"] = retailer_id
        response = requests.post(
            self.__sites_url,
            headers=headers,
            data=site.to_json(),  # type:ignore
        )

        return SiteInfoSiteResponse.from_dict(  # type:ignore
            handle_response(response, 200, 201)
        )

    def get_sites(
        self,
        site_params: SiteInfoSiteQuery = SiteInfoSiteQuery(),
        correlation_id: str | None = None,
    ) -> list[SiteInfoSiteResponse]:
        """
        This method gets a list of sites filtered based on input.
        - The default return size is 25 but SiteInfoSiteQuery.page_size can be changed
        - A key 'next_page_token' is returned if not all sites are listed. This can be
          used in SiteInfoSiteQuery.page_token to get the next page.
          !! page_token is not implemented, for now just raise page_size

        Args:
        site_params (SiteInfoSiteQuery): A dataclass representing all parameters that
                                         can be used in the filter query.
        correlation_id (str): A tag used to track calls through the system.

        Return:
        list[SiteInfoSiteResponse]: A filtered list of objects that represent all of the
                                    data known about a site.
        """
        response = requests.get(
            self.__sites_url,
            headers=self.headers(correlation_id=correlation_id),
            params=site_params.to_dict(),  # type:ignore
        )
        resp = handle_response(response, 200, 201)
        sites = resp["sites"]
        return [
            SiteInfoSiteResponse.from_dict(x)  # type:ignore
            for x in sites
        ]

    def site_activate(
        self,
        etag: str,
        retailer_id: str,
        site_id: str,
        correlation_id: str | None = None,
    ) -> SiteInfoRetailerResponse:
        headers = self.headers(correlation_id=correlation_id)
        headers["If-Match"] = etag
        headers["retailer_id"] = retailer_id
        url = f"{self.__sites_url}/{site_id}:active"
        response = requests.post(url=url, headers=headers)

        return SiteInfoSiteResponse.from_dict(  # type:ignore
            handle_response(response, 200, 201)
        )

    def create_retailer(
        self, retailer: SiteInfoRetailerPayload, correlation_id: str | None = None
    ) -> SiteInfoRetailerResponse:
        headers = self.headers(correlation_id=correlation_id)
        response = requests.post(
            self.__retailer_url,
            headers=headers,
            data=retailer.to_json(),  # type:ignore
        )
        return SiteInfoRetailerResponse.from_dict(  # type:ignore
            handle_response(response, 200, 201)
        )

    def get_retailers(
        self,
        correlation_id: str | None = None,
        parameters: SiteInfoRetailerQuery = SiteInfoRetailerQuery(),
    ) -> list[SiteInfoRetailerResponse]:
        response = requests.get(
            self.__retailer_url,
            headers=self.headers(correlation_id=correlation_id),
            params=parameters.to_dict(),  # type:ignore
        )
        resp = handle_response(response, 200, 201)
        retailers = resp["retailers"]
        return [SiteInfoRetailerResponse.from_dict(x) for x in retailers]  # type: ignore
