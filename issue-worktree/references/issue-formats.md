# Issue 输入格式与命名约定

## 支持的 Issue 输入

### GitHub

- `#123` 或 `123`（要求当前仓库 `origin` 指向 GitHub，且能从 remote URL 推断 `owner/repo`）
- `owner/repo#123`
- `https://github.com/<owner>/<repo>/issues/<number>`

GitHub issue 元信息（title/url）推荐通过 MCP 获取；脚本也支持 best-effort 用 `gh` 获取（可选，不再是硬前置）。
如果使用 `gh`：
- 依赖：`gh`（且已登录）
- 获取字段：`title`/`number`/`url`

### Linear

- `ABC-123`
- `https://linear.app/<workspace>/issue/ABC-123/<slug>`

Linear issue 元信息（title/url）推荐通过 MCP 获取；脚本也支持 best-effort 用 Linear GraphQL API 获取（可选）。
如果使用 Linear API：
- 依赖：`LINEAR_API_KEY` 环境变量
- 获取字段：`identifier`/`title`/`url`

## 分支命名（默认）

- GitHub：`issue/gh-<number>-<slug>`
- Linear：`issue/lin-<identifier>-<slug>`

说明：
- 分支名必须为英文/ASCII（团队约束）；脚本会强制校验。
- `<slug>` 来自 issue 标题，做 ASCII 化、去噪与截断；生成失败则省略。
- 你们团队如果有固定分支规范（如 `feat/`、`fix/`、`chore/`），可以在脚本里加 `--prefix` 或直接改默认前缀。

## worktree 目录命名（默认）

默认 worktree 根目录在仓库的“父目录”下，避免污染仓库：

`../worktrees/<repo-name>/<branch>`

如果你们希望统一管理到某个目录（如 `~/worktrees`），用 `--worktrees-root` 指定。
