from __future__ import annotations

import pandas as pd
import plotly.express as px

from ..domain.models import SimulationResult


def comparison_frame(results: list[SimulationResult]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Scenario": result.scenario_id.value,
                "Name": result.scenario_name,
                "Flood volume (m³)": result.hydraulic.total_flood_volume_m3,
                "Reduction (%)": result.flood_reduction_pct,
                "Flooded nodes": result.hydraulic.flooded_node_count,
                "Peak outfall (m³/s)": result.hydraulic.peak_outfall_flow_cms,
                "Cost (CNY assumption)": result.estimated_cost,
                "Cost / avoided m³": result.cost_per_avoided_flood_volume,
                "QA": result.qa.routing_status.value,
            }
            for result in results
        ]
    )


def flood_volume_figure(results: list[SimulationResult]):
    frame = comparison_frame(results)
    return px.bar(
        frame,
        x="Scenario",
        y="Flood volume (m³)",
        color="QA",
        hover_name="Name",
        title="Flood volume by scenario",
    )


def cost_effect_figure(results: list[SimulationResult]):
    frame = comparison_frame(results)
    return px.scatter(
        frame,
        x="Reduction (%)",
        y="Cost (CNY assumption)",
        size="Flood volume (m³)",
        color="QA",
        text="Scenario",
        hover_name="Name",
        title="Cost assumption vs flood reduction",
    )
