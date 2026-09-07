from __future__ import annotations

import pandas as pd
import plotly.express as px

from ..domain.models import SimulationResult


def node_timeseries_figure(result: SimulationResult, node_id: str):
    series = result.timeseries.get("nodes", {}).get(node_id)
    if not series:
        return px.line(title="No node time series available")
    frame = pd.DataFrame(
        {
            "time": pd.to_datetime(result.timeseries["timestamps"]),
            "depth_m": series["depth_m"],
            "flooding_rate_cms": series["flooding_rate_cms"],
        }
    )
    return px.line(
        frame, x="time", y=["depth_m", "flooding_rate_cms"], title=f"Node {node_id} time series"
    )
