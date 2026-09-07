from __future__ import annotations

import argparse
import json
import sys

import pandas as pd

from sitedrainguard.config import ARTIFACTS_DIR, BASE_MODEL_PATH, COSTS_PATH, MODEL_METADATA_PATH
from sitedrainguard.services.analysis_service import AnalysisService


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the real-engine SiteDrainGuard demo batch.")
    parser.add_argument("--rainfall", choices=["moderate", "heavy"], default="moderate")
    args = parser.parse_args()
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    service = AnalysisService(BASE_MODEL_PATH, MODEL_METADATA_PATH, COSTS_PATH)
    bundle = service.run_builtin(
        args.rainfall, include_sensitivity=True, output_dir=ARTIFACTS_DIR / "runs"
    )
    records = [
        result.model_dump(mode="json", exclude={"timeseries", "node_metrics", "link_metrics"})
        for result in bundle.scenarios
    ]
    (ARTIFACTS_DIR / "demo_results.json").write_text(
        json.dumps(
            {
                "rainfall": bundle.rainfall.model_dump(mode="json"),
                "scenarios": records,
                "sensitivity": [point.model_dump() for point in bundle.sensitivity],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    pd.DataFrame(records).to_csv(ARTIFACTS_DIR / "demo_results.csv", index=False)
    print(
        f"Rainfall: {bundle.rainfall.name}, total={bundle.rainfall.total_depth_mm:.2f} mm, peak={bundle.rainfall.peak_intensity_mm_h:g} mm/h"
    )
    all_valid = True
    for result in bundle.scenarios:
        print(
            f"{result.scenario_id.value} {result.scenario_name}: PASS "
            f"flood={result.hydraulic.total_flood_volume_m3:.2f} m3, "
            f"reduction={result.flood_reduction_pct if result.flood_reduction_pct is not None else 'N/A'}, "
            f"routing={result.system.routing_continuity_error_pct:.3f}%, "
            f"qa={result.qa.routing_status.value}"
        )
        all_valid = all_valid and result.qa.ranking_valid
    print(f"Artifacts: {ARTIFACTS_DIR}")
    return 0 if all_valid else 1


if __name__ == "__main__":
    sys.exit(main())
