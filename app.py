from __future__ import annotations

import pandas as pd
import streamlit as st

from sitedrainguard.config import BASE_MODEL_PATH, COSTS_PATH, DEMO_DIR, MODEL_METADATA_PATH
from sitedrainguard.domain.models import CostAssumptions
from sitedrainguard.io.rainfall import (
    RainfallValidationError,
    load_builtin_rainfall,
    validate_rainfall_frame,
)
from sitedrainguard.metrics.economics import apply_economics
from sitedrainguard.scenario.definitions import default_scenarios
from sitedrainguard.services.analysis_service import AnalysisService
from sitedrainguard.simulation.errors import SimulationExecutionError
from sitedrainguard.visualization.comparison import (
    comparison_frame,
    cost_effect_figure,
    flood_volume_figure,
)
from sitedrainguard.visualization.network import network_figure
from sitedrainguard.visualization.timeseries import node_timeseries_figure

DISCLAIMER = (
    "SiteDrainGuard 为学习与方案决策支持原型。内置场地、降雨、成本及设施参数均为合成演示数据，"
    "结果不能替代率定工程设计、当地规范、专业审核、实测地形或现场监测。"
)


def _hydraulic_signature(rainfall, selected_ids: list[str]) -> tuple[object, ...]:
    """Fingerprint only inputs that require a fresh SWMM run; cost edits are excluded."""
    rainfall_points = tuple(
        (round(point.elapsed_min, 8), round(point.intensity_mm_h, 8)) for point in rainfall.points
    )
    return (rainfall_points, tuple(sorted(selected_ids)))


@st.cache_resource
def get_service() -> AnalysisService:
    return AnalysisService(BASE_MODEL_PATH, MODEL_METADATA_PATH, COSTS_PATH)


