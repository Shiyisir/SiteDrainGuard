from ..domain.enums import ScenarioId
from ..domain.models import ScenarioConfig


def default_scenarios() -> list[ScenarioConfig]:
    return [
        ScenarioConfig(
            id=ScenarioId.S0, name="Baseline", description="当前 synthetic 临时排水系统。"
        ),
        ScenarioConfig(
            id=ScenarioId.S1,
            name="PumpAssist",
            description="启用预置临时泵 P01 的高能力曲线。",
            pump_curve="PUMP_ASSIST",
            cost_keys=("pump",),
        ),
        ScenarioConfig(
            id=ScenarioId.S2,
            name="PipeUpsize",
            description="将瓶颈管段 C05 的直径由 0.20 m 扩大到 0.45 m。",
            pipe_diameter_m=0.45,
            cost_keys=("pipe",),
        ),
        ScenarioConfig(
            id=ScenarioId.S3,
            name="StorageExpand",
            description="扩大 ST01 临时调蓄/集水空间曲线。",
            storage_area_start_m2=60.0,
            storage_area_end_m2=300.0,
            cost_keys=("storage",),
        ),
        ScenarioConfig(
            id=ScenarioId.S4,
            name="Hybrid",
            description="组合 PumpAssist、PipeUpsize 与 StorageExpand。",
            pump_curve="PUMP_ASSIST",
            pipe_diameter_m=0.45,
            storage_area_start_m2=60.0,
            storage_area_end_m2=300.0,
            cost_keys=("pump", "pipe", "storage"),
        ),
    ]
