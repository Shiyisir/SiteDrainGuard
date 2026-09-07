from __future__ import annotations

from ..domain.enums import ScenarioId
from ..domain.models import CostAssumptions, SimulationResult


def apply_economics(
    results: list[SimulationResult], costs: CostAssumptions
) -> list[SimulationResult]:
    baseline = next(result for result in results if result.scenario_id == ScenarioId.S0)
    baseline_flood = baseline.hydraulic.total_flood_volume_m3
    enriched: list[SimulationResult] = []
    for result in results:
        cost = costs.cost_for(result.scenario_id)
        reduction = baseline_flood - result.hydraulic.total_flood_volume_m3
        reduction_pct = reduction / baseline_flood * 100 if baseline_flood else None
        unit_cost = cost / reduction if reduction > 0 else None
        enriched.append(
            result.model_copy(
                update={
                    "estimated_cost": cost,
                    "flood_volume_reduction_m3": reduction,
                    "flood_reduction_pct": reduction_pct,
                    "cost_per_avoided_flood_volume": unit_cost,
                }
            )
        )
    return enriched
