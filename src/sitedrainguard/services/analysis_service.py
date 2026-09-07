from __future__ import annotations

from pathlib import Path

import yaml

from ..domain.enums import ScenarioId
from ..domain.models import AnalysisBundle, CostAssumptions, ScenarioConfig, SensitivityPoint
from ..io.model_metadata import load_model_metadata
from ..io.rainfall import load_builtin_rainfall
from ..metrics.economics import apply_economics
from ..scenario.definitions import default_scenarios
from ..simulation.runner import run_simulation
from ..validation.model_checks import require_base_model
from ..validation.sensitivity import sensitivity_point


class AnalysisService:
    """Thin application layer; all simulations are deliberately sequential."""

    def __init__(self, base_model: Path, metadata_path: Path, costs_path: Path | None = None):
        require_base_model(base_model)
        self.base_model = base_model
        self.metadata = load_model_metadata(base_model, metadata_path)
        self.costs = self._load_costs(costs_path) if costs_path else CostAssumptions()

    @staticmethod
    def _load_costs(path: Path) -> CostAssumptions:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return CostAssumptions(
            currency=data.get("currency", "CNY"),
            assumption_only=data.get("assumption_only", True),
            pump_fixed_cost=data.get("pump_fixed_cost", 12000),
            pipe_unit_cost_per_m=data.get("pipe_unit_cost_per_m", 800),
            pipe_affected_length_m=data.get("pipe_affected_length_m", 70),
            storage_unit_cost_per_m3=data.get("storage_unit_cost_per_m3", 300),
            added_storage_volume_m3=data.get("added_storage_volume_m3", 200),
        )

    def run(
        self,
        rainfall,
        scenarios: list[ScenarioConfig] | None = None,
        include_sensitivity: bool = True,
        output_dir: Path | None = None,
    ) -> AnalysisBundle:
        scenario_list = scenarios or default_scenarios()
        if not any(scenario.id == ScenarioId.S0 for scenario in scenario_list):
            scenario_list = [default_scenarios()[0], *scenario_list]
        deduplicated: list[ScenarioConfig] = []
        seen: set[ScenarioId] = set()
        for scenario in scenario_list:
            if scenario.id not in seen:
                deduplicated.append(scenario)
                seen.add(scenario.id)
        results = [
            run_simulation(
                self.base_model,
                rainfall,
                scenario,
                self.metadata,
                output_dir=output_dir,
            )
            for scenario in deduplicated
        ]
        results = apply_economics(results, self.costs)
        sensitivity: list[SensitivityPoint] = []
        if include_sensitivity:
            baseline_config = next(
                scenario for scenario in deduplicated if scenario.id == ScenarioId.S0
            )
            baseline = next(result for result in results if result.scenario_id == ScenarioId.S0)
            sensitivity.append(sensitivity_point(1.0, baseline))
            for scale in (0.8, 1.2):
                scaled_result = run_simulation(
                    self.base_model,
                    rainfall.scaled(scale),
                    baseline_config,
                    self.metadata,
                    output_dir=output_dir,
                )
                sensitivity.append(sensitivity_point(scale, scaled_result))
            sensitivity.sort(key=lambda item: item.scale)
        return AnalysisBundle(
            rainfall=rainfall,
            scenarios=results,
            sensitivity=sensitivity,
            metadata=self.metadata,
            costs=self.costs,
        )

    def run_builtin(
        self, kind: str = "heavy", include_sensitivity: bool = True, output_dir: Path | None = None
    ) -> AnalysisBundle:
        from ..config import DEMO_DIR

        return self.run(
            load_builtin_rainfall(kind, DEMO_DIR),
            include_sensitivity=include_sensitivity,
            output_dir=output_dir,
        )
