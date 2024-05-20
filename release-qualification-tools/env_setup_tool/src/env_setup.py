import os
import sys
from dataclasses import dataclass

import typer

from env_setup_tool.src.cli_helpers import product_catalog_cli, tsc_cli, ims_cli
from src.config.config import Config, get_token
from env_setup_tool.src.config_providers.config_provider_mapping import config_providers
from env_setup_tool.src.config_types import ConfigType
from env_setup_tool.src import utils

from src import logger

log = logger.get_logger(__name__)

# We are using location_id from config data, but RQ-Tools config still requires the value
LOCATION_DEFAULT = "9999"
ENV_DEFAULT = "ode"

#  Please see the usage below in the apply_feature_configs() cmd - if config_tpe is passed we apply only it,
#  otherwise all configs for a specific feature
env_setup_tool = typer.Typer()
env_setup_tool.add_typer(
    product_catalog_cli.app,
    name="product-catalog",
    help="Subcommand to access Product Catalog Configurations",
)
env_setup_tool.add_typer(
    tsc_cli.app, name="tsc", help="Subcommand to access TSC Configurations"
)
env_setup_tool.add_typer(
    ims_cli.app, name="ims", help="Subcommand to access IMS Configurations"
)


@dataclass
class GlobalOptions:
    config: Config
    feature: str
    branch: str


@env_setup_tool.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    feature: str = typer.Option(
        "base", help="Either Base or the Feature to be applied"
    ),
    branch: str = typer.Option(
        "master", help="Custom branch to retrieve the base configuration from"
    ),
) -> None:
    # Don't Process Config if calling help
    if "--help" in sys.argv:
        return

    retailer = os.environ["RETAILER_CONFIGURATION"]
    if not retailer:
        log.error("Missing RETAILER_CONFIGURATION env var")
        raise ValueError("RETAILER_CONFIGURATION is not set")
    """Set GlobalOptions in the context so it can be accessed by sub commands."""
    conf = Config(
        retailer,
        ENV_DEFAULT,
        LOCATION_DEFAULT,
        token=get_token(retailer, ENV_DEFAULT),
        disallow=True,
        skip_location_check=True,
    )
    typer.echo("Fetching data from configuration repository")
    ctx.obj = GlobalOptions(
        config=conf,
        feature=feature,
        branch=branch,
    )


@env_setup_tool.command(help="Apply all base/feature configurations")
def apply_configs(
    ctx: typer.Context,
) -> None:
    typer.echo(f"Applying configurations for {ctx.obj.feature} feature")
    apply_all_configs(ctx)


def apply_all_configs(ctx: typer.Context) -> None:
    """Applies all configurations."""
    # Load all parent feature files data
    apply_results = {}
    all_feature_files = utils.load_feature(ctx.obj.feature, branch=ctx.obj.branch)
    for ff in all_feature_files:
        ff_results = []
        log.info(f"Applying configurations for feature {ff.key}")
        for cfg_type in ConfigType:
            provider_cls = config_providers.get(cfg_type)
            if provider_cls is not None:
                if cfg_type.value in ff.configs.keys():
                    msg_applying = f"Applying {cfg_type.value} for feature {ff.key}"
                    log.info(msg_applying)
                    provider = provider_cls(ctx.obj.config)
                    config_data = ff.configs.get(cfg_type.value)
                    result = provider.apply(config_data)
                    ff_results.append(result)
        apply_results[ff.key] = (
            ff_results  # Associate the results with the feature file key
        )
    print_summary(apply_results)


def print_summary(apply_results: dict) -> None:
    """
    Prints a summary of configuration application results for each feature file,
    including both top-level configurations and sub-configurations.
    """
    for ff_key, results in apply_results.items():
        print(f"Results for feature file {ff_key}:")
        for result in results:
            for k, v in result.items():
                print(
                    f"  Application of {k} {'was successful' if v else 'has failed'}."
                )


def apply_specific_config(ctx: typer.Context, config_type: str) -> None:
    """Applies a specific configuration."""
    try:
        # Load all parent feature files data
        all_feature_files = utils.load_feature(ctx.obj.feature, branch=ctx.obj.branch)
        for ff in all_feature_files:
            log.info(f"Applying feature {ff.key}")
            cfg_enum = ConfigType(config_type)
            ProviderClass = config_providers.get(ConfigType(cfg_enum))
            config_data = ff.configs.get(config_type)
            if ProviderClass and config_data:
                provider_instance = ProviderClass(ctx.obj.config)
                provider_instance.apply(config_data)
            else:
                print(f"No provider found for config type: {config_type}")
    except FileNotFoundError:
        log.info(f"Feature {ctx.obj.feature} not found")
        exit(1)


# python -m env_setup_tool.src.env_setup --help
# python -m env_setup_tool.src.env_setup apply-sleeping-area-rules


@env_setup_tool.command(help="Apply sleeping-area-rules configurations")
def apply_sleeping_area_rules(
    ctx: typer.Context,
) -> None:
    typer.echo("Applying sleeping-area-rules configurations")
    apply_specific_config(ctx, "sleeping_area_rules")


@env_setup_tool.command(help="Apply wave plans configurations")
def apply_wave_plans(
    ctx: typer.Context,
) -> None:
    typer.echo("Applying wave plans configurations")
    apply_specific_config(ctx, "waves")


if __name__ == "__main__":
    env_setup_tool()
