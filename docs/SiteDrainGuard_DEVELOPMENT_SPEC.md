# SiteDrainGuard 开发规格与 Agent 自审计手册

> **项目定位**：面向施工场地/小型园区的暴雨积水风险与临时排水方案评估原型
> **目标用户**：施工技术人员、排水/水利工程学生、方案比选人员
> **作品定位**：个人开源工程项目 / 决策支持原型，不是生产级工程设计软件
> **核心技术**：Python + EPA SWMM + PySWMM + Streamlit + Plotly
> **文档版本**：v1.0
> **基准日期**：2026-09-07
> **开发优先级**：先做一个可以真实运行、可验证、可复现、可讲清楚的 v0.1，再扩展功能
> **硬性原则**：不得伪造真实工程数据、真实企业应用、真实项目效果或未经验证的工程结论

---

## 0. 本文档怎么使用

本文档既是 PRD，也是技术设计、测试计划、科学计算 QA、发布清单和 Agent 执行协议。

给 Codex / coding agent 后，Agent 应：

1. 先完整阅读本文档。
2. 检查仓库当前状态，不覆盖用户已有有效代码。
3. 建立需求追踪表。
4. 按 Phase 0 → Phase 8 顺序开发。
5. 每个阶段完成后执行自审计。
6. **必须运行真实 SWMM/PySWMM 仿真**，不能只用 mock 伪造“通过”。
7. 遇到依赖/API 差异时，以当前官方文档和实际运行结果为准，并记录偏差。
8. 最终生成 `AUDIT_REPORT.md`，明确哪些完成、哪些未完成、哪些结论不能写进简历。
9. P0 功能未完成时不得用占位结果、随机结果或硬编码结果假装完成。

---

# 1. 产品目标

## 1.1 核心问题

施工阶段永久排水系统可能尚未形成，临时道路、基坑周边、材料场、办公生活区等在暴雨条件下可能出现积水、节点溢流、排水能力不足。

SiteDrainGuard 需要回答：

- 当前临时排水系统在给定降雨过程下是否存在风险？
- 哪些节点/区域最先出现高水位或溢流？
- 风险持续多久、总溢流量多大？
- 如果只能采取有限工程措施，应优先：
  - 启用/增加临时泵？
  - 扩大关键排水管？
  - 扩大临时调蓄/集水空间？
  - 采用组合方案？
- 在用户输入的**假设成本**下，哪个方案的单位减灾效益更高？
- 模型计算结果是否至少通过基本的连续性检查、数量级校核和敏感性检查？

## 1.2 项目价值

项目不是“SWMM 网页壳”，而应体现完整链路：

`工程场景 -> 数据校验 -> SWMM 模型 -> 情景生成 -> 批量仿真 -> 风险指标 -> 方案比选 -> 成本效益 -> 科学校核 -> 可视化 -> 可复现报告`

## 1.3 成功标准

v0.1 成功的最低标准：

- 新用户 clone 后可在 10 分钟内按 README 跑起来。
- Demo 使用明确标注为 synthetic 的场地和降雨数据。
- 至少 1 个基准场景 + 4 个工程方案可以真实运行。
- 结果来自真实 SWMM 计算，不是硬编码。
- 页面能展示：
  - 排水网络图；
  - 风险节点；
  - 关键 KPI；
  - 方案对比；
  - 成本效益；
  - 模型 QA。
- 自动化测试存在并通过。
- CI 存在并通过。
- 有至少一个真实 SWMM smoke/integration test。
- README 能让招聘面试官在 2 分钟内理解：
  - 为什么做；
  - 怎么做；
  - 你做了什么；
  - 模型边界是什么。
- `AUDIT_REPORT.md` 明确列出已验证与未验证事项。

---

# 2. 明确不做什么

以下内容 **不是 v0.1 目标**：

- 用户登录、账号系统、权限系统。
- 数据库。
- 微服务。
- Kubernetes。
- LLM 聊天机器人。
- 工地视频/目标检测。
- BIM。
- 真实 GIS 在线地图底图。
- 实时 IoT 接入。
- 自动获取气象站数据。
- 根据经纬度自动生成真实设计暴雨。
- 自动生成施工图。
- 自动给出“工程设计合格/不合格”法律或规范结论。
- 生产级多用户并发。
- 高可用部署。
- 复杂全局优化算法。
- 机器学习预测。
- 真实造价数据库。
- 真实企业项目数据。

任何 P1/P2 扩展都不得阻塞 P0。

---

# 3. 科学与工程边界

## 3.1 必须在 UI 和 README 中声明

至少包含：

> SiteDrainGuard is an educational and decision-support prototype. The bundled site, rainfall, cost and facility data are synthetic unless explicitly stated otherwise. Results are not a substitute for calibrated engineering design, local codes, professional review, survey data, or site monitoring.

中文版：

> SiteDrainGuard 为学习与方案决策支持原型。仓库内置场地、降雨、成本及设施参数均为合成演示数据（除非另有明确说明），结果不能替代经过率定的工程设计、当地规范、专业审核、实测地形及现场监测。

## 3.2 禁止的表述

不得出现：

- “已用于中建三局项目”
- “已服务某央企”
- “真实施工现场验证”
- “工程精度达到 XX%”
- “满足国家规范”
- “可直接用于工程设计”
- “智能设计系统”
- “自动替代工程师”
- 任何没有证据的“节省 XX 万元”“减少 XX%事故”

## 3.3 可以使用的表述

- synthetic demonstration
- proof of concept
- decision-support prototype
- scenario comparison
- hydrologic-hydraulic simulation
- internal QA threshold
- user-supplied assumption
- educational validation
- sensitivity analysis

---

# 4. 推荐技术栈与版本策略

## 4.1 基准环境

优先：

- Python 3.11
- PySWMM 2.1.x
- SWMM engine 5.2.4（通过 PySWMM extra 或当前官方兼容方式）
- Streamlit
- pandas
- numpy
- Plotly
- Pydantic
- PyYAML
- pytest
- pytest-cov
- Ruff

可选：

- NetworkX：网络拓扑辅助
- filelock：如 Agent 判断需要跨线程/跨进程保护
- mypy：P1，不得为类型覆盖率牺牲开发速度

## 4.2 依赖原则

1. **不要盲目追最新版本。**
2. 以实际可安装、可运行的组合为准。
3. 先在 Python 3.11 验证。
4. 如果 Python 3.12 也通过，可加入 CI。
5. 在 `pyproject.toml` 中固定关键主版本或使用兼容范围。
6. 生成 lock file（Agent 根据选择的包管理器决定，如 `uv.lock`）。
7. 在 `docs/environment.md` 记录最终实际测试版本。
8. 不能只写“理论兼容”；必须运行验证。

