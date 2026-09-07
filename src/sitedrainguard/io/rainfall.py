from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..domain.models import RainfallEvent, RainfallPoint


class RainfallValidationError(ValueError):
    """Raised when a rainfall CSV cannot safely drive the model."""


def validate_rainfall_frame(frame: pd.DataFrame, source: str = "uploaded") -> RainfallEvent:
    required = ["elapsed_min", "intensity_mm_h"]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise RainfallValidationError(f"缺少必需列: {', '.join(missing)}")
    if len(frame) < 3:
        raise RainfallValidationError("降雨数据至少需要 3 行。")
    values = frame[required].apply(pd.to_numeric, errors="coerce")
    if values.isna().any().any():
        raise RainfallValidationError(
            "elapsed_min 和 intensity_mm_h 必须全部是有效数字，不能含空值。"
        )
    times = values["elapsed_min"].tolist()
    intensities = values["intensity_mm_h"].tolist()
    if times[0] < 0 or any(b <= a for a, b in zip(times, times[1:], strict=False)):
        raise RainfallValidationError("elapsed_min 必须从 0 开始或更大，并严格单调递增。")
    steps = [round(b - a, 8) for a, b in zip(times, times[1:], strict=False)]
    if len(set(steps)) != 1:
        raise RainfallValidationError("降雨时间步必须保持恒定。")
    if not 1 <= steps[0] <= 60:
        raise RainfallValidationError("P0 只接受 1–60 分钟的恒定时间步。")
    if any(value < 0 for value in intensities):
        raise RainfallValidationError("降雨强度不能为负数。")
    if any(value > 500 for value in intensities):
        raise RainfallValidationError("降雨强度超过 500 mm/h 的安全输入上限。")
    if times[-1] > 24 * 60:
        raise RainfallValidationError("降雨历时不能超过 24 小时。")
    return RainfallEvent(
        name=Path(source).stem if source != "uploaded" else "uploaded",
        source=source,
        points=[
            RainfallPoint(elapsed_min=float(t), intensity_mm_h=float(i))
            for t, i in zip(times, intensities, strict=True)
        ],
    )


def load_rainfall_csv(path: Path, name: str | None = None) -> RainfallEvent:
    try:
        frame = pd.read_csv(path)
    except (OSError, pd.errors.ParserError) as exc:
        raise RainfallValidationError(f"无法读取降雨 CSV: {exc}") from exc
    event = validate_rainfall_frame(frame, source=str(path))
    if name:
        event = event.model_copy(update={"name": name})
    return event


def load_builtin_rainfall(kind: str, demo_dir: Path) -> RainfallEvent:
    if kind not in {"moderate", "heavy"}:
        raise RainfallValidationError("内置降雨只支持 moderate 或 heavy。")
    return load_rainfall_csv(demo_dir / f"rainfall_{kind}.csv", name=kind)


def _clock_time(elapsed_min: float) -> str:
    total_seconds = round(elapsed_min * 60)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if seconds:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{hours:02d}:{minutes:02d}"


def replace_timeseries(inp_path: Path, rainfall: RainfallEvent, target: str = "RAIN_DEMO") -> None:
    """Replace only one whitelisted SWMM timeseries while preserving other sections."""
    lines = inp_path.read_text(encoding="utf-8").splitlines(keepends=True)
    start = next(
        (i for i, line in enumerate(lines) if line.strip().upper() == "[TIMESERIES]"), None
    )
    if start is None:
        raise RainfallValidationError("模型缺少 [TIMESERIES] section。")
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].strip().startswith("["):
            end = i
            break
    target_lower = target.lower()
    old_indices = [
        i
        for i in range(start + 1, end)
        if lines[i].strip()
        and not lines[i].lstrip().startswith(";")
        and lines[i].split()[0].lower() == target_lower
    ]
    insert_at = old_indices[0] if old_indices else start + 1
    generated = [
        f"{target} {_clock_time(point.elapsed_min)} {point.intensity_mm_h:.10g}\n"
        for point in rainfall.points
    ]
    kept = [
        line for i, line in enumerate(lines[start + 1 : end], start + 1) if i not in old_indices
    ]
    relative_insert = sum(1 for i in range(start + 1, insert_at) if i not in old_indices)
    lines[start + 1 : end] = kept[:relative_insert] + generated + kept[relative_insert:]
    inp_path.write_text("".join(lines), encoding="utf-8", newline="")


def rainfall_csv_text(event: RainfallEvent) -> str:
    rows = [("elapsed_min", "intensity_mm_h")]
    rows.extend((f"{point.elapsed_min:g}", f"{point.intensity_mm_h:g}") for point in event.points)
    return "\n".join(",".join(row) for row in rows) + "\n"
