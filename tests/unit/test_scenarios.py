from pathlib import Path

import pytest

from sitedrainguard.scenario.definitions import default_scenarios
from sitedrainguard.scenario.mutations import ScenarioMutationError, apply_mutations, mutation_plan


def test_s0_has_no_mutation_and_s4_has_four() -> None:
    scenarios = {scenario.id.value: scenario for scenario in default_scenarios()}
    assert len(mutation_plan(scenarios["S0"])) == 0
    assert len(mutation_plan(scenarios["S4"])) == 4


def test_s4_mutation_plan_is_exact_union_of_s1_s2_s3() -> None:
    scenarios = {scenario.id.value: scenario for scenario in default_scenarios()}

    def normalized(scenario_id: str) -> set[tuple[object, ...]]:
        return {
            (
                item.section,
                item.object_id,
                item.row,
                item.token_index,
                item.before,
                item.after,
            )
            for item in mutation_plan(scenarios[scenario_id])
        }

    expected = normalized("S1") | normalized("S2") | normalized("S3")
    actual = normalized("S4")
    assert actual == expected
    assert actual - expected == set()
    assert expected - actual == set()


def test_controlled_mutation_changes_only_whitelisted_fields(
    tmp_path: Path, project_root: Path
) -> None:
    source = project_root / "data" / "demo_site" / "base_model.inp"
    destination = tmp_path / "mutated.inp"
    scenario = next(item for item in default_scenarios() if item.id.value == "S4")
    applied = apply_mutations(source, destination, scenario)
    text = destination.read_text(encoding="utf-8")
    assert len(applied) == 4
    assert "PUMP_ASSIST" in text
    assert (
        source.read_bytes() == (project_root / "data" / "demo_site" / "base_model.inp").read_bytes()
    )


def test_mutation_rejects_unexpected_base_value(tmp_path: Path, project_root: Path) -> None:
    source = project_root / "data" / "demo_site" / "base_model.inp"
    bad = tmp_path / "bad.inp"
    bad.write_text(
        source.read_text(encoding="utf-8").replace("PUMP_OFF", "OTHER_CURVE", 1), encoding="utf-8"
    )
    scenario = next(item for item in default_scenarios() if item.id.value == "S1")
    with pytest.raises(ScenarioMutationError, match="预期"):
        apply_mutations(bad, tmp_path / "out.inp", scenario)
