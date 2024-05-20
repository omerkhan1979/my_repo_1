from env_setup_tool.src.config_providers.ims_provider import ImsProvider
from env_setup_tool.src.config_providers.product_catalog_provider import (
    ProductCatalogProvider,
)
from env_setup_tool.src.config_providers.site_info_provider import SiteInfoProvider
from env_setup_tool.src.config_providers.sleeping_area_rules_provider import (
    SleepingAreaRulesProvider,
)
from env_setup_tool.src.config_providers.tsc_provider import TscProvider
from env_setup_tool.src.config_providers.wave_planner_provider import (
    WavePlannerProvider,
)
from env_setup_tool.src.config_types import ConfigType

config_providers = {
    ConfigType.TSC: TscProvider,
    ConfigType.IMS: ImsProvider,
    ConfigType.SleepingAreaRules: SleepingAreaRulesProvider,
    ConfigType.WAVE_PLANS: WavePlannerProvider,
    ConfigType.PRODUCT_CATALOG: ProductCatalogProvider,
    ConfigType.SITE_INFO: SiteInfoProvider,
}
