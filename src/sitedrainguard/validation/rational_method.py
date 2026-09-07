from __future__ import annotations

from ..domain.models import ModelMetadata, RainfallEvent, RationalCheck


def rational_peak_flow(runoff_coefficient: float, intensity_mm_h: float, area_ha: float) -> float:
    if not 0 <= runoff_coefficient <= 1:
        raise ValueError("runoff coefficient C must be between 0 and 1")
    if intensity_mm_h < 0 or area_ha <= 0:
        raise ValueError("rainfall intensity must be non-negative and area must be positive")
    return 0.00278 * runoff_coefficient * intensity_mm_h * area_ha


def build_rational_check(
    metadata: ModelMetadata, rainfall: RainfallEvent, swmm_peak_cms: float
) -> RationalCheck:
    rational = rational_peak_flow(
        metadata.runoff_coefficient, rainfall.peak_intensity_mm_h, metadata.area_ha
    )
    ratio = swmm_peak_cms / rational if rational else None
    warning = None
    if ratio is not None and (ratio < 0.25 or ratio > 4):
        warning = "SWMM 与 Rational Method 峰值差异较大，需要检查汇流、入渗、蓄泄和峰值时刻。"
    return RationalCheck(
        assumed_c=metadata.runoff_coefficient,
        rainfall_intensity_mm_h=rainfall.peak_intensity_mm_h,
        area_ha=metadata.area_ha,
        rational_peak_cms=rational,
        swmm_peak_cms=swmm_peak_cms,
        ratio=ratio,
        warning=warning,
    )
