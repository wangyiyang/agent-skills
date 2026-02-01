#!/usr/bin/env python3
"""
从 GitHub/Linear issue 创建（或复用）git worktree。

设计目标（第一性原理）：
- git 操作必须可本地确定性执行；
- issue 元信息（title/url）属于“可选增强”，可由 MCP/CLI/API 任一渠道提供；
- 没有 gh / 没有 LINEAR_API_KEY 也不应“硬失败”，最多降级为无 slug 的分支名。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import unicodedata
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from git_worktree import default_base_branch, ensure_worktree, run, shell_quote, validate_branch_name_english
from private_links import apply_links


@dataclass(frozen=True)
class IssueInfo:
    source: str  # "github" | "linear"
    key: str  # "123" or "ABC-123"
    title: str
    url: str


def _run(
    args: list[str],
    *,
    cwd: Optional[Path] = None,
    check: bool = True,
    capture: bool = True,
) -> subprocess.CompletedProcess:
    # 兼容旧实现：保留函数名，但转到共享实现。
    return run(args, cwd=cwd, check=check, capture=capture)


def _die(msg: str, code: int = 1) -> "NoReturn":
    print(f"[ERROR] {msg}", file=sys.stderr)
    raise SystemExit(code)

def _warn(msg: str) -> None:
    print(f"[WARN] {msg}", file=sys.stderr)


def _slugify_ascii(title: str, max_len: int = 50) -> str:
    # ASCII 化 + 仅保留 a-z0-9；其他转为 -
    norm = unicodedata.normalize("NFKD", title)
    ascii_s = norm.encode("ascii", "ignore").decode("ascii").lower()
    ascii_s = re.sub(r"[^a-z0-9]+", "-", ascii_s).strip("-")
    if len(ascii_s) > max_len:
        ascii_s = ascii_s[:max_len].rstrip("-")
    return ascii_s


def _repo_root(repo: Optional[str]) -> Path:
    if repo:
        p = Path(repo).expanduser().resolve()
        if not p.exists():
            _die(f"--repo 路径不存在: {p}")
        return p
    try:
        cp = _run(["git", "rev-parse", "--show-toplevel"])
    except Exception as e:
        stderr = getattr(e, "stderr", "") or ""
        _die(f"当前目录不在 git 仓库内：{stderr.strip()}".strip())
    return Path(cp.stdout.strip())

def _parse_github_owner_repo_from_remote(repo_root: Path) -> Optional[str]:
    try:
        cp = _run(["git", "remote", "get-url", "origin"], cwd=repo_root)
    except subprocess.CalledProcessError:
        return None
    url = cp.stdout.strip()

    # https://github.com/owner/repo(.git)
    m = re.match(r"^https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?$", url)
    if m:
        return f"{m.group(1)}/{m.group(2)}"

    # git@github.com:owner/repo(.git)
    m = re.match(r"^git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$", url)
    if m:
        return f"{m.group(1)}/{m.group(2)}"

    return None


def _classify_issue_input(raw: str) -> Tuple[str, str]:
    s = raw.strip()

    # Linear URL or key: ABC-123
    m = re.search(r"\b([A-Z][A-Z0-9]+-\d+)\b", s)
    if m and ("linear.app" in s or s == m.group(1)):
        return "linear", m.group(1)

    # GitHub issue URL
    m = re.match(r"^https?://github\.com/([^/]+)/([^/]+)/issues/(\d+)(?:/.*)?$", s)
    if m:
        return "github", f"{m.group(1)}/{m.group(2)}#{m.group(3)}"

    # owner/repo#123
    m = re.match(r"^([^/\s]+/[^#\s]+)#(\d+)$", s)
    if m:
        return "github", s

    # #123 or 123
    m = re.match(r"^#?(\d+)$", s)
    if m:
        return "github", m.group(1)

    # Linear key without url
    m = re.match(r"^([A-Z][A-Z0-9]+-\d+)$", s)
    if m:
        return "linear", m.group(1)

    _die(f"无法识别 issue 输入：{raw}")
    raise AssertionError("unreachable")

def _github_number_from_hint(hint: str) -> str:
    m = re.match(r"^([^/\s]+/[^#\s]+)#(\d+)$", hint)
    if m:
        return m.group(2)
    m = re.match(r"^#?(\d+)$", hint)
    if m:
        return m.group(1)
    m = re.match(r"^https?://github\.com/[^/]+/[^/]+/issues/(\d+)(?:/.*)?$", hint)
    if m:
        return m.group(1)
    return hint


def _fetch_github_issue(repo_root: Path, issue_hint: str) -> IssueInfo:
    # issue_hint:
    # - "123"
    # - "owner/repo#123"
    # - URL
    gh_args = ["gh", "issue", "view"]
    repo_flag: list[str] = []
    issue_arg = issue_hint

    # 如果是 owner/repo#123，则拆分 repo + number，兼容 gh 的参数形态
    m = re.match(r"^([^/\s]+/[^#\s]+)#(\d+)$", issue_hint)
    if m:
        repo_flag = ["--repo", m.group(1)]
        issue_arg = m.group(2)

    # 如果只是数字，尽量从 origin 推断 repo
    if re.match(r"^\d+$", issue_arg):
        owner_repo = _parse_github_owner_repo_from_remote(repo_root)
        if owner_repo:
            repo_flag = ["--repo", owner_repo]

    cp = _run(
        gh_args
        + [issue_arg]
        + repo_flag
        + ["--json", "title,number,url"],
        cwd=repo_root,
    )

    data = json.loads(cp.stdout)
    return IssueInfo(
        source="github",
        key=str(data["number"]),
        title=data["title"] or "",
        url=data["url"] or "",
    )


def _linear_graphql(
    query: str,
    variables: dict,
    *,
    api_key: str,
    timeout_s: int = 20,
) -> dict:
    endpoint = "https://api.linear.app/graphql"
    payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")

    def _do(auth_value: str) -> dict:
        req = urllib.request.Request(
            endpoint,
            data=payload,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": auth_value,
            },
        )
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)

    # Linear 的 Authorization 头在不同环境里可能是 “Bearer <token>” 或直接 token；
    # 这里做一次容错重试。
    try:
        return _do(f"Bearer {api_key}")
    except urllib.error.HTTPError as e:
        if e.code == 401:
            try:
                return _do(api_key)
            except Exception:
                raise
        raise


def _fetch_linear_issue(identifier: str) -> IssueInfo:
    api_key = os.environ.get("LINEAR_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("未设置 LINEAR_API_KEY，无法读取 Linear issue。")

    # 1) 尝试使用 filter.identifier（更精确）
    q1 = """
    query($identifier: String!) {
      issues(filter: { identifier: { eq: $identifier } }, first: 1) {
        nodes { identifier title url }
      }
    }
    """
    try:
        r1 = _linear_graphql(q1, {"identifier": identifier}, api_key=api_key)
    except Exception as e:
        raise RuntimeError(f"请求 Linear API 失败：{e}")

    if "errors" not in r1:
        nodes = (((r1.get("data") or {}).get("issues") or {}).get("nodes")) or []
        if nodes:
            n = nodes[0]
            return IssueInfo(
                source="linear",
                key=str(n.get("identifier") or identifier),
                title=str(n.get("title") or ""),
                url=str(n.get("url") or ""),
            )

    # 2) 回退：issueSearch（如果 schema 支持）
    q2 = """
    query($query: String!) {
      issueSearch(query: $query, first: 1) {
        nodes { identifier title url }
      }
    }
    """
    r2 = _linear_graphql(q2, {"query": identifier}, api_key=api_key)
    if "errors" in r2:
        # 把最关键的错误信息吐出来，便于用户快速修复 schema/权限/字段名
        raise RuntimeError(f"Linear API 返回错误：{r2['errors']}")

    nodes = (((r2.get("data") or {}).get("issueSearch") or {}).get("nodes")) or []
    if not nodes:
        raise RuntimeError(f"未找到 Linear issue：{identifier}")
    n = nodes[0]
    return IssueInfo(
        source="linear",
        key=str(n.get("identifier") or identifier),
        title=str(n.get("title") or ""),
        url=str(n.get("url") or ""),
    )


def _worktree_branch_name(issue: IssueInfo, prefix: str) -> str:
    slug = _slugify_ascii(issue.title)
    if issue.source == "github":
        base = f"{prefix}/gh-{issue.key}"
    else:
        base = f"{prefix}/lin-{issue.key.lower()}"
    return f"{base}-{slug}" if slug else base


def _validate_prefix_english(prefix: str) -> None:
    try:
        prefix.encode("ascii")
    except UnicodeEncodeError:
        _die(f"--prefix 必须为英文/ASCII：{prefix}")


def _best_effort_issue_info(
    *,
    repo_root: Path,
    raw_issue: str,
    title_override: Optional[str],
    url_override: Optional[str],
    allow_fetch: bool,
) -> IssueInfo:
    source, hint = _classify_issue_input(raw_issue)
    if source == "github":
        key = _github_number_from_hint(hint)
        base = IssueInfo(source="github", key=key, title=title_override or "", url=url_override or "")
        if (base.title or base.url) or (not allow_fetch):
            return base
        # 尝试用 gh 获取（失败则降级，不硬失败）
        try:
            fetched = _fetch_github_issue(repo_root, hint)
            return IssueInfo(
                source="github",
                key=fetched.key,
                title=title_override or fetched.title or "",
                url=url_override or fetched.url or "",
            )
        except FileNotFoundError:
            _warn("未找到 gh：跳过 GitHub issue 元信息获取（将使用无 slug 的分支名）。")
            return base
        except Exception as e:
            msg = getattr(e, "stderr", "") or str(e)
            _warn(f"获取 GitHub issue 失败：{msg.strip() or 'unknown error'}；继续降级执行。")
            return base

    # linear
    key = hint
    base = IssueInfo(source="linear", key=key, title=title_override or "", url=url_override or "")
    if (base.title or base.url) or (not allow_fetch):
        return base
    try:
        fetched = _fetch_linear_issue(hint)
        return IssueInfo(
            source="linear",
            key=fetched.key,
            title=title_override or fetched.title or "",
            url=url_override or fetched.url or "",
        )
    except Exception as e:
        msg = getattr(e, "stderr", "") or str(e)
        _warn(f"获取 Linear issue 失败：{msg.strip() or 'unknown error'}；继续降级执行。")
        return base


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="从 GitHub/Linear issue 创建 git worktree")
    ap.add_argument("issue", nargs="?", help="GitHub: #123/123/owner/repo#123/url；Linear: ABC-123/url")
    ap.add_argument("--repo", help="git 仓库路径（默认：当前目录向上探测）")
    ap.add_argument("--base", help="基线分支（默认：origin/HEAD 指向的分支）")
    ap.add_argument(
        "--worktrees-root",
        help="worktree 根目录（默认：<repo-parent>/worktrees）",
    )
    ap.add_argument(
        "--prefix",
        default="issue",
        help="分支名前缀（默认：issue；最终会生成 issue/gh-... 或 issue/lin-...）",
    )
    ap.add_argument(
        "--branch",
        help="直接指定分支名（此时不解析/不获取 issue 元信息，适合 MCP 先取 title 后自行生成分支名的场景）",
    )
    ap.add_argument("--title", help="issue 标题（由 MCP/其他渠道提供，用于生成 slug；提供后将跳过外部 fetch）")
    ap.add_argument("--url", help="issue URL（由 MCP/其他渠道提供；提供后将跳过外部 fetch）")
    ap.add_argument(
        "--no-fetch",
        action="store_true",
        help="不尝试从 gh/Linear API 获取 issue 元信息（完全离线/仅依赖 git）",
    )
    ap.add_argument(
        "--links-file",
        help="私密文件软链接配置（JSON）。默认：<repo>/.worktree-links.local.json（存在则自动应用）",
    )
    ap.add_argument("--no-links", action="store_true", help="不应用任何私密文件软链接")
    ap.add_argument(
        "--link-force",
        action="store_true",
        help="允许覆盖目标（仅文件/软链接；目录不允许删除）",
    )
    ap.add_argument("--dry-run", action="store_true", help="只打印将执行的命令，不实际创建")
    ap.add_argument(
        "--print-path-only",
        action="store_true",
        help="只输出 worktree 路径（适合脚本/编辑器集成）",
    )
    ns = ap.parse_args(argv)

    if not ns.issue and not ns.branch:
        _die("请提供 issue（如 #123 / ABC-123）或使用 --branch 直接指定分支名。")

    repo_root = _repo_root(ns.repo)
    base = ns.base or default_base_branch(repo_root)

    _validate_prefix_english(ns.prefix)

    # print-path-only 常用于集成场景，默认不触发外部 fetch，保证稳定与低依赖。
    allow_fetch = (not ns.no_fetch) and (not ns.print_path_only) and (not ns.title) and (not ns.url)

    if ns.branch:
        branch = ns.branch
        issue = None
    else:
        assert ns.issue
        issue = _best_effort_issue_info(
            repo_root=repo_root,
            raw_issue=ns.issue,
            title_override=ns.title,
            url_override=ns.url,
            allow_fetch=allow_fetch,
        )
        branch = _worktree_branch_name(issue, ns.prefix)

    validate_branch_name_english(repo_root, branch, _die)

    repo_name = repo_root.name
    parent = repo_root.parent
    worktrees_root = (
        Path(ns.worktrees_root).expanduser().resolve()
        if ns.worktrees_root
        else (parent / "worktrees")
    )
    worktree_path = worktrees_root / repo_name / branch

    if ns.print_path_only:
        print(str(worktree_path))
        return 0

    print(f"[INFO] repo   : {repo_root}")
    print(f"[INFO] base   : {base}")
    if issue:
        print(f"[INFO] issue  : {issue.source} {issue.key}")
        if issue.title:
            print(f"[INFO] title : {issue.title}")
        if issue.url:
            print(f"[INFO] url   : {issue.url}")
    print(f"[INFO] branch : {branch}")
    print(f"[INFO] path  : {worktree_path}")

    ensure_worktree(
        repo_root=repo_root,
        branch=branch,
        worktree_path=worktree_path,
        base=base,
        dry_run=ns.dry_run,
        warn=_warn,
        die=_die,
    )

    # 按用户习惯：把私密文件软链接到 worktree 对应位置（可选）。
    if not ns.no_links:
        links_file = (
            Path(ns.links_file).expanduser().resolve()
            if ns.links_file
            else (repo_root / ".worktree-links.local.json")
        )
        apply_links(
            worktree_path=worktree_path,
            links_file=links_file,
            dry_run=ns.dry_run,
            force=ns.link_force,
            warn=_warn,
            die=_die,
        )

    print("\n[HINT] 后续（GitHub Flow）：")
    print(f"  cd {shell_quote(str(worktree_path))}")
    print(f"  git push -u origin {shell_quote(branch)}")
    print("  然后创建 PR（必要时在 PR 描述里关联 issue）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