推荐项目管理方式：

- 优先 `pyproject.toml`
- 可以使用 `uv`，但 README 同时给出标准 `python -m venv` + `pip` 路径，避免工具锁定。

## 4.3 PySWMM 特别约束

PySWMM / SWMM 引擎不是可以随意并发创建多个 `Simulation` 对象的普通纯 Python 计算库。

开发时必须：

- 每次仿真使用 context manager，确保 close。
- 场景按顺序执行。
- **禁止同一 Python 进程内并行跑多个 Simulation。**
- 不使用 Streamlit 的并行 fragment 来执行 SWMM。
- UI 的“批量场景运行”必须串行。
- 如有多个 Streamlit session 同时触发计算，至少在本地单进程范围内使用全局锁防止重入。
- 文档明确：v0.1 不承诺生产级多用户并发。
- 测试必须包含“异常后可以继续启动下一次 Simulation”的资源释放检查。

---

# 5. 总体架构

建议采用“薄 UI、厚 domain/service”：

```text
Streamlit UI
    |
    v
Application Services
    |
    +--> Input Validation
    +--> Rainfall Builder
    +--> Scenario Builder
    +--> Simulation Runner
    +--> Metrics Calculator
    +--> Economics
    +--> Validation / QA
    |
    v
PySWMM / SWMM Engine
```

严格禁止把核心逻辑全部写进 `app.py`。

## 5.1 推荐目录

```text
SiteDrainGuard/
├── app.py
├── pyproject.toml
├── uv.lock                      # 如果使用 uv
├── README.md
├── LICENSE
├── CITATION.cff
├── THIRD_PARTY_NOTICES.md
├── AGENTS.md
├── AUDIT_REPORT.md
├── CHANGELOG.md
├── .gitignore
├── .python-version
├── .streamlit/
│   └── config.toml
├── .github/
│   ├── workflows/
│   │   └── ci.yml
│   ├── ISSUE_TEMPLATE/
│   └── pull_request_template.md
├── data/
│   └── demo_site/
│       ├── base_model.inp
│       ├── site_metadata.yaml
│       ├── rainfall_moderate.csv
│       ├── rainfall_heavy.csv
│       └── costs.yaml
├── src/
│   └── sitedrainguard/
│       ├── __init__.py
│       ├── config.py
│       ├── domain/
│       │   ├── models.py
│       │   ├── enums.py
│       │   └── units.py
│       ├── io/
│       │   ├── rainfall.py
│       │   ├── model_metadata.py
│       │   └── inp_timeseries.py
│       ├── scenario/
│       │   ├── definitions.py
│       │   ├── builder.py
│       │   └── mutations.py
│       ├── simulation/
│       │   ├── runner.py
│       │   ├── extractor.py
│       │   ├── lock.py
│       │   └── errors.py
│       ├── metrics/
│       │   ├── hydraulic.py
│       │   ├── risk.py
│       │   └── economics.py
│       ├── validation/
│       │   ├── continuity.py
│       │   ├── rational_method.py
│       │   ├── sensitivity.py
│       │   └── model_checks.py
│       ├── visualization/
│       │   ├── network.py
│       │   ├── timeseries.py
│       │   └── comparison.py
│       └── services/
│           └── analysis_service.py
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── fixtures/
│   └── conftest.py
├── docs/
│   ├── architecture.md
│   ├── methodology.md
│   ├── validation.md
│   ├── environment.md
│   ├── data_dictionary.md
│   ├── limitations.md
│   ├── development_log.md
│   └── resume_claims.md
└── scripts/
    ├── run_demo_batch.py
    ├── validate_environment.py
    └── export_demo_results.py
```

如 Agent 有更简洁的结构可调整，但必须保留模块边界。

---

# 6. Demo 工程模型

## 6.1 数据性质

所有内置数据均为合成数据。

`data/demo_site/README.md` 必须说明：

- 场地为虚构施工场地；
- 坐标是局部平面坐标；
- 高程、管径、坡度、面积、成本均用于演示；
- 不对应真实项目；
- 参数只用于展示工作流，不代表任何规范推荐值。

## 6.2 模型规模

目标规模：

- 总汇水面积：约 8–15 ha
- 子汇水区：8 个左右
- Junction：8–12
- Storage：1
- Outfall：1
- Conduit：8–15
- Pump：1
- Raingage：1
- 排水系统形成清晰上游 → 下游路径
- 至少有一个基准暴雨场景会产生可观察风险
- 但不能让模型数值完全失稳

推荐对象命名：

```text
Subcatchments: S01 ... S08
Junctions:     J01 ... J08
Storage:       ST01
Outfall:       O01
Conduits:      C01 ... C09
Pump:          P01
Raingage:      RG01
```

## 6.3 单位

优先使用 SI：

- Flow: CMS
- length: m
- area: ha（按 SWMM INP 对应单位）
- rainfall intensity: mm/h
- rainfall depth: mm
- time: min / h
- volume: m³（仅在确认 SWMM/PySWMM 返回单位后标注）

**Agent 必须核实 PySWMM 对 node statistics、routing statistics 中体积和时长的单位。未经核实不得在 UI 直接写 `m³` 或 `min`。**

## 6.4 路由

推荐：

- `FLOW_ROUTING DYNWAVE`
- 合理 routing step
- 合理 report step
- 使用同一基准设置比较所有场景

Agent 必须通过模型运行检查：

- 无致命错误；
- continuity error 可接受；
- 无大量数值警告；
- 方案修改不导致时间步崩溃；
- 所有 scenario 使用同一降雨、时段及非目标参数。

---

# 7. 降雨输入

## 7.1 P0 输入方式

必须支持两种：

### A. 内置 synthetic rainfall

至少：

- `moderate`
- `heavy`

CSV 建议格式：

```csv
elapsed_min,intensity_mm_h
0,0
5,12
10,24
15,48
20,72
25,48
30,24
35,12
40,0
```

上面只是格式示意，Agent 应生成更平滑、能驱动模型产生合理差异的 synthetic event。

### B. 用户 CSV

固定 schema：

```csv
elapsed_min,intensity_mm_h
0,0
5,10
10,30
...
```

校验：

- 两列必须存在。
- 均为数值。
- `elapsed_min >= 0`
- 必须单调递增。
- 时间步必须为常数。
- P0 仅允许 1–60 min 的时间步。
- `intensity_mm_h >= 0`
- 设置一个合理上限防止误输入，如 500 mm/h；超过时拒绝或强警告。
- 至少 3 行。
- 总历时不宜超过 24h；超过时警告/拒绝，避免 UI 阻塞。
- 空文件、NaN、重复时间必须给用户可读错误。
- 不接受公式、宏、可执行内容。

