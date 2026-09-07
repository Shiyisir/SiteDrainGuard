import pytest

from sitedrainguard.domain.enums import QAStatus, RiskLevel, ScenarioId
from sitedrainguard.domain.models import CostAssumptions
from sitedrainguard.validation.continuity import continuity_status
from sitedrainguard.validation.rational_method import rational_peak_flow
from sitedrainguard.validation.risk import classify_risk


def test_risk_and_continuity_thresholds() -> None:
    assert classify_risk(1.0, 0, 0) == RiskLevel.RED
    assert classify_risk(0.5, 0, 0) == RiskLevel.GREEN
    assert classify_risk(0.4, 2, 0.1) == RiskLevel.ORANGE
    assert continuity_status(2.0) == QAStatus.PASS
    assert continuity_status(3.0) == QAStatus.WARNING
    assert continuity_status(6.0) == QAStatus.INVALID_FOR_RANKING


def test_rational_method_known_calculation() -> None:
    assert rational_peak_flow(0.8, 100, 10) == pytest.approx(2.224)
    with pytest.raises(ValueError):
        rational_peak_flow(1.2, 100, 10)


def test_cost_assumption_combination() -> None:
    costs = CostAssumptions()
    assert costs.cost_for(ScenarioId.S0) == 0
    assert costs.cost_for(ScenarioId.S4) == pytest.approx(
        costs.cost_for(ScenarioId.S1)
        + costs.cost_for(ScenarioId.S2)
        + costs.cost_for(ScenarioId.S3)
    )
