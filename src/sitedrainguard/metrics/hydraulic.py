from ..domain.models import HydraulicMetrics, NodeMetric


def summarize_nodes(nodes: list[NodeMetric], peak_outfall_flow_cms: float) -> HydraulicMetrics:
    return HydraulicMetrics(
        total_flood_volume_m3=sum(node.flooding_volume_m3 for node in nodes),
        flooded_node_count=sum(node.flooding_volume_m3 > 0 for node in nodes),
        max_node_depth_m=max((node.max_depth_m for node in nodes), default=0.0),
        max_depth_ratio=max((node.depth_ratio for node in nodes), default=0.0),
        max_flood_duration_h=max((node.flooding_duration_h for node in nodes), default=0.0),
        peak_outfall_flow_cms=peak_outfall_flow_cms,
    )