## 7.2 INP 时间序列写入

推荐方案：

- 保持 `base_model.inp` 为只读源。
- 每次运行复制到临时工作目录。
- 用受控函数替换目标 `[TIMESERIES]` 中 `RAIN_DEMO` 数据。
- 禁止对用户任意文本做 eval。
- 修改后重新解析/运行验证。
- 单元测试覆盖：
  - section 存在；
  - section 缺失；
  - 目标 timeseries 存在；
  - 目标缺失；
  - 保留其他 timeseries；
  - 不破坏下一个 section；
  - 换行格式；
  - UTF-8；
  - 生成文件可被 SWMM 读取。

如果当前 PySWMM API 提供更安全的现成方式，可采用，但必须在 `docs/architecture.md` 说明原因。

---

# 8. Scenario Engine

## 8.1 P0 场景

固定 5 个：

### S0 — Baseline

当前 synthetic 临时排水系统。

### S1 — PumpAssist

启用预置的临时泵 P01。

要求：

- Pump 和 curve 可以预置在 base INP。
- 基准状态为 OFF 或等效不可用。
- S1 只改变泵状态或等效控制参数。
- 不得在运行过程中手工注入“假流量”来伪造泵作用。

### S2 — PipeUpsize

将关键瓶颈管段（如 C05）管径从基准值调整为扩大值。

要求：

- 修改 `[XSECTIONS]` 对应参数。
- 修改值写入 scenario config。
- UI 显示 baseline 和 proposed diameter。
- 必须验证扩大管径后目标对象确实变化。

### S3 — StorageExpand

将 ST01 的有效调蓄能力从基准值扩大。

推荐通过修改 storage 的面积/曲线参数实现。

要求：

- 明确叫“扩大临时调蓄/集水空间”，不要说“新增真实调蓄池设计”。
- 必须保证只有目标参数变化。

### S4 — Hybrid

组合：

- PumpAssist
- PipeUpsize
- StorageExpand

用于展示多措施联合效果。

## 8.2 场景修改方式

优先使用 PySWMM `SimulationPreConfig` 对已有对象做 token-based pre-simulation modification。

原因：

- 避免写一个完整 INP parser；
- 便于追踪哪些参数被修改；
- 可用测试确认。

若某参数无法安全修改：

- 实现最小范围 INP section modifier；
- 只能允许白名单 section/object/field；
- 必须单元测试；
- 不允许通用“字符串替换全部”。

## 8.3 场景数据模型

示例：

```python
class ScenarioConfig(BaseModel):
    id: str
    name: str
    description: str
    enabled_pump: bool = False
    pipe_diameter_m: float | None = None
    storage_area_m2: float | None = None
    cost_items: dict[str, float] = {}
```

实际字段可以调整。

## 8.4 场景不变量

所有场景必须：

- 使用同一 base model。
- 使用同一 rainfall event。
- 使用同一 simulation time。
- 使用同一 infiltration/routing settings。
- 除 scenario 声明的参数外不得改变其它参数。
- 输出一个 mutation manifest。

示例：

```json
{
  "scenario": "S2",
  "mutations": [
    {
      "section": "XSECTIONS",
      "object_id": "C05",
      "field": "Geom1",
      "before": 0.45,
      "after": 0.70
    }
  ]
}
```

UI 或结果详情应能查看该 manifest。

---

# 9. Simulation Runner

## 9.1 输入

`SimulationRequest`：

- base model path
- rainfall
- scenario
- run id
- optional output directory

## 9.2 输出

`SimulationResult` 至少包含：

```text
run_id
scenario_id
success
started_at
finished_at
runtime_seconds
engine/version metadata
node_metrics
link_metrics
system_metrics
timeseries
mutation_manifest
warnings
qa_flags
```

## 9.3 工作目录

每个 run：

```text
/tmp/sitedrainguard/<run_id>/
    model.inp
    model.rpt
    model.out
    rainfall.csv
    manifest.json
```

要求：

- 用户本地默认可在 run 后清理。
- 测试可以保留失败 artifact 方便 debug。
- 不直接修改 `data/demo_site/base_model.inp`。
- 文件名使用 UUID/安全 slug。
- 不允许用户输入直接拼接任意路径。

## 9.4 异常处理

捕获并分类：

- invalid input
- model mutation error
- SWMM open error
- SWMM execution error
- output parse error
- continuity QA failure
- unexpected exception

UI：

- 展示可理解的中文摘要；
- 展开区域可看技术细节；
- 不把完整 traceback 默认暴露给普通用户；
- 开发模式记录 traceback。

## 9.5 资源释放

无论成功失败：

- `Simulation` 必须 close。
- 临时文件句柄关闭。
- 下一次 simulation 能正常启动。
- lock 释放。

需要专门测试：

1. 启动一个故意失败的模型；
2. 捕获异常；
3. 紧接着运行正常模型；
4. 正常模型成功。

---

# 10. 结果提取

## 10.1 Node

至少：

- max depth
- flooding volume
- flooding duration
- peak flooding rate
- max ponded volume（如有效）
- depth timeseries
- flooding timeseries

## 10.2 Link

至少：

- peak flow
- max depth / capacity proxy（如 API 可稳定获得）
- flow timeseries
- 关键管 C05 的峰值流量

## 10.3 System

至少：

- runoff continuity / routing continuity error
- total flooding
- outfall / system peak flow（选择稳定 API）
- rainfall total
- runoff total（如可获得）

## 10.4 单位审计

这是 P0 阻塞项。

Agent 必须：

1. 查当前 PySWMM 官方文档/API。
2. 检查 SWMM `.rpt` 对应值。
3. 对 node/system 同一指标做交叉比对。
4. 写 `tests/integration/test_units_and_stats.py`。
5. 在 `docs/data_dictionary.md` 记录每个字段：
   - source API
   - raw unit
   - display unit
   - conversion
6. 若不能确认，UI 必须显示 `raw` 或去掉该 KPI，而不是猜单位。

---

# 11. 核心指标

## 11.1 必须指标

每个 scenario：

- `total_flood_volume`
- `flooded_node_count`
- `max_node_depth`
- `max_depth_ratio`
- `max_flood_duration`
- `peak_outfall_flow`
- `routing_continuity_error`
- `runoff_continuity_error`
- `estimated_cost`
- `flood_volume_reduction`
- `flood_reduction_pct`
- `cost_per_avoided_flood_volume`

## 11.2 基准

所有“减少”指标相对 S0。

```text
reduction = baseline - scenario
reduction_pct = reduction / baseline * 100
```

边界：

- baseline = 0 时不可除；显示 N/A。
- scenario 比 baseline 更差时 reduction 为负，不要截成 0。
- 不允许为了“方案更好看”隐藏负结果。

