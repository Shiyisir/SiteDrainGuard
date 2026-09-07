from pathlib import Path

import pandas as pd

from sitedrainguard.io.rainfall import replace_timeseries, validate_rainfall_frame


def test_timeseries_replacement_preserves_other_sections(
    tmp_path: Path, project_root: Path
) -> None:
    model = tmp_path / "model.inp"
    model.write_text(
        (project_root / "data" / "demo_site" / "base_model.inp").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    event = validate_rainfall_frame(
        pd.DataFrame({"elapsed_min": [0, 5, 10, 15], "intensity_mm_h": [0, 20, 40, 0]})
    )
    replace_timeseries(model, event)
    text = model.read_text(encoding="utf-8")
    assert "RAIN_DEMO 00:10 40" in text
    assert "[JUNCTIONS]" in text
    assert sum(line.startswith("RAIN_DEMO ") for line in text.splitlines()) == 4
