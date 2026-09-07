# Codex 执行 Prompt：SiteDrainGuard

你现在是本仓库的主开发 Agent。请独立完成 SiteDrainGuard v0.1。

## 第一优先级

先打开并完整阅读仓库中的：

`SiteDrainGuard_DEVELOPMENT_SPEC.md`

该文档是本项目的唯一主规格，包含 PRD、架构、工程约束、测试计划、科学 QA、开发阶段、Definition of Done 和最终自审计要求。

**不要只读前几节。必须完整读取后再开始。**

---

## 你的任务

从当前仓库状态出发，完成一个可以真实运行、可复现、可开源、可放入应届生简历的 SiteDrainGuard v0.1：

> 基于 Python + EPA SWMM + PySWMM + Streamlit 的施工场地暴雨积水风险与临时排水方案评估原型。

必须实现：

- synthetic construction-site SWMM model
- validated rainfall input
- S0 Baseline
- S1 PumpAssist
- S2 PipeUpsize
- S3 StorageExpand
- S4 Hybrid
- real SWMM/PySWMM simulation
- scenario mutation manifest
- hydraulic/flood metrics
- risk classification
- cost-effectiveness comparison
- runoff/routing continuity QA
- Rational Method sanity check
- at least one sensitivity analysis
- reproducible batch CLI
- Streamlit dashboard
- unit tests
- real-engine integration tests
- Ruff
- GitHub Actions
- README + methodology + validation + limitations
- LICENSE / third-party notices / citation
- final `AUDIT_REPORT.md`

---

## 执行方式

### 1. 先检查，不要先重写

先执行：

- 查看目录
- 查看 git status / log（如果是 git 仓库）
- 查看已有文件和已有实现
- 检查 Python/OS
- 检查是否已有环境配置

不要覆盖用户已经正确实现的内容。

### 2. 建立需求追踪

在你的工作记录中，把规格中的 P0 requirement 映射到代码/测试。

开发中持续更新。

### 3. 严格按 Phase 0 → Phase 8

尤其：

**Phase 0 的真实 SWMM smoke test 没跑通前，不要开始堆 Streamlit UI。**

优先解决 engine/版本/模型。

### 4. 允许你自主查官方资料

如 API、版本、单位、license、平台兼容存在疑问：

- 查 PySWMM 官方文档/源码
- 查 EPA SWMM 官方仓库
- 查 Streamlit 官方文档
- 查 GitHub Actions 官方文档

不要凭记忆猜 API。

如规格与当前实际 API 冲突，以官方当前行为和真实运行结果为准，同时记录到：

`docs/development_log.md`

以及最终：

`AUDIT_REPORT.md`

### 5. 不要频繁向我提问

能从规格、仓库、官方文档、测试结果合理推导的，你自行决定。

只有出现以下情况才询问：

- 会删除/覆盖明显属于用户的重要现有资产；
- 需要用户提供凭证/私有数据；
- 两种产品方向互斥且规格没有任何判断依据；
- 环境完全无法安装核心 SWMM 且所有合理路径均已验证失败。

否则继续做并记录决策。

---

## 核心不可违反规则

### A. 禁止 fake

绝对禁止：

- mock SWMM 作为最终计算结果
- 硬编码 dashboard KPI 冒充仿真
- 随机生成“看起来合理”的结果
- 伪造测试通过
- 伪造 CI
- 伪造截图
- 伪造 GitHub Star
- 伪造企业落地
- 伪造真实场地
- 伪造工程验证
- 伪造节省成本

mock 只允许用于 isolated unit tests；P0 必须存在真实 engine integration test。

### B. Base model 不可被 scenario 污染

- 永远从只读 synthetic base 开始。
- 每次 run 使用 temp copy。
- 所有变更输出 mutation manifest。
- 测试 base file checksum 前后不变。

### C. SWMM 串行

不要并行创建多个 PySWMM `Simulation`。

- context manager
- sequential scenario batch
- proper cleanup
- failure cleanup test
- Streamlit 多次点击要防重入

### D. 单位不能猜

尤其：

- flooding volume
- flooding duration
- system routing totals

必须通过：

- 官方 API 文档
- `.rpt`
- integration cross-check

确认。

不能确认则不要在 UI 标错误单位。

