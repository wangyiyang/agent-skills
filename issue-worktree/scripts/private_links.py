#!/usr/bin/env python3
"""
将用户的“私密文件”以软链接方式放到 worktree 目标位置。

约束（避免破坏性操作）：
- 默认只创建缺失的链接；目标已存在且不是同一链接时，直接报错；
- --force 仅允许替换“文件/软链接”，不允许删除目录。
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional


def _expand_path(p: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(p))).resolve()


def _is_same_symlink(dest: Path, src: Path) -> bool:
    if not dest.is_symlink():
        return False
    try:
        target = os.readlink(dest)
    except OSError:
        return False

    # readlink 返回的是创建时写入的路径，可能是相对/绝对；统一转绝对后比较
    target_path = (dest.parent / target).resolve() if not os.path.isabs(target) else Path(target).resolve()
    return target_path == src.resolve()


def _parse_links(data: Any, die: callable) -> list[tuple[str, str]]:
    if not isinstance(data, list):
        die("links 配置必须是 JSON array，例如: [{\"src\": \"...\", \"dest\": \".env\"}]")

    out: list[tuple[str, str]] = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            die(f"links[{i}] 必须是 object")
        src = item.get("src") or item.get("source")
        dest = item.get("dest") or item.get("target")
        if not src or not dest:
            die(f"links[{i}] 必须包含 src+dest（或 source+target）")
        out.append((str(src), str(dest)))
    return out


def apply_links(
    *,
    worktree_path: Path,
    links_file: Path,
    dry_run: bool,
    force: bool,
    warn: callable,
    die: callable,
) -> None:
    if not links_file.exists():
        return

    try:
        data = json.loads(links_file.read_text(encoding="utf-8"))
    except Exception as e:
        die(f"解析 links 文件失败：{links_file}：{e}")

    links = _parse_links(data, die)
    if not links:
        return

    print(f"[INFO] links : {links_file}")
    for raw_src, raw_dest in links:
        src = _expand_path(raw_src)
        if not src.exists():
            warn(f"源文件不存在，跳过：{src}")
            continue

        dest_rel = Path(raw_dest)
        if dest_rel.is_absolute() or ".." in dest_rel.parts:
            die(f"dest 必须是 worktree 内的相对路径（禁止绝对路径/..）：{raw_dest}")

        dest = (worktree_path / dest_rel).resolve()
        if not str(dest).startswith(str(worktree_path.resolve()) + os.sep):
            die(f"dest 必须位于 worktree 内：{raw_dest}")

        if dest.exists() or dest.is_symlink():
            if _is_same_symlink(dest, src):
                continue
            if not force:
                die(f"目标已存在且不同：{dest}（用 --link-force 才允许覆盖文件/软链接）")
            if dest.is_dir() and not dest.is_symlink():
                die(f"--link-force 不允许删除目录：{dest}")
            if dry_run:
                print(f"[DRY-RUN] replace {dest} -> {src}")
            else:
                dest.unlink()

        dest.parent.mkdir(parents=True, exist_ok=True)
        if dry_run:
            print(f"[DRY-RUN] ln -s {src} {dest}")
        else:
            os.symlink(src, dest)

