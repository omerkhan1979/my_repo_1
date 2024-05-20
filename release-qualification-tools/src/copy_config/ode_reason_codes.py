import json
import os
import sys
import typer


project_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_root_dir)


from src.api.takeoff.ims import IMS
from src.config.config import Config
from src.config.constants import ODE_RETAILER

app = typer.Typer()


@app.command()
def add_reason_codes(location_code_tom: str):
    """Replace reason codes with the ones default for winter/wakefern"""
    token = os.environ.get("SERVICE_WORKER_TOKEN")
    if not token:
        raise RuntimeError(
            "This is only valid for running with rq-tools container in ODE context"
        )
    cfg = Config(ODE_RETAILER, "ode", location_code_tom, token)

    with open(os.path.join(project_root_dir, "data", "ims_reason_codes.json")) as fp:
        code_data = json.load(fp)
    ims = IMS(cfg)
    print(ims.replace_reason_codes(code_data))


if __name__ == "__main__":
    app()