## 11.3 成本

成本全部是用户假设。

`costs.yaml` 示例：

```yaml
currency: CNY
assumption_only: true

pump_assist:
  fixed_cost: 12000

pipe_upsize:
  unit_cost_per_m: 800
  affected_length_m: 80

storage_expand:
  unit_cost_per_m3: 300
  added_storage_m3: 150
```

**数值仅为 synthetic placeholder，页面必须标注“演示成本假设”。**

公式：

```text
estimated_cost = sum(cost item)
cost_per_avoided_flood_volume =
    estimated_cost / max(baseline_flood_volume - scenario_flood_volume, 0)
```

如果 avoided volume <= 0：

- 显示 N/A 或 “no benefit”
- 不显示负的“单位减灾成本”

## 11.4 排序

推荐默认排序：

1. 过滤 QA invalid scenario；
2. 过滤没有减灾效果的 scenario；
3. 优先 `cost_per_avoided_flood_volume`；
4. 同时展示 `flood_reduction_pct`，避免只看成本。

不得宣传为“自动最优设计”。

应该写：

> 在当前 synthetic 参数和用户成本假设下的方案排序。

---

# 12. 节点风险等级

风险等级是**展示启发式**，不是规范。

推荐输入：

- `depth_ratio = max_depth / node_full_depth`
- flooding_volume
- flooding_duration

推荐初版规则：

```text
RED:
    flooding_volume > 0 AND flooding_duration >= threshold
    OR depth_ratio >= 1.0

ORANGE:
    flooding_volume > 0
    OR depth_ratio >= 0.8

YELLOW:
    depth_ratio >= 0.6

GREEN:
    otherwise
```

阈值写入 config。

UI 必须有 tooltip：

> 风险等级为本项目用于方案对比的启发式展示规则，不对应任何法规或设计规范分级。

---

# 13. Rational Method 数量级校核

## 13.1 公式

用于简单数量级 sanity check：

\[
Q_p = 0.00278 C i A
\]

其中：

- Q: m³/s
- C: dimensionless runoff coefficient
- i: mm/h
- A: ha

## 13.2 目的

**不是用于“验证 SWMM 正确”**，而是：

- 检查输入数量级；
- 检查结果是否出现明显异常；
- 帮助面试解释动态模型与简单峰值公式差异。

## 13.3 参数

Demo 使用明确声明的 `C_assumed`。

可根据不透水率生成演示 C，但必须标注为简化假设。

## 13.4 对比

```text
ratio = SWMM_peak_outflow / Rational_Qp
```

只做提示：

- ratio 极端异常时生成 warning；
- 不做硬性 pass/fail；
- 例如 `<0.25` 或 `>4` 提示“需要检查模型参数/汇流滞后/储蓄/入渗等因素”。

文档解释为什么二者不应相等：

- SWMM 是动态过程；
- 有入渗、地表蓄水；
- 管网有蓄泄；
- 峰值并非同一时刻；
- Rational Method 本身有适用条件。

---

# 14. 连续性 QA

## 14.1 读取

从 SWMM / PySWMM system statistics 获取：

- runoff continuity error
- flow routing continuity error

## 14.2 项目内部 QA 阈值

这是项目自定义质量门，不声称为普遍规范：

```text
|error| <= 2%        -> PASS
2% < |error| <= 5%   -> WARNING
|error| > 5%         -> INVALID_FOR_RANKING
```

如实测 demo 无法达到，应：

1. 检查 routing step、管道、节点、模型边界；
2. 优先修模型；
3. 如仍无法解决，记录原因；
4. 不得静默忽略。

---

# 15. 敏感性分析

## 15.1 P0-lite

至少实现一个参数的 one-at-a-time 敏感性：

- rainfall intensity scale: 0.8 / 1.0 / 1.2

输出：

- total flood volume
- flooded node count
- peak outfall flow

预期：

降雨增大时，风险总体趋势不应反常降低。若反常：

- 不直接判 bug；
- 检查模型控制/调蓄/数值；
- 在 audit 记录。

## 15.2 P1

可增加：

- percent impervious: 0.9x / 1.0x / 1.1x（clip 0–100）
- storage capacity ±20%
- pipe diameter ±20%

## 15.3 禁止

不要在 v0.1 做 Sobol、Morris、贝叶斯优化等复杂分析。

---

# 16. Streamlit UI

## 16.1 页面结构

推荐单页，避免过度设计。

### Header

- SiteDrainGuard
- 一句话说明
- Prototype / Synthetic Data badge
- disclaimer

### Sidebar

#### 1. Rainfall

- 内置 moderate/heavy
- upload CSV
- rainfall total
- duration
- peak intensity

#### 2. Scenario

复选：

- S0 Baseline（必须）
- S1 PumpAssist
- S2 PipeUpsize
- S3 StorageExpand
- S4 Hybrid

默认全部选中。

#### 3. Cost assumptions

可编辑：

- pump fixed cost
- pipe unit cost
- storage unit cost

所有成本注明“演示/用户假设”。

#### 4. Run

按钮：

`Run analysis`

运行时：

- `st.status` / progress
- 显示当前 scenario
- 禁止重复点击造成 reentry

### Main — Section A: Site Network

Plotly 网络：

- node coordinate
- link line
- node color = risk
- hover：
  - node id
  - max depth
  - depth ratio
  - flooding volume
  - flooding duration
- critical nodes 更突出

不使用网络底图，避免不必要 GIS。

### Section B: KPI

至少：

- Total flood volume
- Flooded nodes
- Max node depth
- Peak outfall flow
- Continuity QA

### Section C: Scenario Comparison

表格：

| Scenario | Flood volume | Reduction % | Flooded nodes | Peak outflow | Cost | Cost/avoided m³ | QA |

图：

- Flood volume by scenario
- Cost vs flood reduction scatter

### Section D: Time Series

选择 node：

- depth over time
- flooding rate over time

### Section E: Engineering QA

展示：

- runoff continuity
- routing continuity
- Rational Method sanity check
- warnings
- model/run metadata

### Section F: Method & Limitations

简洁展开：

- synthetic data
- not calibrated
- not design software
- model assumptions

## 16.2 State

Streamlit 每次交互会 rerun。

必须避免：

- 每次改一个成本输入就重跑 SWMM。
- 在 UI rerun 时残留打开的 Simulation。
- 把 Simulation 对象存进 session state。

建议：

- 只有按 Run 才计算。
- session state 保存纯结果对象/序列化数据。
- 成本变化可以基于已有 hydraulic results 重新计算 economics，无需重跑 SWMM。
- rainfall/scenario 参数变化后显示 “Results out of date”。

