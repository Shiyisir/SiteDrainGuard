from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .enums import QAStatus, RiskLevel, ScenarioId


class RainfallPoint(BaseModel):
    elapsed_min: float = Field(ge=0)
    intensity_mm_h: float = Field(ge=0)


class RainfallEvent(BaseModel):
    name: str
    points: list[RainfallPoint] = Field(min_length=3)
    source: str = "synthetic"

    @property
    def duration_min(self) -> float:
        return self.points[-1].elapsed_min

    @property
    def total_depth_mm(self) -> float:
        return sum(
            point.intensity_mm_h * (next_point.elapsed_min - point.elapsed_min) / 60
            for point, next_point in zip(self.points, self.points[1:], strict=False)
        )

    @property
    def peak_intensity_mm_h(self) -> float:
        return max(point.intensity_mm_h for point in self.points)

    def scaled(self, factor: float, name: str | None = None) -> RainfallEvent:
        return RainfallEvent(
            name=name or f"{self.name} x {factor:g}",
            points=[
                RainfallPoint(
                    elapsed_min=point.elapsed_min,
                    intensity_mm_h=point.intensity_mm_h * factor,
                )
                for point in self.points
            ],
            source=f"{self.source}; scale={factor:g}",
        )


class ScenarioConfig(BaseModel):
    id: ScenarioId
    name: str
    description: str
    pump_curve: str = "PUMP_OFF"
    pipe_diameter_m: float = 0.20
    storage_area_start_m2: float = 25.0
    storage_area_end_m2: float = 125.0
    cost_keys: tuple[str, ...] = ()


class CostAssumptions(BaseModel):
    currency: str = "CNY"
    assumption_only: bool = True
    pump_fixed_cost: float = Field(default=12000, ge=0)
    pipe_unit_cost_per_m: float = Field(default=800, ge=0)
    pipe_affected_length_m: float = Field(default=70, ge=0)
    storage_unit_cost_per_m3: float = Field(default=300, ge=0)
    added_storage_volume_m3: float = Field(default=200, ge=0)

    def cost_for(self, scenario: ScenarioId) -> float:
        if scenario == ScenarioId.S1:
            return self.pump_fixed_cost
        if scenario == ScenarioId.S2:
            return self.pipe_unit_cost_per_m * self.pipe_affected_length_m
        if scenario == ScenarioId.S3:
            return self.storage_unit_cost_per_m3 * self.added_storage_volume_m3
        if scenario == ScenarioId.S4:
            return (
                self.cost_for(ScenarioId.S1)
                + self.cost_for(ScenarioId.S2)
                + self.cost_for(ScenarioId.S3)
            )
        return 0.0


class Mutation(BaseModel):
    section: str
    object_id: str
    field: str
    before: str
    after: str
    row: int = 0
    token_index: int


class NodeMetadata(BaseModel):
    node_id: str
    kind: str
    x: float = 0
    y: float = 0
    elevation_m: float = 0
    full_depth_m: float = 1.0


class LinkMetadata(BaseModel):
    link_id: str
    from_node: str
    to_node: str
    kind: str = "CONDUIT"
    length_m: float = 0


class ModelMetadata(BaseModel):
    site_name: str
    synthetic: bool = True
    area_ha: float
    runoff_coefficient: float
    nodes: list[NodeMetadata]
    links: list[LinkMetadata]

    @property
    def node_map(self) -> dict[str, NodeMetadata]:
        return {node.node_id: node for node in self.nodes}


class NodeMetric(BaseModel):
    node_id: str
    kind: str
    max_depth_m: float
    full_depth_m: float
    depth_ratio: float
    flooding_volume_m3: float
    flooding_duration_h: float
    peak_flooding_rate_cms: float
    max_ponded_volume_m3: float
    risk: RiskLevel


class LinkMetric(BaseModel):
    link_id: str
    kind: str
    peak_flow_cms: float
    max_depth_m: float
    flow_series_cms: list[float] = Field(default_factory=list)


class SystemMetrics(BaseModel):
    runoff_continuity_error_pct: float
    routing_continuity_error_pct: float
    total_flooding_m3: float
    peak_outfall_flow_cms: float
    rainfall_total_mm: float
    runoff_total_m3: float | None = None
    routing_outflow_m3: float | None = None
    engine_version: str
    flow_units: str
    system_units: str


class QAResult(BaseModel):
    runoff_status: QAStatus
    routing_status: QAStatus
    ranking_valid: bool
    warnings: list[str] = Field(default_factory=list)


class RationalCheck(BaseModel):
    assumed_c: float
    rainfall_intensity_mm_h: float
    area_ha: float
    rational_peak_cms: float
    swmm_peak_cms: float
    ratio: float | None
    warning: str | None = None


class HydraulicMetrics(BaseModel):
    total_flood_volume_m3: float
    flooded_node_count: int
    max_node_depth_m: float
    max_depth_ratio: float
    max_flood_duration_h: float
    peak_outfall_flow_cms: float


class SimulationResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    run_id: str
    scenario_id: ScenarioId
    scenario_name: str
    success: bool = True
    started_at: datetime
    finished_at: datetime
    runtime_seconds: float
    engine_version: str
    node_metrics: list[NodeMetric]
    link_metrics: list[LinkMetric]
    system: SystemMetrics
    hydraulic: HydraulicMetrics
    qa: QAResult
    rational: RationalCheck
    mutation_manifest: list[Mutation] = Field(default_factory=list)
    timeseries: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    estimated_cost: float = 0.0
    flood_volume_reduction_m3: float | None = None
    flood_reduction_pct: float | None = None
    cost_per_avoided_flood_volume: float | None = None
    artifact_dir: str | None = None


class SensitivityPoint(BaseModel):
    scale: float
    total_flood_volume_m3: float
    flooded_node_count: int
    peak_outfall_flow_cms: float
    qa_status: QAStatus


class AnalysisBundle(BaseModel):
    rainfall: RainfallEvent
    scenarios: list[SimulationResult]
    sensitivity: list[SensitivityPoint] = Field(default_factory=list)
    metadata: ModelMetadata
    costs: CostAssumptions

    @property
    def baseline(self) -> SimulationResult:
        return next(result for result in self.scenarios if result.scenario_id == ScenarioId.S0)
