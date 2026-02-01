#!/usr/bin/env python3
"""
git worktree 相关的纯本地工具函数（不依赖 MCP/外部 API）。
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class RunResult:
    stdout: str
    stderr: str


def validate_branch_name_english(repo_root: Path, branch: str, die: callable) -> None:
    # 团队约束：分支名必须是英文/ASCII，避免编码与工具链兼容问题。
    try:
        branch.encode("ascii")
    except UnicodeEncodeError:
        die(f"分支名必须为英文/ASCII：{branch}")

    # 再做一次 git 级别校验，避免出现非法 ref（空格、~、^、.. 等）
    try:
        run(["git", "check-ref-format", "--branch", branch], cwd=repo_root)
    except subprocess.CalledProcessError:
        die(f"非法分支名（不符合 git ref 格式）：{branch}")


def run(
    args: list[str],
    *,
    cwd: Optional[Path] = None,
    check: bool = True,
    capture: bool = True,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        check=check,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def ref_exists(repo_root: Path, ref: str) -> bool:
    try:
        run(["git", "show-ref", "--verify", "--quiet", ref], cwd=repo_root, capture=False)
        return True
    except subprocess.CalledProcessError:
        return False


def default_base_branch(repo_root: Path) -> str:
    # 优先 origin/HEAD（最贴近“远端默认基线”为真）
    try:
        cp = run(
            ["git", "symbolic-ref", "-q", "--short", "refs/remotes/origin/HEAD"],
            cwd=repo_root,
        )
        ref = cp.stdout.strip()  # origin/main
        if ref.startswith("origin/"):
            return ref.split("/", 1)[1]
    except subprocess.CalledProcessError:
        pass

    for candidate in ("main", "master"):
        if ref_exists(repo_root, f"refs/remotes/origin/{candidate}") or ref_exists(
            repo_root, f"refs/heads/{candidate}"
        ):
            return candidate
    return "main"


def parse_worktree_list(repo_root: Path) -> dict[str, Path]:
    # branch_short -> worktree_path
    cp = run(["git", "worktree", "list", "--porcelain"], cwd=repo_root)
    branch_to_path: dict[str, Path] = {}
    current_path: Optional[Path] = None
    current_branch: Optional[str] = None
    for line in cp.stdout.splitlines():
        if line.startswith("worktree "):
            current_path = Path(line.split(" ", 1)[1].strip())
            current_branch = None
        elif line.startswith("branch "):
            ref = line.split(" ", 1)[1].strip()
            if ref.startswith("refs/heads/"):
                current_branch = ref[len("refs/heads/") :]
        elif line == "" and current_path and current_branch:
            branch_to_path[current_branch] = current_path
            current_path, current_branch = None, None
    if current_path and current_branch:
        branch_to_path[current_branch] = current_path
    return branch_to_path


def shell_quote(s: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9@%_+=:,./-]+", s):
        return s
    return "'" + s.replace("'", "'\"'\"'") + "'"


def ensure_worktree(
    *,
    repo_root: Path,
    branch: str,
    worktree_path: Path,
    base: str,
    dry_run: bool,
    warn: callable,
    die: callable,
) -> None:
    existing = parse_worktree_list(repo_root)
    if branch in existing:
        print(f"[OK] worktree 已存在：{existing[branch]}")
        return

    if worktree_path.exists():
        die(f"目标路径已存在但不是已注册的 worktree：{worktree_path}")

    worktree_path.parent.mkdir(parents=True, exist_ok=True)

    branch_exists = ref_exists(repo_root, f"refs/heads/{branch}")
    base_ref = f"origin/{base}" if ref_exists(repo_root, f"refs/remotes/origin/{base}") else base

    cmds: list[list[str]] = []
    cmds.append(["git", "fetch", "--prune", "origin", base])
    if branch_exists:
        cmds.append(["git", "worktree", "add", str(worktree_path), branch])
    else:
        cmds.append(["git", "worktree", "add", "-b", branch, str(worktree_path), base_ref])

    if dry_run:
        print("[DRY-RUN] 将执行：")
        for c in cmds:
            print("  " + " ".join(shell_quote(x) for x in c))
        return

    # fetch 失败不一定致命（离线/权限等），因此不 check
    run(cmds[0], cwd=repo_root, check=False)
    for c in cmds[1:]:
        try:
            run(c, cwd=repo_root)
        except subprocess.CalledProcessError as e:
            msg = (e.stderr or e.stdout or "").strip()
            die(msg or f"执行失败：{c}")
