import pytest

from sitedrainguard.config import DEMO_DIR
from sitedrainguard.io.rainfall import load_builtin_rainfall
from sitedrainguard.scenario.definitions import default_scenarios
from sitedrainguard.simulation.runner import run_simulation


@pytest.mark.integration
def test_real_engine_smoke(service) -> None:
    rainfall = load_builtin_rainfall("moderate", DEMO_DIR)
    baseline = default_scenarios()[0]
    result = run_simulation(service.base_model, rainfall, baseline, service.metadata)
    assert result.engine_version == "5.2.4"
    assert result.system.flow_units == "CMS"
    assert result.system.system_units == "SI"
    assert result.hydraulic.total_flood_volume_m3 > 0
