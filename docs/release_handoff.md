# v0.1.0 发布交接

日期：2026-09-07。当前状态 **PARTIAL**：本地验证、真实截图、作者字段和双语 README 已完成；远端权限阻止 push。

## 已验证

- Windows 11 build 26200；Python 3.11.12；PySWMM 2.1.0；SWMM 5.2.4。
- 七条发布验证命令全部退出 0；Ruff PASS；19 tests PASS；coverage 85%。原始日志在忽略目录 artifacts/release/。
- Heavy S0–S4 溢流体积依次为 3338.20、3320.33、3321.33、3306.33、2730.55 m³；S4 reduction 18.20%。
- S4 = S1 ∪ S2 ∪ S3；extra=0、missing=0；rainfall identical；continuity QA PASS。
- assets/dashboard.png 是实际浏览器点击 Heavy S0–S4 分析后的截图，已检查页面结果与 CLI 一致。
- 暂存文件不包含环境、缓存、coverage、SWMM 临时文件；秘密值模式扫描无命中。
- INDEPENDENT_REVIEW.md 原文未变，SHA256 为 50C444CA45C6FB6FDB778287F2EA345EC12B7A6E7484F3F75AD76E7F9A35B2EC。

## GitHub 阻塞

公开仓库：https://github.com/Shiyisir/SiteDrainGuard 。用户已授权创建、push 和满足门槛后的 Release。

首次 push 被 GitHub 拒绝：OAuth App 无 workflow scope，不能创建或更新 .github/workflows/ci.yml。远端无已发布分支，Actions 列表为空，未创建 tag/Release。

需要用户同意补充 GitHub CLI workflow 权限并完成 GitHub 授权。不能删掉工作流绕过。之后重试 push main，读取真实 CI 结果，绿色后才更新 READY 并发布。

## 本次变更文件（相对网页端更新包）

- .gitignore：补充临时输出、coverage 和秘密文件忽略规则。
- AGENTS.md、CONTEXT.md：从原项目恢复，追加当前发布约束与状态。
- README.md：中英双语、真实截图、验证命令与发布状态。
- LICENSE、CITATION.cff、pyproject.toml：用户确认的作者及仓库信息。
- app.py、scripts/audit_hybrid_synergy.py：仅 Ruff 换行格式。
- assets/dashboard.png：新增真实运行截图。
- AUDIT_REPORT.md、RELEASE_CHECKLIST.md：本次真实验证与外部阻塞。
- THIRD_PARTY_NOTICES.md、docs/environment.md：记录依赖元数据复核与实际环境复用方式。
- docs/SiteDrainGuard_DEVELOPMENT_SPEC.md、docs/SiteDrainGuard_CODEX_PROMPT.md：恢复原项目事实源；主规格只清理 Markdown 行尾空格。
- docs/development_log.md、docs/release_handoff.md：收尾过程及交接证据。
- task_plan.md、findings.md、progress.md：发布计划、发现和执行记录。

基础模型、src 下水力逻辑、独立审查文档和现有 CI 工作流未修改。
