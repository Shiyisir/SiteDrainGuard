from __future__ import annotations

from ..domain.models import SensitivityPoint, SimulationResult


def sensitivity_point(scale: float, result: SimulationResult) -> SensitivityPoint:
    return SensitivityPoint(
        scale=scale,
        total_flood_volume_m3=result.hydraulic.total_flood_volume_m3,
        flooded_node_count=result.hydraulic.flooded_node_count,
        peak_outfall_flow_cms=result.hydraulic.peak_outfall_flow_cms,
        qa_status=result.qa.routing_status,
    )
