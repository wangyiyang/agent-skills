# dev-agent-skills

个人开发使用的 Agent Skills 仓库，适用于 Claude Code、Pi、Codex 等各类开发 Agent。

## 安装

使用 [skills CLI](https://github.com/vercel-labs/skills) 安装，自动检测本机 Agent（Claude Code、Pi、Codex 等）并写入对应 skills 目录：

```bash
# 交互式选择要安装的 skill 和目标 Agent
npx skills add wangyiyang/dev-agent-skills

# 全部 skills 装到所有 Agent，跳过确认
npx skills add wangyiyang/dev-agent-skills --all
```

常用命令：

```bash
npx skills list -g          # 查看已安装
npx skills update           # 更新到最新版本
npx skills remove <skill>   # 卸载
```

常用选项：`-g` 安装到用户级（全局）、`-a <agent>` 指定目标 Agent、`--copy` 用复制代替默认的 symlink。

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

## fetch-github-issue-images

从 GitHub Issue 中提取并下载截图/附件图片。

说明：
- 通过 `gh api` 的 `body_html` 响应获取 CDN 直链，绕过 `github.com` 直连限制。
- 适合分析 Issue 附图、下载 Issue 附件的场景。

## prompt-engineering

用于编写和优化 prompts、commands、hooks、skills、sub-agent prompts 等一切 LLM 指令资产。

说明：
- 适合把模糊需求收敛成稳定、可复用、可验证的 prompt 模板。
- 当前版本主 skill 保持精简，扩展知识拆到 `references/`。
