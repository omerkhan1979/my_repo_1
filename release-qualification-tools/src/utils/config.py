from functools import partial
from urllib.parse import urljoin
from src.config.constants import BASE_DOMAIN, ODE_RETAILER
from src.utils.console_printing import cyan


def make_env_url(retailer, env, base_domain=BASE_DOMAIN):
    if ODE_RETAILER and env != "prod":
        return f"{ODE_RETAILER}-{env}.{base_domain}"
    else:
        if env == "prod":
            return f"{retailer}-{env}.tom.takeoff.com"
        else:
            return f"{retailer}-{env}.{base_domain}"


def url_builder(
    base,
    service_name,
    retailer=None,
    env=None,
    rel="",
    protocol="https",
    use_env_url=True,
):
    if base:
        endpart = "/".join([base, rel])
    else:
        endpart = rel
    if use_env_url:
        separator = "-" if service_name else ""
        return urljoin(
            f"{protocol}://{service_name}{separator}{make_env_url(retailer, env)}",
            endpart,
        )
    else:
        if not retailer and not env:
            return urljoin(f"{protocol}://{service_name}.{endpart}", url=None)

        return urljoin(f"{protocol}://{service_name}", endpart)


def get_url_builder(base, service_name):
    return partial(url_builder, base, service_name)


def make_bifrost_url(
    retailer: str,
    env: str,
    location_gold: str,
    base_domain: str = BASE_DOMAIN,
    protocol="https",
):
    if location_gold:
        if ODE_RETAILER and env != "prod":
            return f"{protocol}://bifrost-{location_gold}-{env}-{ODE_RETAILER}.{base_domain}"
        elif env == "prod":
            return (
                f"{protocol}://bifrost-{location_gold}-{env}-{retailer}.tom.takeoff.com"
            )
        else:
            return (
                f"{protocol}://bifrost-{location_gold}-{env}-{retailer}.{base_domain}"
            )


def make_inventorymanager_url(
    env: str,
    base_domain: str = BASE_DOMAIN,
    protocol="https",
):
    if ODE_RETAILER and env != "prod":
        print(cyan("Endpoint TO be added once ODE endpoint is updated/developed"))
    elif env == "prod":
        print(cyan("Endpoint TO be added once prod endpoint is updated/developed"))
    else:
        return f"{protocol}://{env}.nonprod-api.{base_domain}"
