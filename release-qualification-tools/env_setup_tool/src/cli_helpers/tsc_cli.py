import typer

from env_setup_tool.src import utils
from src import logger
from src.config.config import Config
from env_setup_tool.src.config_providers.tsc_provider import TscProvider

app = typer.Typer()
log = logger.get_logger(__name__)


@app.command(help="Apply all TSC configurations")
def apply_configs(ctx: typer.Context) -> None:
    apply_all_configs(ctx)


@app.command(help="Apply TSC-Config-Items configurations")
def apply_config_items(ctx: typer.Context) -> None:
    apply_specific_config(ctx, "config_items")


@app.command(help="Apply TSC-Flow-Racks configurations")
def apply_flow_racks(ctx: typer.Context) -> None:
    apply_specific_config(ctx, "flow_racks")


@app.command(help="Apply TSC-Spokes configurations")
def apply_spokes(ctx: typer.Context) -> None:
    apply_specific_config(ctx, "spokes")


@app.command(help="Apply TSC-Tote-Types configurations")
def apply_tote_types(ctx: typer.Context) -> None:
    apply_specific_config(ctx, "tote_types")


@app.command(help="Apply TSC-Staging-Config configurations")
def apply_staging_config(ctx: typer.Context) -> None:
    apply_specific_config(ctx, "staging_config")


@app.command(help="Apply TSC-Staging-Locations configurations")
def apply_staging_locations(ctx: typer.Context) -> None:
    apply_specific_config(ctx, "staging_locations")


@app.command(help="Apply TSC-Routes configurations")
def apply_routes(ctx: typer.Context) -> None:
    apply_specific_config(ctx, "routes")


@app.command(help="Apply TSC-Locations configurations")
def apply_locations(ctx: typer.Context) -> None:
    apply_specific_config(ctx, "locations")


def apply_specific_config(ctx: typer.Context, config_type: str) -> None:
    """Applies a specific configuration."""
    try:
        all_feature_files = utils.load_feature(ctx.obj.feature, branch=ctx.obj.branch)
        for ff in all_feature_files:
            config: Config = ctx.obj.config
            tsc_provider = TscProvider(config)
            if ff.configs.get("tsc") and ff.configs.get("tsc").configs.get(config_type):
                log.info(
                    f"Applying TSC {config_type} configurations for feature {ff.key}"
                )
                tsc_provider.apply(ff.configs.get("tsc"), config_type)
    except FileNotFoundError:
        log.info(f"Feature {ctx.obj.feature} not found")
        exit(1)


def apply_all_configs(ctx: typer.Context) -> None:
    """Applies all configurations."""
    try:
        all_feature_files = utils.load_feature(ctx.obj.feature, branch=ctx.obj.branch)
        for ff in all_feature_files:
            config: Config = ctx.obj.config
            tsc_provider = TscProvider(config)
            if ff.configs.get("tsc"):
                typer.echo(f"Applying TSC Configurations for feature {ff.key}")
                tsc_provider.apply(ff.configs.get("tsc"))
    except FileNotFoundError:
        log.info(f"Feature {ctx.obj.feature} not found")
        exit(1)
