from enum import StrEnum


class ScenarioId(StrEnum):
    S0 = "S0"
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"
    S4 = "S4"


class RiskLevel(StrEnum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    ORANGE = "ORANGE"
    RED = "RED"


class QAStatus(StrEnum):
    PASS = "PASS"
    WARNING = "WARNING"
    INVALID_FOR_RANKING = "INVALID_FOR_RANKING"
