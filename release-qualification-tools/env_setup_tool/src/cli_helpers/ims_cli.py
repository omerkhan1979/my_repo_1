import typer

from src.config.config import Config
from env_setup_tool.src import utils
from src import logger
from env_setup_tool.src.config_providers.ims_provider import ImsProvider

app = typer.Typer()
log = logger.get_logger(__name__)


@app.command(help="Apply all IMS configurations")
def apply_configs(ctx: typer.Context) -> None:
    typer.echo("Applying All IMS configurations ...")
    apply_all_configs(ctx)


@app.command(help="Apply IMS-Addresses configurations")
def apply_addresses(ctx: typer.Context) -> None:
    typer.echo("Applying IMS-Addresses configurations ...")
    apply_specific_config(ctx, "addresses")


@app.command(help="Apply IMS-Reason-Codes configurations")
def apply_reason_codes(ctx: typer.Context) -> None:
    typer.echo("Applying IMS-Reason-Codes configurations ...")
    apply_specific_config(ctx, "reason_codes")


def apply_specific_config(ctx: typer.Context, config_type: str) -> None:
    """Applies a specific configuration."""
    try:
        all_feature_files = utils.load_feature(ctx.obj.feature, branch=ctx.obj.branch)
        for ff in all_feature_files:
            config: Config = ctx.obj.config
            ims_provider = ImsProvider(config)
            if ff.configs.get("ims") and ff.configs.get("ims").configs.get(config_type):
                log.info(
                    f"Applying IMS {config_type} configurations for feature {ff.key}"
                )
                ims_provider.apply(ff.configs.get("ims"), config_type)
    except FileNotFoundError:
        log.info(f"Feature {ctx.obj.feature} not found")
        exit(1)


def apply_all_configs(ctx: typer.Context) -> None:
    """Applies all configurations."""
    try:
        all_feature_files = utils.load_feature(ctx.obj.feature, branch=ctx.obj.branch)
        for ff in all_feature_files:
            config: Config = ctx.obj.config
            ims_provider = ImsProvider(config)
            if ff.configs.get("ims"):
                typer.echo(f"Applying all IMS Configurations for feature {ff.key}")
                ims_provider.apply(ff.configs.get("ims"))
    except FileNotFoundError:
        log.info(f"Feature {ctx.obj.feature} not found")
        exit(1)
