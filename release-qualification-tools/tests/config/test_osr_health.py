from pytest import mark
from src.api.takeoff.osr_replicator import OSRR
from src.config.config import Config


@mark.osr_health_test
@mark.testrail("633685")
def test_osrr_health_test(osrr: OSRR, cfg: Config):
    osr_health = osrr.get_osrr_health(cfg)
    assert osr_health["status"] == "pass"