### E. 模型 QA 不得省略

必须包含：

- runoff continuity
- routing continuity
- Rational Method sanity check
- rainfall sensitivity

QA invalid scenario 不得被推荐为“最佳方案”。

### F. synthetic 透明

所有内置：

- site
- rainfall
- costs

必须明确 synthetic/assumption。

不得出现任何中建、中铁、电建等企业真实项目暗示。

---

## 推荐技术选择

基准：

- Python 3.11
- PySWMM 2.1.x
- SWMM engine 5.2.4 if compatible through official PySWMM install path
- Streamlit
- Plotly
- pandas
- numpy
- Pydantic
- PyYAML
- pytest + pytest-cov
- Ruff

优先 `pyproject.toml`。

可以用 `uv`，但 README 也给标准 venv/pip 安装方法。

如果当前依赖有更新，不要无脑升级。先找到可复现组合，记录 exact tested versions。

---

## UI 原则

不要把时间浪费在“科技感”设计。

优先做：

1. Rainfall
2. Scenario
3. Run
4. Network risk
5. KPI
6. Scenario comparison
7. Cost effectiveness
8. Time series
9. Engineering QA
10. Limitations

只有用户按 `Run analysis` 才重跑 SWMM。

成本输入变化只重算 economics，不重跑 hydraulic simulation。

---

## Demo 模型调试目标

请认真调 synthetic base model。

Heavy rainfall 下：

- S0 应出现可观察的 flood risk；
- S1/S2/S3 应产生有物理解释的差异；
- S4 通常有较明显综合效果；
- 但不要强行保证每个单措施都“变好”；
- 如果某措施反而恶化，要检查物理/代码原因，合理则保留。

不要用 UI 层篡改结果。

Continuity error 必须达到规格中的项目 QA 目标，或明确标为 invalid 并继续修模型。

---

## 测试硬要求

最终至少有：

- rainfall validation unit tests
- scenario mutation unit tests
- economics tests
- rational method tests
- risk tests
- INP writer tests
- real SWMM smoke integration
- S0–S4 real scenario integration
- units/stats cross-check integration
- cleanup-after-failure integration
- Streamlit headless startup smoke

运行：

```bash
ruff check .
ruff format --check .
pytest --cov=src/sitedrainguard --cov-report=term-missing
python scripts/validate_environment.py
python scripts/run_demo_batch.py
```

不要只运行“你认为会通过的测试子集”。

---

## Git 规则

如果仓库已初始化 git：

- 不 force push
- 不 reset/checkout 覆盖用户工作
- 不改写历史
- 可以按规格建议做阶段性 commit
- commit 前运行对应测试
- 不提交大量 `.out/.rpt` 临时文件
- 不提交 `.env`/token

如果仓库未初始化，可以初始化，但不要创建远程或假装已 push。

---

## 最终自审计

实现结束后，必须生成：

`AUDIT_REPORT.md`

格式严格参考主规格。

报告必须给 Evidence，不写“应该可以”。

同时执行：

```bash
git status
git diff --check
git grep -n "TODO\|FIXME\|HACK"
```

如果 P0 仍有 TODO/FIXME：

- 修完；
- 或明确判定项目 PARTIAL，不得假装 Ready。

---

## 最终回复给我时

不要只说“完成了”。

请给我：

1. 最终状态：`READY / PARTIAL / BLOCKED`
2. 主要实现
3. 实际测试环境
4. 真实执行过的命令
5. test/coverage 结果
6. S0–S4 是否真实跑通
7. QA 是否通过
8. 已知限制
9. 需要我人工做的事情（例如 GitHub push、真实截图、填写作者名）
10. `AUDIT_REPORT.md` 路径

如果未完成，直接说未完成以及原因，不要包装。

---

## 完成标准

这个项目不是为了代码量，也不是为了做一个“看起来像 SaaS 的页面”。

完成的 v0.1 应让我能真实说：

> 我基于 EPA SWMM/PySWMM 构建了一个可复现的施工场地暴雨积水与临时排水方案评估原型，实现多工程情景的水文水力仿真、风险指标、成本效益比选和基础工程 QA；所有 demo 数据为合成数据，并通过真实 engine 测试、连续性检查和敏感性分析验证工作流。

只有代码和测试真正支持这句话，才算完成。
