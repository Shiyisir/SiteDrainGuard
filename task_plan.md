# v0.1.0 最终发布计划

## Next Step
创建已授权的 Shiyisir/SiteDrainGuard 公开仓库并验证 hosted CI。

## 阶段
- [x] 阅读全局规范、引用任务及指定发布材料；检查结构和环境。
- [x] 补齐缺失的项目规范草案。
- [x] 用户指出原项目位置；恢复原规范及主规格，不再等待草案确认。
- [x] 复用既有依赖，uv lock --check --offline 通过，全部七条本地验证命令退出码为 0。
- [x] Heavy 数值与基准一致，S4 union、rainfall 和 continuity QA 全部通过。
- [x] 真实浏览器运行 Heavy S0–S4 并保存 assets/dashboard.png，引用至双语 README。
- [x] 用户确认署名 Shiyisir、公开仓库 Shiyisir/SiteDrainGuard；检查许可与仓库卫生。
- [ ] 初始化项目独立 Git 仓库、审查暂存范围并提交。
- [ ] 正确远端 push main，检查真实 hosted Actions 日志和证据。
- [ ] CI green 后更新发布文档，确认清单和 Git clean，再创建 tag/Release。

## 问题
- 读取 AGENTS.md / CONTEXT.md 失败：当前包缺少这两个文件，已补草案，按用户规范等待确认。
- py 命令不存在：uv python find 3.11 已找到可执行的 3.11.12。
- Git 会向上找到父工作区仓库：后续只在本项目初始化独立仓库，禁止混入父仓库内容。