## 16.3 Cache

P0 可不使用 Streamlit cache。

若使用：

- 只 cache 纯数据结果；
- cache key 包含：
  - model hash
  - rainfall hash
  - scenario config hash
  - engine version
- 不 cache `Simulation` 对象；
- 不依赖不安全 pickle 输入；
- 不对用户上传内容反序列化任意 Python 对象。

---

# 17. Visualization

## 17.1 网络图

数据源：

- `[COORDINATES]`
- `[CONDUITS]`
- `[PUMPS]`
- node IDs

要求：

- 没坐标时 graceful fallback。
- hover 不出错。
- outfall、storage、junction 用不同 marker symbol。
- risk color palette 有文字/图例，不只靠颜色表达。
- 至少考虑色觉可访问性：风险同时用形状/边框/label 表示。

## 17.2 图表真实性

禁止：

- y-axis 截断制造夸张差异而不注明。
- 按错误单位显示。
- 将无 QA 的 scenario 和有效 scenario 混合排序而不标注。
- “综合评分”使用不透明魔法权重。

---

# 18. 数据模型

推荐 Pydantic：

```text
RainfallEvent
ScenarioConfig
CostAssumptions
ModelMetadata
Mutation
SimulationRequest
NodeMetric
LinkMetric
SystemMetric
SimulationResult
ScenarioComparison
QAResult
```

要求：

- 单位写入字段名或 metadata。
- 输入 validation 统一。
- 避免到处传裸 dict。
- 但不要为了“架构漂亮”写几十个空类。

---

# 19. Service 层

核心入口建议：

```python
class AnalysisService:
    def run(
        self,
        rainfall: RainfallEvent,
        scenarios: list[ScenarioConfig],
        costs: CostAssumptions,
    ) -> AnalysisBundle: ...
```

流程：

```text
validate request
  ->
build rainfall
  ->
for scenario sequentially:
    build temp model
    run SWMM
    extract metrics
    run QA
  ->
compare against S0
  ->
calculate economics
  ->
return bundle
```

该 service 可以同时被：

- Streamlit
- CLI script
- tests

调用。

---

# 20. CLI / 可复现批处理

必须有：

```bash
python scripts/run_demo_batch.py
```

要求：

- 不依赖 Streamlit。
- 自动运行 moderate rainfall 下 S0–S4。
- 输出 console summary。
- 导出 CSV/JSON 到 `artifacts/`（gitignore）。
- 退出码：
  - 0: 运行成功，且关键 QA 达标；
  - 非 0: P0 QA 失败。

这是最重要的 reproducibility 入口之一。

---

# 21. 测试策略

## 21.1 原则

测试分：

1. unit
2. integration
3. end-to-end smoke

不能全部 mock。

## 21.2 Unit tests

至少覆盖：

### rainfall

- valid CSV
- missing columns
- negative
- NaN
- duplicate time
- nonuniform step
- too large intensity
- too few rows

### scenario

- each scenario mutation manifest
- S0 no mutation
- S4 == S1+S2+S3
- only whitelisted fields can mutate
- no accidental base file change

### economics

- positive benefit
- zero baseline
- no benefit
- negative benefit
- zero cost
- cost combination

### metrics

- normalization
- risk classification
- depth ratio
- missing optional values

### rational method

- known hand calculation
- unit conversion
- invalid C/i/A

### INP writer

- section replacement
- newline
- preserve other sections
- input file unchanged

## 21.3 Integration tests

必须使用真实 engine：

### `test_real_swmm_smoke.py`

- load base INP
- run
- `.rpt` and `.out` generated
- no fatal error
- extract at least one node statistic

### `test_scenario_effects.py`

至少验证：

- S0 能跑
- S1 能跑
- S2 能跑
- S3 能跑
- S4 能跑
- mutation 实际进入模型

**不要强行断言每个工程方案一定减少洪涝。**
但 demo 模型应调到多数合理方案有可解释效果。

### `test_units_and_stats.py`

- 交叉验证关键单位/统计量。
- 对 system/node aggregate 做合理一致性检查。

### `test_cleanup_after_failure.py`

- 失败后下一仿真可运行。

## 21.4 E2E smoke

至少启动 Streamlit：

```bash
streamlit run app.py --server.headless true
```

检查：

- 进程能启动；
- 首页 HTTP 可访问；
- 无 import exception。

如果环境允许 Playwright：

- 打开首页；
- 触发 Demo 分析；
- 等到结果；
- 验证 KPI 元素出现。

Playwright 不是 P0 阻塞项，但启动 smoke 是 P0。

## 21.5 Coverage

目标：

- core `src/sitedrainguard`: >= 80%
- 不要通过排除关键模块骗 coverage。
- integration 代码可以适当降低要求，但核心计算必须覆盖。

---

# 22. CI

`.github/workflows/ci.yml`

最低 jobs：

## lint

```text
ruff check .
ruff format --check .
```

## test

优先 matrix：

- ubuntu-latest, Python 3.11
- windows-latest, Python 3.11

如 Windows 的 native 依赖存在暂时性不可解决问题，可以：

- 先保证 Ubuntu 为 required；
- Windows 作为 allow-failure 只能是临时状态；
- `AUDIT_REPORT.md` 必须明确。

不得直接删除 Windows 测试来隐藏问题。

## commands

```text
install
validate environment
pytest
run demo batch
```

## artifact

失败时可上传：

- pytest report
- SWMM `.rpt`
- diagnostics

不要上传用户私有数据。

---

# 23. Code Quality

## 23.1 风格

- Python type hints
- docstrings 只给公共 API/复杂函数
- 函数尽量单一职责
- 不写 800 行 `app.py`
- 不做无意义设计模式

## 23.2 Ruff

配置：

- E/F/I/B/UP 等合理规则
- 不为了 0 warning 写反可读代码

## 23.3 Error messages

领域异常：

```text
RainfallValidationError
ScenarioMutationError
SimulationExecutionError
OutputExtractionError
ModelQAError
```

UI 捕获领域异常。

## 23.4 Logging

- `logging`
- 不打印用户上传完整内容
- run_id
- scenario_id
- execution time
- error type

---

# 24. 安全

虽为本地工具，也要有基本安全约束。

## 24.1 文件上传

仅 CSV。

- 限制 size，例如 2 MB。
- 禁止 `.pkl` / Python object。
- 不执行上传内容。
- 不允许路径穿越。
- 使用 temp dir。

## 24.2 INP

v0.1 **不允许用户上传任意 INP**。

原因：

- 增大验证、安全、兼容复杂度；
- 项目重点是 demo 工作流。

用户自定义 INP 作为 P2。

## 24.3 HTML

如 Streamlit 使用 markdown：

