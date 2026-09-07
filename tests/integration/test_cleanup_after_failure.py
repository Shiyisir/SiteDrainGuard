import pytest

from sitedrainguard.config import DEMO_DIR
from sitedrainguard.io.rainfall import load_builtin_rainfall
from sitedrainguard.scenario.definitions import default_scenarios
from sitedrainguard.simulation.errors import SimulationExecutionError
from sitedrainguard.simulation.runner import run_simulation


@pytest.mark.integration
def test_failure_does_not_poison_next_simulation(service) -> None:
    rainfall = load_builtin_rainfall("moderate", DEMO_DIR)
    with pytest.raises(SimulationExecutionError):
        run_simulation(
            service.base_model,
            rainfall,
            default_scenarios()[0],
            service.metadata,
            failure_injection=True,
        )
    result = run_simulation(service.base_model, rainfall, default_scenarios()[0], service.metadata)
    assert result.success
