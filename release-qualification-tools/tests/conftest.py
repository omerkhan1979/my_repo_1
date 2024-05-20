import os

import pytest
from pytest import hookimpl, skip, fixture
from scripts.steps.orderflow.setup import prepare_orderflow_data
from src.api.takeoff.auth_service import AuthService
from src.api.takeoff.bifrost import Bifrost
from src.api.takeoff.decanting import Decanting
from src.api.takeoff.distiller import Distiller
from src.api.takeoff.ff_tracker import FFTracker
from src.api.takeoff.ims import IMS
from src.api.takeoff.inventory_manager import InventoryManager
from src.api.takeoff.mobile import Mobile
from src.api.takeoff.oms import OMS
from src.api.takeoff.ops_api import OpsApi
from src.api.takeoff.osr_replicator import OSRR
from src.api.takeoff.outbound_api import OutboundBackend
from src.api.takeoff.pickerman_facade import PickermanFacade
from src.api.takeoff.rint import RInt
from src.api.takeoff.isps import ISPS
from src.api.takeoff.tsc import TSC
from src.api.takeoff.wave_planner import WavePlanner
from src.api.collections import InitializedApis
from src.api.third_party.gcp import change_gcp_project, login_to_gcp
from src.config.config import Config, get_firebase_key, get_token, get_user_token
from src.config.constants import (
    RETAILERS_WITH_ISPS,
    RETAILERS_DEFAULT_LOCATION,
    RETAILERS_WITHOUT_STAGING,
    DEFAULT_USER_PASSWORD,
)
from src.config.constants import USER_ROLES
from src.utils.user import delete_test_user, create_test_user, AuthServiceUser
from src.utils.console_printing import error_print, red, blue, cyan, yellow
from src.utils.order_picking import (
    clear_dispatch_lane_order,
    process_unassigned_orders,
)
from src.utils.place_order import place_order
from src.utils.order_timings import (
    get_retailer_future_event,
    MFCRelativeFutureTime,
)
from src.utils.locations import is_location_code_tom_valid
from src.utils.locations import get_location_without_token


def pytest_addoption(parser):
    group = parser.getgroup("rqt")
    group.addoption(
        "--l",
        action="store",
        help="Location-id to execute tests against, e.g. WF0001, ABS1574",
    )
    group.addoption(
        "--d",
        action="store",
        help="Date for order creation, e.g. 2022-05-15, 2022-06-24",
    )
    group.addoption(
        "--u",
        action="store",
        help="User login to execute tests against, e.g. it@takeoff.com",
    )
    group.addoption(
        "--p",
        action="store",
        help="Password to execute tests against",
    )
    group.addoption(
        "--ur",
        action="store",
        help="User role to create user with",
    )
    group.addoption(
        "--g",
        action="store",
        help="path to pass the garden file for setting up ode env for RQT",
    )


@hookimpl
def pytest_configure(config: Config) -> None:
    # register an additional marker
    config.addinivalue_line(
        "markers",
        "retailers(name): mark test with retailers, to allow them to run only for relevant ones",
    )


def pytest_runtest_setup(item):
    retailers = []
    try:
        retailers = [mark.args for mark in item.iter_markers(name="retailers")][0]
    except IndexError:
        pass
    if retailers:
        retailer = os.getenv("RETAILER_CONFIGURATION")
        if retailer not in retailers:
            skip(
                yellow(
                    f"Test is relevant only for {retailers}. Make sure you set RETAILER_CONFIGURATION to a valid "
                    f"retailer name"
                )
            )


def pytest_collection_modifyitems(session, config, items):
    for item in items:
        for marker in item.iter_markers(name="testrail"):
            # for @mark.testrail("id1", "id2", ...)
            # testrail expects a property of 'test_id' with a value of C<id>
            # for parameterized tests, things are a bit awkward- we can have 2 cases
            # 1. we want @mark.testrail("id1", "id2") to apply to all cases
            # 2. We want each case to be for one or more ids.
            # to support this, we must use `pytest.param(args.., pytest.marks.testrail("id1", "id2"))`
            # NOTE: trcli may not support multiple Cids in a single test, but
            # adding that functionality looks simple enough if desired - for now
            # keeping "primary" case id first is recommended/ one Cid per case is preferred
            for test_id in marker.args:
                # add the "C" if it wasn't already there
                if not test_id.startswith("C"):
                    test_id = f"C{test_id}"
                item.user_properties.append(("test_id", test_id))


