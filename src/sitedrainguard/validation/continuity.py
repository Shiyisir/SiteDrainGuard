from __future__ import annotations

from ..config import CONTINUITY_PASS_PCT, CONTINUITY_WARNING_PCT
from ..domain.enums import QAStatus
from ..domain.models import QAResult


def continuity_status(error_pct: float) -> QAStatus:
    absolute = abs(error_pct)
    if absolute <= CONTINUITY_PASS_PCT:
        return QAStatus.PASS
    if absolute <= CONTINUITY_WARNING_PCT:
        return QAStatus.WARNING
    return QAStatus.INVALID_FOR_RANKING


def build_qa_result(runoff_error_pct: float, routing_error_pct: float) -> QAResult:
    runoff_status = continuity_status(runoff_error_pct)
    routing_status = continuity_status(routing_error_pct)
    warnings: list[str] = []
    if runoff_status != QAStatus.PASS:
        warnings.append(f"runoff continuity {runoff_error_pct:.3f}% is {runoff_status.value}")
    if routing_status != QAStatus.PASS:
        warnings.append(f"routing continuity {routing_error_pct:.3f}% is {routing_status.value}")
    return QAResult(
        runoff_status=runoff_status,
        routing_status=routing_status,
        ranking_valid=QAStatus.INVALID_FOR_RANKING not in {runoff_status, routing_status},
        warnings=warnings,
    )
