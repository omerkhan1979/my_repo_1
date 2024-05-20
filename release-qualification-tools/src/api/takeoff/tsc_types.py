from dataclasses import dataclass
from typing import List, Optional
import typing
from dacite import from_dict


@dataclass
class StagingLocationCode:
    """staging location code"""

    staging_location_code: str


@dataclass
class StagingLocationAdd(StagingLocationCode):
    """Add new staging location"""

    mfc_tom_code: str


@dataclass
class StagingLocation(StagingLocationAdd):
    """Staging location details"""

    default: bool


@dataclass
class RouteConfiguration:
    type: list[str]
    code: str


@dataclass
class MappedRoutes(RouteConfiguration):
    last_modified_at: str


@dataclass
class StagingConfigurationInfo(object):
    """Staging configuration information"""

    staging_location_code: str
    mapped_routes: list[RouteConfiguration]

    @classmethod
    def from_json(cls, json_content) -> List:
        return from_dict(StagingConfigurationInfo, json_content)


@dataclass
class StagingConfiguration(object):
    """Add new staging configuration"""

    mfc_tom_code: str
    staging_configurations: list[StagingConfigurationInfo]

    @classmethod
    def from_json(cls, json_content) -> List:
        return from_dict(StagingConfiguration, json_content)


@dataclass
class FlowRackConfigPayload:
    """Add new staging configuration"""

    location_code_tom: str
    flow_racks: dict


@dataclass
class Route:
    """Route for mfc location"""

    mfc_tom_code: str
    route_code: str


@dataclass
class Routes:
    """Routes for mfc location"""

    routes: list[Route]


@dataclass
class ToteType:
    """Add new tote-type"""

    is_applicable_for_osr: bool
    tote_description: str
    custom_tote_prefix: str
    tote_threshold_size: int
    barcode_format_name: str
    tote_dimensions: dict
    temp_zone_name: str
    location_code_tom: str
    is_standard: bool
    is_product_category_limit: bool
    tote_kind_name: str


@dataclass
class ToteTypeResponse(ToteType):
    """tote-type response"""

    tote_type_id: int


@dataclass
class Profile:
    """Profile"""

    tom_code: str
    profile_name: str


class ConfigItem(object):
    """Configuration Item"""

    name: str
    value: "typing.Any"
    # "value-type": Optional[str]
    # "config-item-id": Optional[int]
    categories: Optional[list]
    level: Optional[str]
    unit: Optional[str]
    # "location-code-tom": Optional[str]

    def __init__(self, config_item_dict):
        for key in config_item_dict:
            setattr(self, str(key).replace("-", "_"), config_item_dict[key])


@dataclass
class Geolocation:
    """Geo coordinates"""

    lat: float
    lon: float


@dataclass
class ServiceInfo:
    phone: Optional[str] = None
    desctext: Optional[str] = None
    email: Optional[str] = None


@dataclass
class Address:
    """Address of a location"""

    state: str
    iso_state: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = None
    zip_code: Optional[str] = None


@dataclass
class LocationSpoke:
    """Location Spoke or MFC"""

    timezone: str
    location_address: Address
    location_pickup: Geolocation
    location_name: str
    location_contract_phone: str
    location_code_retailer: str
    location_code_tom: str
    location_service_info: Optional[ServiceInfo] = None
    location_code_gold: Optional[str] = None
    location_id: Optional[int] = None
    location_type: Optional[str] = None
    mfc_ref_code: Optional[str] = None
    enabled: Optional[bool] = None