@fixture(scope="session")
def retailer(request, env):
    if "RETAILER_CONFIGURATION" in os.environ:
        retailer = os.environ["RETAILER_CONFIGURATION"]
        return retailer
    else:
        pytest.skip("RETAILER_CONFIGURATION environment variable must be set!")


@fixture(scope="session")
def env(request):
    env = os.environ.get("ENV", None)
    if env in ["prod"]:
        raise ValueError("Cannot be run on production environment")
    elif env:
        return env
    elif env is None:
        env = "ode"
        return env
    else:
        pytest.skip("ENV environment variable must be set!")


def print_default_location(location):
    print(cyan(f"Default {location} location is set for the test"))


@fixture(scope="session")
def location_code_tom(request, env, retailer):
    location_code_tom = request.config.getoption("--l")
    if env == "ode":
        if location_code_tom:
            return location_code_tom
        else:
            if os.environ.get("BASE_DOMAIN"):
                ode_location = get_location_without_token(
                    retailer, env, "service-catalog"
                )
                if ode_location is not None:
                    return ode_location[0]
                else:
                    print("Invalid tom code location")
            else:
                print("Base domain not found")
    else:
        if location_code_tom:
            return location_code_tom

        else:
            # here we provide the default location code for each retailer
            # the default location is used for release qualification testing as a primary location
            match retailer:
                case "abs":
                    location_code_tom = RETAILERS_DEFAULT_LOCATION.get("abs")
                    print_default_location(location_code_tom)
                    return location_code_tom
                case "maf":
                    location_code_tom = RETAILERS_DEFAULT_LOCATION.get("maf")
                    print_default_location(location_code_tom)
                    return location_code_tom
                case "wings":
                    location_code_tom = RETAILERS_DEFAULT_LOCATION.get("wings")
                    print_default_location(location_code_tom)
                    return location_code_tom
                case "winter":
                    location_code_tom = RETAILERS_DEFAULT_LOCATION.get("winter")
                    print_default_location(location_code_tom)
                    return location_code_tom
                case "smu":
                    location_code_tom = RETAILERS_DEFAULT_LOCATION.get("smu")
                    print_default_location(location_code_tom)
                    return location_code_tom
                case "pinemelon":
                    location_code_tom = RETAILERS_DEFAULT_LOCATION.get("pinemelon")
                    print_default_location(location_code_tom)
                    return location_code_tom
                case _:
                    print(
                        red(
                            "You didn't provide a retailer name or the name isn't correct or specify --l"
                        )
                    )


@fixture(scope="session")
def date(request):
    date = request.config.getoption("--d")
    if date:
        return date
    else:
        skip(red("Date (--d) must be set"))


@fixture(scope="function")
def location_code_gold(tsc: TSC) -> str:
    return tsc.get_location_code("location-code-gold")


@fixture(scope="session")
def user(request):
    return request.config.getoption("--u")


@fixture(scope="session")
def password(request):
    return request.config.getoption("--p") or DEFAULT_USER_PASSWORD


@fixture(scope="session")
def user_role(request):
    role = request.config.getoption("--ur")
    if role:
        if role in USER_ROLES:
            return role
        else:
            print(red("You didn't specify a correct role name or --ur"))
    else:
        default_role = "operator"
        return default_role


@pytest.fixture(scope="session")
def garden_file(pytestconfig):
    return pytestconfig.getoption("--g", default=None)


@fixture(scope="session")
def auth_cfg(retailer, env, location_code_tom, user, password, user_role) -> Config:
    token = get_token(retailer, env)
    if is_location_code_tom_valid(retailer, env, token, location_code_tom) is None:
        skip("Invalid location-code-tom provided")

    return Config(
        retailer,
        env,
        location_code_tom,
        token,
        user_role,
        user=user,
        password=password,
    )


@fixture(scope="session")
def auth_service(auth_cfg) -> AuthService:
    return AuthService(auth_cfg)


