# agent-skills

团队共享的 Codex Skills 仓库（GitHub Flow）。

## Codex 安装

当前仓库维护的是一组自定义 Codex skills，建议直接同步到个人目录 `~/.codex/skills/`。

单个 skill 安装：

```bash
mkdir -p ~/.codex/skills
rsync -a ./issue-worktree/ ~/.codex/skills/issue-worktree/
```

批量同步当前仓库全部自定义 skills：

```bash
mkdir -p ~/.codex/skills
for skill in agree-and-execute changelog-generator commit-push-pr issue-worktree prompt-engineering; do
  rsync -a "./$skill/" "~/.codex/skills/$skill/"
done
```

如果你希望团队共享同一套 skills，最佳实践不是“每个人手工复制一次”，而是把这份仓库作为技能源，并约定统一的同步脚本或安装流程。

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

## changelog-generator

从 Git 提交历史生成面向用户的 changelog 或 release notes。

说明：
- 适合版本发布、周报/月报、产品更新公告。
- 会把技术性提交转成更易读的用户语言。

## prompt-engineering

用于编写和优化 prompts、commands、hooks、skills、sub-agent prompts 等一切 LLM 指令资产。

说明：
- 适合把模糊需求收敛成稳定、可复用、可验证的 prompt 模板。
- 当前版本已按 Codex 使用场景压缩主 skill，并把扩展知识拆到 `references/`。
