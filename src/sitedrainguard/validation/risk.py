from ..config import (
    RISK_DEPTH_RATIO_ORANGE,
    RISK_DEPTH_RATIO_RED,
    RISK_DEPTH_RATIO_WARNING,
    RISK_FLOOD_DURATION_H,
)
from ..domain.enums import RiskLevel


def classify_risk(
    depth_ratio: float, flooding_volume_m3: float, flooding_duration_h: float
) -> RiskLevel:
    if (
        flooding_volume_m3 > 0 and flooding_duration_h >= RISK_FLOOD_DURATION_H
    ) or depth_ratio >= RISK_DEPTH_RATIO_RED:
        return RiskLevel.RED
    if flooding_volume_m3 > 0 or depth_ratio >= RISK_DEPTH_RATIO_ORANGE:
        return RiskLevel.ORANGE
    if depth_ratio >= RISK_DEPTH_RATIO_WARNING:
        return RiskLevel.YELLOW
    return RiskLevel.GREEN
