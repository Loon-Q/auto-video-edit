#!/usr/bin/env python3
"""Install or upgrade the complete auto-video-edit skill suite for Codex and Google Antigravity."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys


SKILLS = ("wlj-script-rewrite", "product-video-edit")


def copy_skill(src: Path, dst: Path, upgrade: bool) -> str:
    if src.resolve() == dst.resolve():
        return f"skipped (same path): {dst}"
    if dst.exists() or dst.is_symlink():
        if not upgrade:
            raise RuntimeError(f"目标已存在技能：{dst}（如需覆盖更新请加 --upgrade）")
        if dst.is_symlink() or dst.is_file():
            dst.unlink()
        else:
            shutil.rmtree(dst)
        action = "upgraded"
    else:
        action = "installed"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        src,
        dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".DS_Store"),
    )
    return f"{action}: {dst}"


def global_roots() -> list[Path]:
    home = Path.home()
    roots = [home / ".gemini" / "config" / "skills"]
    codex_dir = home / ".codex"
    if codex_dir.is_dir():
        roots.append(codex_dir / "skills")
    return roots


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", nargs="?", type=Path, default=None, help="剪辑项目目录（安装到 <项目>/.agents/skills/）")
    parser.add_argument("--global", dest="install_global", action="store_true", help="安装到本机全局（Antigravity ~/.gemini/config/skills 与 Codex ~/.codex/skills）")
    parser.add_argument("--upgrade", action="store_true", help="覆盖升级已安装的同名技能")
    parser.add_argument("--with-libtv", action="store_true", help="同时拉取 guizang-magi2-skill 并自动配置双端 LibTV MCP")
    args = parser.parse_args()

    if not args.workspace and not args.install_global:
        parser.error("请指定剪辑项目目录（如 python3 install.py \"/你的/剪辑项目\"），或传入 --global 安装到本机全局。")

    repo_skills_dir = Path(__file__).resolve().parent / ".agents" / "skills"
    target_roots: list[Path] = []

    if args.workspace:
        ws = args.workspace.expanduser().resolve()
        if not ws.is_dir():
            parser.error(f"找不到项目目录：{ws}")
        target_roots.append(ws / ".agents" / "skills")

    if args.install_global:
        target_roots.extend(global_roots())

    results: list[str] = []
    for root in target_roots:
        for skill_name in SKILLS:
            src = repo_skills_dir / skill_name
            if not src.is_dir():
                raise RuntimeError(f"仓库缺少技能目录：{src}")
            results.append(copy_skill(src, root / skill_name, upgrade=args.upgrade))

    for line in results:
        print(line)

    if args.with_libtv:
        libtv_script = repo_skills_dir / "product-video-edit" / "scripts" / "libtv_setup.py"
        cmd = [sys.executable, str(libtv_script), "--apply-codex"]
        if args.workspace:
            cmd += ["--workspace", str(args.workspace.expanduser().resolve())]
        if not args.install_global and args.workspace:
            cmd.append("--no-global-skill")
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as err:
        sys.exit(f"[ERROR] {err}")
