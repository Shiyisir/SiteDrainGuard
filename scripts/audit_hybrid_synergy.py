from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


class HybridAuditError(RuntimeError):
    """Raised when the retained real-engine artifacts violate scenario isolation."""


def _scenario_records(results_path: Path) -> dict[str, dict[str, Any]]:
    payload = json.loads(results_path.read_text(encoding="utf-8"))
    records = {record["scenario_id"]: record for record in payload.get("scenarios", [])}
    required = {"S0", "S1", "S2", "S3", "S4"}
    missing = required - records.keys()
    if missing:
        raise HybridAuditError(f"demo results missing scenarios: {sorted(missing)}")
    return records


def _normalized_mutations(record: dict[str, Any]) -> set[tuple[Any, ...]]:
    return {
        (
            item["section"],
            item["object_id"],
            int(item.get("row", 0)),
            int(item["token_index"]),
            str(item["before"]),
            str(item["after"]),
        )
        for item in record.get("mutation_manifest", [])
    }


def _inp_token_map(path: Path) -> dict[tuple[str, str, int], list[str]]:
    section = ""
    occurrence: defaultdict[tuple[str, str], int] = defaultdict(int)
    rows: dict[tuple[str, str, int], list[str]] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith(";"):
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            section = stripped[1:-1].upper()
            continue
        if not section:
            continue
        tokens = stripped.split()
        object_id = tokens[0]
        row = occurrence[(section, object_id.lower())]
        occurrence[(section, object_id.lower())] += 1
        rows[(section, object_id, row)] = tokens
    return rows


def _token_changes(
    baseline: dict[tuple[str, str, int], list[str]],
    candidate: dict[tuple[str, str, int], list[str]],
) -> set[tuple[Any, ...]]:
    if baseline.keys() != candidate.keys():
        missing = sorted(set(baseline) - set(candidate))
        extra = sorted(set(candidate) - set(baseline))
        raise HybridAuditError(f"INP row set changed; missing={missing}, extra={extra}")
    changes: set[tuple[Any, ...]] = set()
    for key, before_tokens in baseline.items():
        after_tokens = candidate[key]
        if len(before_tokens) != len(after_tokens):
            raise HybridAuditError(
                f"token count changed for {key}: {before_tokens} -> {after_tokens}"
            )
        section, object_id, row = key
        for token_index, (before, after) in enumerate(
            zip(before_tokens, after_tokens, strict=True)
        ):
            if before != after:
                changes.add((section, object_id, row, token_index, before, after))
    return changes


def _report_row(report_path: Path, section_title: str, row_id: str) -> list[str]:
    lines = report_path.read_text(encoding="utf-8").splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if section_title in line)
    except StopIteration as exc:
        raise HybridAuditError(f"{report_path} missing {section_title}") from exc
    for line in lines[start + 1 :]:
        stripped = line.strip()
        if stripped.startswith(row_id + " "):
            return stripped.split()
        if stripped and set(stripped) == {"*"} and section_title not in stripped:
            # Keep scanning: the first star line belongs to the current section header.
            continue
    raise HybridAuditError(f"{report_path} missing {row_id} in {section_title}")


def _extract_mechanism(report_path: Path) -> dict[str, float]:
    j05 = _report_row(report_path, "Node Flooding Summary", "J05")
    storage = _report_row(report_path, "Storage Volume Summary", "ST01")
    outfall = _report_row(report_path, "Outfall Loading Summary", "O01")
    c05 = _report_row(report_path, "Link Flow Summary", "C05")
    p01_link = _report_row(report_path, "Link Flow Summary", "P01")
    pump = _report_row(report_path, "Pumping Summary", "P01")
    return {
        "j05_flood_hours": float(j05[1]),
        "j05_peak_flood_cms": float(j05[2]),
        "j05_flood_volume_m3": float(j05[5]) * 1000.0,
        "storage_max_volume_m3": float(storage[5]) * 1000.0,
        "storage_max_outflow_cms": float(storage[9]),
        "outfall_max_flow_cms": float(outfall[3]),
        "outfall_total_volume_m3": float(outfall[4]) * 1000.0,
        "c05_max_flow_cms": float(c05[2]),
        "p01_max_flow_cms": float(p01_link[2]),
        "pump_total_volume_m3": float(pump[6]) * 1000.0,
    }