- 避免不必要 `unsafe_allow_html=True`
- 如必须使用，内容只能是代码内静态模板，不拼接上传内容。

## 24.4 Secrets

仓库不得有：

- API key
- token
- 用户路径
- `.env`
- IDE credential
- 真实企业文件

提交前扫描：

```bash
git grep -n -E "(api[_-]?key|secret|token|password)" .
```

人工判断误报。

---

# 25. License 与第三方归属

## 25.1 自有仓库

推荐 MIT，除非用户另指定。

## 25.2 必须生成

`THIRD_PARTY_NOTICES.md`

至少列：

- EPA SWMM
- PySWMM
- Streamlit
- Plotly
- pandas
- NumPy
- Pydantic

Agent 必须根据安装包/官方仓库核实 license，不凭记忆乱写。

## 25.3 SWMM

不得使用 EPA logo 暗示 endorsement。

README 可以写：

> Built on the US EPA Storm Water Management Model (SWMM).

但需保持第三方/非官方性质。

## 25.4 引用

`CITATION.cff`：

- 本项目作者留用户可填写 placeholder `YOUR_NAME` 可以存在，但 README 发布前必须提醒。
- 引用 PySWMM JOSS paper。
- 引用 SWMM 官方项目。

---

# 26. README 结构

README 第一屏必须面向招聘者，而不是开发者。

推荐：

```text
# SiteDrainGuard

一句话定位

[demo screenshot/gif]

Why
What it does
Key results from synthetic demo
Architecture
Engineering methodology
Quick start
Demo
Scenario definitions
Validation / QA
Project structure
Limitations
Roadmap
License / Acknowledgements
```

## 26.1 Key results

只能填真实跑出来的 synthetic demo 数字。

生成前：

```text
TODO: replace after verified run
```

最终 release 前：

- P0 README 不允许遗留结果 TODO。
- Agent 应运行 `scripts/export_demo_results.py` 自动生成数据，避免手工写错。

## 26.2 Screenshot

如 Agent 有浏览器能力：

- 运行 app
- 真实截图
- 保存 `assets/dashboard.png`

不得生成一张“概念 UI 图”冒充真实软件截图。

如果不能截图：

- README 暂不放截图；
- `AUDIT_REPORT.md` 写“需人工截图”。

---

# 27. 文档

## 27.1 `docs/methodology.md`

包括：

- SWMM 建模概念
- synthetic site
- rainfall
- scenarios
- metrics
- economics
- risk
- rational method
- limitations

## 27.2 `docs/validation.md`

包括：

- real engine smoke
- continuity
- rational sanity check
- sensitivity
- cross-check
- 未进行的：
  - calibration
  - field validation
  - code compliance

## 27.3 `docs/data_dictionary.md`

字段级：

| Field | Meaning | Source | Raw unit | Display unit | Notes |

## 27.4 `docs/limitations.md`

至少：

- synthetic site
- no calibration
- no survey DEM
- simplified cost
- no real-time monitoring
- single-process simulation
- no design-code judgement
- no uncertainty quantification
- rainfall is user input, not local design storm generator

## 27.5 `docs/resume_claims.md`

生成两栏：

### 可以写

只写已验证事实，例如：

- 使用 Python/PySWMM/SWMM 开发
- 实现 5 scenario batch
- 实现连续性 QA
- 实现 synthetic demo
- 实际测试数量
- 真实算出的指标

### 不可以写

- 企业落地
- 工程实测验证
- 未达到的性能
- 虚构 Star
- 虚构用户
- 虚构节省成本

---

# 28. 性能

Demo 很小，不做过度优化。

P0 性能目标：

- 单 scenario 本地开发机通常应在秒级；
- S0–S4 batch 目标 < 60s；
- 如 >60s，必须 profiling。

优化顺序：

1. 检查 report step / simulation duration。
2. 不在 Python 每个 hydraulic tiny timestep 收集所有对象。
3. 优先 SWMM output / summary statistics。
4. 只提取 UI 真正需要的 node timeseries。
5. 不并行 SWMM。

不要为了速度牺牲正确性。

---

# 29. Demo 结果设计

项目演示模型应体现：

- moderate rain：
  - S0 风险较低或中等；
  - 方案差异可见。
- heavy rain：
  - S0 出现至少 1–3 个关键风险节点；
  - S1/S2/S3 有不同效果；
  - S4 通常效果更强，但不强制“绝对最好性价比”。

如果所有 scenario 完全一样：

- 说明模型/参数选择失败；
- 调整 synthetic base model；
- 不能在展示层伪造差异。

如果所有节点都严重爆掉：

- 模型也失去比较价值；
- 调整输入/设施能力。

目标是形成有解释空间的 demo。

---

# 30. 典型坑与处理

## 30.1 PySWMM MultiSimulationError

现象：

- “只能有一个 Simulation”相关异常。

处理：

- 检查 context manager。
- 检查异常路径是否 close。
- 串行执行。
- 不把 Simulation 存 session state。

## 30.2 Streamlit rerun 重复运行

处理：

- 只在 button event 创建 run。
- 将结果存 session state。
- 参数变化标记 stale。
- 不用 widget change 直接触发 simulation。

## 30.3 Native library 安装失败

处理：

- 先确认 Python 3.11。
- 使用 PySWMM 官方支持的 SWMM engine extra。
- 清理旧环境。
- 记录 exact versions。
- Docker 可作为 P1 fallback。
- **不能切换成 mock engine 作为最终项目。**

## 30.4 SWMM `.inp` 被破坏

处理：

- base read-only。
- mutation 后保存 temp。
- 加 parser/smoke test。
- mutation manifest。
- diff 检查。

## 30.5 Unit 搞错

处理：

- 不猜。
- API docs + `.rpt` + hand check 三重确认。
- data dictionary。

## 30.6 Flood volume = 0

可能：

- rainfall 太弱；
- node max depth 太大；
- pipes 太大；
- ponding/flooding configuration；
- 结果提取错误。

处理：

- 先看 `.rpt`。
- 看 node statistics。
- 调整 synthetic model，不硬编码结果。

## 30.7 Continuity error 太大

处理：

- routing step；
- dynamic wave；
- node geometry；
- extreme parameter；
- pump control；
- conduit slope；
- simulation start/end；
- report/start；
- model warnings。

## 30.8 Scenario 反而更差

不要先“修数据”。

检查：

- 是否修改错 token index；
- 泵是否产生下游瓶颈；
- 扩管是否将洪峰更快传到下游；
- storage 是否配置错误；
- 指标是否有单位错误。

如果物理上合理，可以保留，作为讨论亮点。

## 30.9 CI 本地不同

