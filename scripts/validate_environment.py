from __future__ import annotations

import importlib.metadata
import sys

from sitedrainguard.config import BASE_MODEL_PATH, COSTS_PATH, MODEL_METADATA_PATH
from sitedrainguard.io.rainfall import load_builtin_rainfall
from sitedrainguard.scenario.definitions import default_scenarios
from sitedrainguard.services.analysis_service import AnalysisService


def main() -> int:
    print(f"Python: {sys.version.split()[0]}")
    for distribution in ("pyswmm", "swmm-toolkit", "streamlit", "pandas", "pydantic"):
        print(f"{distribution}: {importlib.metadata.version(distribution)}")
    service = AnalysisService(BASE_MODEL_PATH, MODEL_METADATA_PATH, COSTS_PATH)
    rainfall = load_builtin_rainfall("moderate", BASE_MODEL_PATH.parent)
    baseline = next(scenario for scenario in default_scenarios() if scenario.id.value == "S0")
    result = service.run(rainfall, [baseline], include_sensitivity=False).baseline
    print(f"SWMM engine: {result.engine_version}")
    print(f"Flow units: {result.system.flow_units}; system units: {result.system.system_units}")
    print(f"Real smoke: PASS; flood={result.hydraulic.total_flood_volume_m3:.3f} m3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
