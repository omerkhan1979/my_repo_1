import typer

from env_setup_tool.src import utils
from env_setup_tool.src.config_providers.product_catalog_provider import (
    ProductCatalogProvider,
)
from src import logger
from src.config.config import Config

app = typer.Typer()
log = logger.get_logger(__name__)


@app.command(help="Upload product catalog to env.")
def upload(ctx: typer.Context) -> None:
    typer.echo("Uploading product catalog ...")
    try:
        all_feature_files = utils.load_feature(ctx.obj.feature, branch=ctx.obj.branch)
        for ff in all_feature_files:
            config: Config = ctx.obj.config
            pc_provider = ProductCatalogProvider(config)
            if ff.configs.get("product_catalog"):
                typer.echo(f"Uploading product catalog for feature {ff.key}")
                pc_provider.apply(ff.configs.get("product_catalog"))
    except FileNotFoundError:
        log.info(f"Feature {ctx.obj.feature} not found")
        exit(1)