- 固定 Python。
- 固定关键依赖。
- 不依赖绝对路径。
- path 使用 `pathlib`.
- LF/CRLF 测试。
- temp dir。

## 30.10 Streamlit Cloud 不工作

在线部署是 P1。

v0.1 release 可以以：

- GitHub repo
- local demo
- README screenshot
- batch reproducibility

作为完成条件。

---

# 31. 开发阶段

# Phase 0 — Repository & Environment

目标：

- 初始化结构
- `pyproject.toml`
- dependencies
- `src` package
- lint/test
- environment validation
- SWMM smoke

必须完成：

```bash
python scripts/validate_environment.py
pytest tests/integration/test_real_swmm_smoke.py
```

Gate：

- 真实 SWMM 跑通之前，**不得进入 UI 开发**。

Agent 自审计：

- [ ] Python 版本记录
- [ ] PySWMM version
- [ ] engine version
- [ ] real simulation success
- [ ] no mock-only path
- [ ] base model source/provenance recorded

---

# Phase 1 — Synthetic Base Model

目标：

- base INP
- metadata
- moderate/heavy rainfall
- baseline output

检查：

- [ ] S0 可跑
- [ ] heavy 有可观察 flood risk
- [ ] model continuity 合理
- [ ] coordinates 完整
- [ ] data README 声明 synthetic
- [ ] no real corporate names/data

产物：

`artifacts/baseline_summary.json`（不 commit 或只 commit verified snapshot，按设计决定）

---

# Phase 2 — Domain + Input Validation

目标：

- Pydantic models
- rainfall parser
- config
- unit tests

Gate：

```bash
pytest tests/unit
ruff check .
```

---

# Phase 3 — Scenario Engine

目标：

- S0–S4
- mutation manifest
- no mutation leakage
- scenario integration tests

Gate：

- 5 个 scenario 全部真实运行。
- base INP checksum 前后不变。

---

# Phase 4 — Metrics + QA

目标：

- hydraulic metrics
- risk
- economics
- continuity
- rational method
- unit audit

Gate：

- 单位确认。
- continuity threshold implemented.
- rational sanity output.
- economics edge cases pass.

---

# Phase 5 — Analysis Service + Batch CLI

目标：

- 一个核心 service
- `run_demo_batch.py`
- result export

Gate：

```bash
python scripts/run_demo_batch.py
```

必须真实完成 S0–S4。

---

# Phase 6 — Streamlit

目标：

- UI 完整
- no logic duplication
- robust errors

Gate：

- headless startup
- demo run
- KPI
- network
- comparison
- QA

---

# Phase 7 — Docs + CI + Release Hygiene

目标：

- README
- docs
- CI
- license
- notices
- citation
- screenshots if possible

Gate：

- fresh clone instructions tested in clean venv if practical。
- CI green.

---

# Phase 8 — Final Self Audit

Agent 必须运行：

```bash
ruff check .
ruff format --check .
pytest --cov=src/sitedrainguard --cov-report=term-missing
python scripts/validate_environment.py
python scripts/run_demo_batch.py
streamlit run app.py --server.headless true
```

Streamlit smoke 可用 timeout/background process。

还应：

```bash
git status
git diff --check
git grep -n "TODO\|FIXME\|HACK"
```

P0 path 不允许遗留 TODO/FIXME。

---

# 32. Definition of Done

只有以下全部达到，才能标记 v0.1 完成。

## Runtime

- [ ] Clean environment installs.
- [ ] Real SWMM engine runs.
- [ ] S0–S4 all run.
- [ ] Failure does not poison next run.
- [ ] Batch CLI works.
- [ ] Streamlit starts.

## Scientific

- [ ] Base model synthetic label.
- [ ] Unit audit completed.
- [ ] Continuity QA.
- [ ] Rational method check.
- [ ] At least rainfall sensitivity.
- [ ] No calibration claim.
- [ ] No design-code claim.

## Software

- [ ] Modular source.
- [ ] Unit tests.
- [ ] Integration test with real engine.
- [ ] Coverage target.
- [ ] Ruff.
- [ ] CI.
- [ ] Cross-platform path.

## Product

- [ ] Network visualization.
- [ ] Risk.
- [ ] KPI.
- [ ] Scenario comparison.
- [ ] Cost assumptions.
- [ ] QA panel.
- [ ] Limitations visible.

## Open Source

- [ ] README.
- [ ] LICENSE.
- [ ] THIRD_PARTY_NOTICES.
- [ ] CITATION.
- [ ] docs.
- [ ] no secrets.
- [ ] no real proprietary data.

## Portfolio integrity

- [ ] Resume claims doc.
- [ ] Verified synthetic demo numbers.
- [ ] No fake star/user/company.
- [ ] No generated fake screenshot.
- [ ] Audit report.

---

# 33. Agent 自审计协议

Agent 不只是“写完代码”，还必须主动找问题。

## 33.1 每阶段自问

### Correctness

- 我是否真实运行了代码？
- 我是否只凭 API 名字猜实现？
- 单位确认了吗？
- 有没有 silently catch exception？
- 有没有为了过 test 改成 mock？

### Engineering

- base INP 是否被修改？
- scenario 是否只改目标参数？
- temp file 是否清理？
- exception 后 SWMM 是否释放？

### Scientific integrity

- 结果是否来自 engine？
- 是否有 continuity error？
- 是否用 synthetic 数据却写成真实？
- 是否把 sanity check 说成校准？

### UX

- 空输入怎么办？
- 上传坏 CSV 怎么办？
- 仿真失败 UI 是否可理解？
- 成本变动是否没必要地重跑 SWMM？
- QA invalid 是否仍被推荐？

### Reproducibility

- clone 后别人能跑吗？
- 是否依赖我的绝对路径？
- 是否依赖未提交文件？
- 是否记录版本？

---

# 34. `AUDIT_REPORT.md` 必须格式

最终文件：

```markdown
# SiteDrainGuard v0.1 Audit Report

## 1. Executive result
PASS / PARTIAL / FAIL

## 2. Environment actually tested
- OS
- Python
- PySWMM
- SWMM engine
- Streamlit

## 3. Requirement traceability
| ID | Requirement | Status | Evidence |

## 4. Commands executed
| Command | Result |

## 5. Real SWMM verification
- base
- S0-S4
- output paths
- engine metadata

## 6. Scientific QA
- continuity
- units
- rational sanity check
- sensitivity

## 7. Automated tests
- total
- passed
- failed
- coverage

## 8. UI smoke
- startup
- demo run
- screenshot status

## 9. Security / repository hygiene
- secrets
- uploads
- temp files
- git status

## 10. Known limitations
...

## 11. Unresolved issues
...

## 12. Claims allowed in README/resume
...

## 13. Claims NOT supported
...

## 14. Final recommendation
Ready for v0.1 tag? yes/no
```

