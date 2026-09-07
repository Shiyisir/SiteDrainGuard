from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path

from pyswmm import Links, Nodes, Simulation, SystemStats

from ..config import ARTIFACTS_DIR
from ..domain.models import (
    HydraulicMetrics,
    LinkMetric,
    ModelMetadata,
    NodeMetric,
    RainfallEvent,
    ScenarioConfig,
    SimulationResult,
    SystemMetrics,
)
from ..io.rainfall import rainfall_csv_text, replace_timeseries
from ..scenario.mutations import apply_mutations, write_manifest
from ..validation.continuity import build_qa_result
from ..validation.rational_method import build_rational_check
from ..validation.risk import classify_risk
from .errors import SimulationExecutionError
from .lock import SIMULATION_LOCK


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _node_kind(metadata: ModelMetadata, node_id: str) -> str:
    return metadata.node_map.get(node_id).kind if node_id in metadata.node_map else "UNKNOWN"


def run_simulation(
    base_model: Path,
    rainfall: RainfallEvent,
    scenario: ScenarioConfig,
    metadata: ModelMetadata,
    output_dir: Path | None = None,
    failure_injection: bool = False,
) -> SimulationResult:
    """Run one scenario in a private model copy; never mutate the base INP."""
    run_id = f"{scenario.id.value.lower()}-{uuid.uuid4().hex[:10]}"
    started_at = datetime.now(UTC)
    base_hash_before = sha256_file(base_model)
    runtime_root = ARTIFACTS_DIR / ".runtime"
    runtime_root.mkdir(parents=True, exist_ok=True)
    temp_context = tempfile.TemporaryDirectory(prefix="sdg-", dir=runtime_root)
    engine_dir = Path(temp_context.name).resolve()
    final_dir = (output_dir / run_id).resolve() if output_dir is not None else None
    input_path = engine_dir / "model.inp"
    report_path = engine_dir / "model.rpt"
    output_path = engine_dir / "model.out"
    rainfall_path = engine_dir / "rainfall.csv"
    manifest_path = engine_dir / "manifest.json"
    shutil.copy2(base_model, input_path)
    rainfall_path.write_text(rainfall_csv_text(rainfall), encoding="utf-8")
    replace_timeseries(input_path, rainfall)
    mutations = apply_mutations(input_path, input_path, scenario)
    write_manifest(manifest_path, scenario, mutations)

    try:
        with SIMULATION_LOCK:
            with Simulation(str(input_path), str(report_path), str(output_path)) as sim:
                node_objects = list(Nodes(sim))
                link_objects = list(Links(sim))
                timestamps: list[str] = []
                node_series = {
                    node.nodeid: {"depth_m": [], "flooding_rate_cms": []} for node in node_objects
                }
                link_series = {
                    link.linkid: {"flow_cms": [], "depth_m": []} for link in link_objects
                }
                for _ in sim:
                    timestamps.append(sim.current_time.isoformat())
                    for node in node_objects:
                        node_series[node.nodeid]["depth_m"].append(float(node.depth))
                        node_series[node.nodeid]["flooding_rate_cms"].append(float(node.flooding))
                    for link in link_objects:
                        link_series[link.linkid]["flow_cms"].append(float(link.flow))
                        link_series[link.linkid]["depth_m"].append(float(link.depth))
                if failure_injection:
                    raise RuntimeError("intentional failure after engine start")
                stats = SystemStats(sim)
                runoff_stats = stats.runoff_stats
                routing_stats = stats.routing_stats
                engine_version = str(sim.engine_version)
                flow_units = str(sim.flow_units)
                system_units = str(sim.system_units)
                node_metrics: list[NodeMetric] = []
                for node in node_objects:
                    raw = node.statistics
                    full_depth = (
                        metadata.node_map.get(node.nodeid).full_depth_m
                        if node.nodeid in metadata.node_map
                        else 1.0
                    )
                    max_depth = float(raw["max_depth"])
                    depth_ratio = max_depth / full_depth if full_depth else 0.0
                    flooding_volume = float(raw["flooding_volume"])
                    flooding_duration = float(raw["flooding_duration"])
                    node_metrics.append(
                        NodeMetric(
                            node_id=node.nodeid,
                            kind=_node_kind(metadata, node.nodeid),
                            max_depth_m=max_depth,
                            full_depth_m=full_depth,
                            depth_ratio=depth_ratio,
                            flooding_volume_m3=flooding_volume,
                            flooding_duration_h=flooding_duration,
                            peak_flooding_rate_cms=float(raw["peak_flooding_rate"]),
                            max_ponded_volume_m3=float(raw["max_ponded_volume"]),
                            risk=classify_risk(depth_ratio, flooding_volume, flooding_duration),
                        )
                    )
                link_metrics = [
                    LinkMetric(
                        link_id=link.linkid,
                        kind="PUMP" if link.linkid.startswith("P") else "CONDUIT",
                        peak_flow_cms=max(series["flow_cms"], default=0.0),
                        max_depth_m=max(series["depth_m"], default=0.0),
                        flow_series_cms=series["flow_cms"],
                    )
                    for link, series in ((link, link_series[link.linkid]) for link in link_objects)
                ]
                total_flood = sum(node.flooding_volume_m3 for node in node_metrics)
                outfall_ids = {node.node_id for node in metadata.nodes if node.kind == "OUTFALL"}
                peak_outfall = max(
                    (
                        node.peak_flooding_rate_cms
                        for node in node_metrics
                        if node.node_id in outfall_ids
                    ),
                    default=0.0,
                )
                peak_outfall = max(
                    (
                        node_stats["peak_total_inflow"]
                        for node, node_stats in ((node, node.statistics) for node in node_objects)
                        if node.nodeid in outfall_ids
                    ),
                    default=peak_outfall,
                )
                system = SystemMetrics(
                    runoff_continuity_error_pct=float(runoff_stats["routing_error"]),
                    routing_continuity_error_pct=float(routing_stats["routing_error"]),
                    total_flooding_m3=total_flood,
                    peak_outfall_flow_cms=float(peak_outfall),
                    rainfall_total_mm=rainfall.total_depth_mm,
                    routing_outflow_m3=float(routing_stats["outflow"]),
                    engine_version=engine_version,
                    flow_units=flow_units,
                    system_units=system_units,
                )
                hydraulic = HydraulicMetrics(
                    total_flood_volume_m3=total_flood,
                    flooded_node_count=sum(
                        metric.flooding_volume_m3 > 0 for metric in node_metrics
                    ),
                    max_node_depth_m=max(
                        (metric.max_depth_m for metric in node_metrics), default=0.0
                    ),
                    max_depth_ratio=max(
                        (metric.depth_ratio for metric in node_metrics), default=0.0
                    ),
                    max_flood_duration_h=max(
                        (metric.flooding_duration_h for metric in node_metrics), default=0.0
                    ),
                    peak_outfall_flow_cms=float(peak_outfall),
                )
                qa = build_qa_result(
                    system.runoff_continuity_error_pct, system.routing_continuity_error_pct
                )
                rational = build_rational_check(metadata, rainfall, hydraulic.peak_outfall_flow_cms)
                timeseries = {"timestamps": timestamps, "nodes": node_series, "links": link_series}
                finished_at = datetime.now(UTC)
                result = SimulationResult(
                    run_id=run_id,
                    scenario_id=scenario.id,
                    scenario_name=scenario.name,
                    started_at=started_at,
                    finished_at=finished_at,
                    runtime_seconds=(finished_at - started_at).total_seconds(),
                    engine_version=engine_version,
                    node_metrics=node_metrics,
                    link_metrics=link_metrics,
                    system=system,
                    hydraulic=hydraulic,
                    qa=qa,
                    rational=rational,
                    mutation_manifest=mutations,
                    timeseries=timeseries,
                    warnings=list(qa.warnings) + ([rational.warning] if rational.warning else []),
                    artifact_dir=str(final_dir) if final_dir else None,
                )
        if final_dir is not None:
            final_dir.mkdir(parents=True, exist_ok=True)
            for artifact in engine_dir.iterdir():
                shutil.copy2(artifact, final_dir / artifact.name)
        return result
    except Exception as exc:
        raise SimulationExecutionError(
            f"{scenario.id.value} {scenario.name} 仿真失败: {exc}"
        ) from exc
    finally:
        temp_context.cleanup()
        if sha256_file(base_model) != base_hash_before:
            raise SimulationExecutionError("base_model.inp 在仿真过程中发生变化，已拒绝返回结果。")


def result_json(result: SimulationResult) -> str:
    return json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2)
