import pandas as pd
import pytest

from sitedrainguard.io.rainfall import RainfallValidationError, validate_rainfall_frame


def valid_frame() -> pd.DataFrame:
    return pd.DataFrame({"elapsed_min": [0, 5, 10], "intensity_mm_h": [0, 10, 0]})


def test_valid_rainfall_and_total_depth() -> None:
    event = validate_rainfall_frame(valid_frame())
    assert event.duration_min == 10
    assert event.total_depth_mm == pytest.approx(0.8333333)


@pytest.mark.parametrize(
    ("frame", "message"),
    [
        (pd.DataFrame({"time": [0, 5, 10], "intensity_mm_h": [0, 1, 0]}), "缺少"),
        (pd.DataFrame({"elapsed_min": [0, 5, 5], "intensity_mm_h": [0, 1, 0]}), "单调"),
        (pd.DataFrame({"elapsed_min": [0, 3, 10], "intensity_mm_h": [0, 1, 0]}), "恒定"),
        (pd.DataFrame({"elapsed_min": [0, 5, 10], "intensity_mm_h": [0, -1, 0]}), "负"),
        (pd.DataFrame({"elapsed_min": [0, 5, 10], "intensity_mm_h": [0, 501, 0]}), "500"),
    ],
)
def test_invalid_rainfall_is_readable(frame: pd.DataFrame, message: str) -> None:
    with pytest.raises(RainfallValidationError, match=message):
        validate_rainfall_frame(frame)


def test_rainfall_requires_three_rows() -> None:
    with pytest.raises(RainfallValidationError, match="3"):
        validate_rainfall_frame(pd.DataFrame({"elapsed_min": [0, 5], "intensity_mm_h": [0, 1]}))