## 34.1 Evidence

Evidence 必须是：

- test name
- command output summary
- code path
- generated report
- real result

不能写“应该可以”。

---

# 35. Agent 的错误处理策略

当 Agent 遇到问题：

## A. 可通过官方文档/源码解决

直接调查、修复、测试。

## B. 依赖版本冲突

- 建干净环境复现。
- 调整版本。
- 记录原因。
- 不随意删核心 dependency。

## C. SWMM 模型本身不稳定

- 读 `.rpt`
- 找 warning
- 调模型
- 记录变化
- 不修改结果表去“变合理”

## D. 无法在线部署

不阻塞 v0.1，完成 local + CI + screenshot。

## E. 无法确认某统计单位

将功能标为未验证，不展示错误单位，继续查文档/源码/报告。

## F. 时间不足

按优先级砍：

1. 保留真实 SWMM
2. 保留 scenario
3. 保留 metrics/QA
4. 保留 batch
5. 保留基础 UI
6. 砍敏感性扩展
7. 砍 Docker
8. 砍在线部署
9. 砍高级图表

**绝不为了做更多功能牺牲核心真实性。**

---

# 36. P0 / P1 / P2

## P0 — 必须

- real PySWMM/SWMM
- synthetic base
- rainfall parser
- S0–S4
- metrics
- continuity
- rational check
- costs
- network visualization
- scenario comparison
- real integration tests
- CLI
- CI
- docs
- audit

## P1 — 完成 P0 后

- rainfall sensitivity UI
- downloadable CSV/JSON report
- Dockerfile
- screenshot automation
- Python 3.12 CI
- deeper link capacity visualization
- better accessibility
- hosted demo

## P2

- user custom INP
- LID S5
- GIS/DEM
- parameter optimization
- local IDF/design storm modules
- report PDF
- calibrated case study
- real sensor integration

---

# 37. Git 工作流

如果仓库已经初始化 git：

推荐阶段性 commit：

```text
chore: bootstrap project and verify swmm runtime
feat: add synthetic demo model and rainfall inputs
feat: implement validated scenario engine
feat: add simulation runner and hydraulic metrics
feat: add engineering qa and economics
feat: add batch analysis workflow
feat: build streamlit dashboard
test: expand real-engine integration coverage
docs: complete methodology validation and release docs
```

原则：

- 不 force push。
- 不重写用户历史。
- 不提交临时 `.out/.rpt` 大量结果。
- 不刷无意义 commit。
- 每个 commit 应能说明一个真实阶段。

---

# 38. GitHub 发布

v0.1.0 前：

- CI green
- README 数字已验证
- screenshot 真实
- `CHANGELOG.md`
- tag `v0.1.0`

Release notes：

```text
SiteDrainGuard v0.1.0

- Synthetic construction-site SWMM model
- S0–S4 mitigation scenario engine
- Flood-risk and hydraulic metrics
- Cost-effectiveness comparison
- Continuity and rational-method QA
- Streamlit dashboard
- Reproducible CLI and CI

Limitations:
- synthetic demo only
- no field calibration
- not an engineering design tool
```

---

# 39. 面试可讲的技术主线

代码设计应支持用户最终讲出：

1. 为什么选择 SWMM 而不是自己写水力求解器；
2. 如何把施工场地概化为子汇水区和排水网络；
3. 为什么用 scenario mutation 而不是 5 套不可维护模型；
4. 如何保证方案比较只有目标参数不同；
5. 如何从 SWMM 提取 flood volume/depth/duration；
6. 如何做 continuity QA；
7. 为什么 Rational Method 只是 sanity check；
8. 为什么方案更强不一定性价比更高；
9. 为什么不做并行 SWMM；
10. 如果用于真实项目，还需要哪些数据和率定。

因此代码中必须有真实实现支撑这些答案。

---

# 40. 可选架构决策记录 ADR

建议建立：

`docs/adr/`

至少：

### ADR-001 — Use EPA SWMM via PySWMM

理由：

- 不重新实现成熟求解器。
- 聚焦工程工作流。

### ADR-002 — Sequential simulation

理由：

- engine non-reentrant / PySWMM simulation state.
- correctness over premature parallelism.

### ADR-003 — Synthetic bundled data

理由：

- 可开源。
- 不侵犯企业数据。
- 可复现。
- 不虚构工程经历。

### ADR-004 — No database for v0.1

理由：

- 结果是临时分析。
- 减少无关复杂度。

---

# 41. 最终验收示例

Agent 最后必须能给出类似但基于**真实运行**的输出：

```text
Environment:
Python 3.11.x
PySWMM 2.1.x
SWMM 5.2.4

Demo batch:
S0 PASS
S1 PASS
S2 PASS
S3 PASS
S4 PASS

Routing continuity:
S0 x.xx%
S1 x.xx%
...

Tests:
NN passed
Coverage: xx%

Streamlit:
startup PASS
interactive demo PASS/PARTIAL

Release recommendation:
READY / NOT READY
```

不能预填虚构数字。

---

# 42. 参考资料与 Agent 调研入口

Agent 开发时优先查官方资料：

- EPA SWMM official GitHub repository
- PySWMM official documentation
- PySWMM `SimulationPreConfig`
- PySWMM Node / Output / SystemStats API
- Streamlit session state documentation
- GitHub Actions Python documentation

当前调研基线：

- PySWMM 官方文档基线为 2.1.0（2025-09）。
- PySWMM 支持通过 extra 选择 SWMM engine，包括 5.2.4。
- PySWMM 提供 `SimulationPreConfig` 做 token-based 参数修改。
- PySWMM 的 `Simulation` 有单实例状态保护，不应在同一进程并行创建多个仿真。
- SWMM 官方 solver 为 EPA 开源/公共领域代码；具体第三方 license 必须由 Agent 发布前重新核实。
- Streamlit 会在交互时从上到下 rerun，因此仿真触发和 session state 必须明确设计。

若当前官方行为与本文档不同：

1. 以实际官方文档/源码/运行结果为准；
2. 不静默偏离；
3. 在 `docs/development_log.md` 记录；
4. 在 `AUDIT_REPORT.md` 说明。

---

# 43. 结束条件

本项目追求的不是代码量，而是：

> **真实的工程模型 + 可复现的软件实现 + 能说明边界的科学态度 + 有业务意义的方案比较。**

Agent 应优先交付一个“小而完整”的 v0.1。

任何时候，如果“漂亮功能”和“计算真实性”冲突：

**选择计算真实性。**

任何时候，如果“简历好看”和“事实准确”冲突：

**选择事实准确。**
