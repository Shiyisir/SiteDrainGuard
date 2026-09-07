import re

import pytest

from sitedrainguard.config import DEMO_DIR
from sitedrainguard.io.rainfall import load_builtin_rainfall
from sitedrainguard.scenario.definitions import default_scenarios
from sitedrainguard.simulation.runner import run_simulation


@pytest.mark.integration
def test_node_volume_and_duration_cross_check_report(service, tmp_path) -> None:
    result = run_simulation(
        service.base_model,
        load_builtin_rainfall("moderate", DEMO_DIR),
        default_scenarios()[0],
        service.metadata,
        output_dir=tmp_path,
    )
    report = (tmp_path / result.run_id / "model.rpt").read_text(encoding="utf-8")
    line = next(line for line in report.splitlines() if "Flooding Loss" in line)
    million_liters = float(re.findall(r"[-+]?\d+\.\d+", line)[-1])
    assert result.hydraulic.total_flood_volume_m3 == pytest.approx(million_liters * 1000, rel=0.01)
    assert max(node.flooding_duration_h for node in result.node_metrics) > 0