def audit(results_path: Path, runs_dir: Path) -> dict[str, Any]:
    records = _scenario_records(results_path)
    if _normalized_mutations(records["S0"]):
        raise HybridAuditError("S0 unexpectedly contains mutations")

    individual_union = set().union(
        _normalized_mutations(records["S1"]),
        _normalized_mutations(records["S2"]),
        _normalized_mutations(records["S3"]),
    )
    hybrid_manifest = _normalized_mutations(records["S4"])
    if hybrid_manifest != individual_union:
        raise HybridAuditError(
            "S4 manifest is not exactly S1 ∪ S2 ∪ S3; "
            f"extra={sorted(hybrid_manifest - individual_union)}, "
            f"missing={sorted(individual_union - hybrid_manifest)}"
        )

    run_paths: dict[str, Path] = {}
    for scenario_id, record in records.items():
        run_path = runs_dir / record["run_id"]
        if not run_path.is_dir():
            raise HybridAuditError(f"missing run artifact directory: {run_path}")
        run_paths[scenario_id] = run_path

    rainfall_bytes = (run_paths["S0"] / "rainfall.csv").read_bytes()
    for scenario_id in ("S1", "S2", "S3", "S4"):
        if (run_paths[scenario_id] / "rainfall.csv").read_bytes() != rainfall_bytes:
            raise HybridAuditError(f"rainfall differs between S0 and {scenario_id}")

    baseline_tokens = _inp_token_map(run_paths["S0"] / "model.inp")
    semantic_diff: dict[str, list[tuple[Any, ...]]] = {"S0": []}
    for scenario_id in ("S1", "S2", "S3", "S4"):
        actual = _token_changes(
            baseline_tokens,
            _inp_token_map(run_paths[scenario_id] / "model.inp"),
        )
        expected = _normalized_mutations(records[scenario_id])
        if actual != expected:
            raise HybridAuditError(
                f"{scenario_id} INP changes do not match manifest; "
                f"extra={sorted(actual - expected)}, missing={sorted(expected - actual)}"
            )
        semantic_diff[scenario_id] = sorted(actual)

    mechanism = {
        scenario_id: _extract_mechanism(run_path / "model.rpt")
        for scenario_id, run_path in run_paths.items()
    }
    flood = {
        scenario_id: float(records[scenario_id]["hydraulic"]["total_flood_volume_m3"])
        for scenario_id in records
    }
    reductions = {scenario_id: flood["S0"] - flood[scenario_id] for scenario_id in records}
    sum_individual = reductions["S1"] + reductions["S2"] + reductions["S3"]
    hybrid_reduction = reductions["S4"]
    interaction_excess = hybrid_reduction - sum_individual
    j05_reduction = mechanism["S0"]["j05_flood_volume_m3"] - mechanism["S4"]["j05_flood_volume_m3"]

    return {
        "status": "PASS",
        "manifest_union": {
            "s4_equals_s1_union_s2_union_s3": True,
            "extra_mutations": 0,
            "missing_mutations": 0,
        },
        "rainfall_identical_across_scenarios": True,
        "semantic_inp_changes_match_manifest": True,
        "semantic_changes": semantic_diff,
        "flood_volume_m3": flood,
        "flood_reduction_m3": reductions,
        "sum_individual_reduction_m3": sum_individual,
        "hybrid_reduction_m3": hybrid_reduction,
        "interaction_excess_m3": interaction_excess,
        "j05_reduction_m3": j05_reduction,
        "j05_share_of_hybrid_reduction_pct": (
            j05_reduction / hybrid_reduction * 100.0 if hybrid_reduction > 0 else None
        ),
        "mechanism": mechanism,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit S4 isolation and explain the observed hybrid bottleneck interaction."
    )
    parser.add_argument(
        "--results", type=Path, default=Path("artifacts/demo_results.json"), help="Batch JSON path"
    )
    parser.add_argument(
        "--runs-dir", type=Path, default=Path("artifacts/runs"), help="Retained run artifacts"
    )
    parser.add_argument(
        "--output", type=Path, default=Path("artifacts/hybrid_audit.json"), help="Audit JSON output"
    )
    args = parser.parse_args()
    try:
        result = audit(args.results, args.runs_dir)
    except (OSError, json.JSONDecodeError, HybridAuditError, ValueError) as exc:
        print(f"Hybrid audit: FAIL — {exc}", file=sys.stderr)
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Hybrid audit: PASS")
    print("S4 = S1 ∪ S2 ∪ S3; extra mutations=0; missing mutations=0")
    print(
        "Flood reduction: "
        f"individual sum={result['sum_individual_reduction_m3']:.2f} m3, "
        f"S4={result['hybrid_reduction_m3']:.2f} m3, "
        f"observed interaction excess={result['interaction_excess_m3']:.2f} m3"
    )
    print(
        "J05 explains "
        f"{result['j05_share_of_hybrid_reduction_pct']:.1f}% of the S0→S4 flood-volume reduction."
    )
    print(f"Evidence: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
