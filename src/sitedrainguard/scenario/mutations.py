from __future__ import annotations

import json
import shutil
from pathlib import Path

from ..domain.enums import ScenarioId
from ..domain.models import Mutation, ScenarioConfig


class ScenarioMutationError(ValueError):
    """Raised when a controlled scenario mutation does not match the base model."""


def mutation_plan(scenario: ScenarioConfig) -> list[Mutation]:
    mutations: list[Mutation] = []
    if scenario.id in {ScenarioId.S1, ScenarioId.S4}:
        mutations.append(
            Mutation(
                section="PUMPS",
                object_id="P01",
                field="Pump curve",
                before="PUMP_OFF",
                after="PUMP_ASSIST",
                token_index=3,
            )
        )
    if scenario.id in {ScenarioId.S2, ScenarioId.S4}:
        mutations.append(
            Mutation(
                section="XSECTIONS",
                object_id="C05",
                field="Geom1 diameter",
                before="0.20",
                after=f"{scenario.pipe_diameter_m:.2f}",
                token_index=2,
            )
        )
    if scenario.id in {ScenarioId.S3, ScenarioId.S4}:
        mutations.extend(
            [
                Mutation(
                    section="CURVES",
                    object_id="STORAGE_CURVE",
                    field="Y-Value at 0 m",
                    before="25.0",
                    after=f"{scenario.storage_area_start_m2:.1f}",
                    row=0,
                    token_index=3,
                ),
                Mutation(
                    section="CURVES",
                    object_id="STORAGE_CURVE",
                    field="Y-Value at 3 m",
                    before="125.0",
                    after=f"{scenario.storage_area_end_m2:.1f}",
                    row=1,
                    token_index=2,
                ),
            ]
        )
    return mutations


def apply_mutations(source: Path, destination: Path, scenario: ScenarioConfig) -> list[Mutation]:
    if source.resolve() != destination.resolve():
        shutil.copy2(source, destination)
    mutations = mutation_plan(scenario)
    if not mutations:
        return []
    lines = destination.read_text(encoding="utf-8").splitlines(keepends=True)
    applied: list[Mutation] = []
    for mutation in mutations:
        section_start = next(
            (i for i, line in enumerate(lines) if line.strip().upper() == f"[{mutation.section}]"),
            None,
        )
        if section_start is None:
            raise ScenarioMutationError(f"模型缺少 [{mutation.section}] section。")
        section_end = len(lines)
        for i in range(section_start + 1, len(lines)):
            if lines[i].strip().startswith("["):
                section_end = i
                break
        matches: list[tuple[int, list[str]]] = []
        for i in range(section_start + 1, section_end):
            stripped = lines[i].strip()
            if not stripped or stripped.startswith(";"):
                continue
            tokens = stripped.split()
            if tokens[0].lower() == mutation.object_id.lower():
                matches.append((i, tokens))
        if mutation.row >= len(matches):
            raise ScenarioMutationError(
                f"{mutation.section}/{mutation.object_id} row {mutation.row} 不存在。"
            )
        line_index, tokens = matches[mutation.row]
        if mutation.token_index >= len(tokens):
            raise ScenarioMutationError(
                f"{mutation.section}/{mutation.object_id} token index 越界。"
            )
        actual = tokens[mutation.token_index]
        if actual != mutation.before:
            raise ScenarioMutationError(
                f"{mutation.section}/{mutation.object_id} 预期 {mutation.before}，实际 {actual}；拒绝静默改错对象。"
            )
        tokens[mutation.token_index] = mutation.after
        newline = "\n" if lines[line_index].endswith("\n") else ""
        lines[line_index] = "     ".join(tokens) + newline
        applied.append(mutation)
    destination.write_text("".join(lines), encoding="utf-8", newline="")
    return applied


def write_manifest(path: Path, scenario: ScenarioConfig, mutations: list[Mutation]) -> None:
    path.write_text(
        json.dumps(
            {
                "scenario": scenario.id.value,
                "mutations": [mutation.model_dump() for mutation in mutations],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
