from dataclasses import dataclass

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


@dataclass
class InitializedApis:
    auth_service: AuthService
    bifrost: Bifrost
    decanting: Decanting
    distiller: Distiller
    fft: FFTracker
    im: InventoryManager
    ims_admin: IMS
    ims: IMS
    isps: ISPS
    mobile: Mobile
    oms: OMS
    ops_api: OpsApi
    osrr: OSRR  # osr emulator
    outbound_backend: OutboundBackend
    pickerman_facade: PickermanFacade
    rint: RInt
    tsc: TSC
    wave_planner: WavePlanner
