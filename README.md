# agent-skills

团队共享的 Agent Skills 仓库（GitHub Flow）。

## Claude Code 安装（推荐：项目级 Skills，团队共享）

按 Claude Code 官方文档，Claude Code 会自动发现三类 Skills：个人 `~/.claude/skills/`、项目 `.claude/skills/`、以及插件内 Skills。

推荐把 Skill 放到业务项目仓库的 `.claude/skills/` 并提交，团队 `git pull` 后自动生效。

```bash
# 在业务项目仓库内
mkdir -p .claude/skills
cp -R /path/to/agent-skills/issue-worktree .claude/skills/issue-worktree
git add .claude/skills/issue-worktree
git commit -m "Add issue-worktree Claude Code skill"
git push
```

个人安装（只对自己生效）：

```bash
mkdir -p ~/.claude/skills
cp -R ./issue-worktree ~/.claude/skills/issue-worktree
```

可选：`npx skills add ...` 这类一键安装工具（如 baoyu-skills 的做法）是第三方分发方案，建议你们团队评估后再采用。

建议把私密配置文件（例如 `.worktree-links.local.json`）加入业务项目的 `.gitignore`，避免泄露。

## issue-worktree

从 GitHub Issue 或 Linear Issue 自动创建 Git 分支 + `git worktree`（并复用已存在 worktree）。

说明：
- issue 元信息（title/url）推荐通过 MCP 获取；脚本也支持 best-effort 的本机方式（可选），但不再是硬前置。
- 分支名强制英文/ASCII（团队约束）。
