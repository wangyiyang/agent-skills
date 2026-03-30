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
- 当前仓库版本已包含 `agents/openai.yaml`，便于 Skill UI 展示与隐式触发。

## agree-and-execute

对用户的简短批准语做“继续执行”语义补全，例如“好的”“继续”“按这个来”“1 & 2”。

说明：
- 适合把上一步已经明确的方案继续推进到执行。
- 不适合替代新的需求描述或变更范围说明。

## commit-push-pr

把当前 Git 改动整理为提交、推送分支，并创建 GitHub Pull Request。

说明：
- 遵循 GitHub Flow，不直接往 `main` 推送功能改动。
- 适合“提交 PR”“帮我 commit 并 push”“开个 PR”这类请求。
