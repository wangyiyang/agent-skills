---
name: issue-worktree
description: 从 GitHub Issue 或 Linear Issue 自动创建 Git 分支 + git worktree（含规范化分支名/目录名），用于 GitHub Flow 开发。用户提到“从 issue 创建 worktree/分支/开发目录”、给出 GitHub issue URL/#123/owner/repo#123，或给出 Linear issue URL/ABC-123 时使用；也适用于“为某个 issue 开一个独立工作区/隔离目录”的需求。
---

# Issue Worktree

## 概览

把“issue → 可工作的本地目录”这件事做成可重复、低认知负担的流程：解析 GitHub/Linear issue，生成稳定的分支名与 worktree 路径，并用 `git worktree` 创建/复用工作区。

## 工作流（建议默认）

路径说明：以下命令以“项目级 skill”路径 `.claude/skills/issue-worktree` 为例；如果你把它安装到个人目录，请把路径替换为 `~/.claude/skills/issue-worktree`。

### 1) 明确输入与目标

- 让用户给出“issue 标识”即可（GitHub 或 Linear 其一）。如果用户没说清来源，优先从形态推断：
  - GitHub：`#123` / `123` / `owner/repo#123` / `https://github.com/.../issues/123`
  - Linear：`ABC-123` / `https://linear.app/.../ABC-123`

需要确认的偏好（只在不确定时问，避免追问过多）：
- worktree 放哪：默认 `../worktrees/<repo-name>/<branch>`（不污染仓库根目录）
- 分支基线：默认 `origin/HEAD` 指向的分支（通常是 `main`）

### 2) 优先：用 MCP 获取 issue 元信息（可选但推荐）

第一性原理：`git worktree` 只需要一个分支名就能工作；issue 的 `title/url` 只是为了生成更可读的 `<slug>` 与便于输出提示。

因此建议把“取 issue 信息”交给 MCP（GitHub/Linear 都可以），再把 `title/url` 传给脚本，避免本机依赖 `gh` / `LINEAR_API_KEY`。

如果你已经配置了对应的 MCP：
- GitHub：用 MCP 读取 `issue.title`、`issue.url`、`issue.number`
- Linear：用 MCP 读取 `issue.title`、`issue.url`、`issue.identifier`

然后执行脚本时带上 `--title/--url`（脚本会跳过外部 fetch）：

```bash
python scripts/issue_worktree.py "<issue>" \
  --title "<title-from-mcp>" \
  --url "<url-from-mcp>"
```

### 3) 执行：创建/复用 worktree

在目标 git 仓库内执行（或用 `--repo` 指定仓库路径）：

```bash
python scripts/issue_worktree.py "<issue>"
```

常用参数：

```bash
python scripts/issue_worktree.py "<issue>" \
  --base main \
  --worktrees-root ../worktrees \
  --dry-run
```

完全离线（不尝试从任何渠道拉取 issue 元信息）：

```bash
python scripts/issue_worktree.py "<issue>" --no-fetch
```

如果你已经在上层逻辑里生成好了分支名（例如用 MCP + 自定义规则），也可以直接传 `--branch`：

```bash
python scripts/issue_worktree.py --branch "issue/gh-123-some-slug"
```

脚本行为约定（保持 KISS + 可预测）：
- GitHub issue 分支名：`issue/gh-<number>-<slug>`
- Linear issue 分支名：`issue/lin-<identifier>-<slug>`（identifier 统一转小写）
- `<slug>` 来自标题，做 ASCII 化与截断；如果标题无法生成 slug，就只用 id/identifier
- 分支名强制英文/ASCII（团队约束）：如 `--prefix`/`--branch` 含中文会直接报错
- 如果分支或 worktree 已存在：尽量复用，并打印现有路径，不重复创建

### 5) 你的习惯：把私密文件软链接进 worktree（可选）

在仓库根目录放一个仅个人使用的 JSON（建议 gitignore）：`.worktree-links.local.json`，脚本会在创建 worktree 后自动应用。

示例：

```json
[
  { "src": "~/.secrets/myrepo/.env", "dest": ".env" },
  { "src": "~/.ssh/config", "dest": ".ssh/config" }
]
```

说明：
- `dest` 必须是 worktree 内相对路径（禁止绝对路径/`..`）
- 默认不覆盖已有文件；需要覆盖文件/软链接时加 `--link-force`（目录不会被删除，避免破坏性操作）
- 若不想应用链接，传 `--no-links`

### 4) GitHub Flow 的后续动作（提醒最佳实践）

- 开发完成后，在 worktree 内 `git push -u origin <branch>` 并开 PR
- PR/commit 如需自动关联 Linear，遵循你们团队对 “magic words/关键词” 的约定（如果有）

## 故障排查（只在报错时用）

- 若你希望“必须校验 issue 存在”，推荐用 MCP 做校验（脚本默认允许降级继续执行）
- 解析 `#123` 失败：检查 `origin` remote 是否存在且指向 GitHub；必要时用 `owner/repo#123` 或 issue URL 明确仓库
- Linear 解析失败：确认输入是 `ABC-123` 或 Linear URL；若需要 title/slug，请确保 MCP 或其他渠道能提供 `title`

## 资源

### scripts/
- `issue_worktree.py`: 主入口脚本（解析 issue → 创建/复用 worktree）
- `git_worktree.py`: 纯本地 git worktree 操作（不依赖 issue 来源）

### references/
- `issue-formats.md`: 允许的输入格式与分支/目录命名规则（用于人类快速对齐）
