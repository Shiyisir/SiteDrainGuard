import hashlib

import pytest

from sitedrainguard.config import DEMO_DIR
from sitedrainguard.io.rainfall import load_builtin_rainfall
from sitedrainguard.scenario.definitions import default_scenarios


@pytest.mark.integration
def test_s0_to_s4_real_runs_and_base_is_unchanged(service, tmp_path) -> None:
    before = hashlib.sha256(service.base_model.read_bytes()).hexdigest()
    bundle = service.run(
        load_builtin_rainfall("heavy", DEMO_DIR),
        default_scenarios(),
        include_sensitivity=False,
        output_dir=tmp_path,
    )
    assert [result.scenario_id.value for result in bundle.scenarios] == [
        "S0",
        "S1",
        "S2",
        "S3",
        "S4",
    ]
    assert all(result.success for result in bundle.scenarios)
    assert all(result.engine_version == "5.2.4" for result in bundle.scenarios)
    assert bundle.scenarios[-1].mutation_manifest
    assert hashlib.sha256(service.base_model.read_bytes()).hexdigest() == before