@fixture(scope="session")
def admin_cfg(
    retailer, env, location_code_tom, user, password, user_role="admin"
) -> Config:
    token = get_token(retailer, env)
    if is_location_code_tom_valid(retailer, env, token, location_code_tom) is None:
        skip("Invalid location-code-tom provided")

    return Config(
        retailer,
        env,
        location_code_tom,
        token,
        user_role,
        user=user,
        password=password,
    )


@fixture(scope="session")
def cfg(retailer, env, location_code_tom, password, user_role, auth_service) -> Config:
    user_with_role = create_test_user(auth_service, password=password)
    auth_service.set_user_role(user_with_role.id, user_role, location_code_tom)
    token = get_user_token(
        get_firebase_key(retailer, env),
        user_with_role.email,
        password,
    )
    print(
        cyan("\nRunning with user:"),
        cyan(user_with_role.email),
        cyan("with role:" + user_role),
    )
    try:
        yield Config(
            retailer,
            env,
            location_code_tom,
            token,
            user_role,
            user=user_with_role.email,
            user_id=user_with_role.id,
            password=password,
        )
    finally:
        print(
            cyan("\nDeleting test user:"),
            cyan(user_with_role.email),
            cyan("with role:" + user_role),
        )

        delete_test_user(retailer, env, user_with_role.email, password)


@fixture(scope="session")
def operator_cfg(cfg, operator_user, operator_token) -> Config:
    return Config(
        cfg.retailer,
        cfg.env,
        cfg.location_code_tom,
        operator_token,
        operator_user.email,
    )


@fixture(scope="session")
def wave_planner(cfg: Config) -> WavePlanner:
    if cfg.env == "ode":
        return WavePlanner(cfg)
    return None


@fixture(scope="session")
def distiller(admin_cfg) -> Distiller:
    return Distiller(admin_cfg)


@fixture(scope="session")
def decanting(cfg) -> Decanting:
    return Decanting(cfg)


@fixture(scope="session")
def fft(cfg) -> FFTracker:
    return FFTracker(cfg)


@fixture(scope="session")
def ims(cfg) -> IMS:
    return IMS(cfg)


@fixture(scope="session")
def admin_ims(admin_cfg) -> IMS:
    return IMS(admin_cfg)


@fixture(scope="session")
def osrr(cfg) -> OSRR:
    return OSRR(cfg)


@fixture(scope="session")
def isps(cfg) -> ISPS:
    return ISPS(cfg)


@fixture(scope="session")
def oms(admin_cfg) -> OMS:
    return OMS(admin_cfg)


@fixture(scope="session")
def ops_api(cfg) -> OpsApi:
    return OpsApi(cfg)


@fixture(scope="session")
def pickerman_facade(cfg) -> PickermanFacade:
    return PickermanFacade(cfg)


@fixture(scope="session")
def rint(cfg) -> RInt:
    return RInt(cfg)


@fixture(scope="session")
def tsc(cfg) -> TSC:
    return TSC(cfg)


@fixture(scope="function")
def bifrost(cfg: Config, location_code_gold: str):
    return Bifrost(cfg, location_code_gold)


@fixture(scope="session")
def apis(cfg: Config, admin_cfg: Config, auth_cfg: Config):
    tsc = TSC(cfg)
    location_code_gold = tsc.get_location_code("location-code-gold")
    return InitializedApis(
        auth_service=AuthService(auth_cfg),
        bifrost=Bifrost(cfg, location_code_gold),
        decanting=Decanting(cfg),
        distiller=Distiller(admin_cfg),
        fft=FFTracker(cfg),
        im=InventoryManager(cfg),
        ims_admin=IMS(admin_cfg),
        ims=IMS(cfg),
        isps=ISPS(cfg),
        mobile=Mobile(cfg),
        oms=OMS(admin_cfg),
        ops_api=OpsApi(cfg),
        osrr=OSRR(cfg),
        outbound_backend=OutboundBackend(cfg),
        pickerman_facade=PickermanFacade(cfg),
        rint=RInt(cfg),
        tsc=tsc,
        wave_planner=WavePlanner(cfg),
    )


@fixture(scope="function")
def staging_location(cfg: Config, tsc: TSC) -> str:
    return (
        tsc.get_default_or_first_staging_location()
        if cfg.retailer not in RETAILERS_WITHOUT_STAGING
        else None
    )


