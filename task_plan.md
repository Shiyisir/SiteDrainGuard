# v0.1.0 最终发布计划

## Next Step
发布文档提交通过 CI 后创建 v0.1.0 tag / GitHub Release；执行结果以远端 Release 与 tag 为准。

## 阶段
- [x] 阅读全局规范、引用任务及指定发布材料；检查结构和环境。
- [x] 补齐缺失的项目规范草案。
- [x] 用户指出原项目位置；恢复原规范及主规格，不再等待草案确认。
- [x] 复用既有依赖，uv lock --check --offline 通过，全部七条本地验证命令退出码为 0。
- [x] Heavy 数值与基准一致，S4 union、rainfall 和 continuity QA 全部通过。
- [x] 真实浏览器运行 Heavy S0–S4 并保存 assets/dashboard.png，引用至双语 README。
- [x] 用户确认署名 Shiyisir、公开仓库 Shiyisir/SiteDrainGuard；检查许可与仓库卫生。
- [x] 初始化项目独立 Git main、审查暂存范围并提交；公开远端已创建。
- [x] 正确远端 push main；hosted CI 34111256789 全部通过，真实日志已检查。
- [x] CI green 后更新发布文档，记录 READY、环境、测试 SHA 与 CI 链接；发布门槛清单完成。

## 问题
- 读取 AGENTS.md / CONTEXT.md 失败：用户已指出原项目，已恢复原规范，问题已解决。
- py 命令不存在：uv python find 3.11 已找到可执行的 3.11.12。
- Git 会向上找到父工作区仓库：已在本项目初始化独立仓库，未混入父仓库内容。

- GitHub push 被拒绝：原 OAuth 缺少 workflow scope；用户授权仅新增该 scope 后已解决，CI 未作绕过。