def main() -> None:
    st.set_page_config(page_title="SiteDrainGuard", page_icon="🌧️", layout="wide")
    st.title("SiteDrainGuard")
    st.caption(
        "Synthetic construction-site stormwater risk and temporary drainage scenario analysis"
    )
    st.info(DISCLAIMER)

    service = get_service()
    scenarios = default_scenarios()
    with st.sidebar:
        st.header("1. Rainfall")
        rainfall_kind = st.radio("Built-in event", ["moderate", "heavy"], index=1)
        uploaded = st.file_uploader(
            "Or upload a validated CSV", type=["csv"], help="Columns: elapsed_min, intensity_mm_h"
        )
        if uploaded is not None:
            if uploaded.size > 2 * 1024 * 1024:
                st.error("CSV 文件不能超过 2 MB。")
                rainfall = load_builtin_rainfall(rainfall_kind, DEMO_DIR)
            else:
                try:
                    rainfall = validate_rainfall_frame(pd.read_csv(uploaded), source="uploaded CSV")
                except (RainfallValidationError, pd.errors.ParserError) as exc:
                    st.error(str(exc))
                    rainfall = load_builtin_rainfall(rainfall_kind, DEMO_DIR)
        else:
            rainfall = load_builtin_rainfall(rainfall_kind, DEMO_DIR)
        st.caption(
            f"{rainfall.name}: {rainfall.duration_min:g} min · {rainfall.total_depth_mm:.2f} mm total · peak {rainfall.peak_intensity_mm_h:g} mm/h"
        )

        st.header("2. Scenarios")
        selected_ids = st.multiselect(
            "Compare",
            [scenario.id.value for scenario in scenarios],
            default=[scenario.id.value for scenario in scenarios],
        )
        if "S0" not in selected_ids:
            selected_ids = ["S0", *selected_ids]
            st.caption("S0 Baseline is always included for reduction metrics.")

        st.header("3. Cost assumptions")
        st.caption("演示成本假设；只影响 economics，不改变已完成的 hydraulic simulation。")
        pump_cost = st.number_input(
            "Pump fixed cost (CNY)",
            min_value=0.0,
            value=float(service.costs.pump_fixed_cost),
            step=1000.0,
        )
        pipe_unit = st.number_input(
            "Pipe unit cost (CNY/m)",
            min_value=0.0,
            value=float(service.costs.pipe_unit_cost_per_m),
            step=100.0,
        )
        storage_unit = st.number_input(
            "Storage unit cost (CNY/m³)",
            min_value=0.0,
            value=float(service.costs.storage_unit_cost_per_m3),
            step=50.0,
        )
        current_costs = CostAssumptions(
            pump_fixed_cost=pump_cost,
            pipe_unit_cost_per_m=pipe_unit,
            pipe_affected_length_m=service.costs.pipe_affected_length_m,
            storage_unit_cost_per_m3=storage_unit,
            added_storage_volume_m3=service.costs.added_storage_volume_m3,
        )
        run_clicked = st.button("Run analysis", type="primary", use_container_width=True)

    if run_clicked:
        selected = [scenario for scenario in scenarios if scenario.id.value in selected_ids]
        with st.status("Running real SWMM scenarios sequentially…", expanded=True) as status:
            try:
                bundle = service.run(rainfall, selected, include_sensitivity=True)
                bundle = bundle.model_copy(
                    update={
                        "costs": current_costs,
                        "scenarios": apply_economics(bundle.scenarios, current_costs),
                    }
                )
                st.session_state["bundle"] = bundle
                st.session_state["hydraulic_signature"] = _hydraulic_signature(
                    rainfall, selected_ids
                )
                status.update(label="Analysis complete", state="complete")
            except (SimulationExecutionError, RainfallValidationError, ValueError) as exc:
                status.update(label="Analysis failed", state="error")
                st.error(f"无法完成仿真：{exc}")

    bundle = st.session_state.get("bundle")
    if bundle is None:
        st.warning("请选择降雨和方案后点击 Run analysis。页面不会因普通控件变化自动重跑 SWMM。")
        return
    current_signature = _hydraulic_signature(rainfall, selected_ids)
    if st.session_state.get("hydraulic_signature") != current_signature:
        st.warning(
            "降雨或方案选择已变化，当前 hydraulic 结果已过期。请再次点击 Run analysis；"
            "成本参数变化除外，因为它只重算 economics。"
        )
        return
    bundle = bundle.model_copy(
        update={
            "costs": current_costs,
            "scenarios": apply_economics(bundle.scenarios, current_costs),
        }
    )
    st.session_state["bundle"] = bundle
    result = bundle.baseline
    st.subheader("A · Site network")
    st.plotly_chart(network_figure(bundle.metadata, result), use_container_width=True)

    st.subheader("B · Baseline KPI")
    kpi = st.columns(5)
    kpi[0].metric("Total flood volume", f"{result.hydraulic.total_flood_volume_m3:,.1f} m³")
    kpi[1].metric("Flooded nodes", result.hydraulic.flooded_node_count)
    kpi[2].metric("Max depth", f"{result.hydraulic.max_node_depth_m:.2f} m")
    kpi[3].metric("Peak outfall flow", f"{result.hydraulic.peak_outfall_flow_cms:.3f} m³/s")
    kpi[4].metric("Routing QA", result.qa.routing_status.value)

    st.subheader("C · Scenario comparison")
    st.dataframe(comparison_frame(bundle.scenarios), use_container_width=True, hide_index=True)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(flood_volume_figure(bundle.scenarios), use_container_width=True)
    with c2:
        st.plotly_chart(cost_effect_figure(bundle.scenarios), use_container_width=True)

    st.subheader("D · Time series")
    node_id = st.selectbox("Node", [metric.node_id for metric in result.node_metrics])
    st.plotly_chart(node_timeseries_figure(result, node_id), use_container_width=True)

    st.subheader("E · Engineering QA")
    qa_rows = [
        {
            "Scenario": item.scenario_id.value,
            "Runoff continuity (%)": item.system.runoff_continuity_error_pct,
            "Routing continuity (%)": item.system.routing_continuity_error_pct,
            "Rational Qp (m³/s)": item.rational.rational_peak_cms,
            "SWMM peak (m³/s)": item.rational.swmm_peak_cms,
            "Rational ratio": item.rational.ratio,
            "Ranking valid": item.qa.ranking_valid,
        }
        for item in bundle.scenarios
    ]
    st.dataframe(pd.DataFrame(qa_rows), use_container_width=True, hide_index=True)
    if bundle.sensitivity:
        st.write("Rainfall sensitivity (S0, one-at-a-time intensity scale)")
        st.dataframe(
            pd.DataFrame([point.model_dump() for point in bundle.sensitivity]),
            use_container_width=True,
            hide_index=True,
        )
    st.caption("风险等级是本项目用于方案对比的启发式规则，不对应法规或设计规范分级。")

    with st.expander("F · Method & limitations"):
        st.markdown(
            "- All bundled inputs are synthetic.\n"
            "- The engine is EPA SWMM 5.2.4 via PySWMM; scenarios run sequentially.\n"
            "- Continuity thresholds are internal QA gates, not universal engineering standards.\n"
            "- Rational Method is a quantity sanity check, not a model calibration.\n"
            "- No field calibration, survey DEM, live monitoring, code-compliance judgement or production multi-user concurrency."
        )


if __name__ == "__main__":
    main()
