# 发布预检发现

- OS: Windows build 26200；默认 Python 3.12.7。最终验证复用原项目归档中的 Python 3.11.12 环境，导入当前更新版源代码。
- 初始 Git 查询落到父工作区；已在项目内初始化独立 main，未修改父仓库。
- 用户确认公开作者 Shiyisir 和目标 Shiyisir/SiteDrainGuard；身份字段已填写。
- 占位符搜索另命中审计/清单中的说明文字；不得清洗独立审查文档。
- .gitignore 已覆盖 .venv、Python/Ruff/pytest 缓存、.coverage、htmlcov、artifacts 和 demo_site 的 out/rpt；发布前还需检查完整暂存文件列表。
- CI 文件已有 Ruff、pytest、真实引擎环境校验、Heavy batch 和 Hybrid audit；本地七条命令均通过，待真实 hosted CI。
- INDEPENDENT_REVIEW.md 初始 SHA256: 50C444CA45C6FB6FDB778287F2EA345EC12B7A6E7484F3F75AD76E7F9A35B2EC。

- 公开仓库 https://github.com/Shiyisir/SiteDrainGuard 已创建；初始 commit 4f8035e1768118a9f4abb7d8f70e234e516a39d6。GitHub 因缺少 workflow scope 拒绝 push；Actions 列表为空，未 tag/Release。

- 用户已批准仅新增 workflow scope，认证成功；main 推送成功。Hosted CI 34111256789 全绿，Ubuntu / Python 3.11.16，19 tests、85% coverage、真实 Heavy 与 Hybrid audit PASS。发布文档已更新 READY，接下来只对通过 CI 的干净提交创建 tag/Release。
