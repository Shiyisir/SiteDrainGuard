from __future__ import annotations

import plotly.graph_objects as go

from ..domain.models import ModelMetadata, SimulationResult

RISK_COLORS = {"GREEN": "#2ca25f", "YELLOW": "#fdae61", "ORANGE": "#f46d43", "RED": "#d73027"}
RISK_SYMBOLS = {"GREEN": "circle", "YELLOW": "triangle-up", "ORANGE": "diamond", "RED": "x"}


def network_figure(metadata: ModelMetadata, result: SimulationResult) -> go.Figure:
    node_map = {node.node_id: node for node in metadata.nodes}
    metrics = {metric.node_id: metric for metric in result.node_metrics}
    figure = go.Figure()
    for link in metadata.links:
        start = node_map.get(link.from_node)
        end = node_map.get(link.to_node)
        if not start or not end:
            continue
        figure.add_trace(
            go.Scatter(
                x=[start.x, end.x],
                y=[start.y, end.y],
                mode="lines",
                line={"color": "#94a3b8", "width": 2},
                hoverinfo="text",
                text=f"{link.link_id}: {link.from_node} → {link.to_node}",
                showlegend=False,
            )
        )
    for kind, symbol in {"JUNCTION": "circle", "STORAGE": "square", "OUTFALL": "star"}.items():
        selected = [node for node in metadata.nodes if node.kind == kind]
        if not selected:
            continue
        figure.add_trace(
            go.Scatter(
                x=[node.x for node in selected],
                y=[node.y for node in selected],
                mode="markers+text",
                text=[node.node_id for node in selected],
                textposition="top center",
                name=kind,
                marker={
                    "size": 12,
                    "symbol": [
                        RISK_SYMBOLS.get(metrics.get(node.node_id, {}).risk.value, symbol)
                        if node.node_id in metrics
                        else symbol
                        for node in selected
                    ],
                    "color": [
                        RISK_COLORS.get(metrics[node.node_id].risk.value, "#64748b")
                        if node.node_id in metrics
                        else "#64748b"
                        for node in selected
                    ],
                    "line": {"color": "#0f172a", "width": 1},
                },
                customdata=[
                    [
                        metrics[node.node_id].max_depth_m,
                        metrics[node.node_id].depth_ratio,
                        metrics[node.node_id].flooding_volume_m3,
                        metrics[node.node_id].flooding_duration_h,
                        metrics[node.node_id].risk.value,
                    ]
                    if node.node_id in metrics
                    else [0, 0, 0, 0, "UNKNOWN"]
                    for node in selected
                ],
                hovertemplate=(
                    "node=%{text}<br>max depth=%{customdata[0]:.3f} m<br>depth ratio=%{customdata[1]:.2f}"
                    "<br>flood volume=%{customdata[2]:.2f} m³<br>flood duration=%{customdata[3]:.2f} h"
                    "<br>risk=%{customdata[4]}<extra></extra>"
                ),
            )
        )
    figure.update_layout(
        height=520, margin={"l": 20, "r": 20, "t": 20, "b": 20}, legend_title="Node type"
    )
    figure.update_yaxes(scaleanchor="x", scaleratio=1, title="local y")
    figure.update_xaxes(title="local x")
    return figure