@fixture(scope="function")
def location_code_retailer(tsc: TSC) -> str:
    return tsc.get_location_code("location-code-retailer")


@fixture(scope="function")
def check_if_retailer_has_isps(cfg: Config):
    if cfg.retailer not in RETAILERS_WITH_ISPS:
        print(red(f"{cfg.retailer} doesn't use ISPS! Skipping test"))
        skip()


@fixture(scope="function")
def order_timeslot_and_spoke(cfg: Config, apis: InitializedApis) -> dict:
    stage_by_data = _stage_by_with_configured_waveplan(
        cfg.retailer, apis, stage_by_in_minutes=1, first_cutoff_minutes=1
    )
    return {
        "stage_by_datetime": stage_by_data.timestamp,
        "service_window_start": stage_by_data.timestamp,
        "spoke_id": stage_by_data.location_code_spoke,
        "location-code-retailer": stage_by_data.location_code_retailer,
    }


@fixture(scope="function")
def cancel_all_draft_orders(oms: OMS):
    oms.cancel_all_draft_orders()


@fixture(scope="function")
def close_all_open_picklists(isps: ISPS):
    isps.close_all_open_picklists()


@fixture(scope="function")
def clear_picking_queue(ops_api: OpsApi):
    ops_api.clear_manual_picking_q()


@fixture(scope="function")
def orderflow_test_data(
    flo,
    osr,
    manual,
    weighted_manual,
    ims,
    distiller,
    tsc,
    retailer,
    bifrost: Bifrost,
    stage_by_in_1_minutes_1_min_cutoff: MFCRelativeFutureTime,
) -> dict:
    if osr > 0 and not bifrost.get_health_pass():
        error_print("Bifrost is unhealthy")
        raise SystemError("Cannot continue as bifrost is unhealthy")
    else:
        return prepare_orderflow_data(
            ims=ims,
            distiller=distiller,
            tsc=tsc,
            retailer=retailer,
            picklist_non_weighted_qty=flo,
            osr_products_qty=osr,
            manual_non_weighted_qty=manual,
            manual_weighted_qty=weighted_manual,
            stage_by_data=stage_by_in_1_minutes_1_min_cutoff,
        )


@fixture(scope="function")
def create_order(
    request,
    cfg: Config,
    orderflow_test_data,
    clear_picking_queue,
    apis: InitializedApis,
) -> str:
    """This fixture does quite a bit.
    * prepares products
    * sets up the data for order cutoff
    * adjusts waveplanner to play nicely with that
    * places the order
    * finally clears dispatch lanes on teardown
    """
    order_id = place_order(
        rint=apis.rint,
        retailer=cfg.retailer,
        products=orderflow_test_data["all_products"],
        store_id=orderflow_test_data["store_id"],
        spoke_id=orderflow_test_data["spoke_id"],
        stage_by_datetime=orderflow_test_data["stage_by_datetime"],
        service_window_start=orderflow_test_data["service_window_start"],
        route_id=orderflow_test_data["route_id"],
        ims=apis.ims_admin,
        oms=apis.oms,
    )

    def teardown():
        print(blue(f"\nClearing dispatch lane(s) if needed for order: {order_id}\n"))
        clear_dispatch_lane_order(apis.ims, order_id)

    request.addfinalizer(teardown)
    return order_id


@fixture(scope="function")
def login_gcp_project(retailer) -> str:
    credentials = ""

    if retailer in ["maf", "wings", "smu", "winter"]:
        credentials = login_to_gcp(interactive=False)
        print(red("\nYour local machine has logged into GCP Cloud"))

    return credentials


@fixture(scope="function")
def switch_gcp_project(retailer, cfg: Config):
    if retailer in ["maf", "wings", "smu", "winter"]:
        change_gcp_project(cfg.google_project_id)
        print(red("\nYour local machine has logged into GCP Cloud"))


@fixture(scope="function")
def get_users_id(auth_service: AuthService) -> str:
    """Return user id of the 'it@takeoff.com' user"""
    return auth_service.get_user_id("it@takeoff.com")


@fixture(scope="session")
def new_user(auth_service: AuthService, password: str) -> AuthServiceUser:
    return create_test_user(auth_service, password=password)


@fixture(scope="session")
def operator_user(cfg: Config, auth_service: AuthService, new_user) -> AuthServiceUser:
    auth_service.set_user_role(new_user.id, "operator", cfg.location_code_tom)
    try:
        yield new_user
    finally:
        delete_test_user(cfg.retailer, cfg.env, new_user.email, new_user.password)


@fixture(scope="session")
def operator_token(cfg: Config, operator_user):
    token = get_user_token(
        cfg.firebase_key,
        operator_user.email,
        operator_user.password,
    )
    return token


# User role is passed as a parameter directly from the test function
@fixture(scope="function")
def user_with_particular_role(
    cfg: Config, auth_service: AuthService, user_role, change_role, password
) -> AuthServiceUser:
    if change_role:
        user_role = change_role
    user = create_test_user(auth_service, password=password)
    auth_service.set_user_role(user.id, user_role, cfg.location_code_tom)
    print(
        cyan("\nRunning with test user:"),
        cyan(user.email),
        cyan("with role:" + user_role),
    )
    try:
        yield user
    finally:
        print(
            cyan("\nDeleting test user:"),
            cyan(user.email),
            cyan("with role:" + user_role),
        )
        delete_test_user(cfg.retailer, cfg.env, user.email, password)


def _stage_by_with_configured_waveplan(
    retailer: str,
    apis: InitializedApis,
    stage_by_in_minutes: int = 10,
    first_cutoff_minutes: int = 1,
    next_cutoff_minutes: int = 60 * 2,  # 2 hours
) -> MFCRelativeFutureTime:
    stage_by_details = get_retailer_future_event(apis.tsc, minutes=stage_by_in_minutes)
    wave_plan_response = apis.wave_planner.create_test_wave_plan(
        retailer,
        stage_by_details.location_code_tom,
        stage_by_details.timezone,
        first_cutoff_minutes=first_cutoff_minutes,
        next_cutoff_minutes=next_cutoff_minutes,
    )
    print(f"Wave Plan Applied: {wave_plan_response}")
    return stage_by_details


@fixture(scope="function")
def stage_by_in_10_minutes_1_min_cutoff(
    cfg: Config, apis: InitializedApis
) -> MFCRelativeFutureTime:
    """set stage by time now + 10 in retailer time zone - update waveplan"""
    return _stage_by_with_configured_waveplan(
        cfg.retailer, apis, stage_by_in_minutes=10, first_cutoff_minutes=1
    )


@fixture(scope="function")
def stage_by_in_1_minutes_1_min_cutoff(
    cfg: Config, apis: InitializedApis
) -> MFCRelativeFutureTime:
    """set stage by time now + 1 in retailer time zone - update waveplan"""
    return _stage_by_with_configured_waveplan(
        cfg.retailer, apis, stage_by_in_minutes=1, first_cutoff_minutes=1
    )


@pytest.fixture(autouse=True)
def consume_unassigned_orders(cfg: Config, apis: InitializedApis):
    """Prior tests may leave unfinished work that impacts future tests.
    Try to clear that before starting the test flow"""
    try:
        process_unassigned_orders(
            apis.pickerman_facade, user_id=cfg.user_id, email=cfg.user
        )
    except TypeError:
        pass
    except Exception as err:
        print(f"Excpetion clearing unassigned: {err}")


@fixture(scope="session")
def mobile(cfg) -> Mobile:
    return Mobile(cfg)


@fixture(scope="session")
def outbound_backend(cfg) -> OutboundBackend:
    return OutboundBackend(cfg)


@fixture(scope="session")
def IM(cfg) -> InventoryManager:
    return InventoryManager(cfg)


def pytest_bdd_apply_tag(tag, function):
    # Sets testrail marker for feature files marked with '@bdd_testrail={CaseID}'
    # This will cause pytest_collection_modifyitems function to pick up and
    # continue the processing (as normal) so the TestRail TC ID is
    # set in the resulting xml output
    if "bdd_testrail" in tag:
        test_id = str.split(tag, "=")[1]
        marker = pytest.mark.testrail(test_id)
        marker(function)
        return True
