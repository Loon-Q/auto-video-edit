#!/usr/bin/env python3
"""Install or upgrade the standalone @kepu (@科普) plugin & skill package for Google Antigravity and Codex."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys

SKILL_NAME = "kepu"
PLUGIN_NAME = "kepu"
# Legacy split skill folders belonging ONLY to earlier versions of this repository
LEGACY_REPO_SKILLS = ("wlj-script-rewrite", "product-video-edit")
IGNORE_PATTERNS = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".DS_Store")


def remove_tree_or_link(p: Path) -> bool:
    if p.is_symlink() or p.is_file():
        p.unlink()
        return True
    if p.exists():
        shutil.rmtree(p)
        return True
    return False


def copy_clean_dir(src: Path, dst: Path, upgrade: bool) -> str:
    if src.resolve() == dst.resolve():
        return f"skipped (same path): {dst}"
    if dst.exists() or dst.is_symlink():
        if not upgrade:
            raise RuntimeError(f"目标已存在：{dst}（如需覆盖升级请加 --upgrade）")
        remove_tree_or_link(dst)
        action = "upgraded"
    else:
        action = "installed"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, ignore=IGNORE_PATTERNS)
    return f"{action}: {dst}"


def install_antigravity_plugin(repo_root: Path, upgrade: bool) -> list[str]:
    """Package and install `~/.gemini/config/plugins/kepu` as a native Antigravity Plugin."""
    logs: list[str] = []
    gemini_cfg = Path.home() / ".gemini" / "config"
    plugin_dst = gemini_cfg / "plugins" / PLUGIN_NAME

    if plugin_dst.exists() or plugin_dst.is_symlink():
        if not upgrade:
            raise RuntimeError(f"目标已存在插件：{plugin_dst}（如需覆盖升级请加 --upgrade）")
        remove_tree_or_link(plugin_dst)
        action = "upgraded plugin"
    else:
        action = "installed plugin"

    (plugin_dst / "skills").mkdir(parents=True, exist_ok=True)
    shutil.copy2(repo_root / "plugin.json", plugin_dst / "plugin.json")
    if (repo_root / "README.md").is_file():
        shutil.copy2(repo_root / "README.md", plugin_dst / "README.md")
    if (repo_root / "assets").is_dir():
        shutil.copytree(repo_root / "assets", plugin_dst / "assets", ignore=IGNORE_PATTERNS)
    shutil.copytree(repo_root / "skills" / SKILL_NAME, plugin_dst / "skills" / SKILL_NAME, ignore=IGNORE_PATTERNS)
    logs.append(f"{action}: {plugin_dst}")

    # Clean up ONLY legacy split skills from earlier versions of this repo (and any loose duplicate `skills/kepu`)
    loose_skills_dir = gemini_cfg / "skills"
    if loose_skills_dir.is_dir():
        for old_name in (*LEGACY_REPO_SKILLS, SKILL_NAME):
            old_path = loose_skills_dir / old_name
            if remove_tree_or_link(old_path):
                logs.append(f"cleaned legacy loose skill: {old_path}")

    return logs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", nargs="?", type=Path, default=None, help="可选：指定单个项目目录（安装到 <项目>/.agents/skills/kepu）")
    parser.add_argument(
        "--global",
        dest="install_global",
        action="store_true",
        help="安装到本机全局（Antigravity 原生插件 ~/.gemini/config/plugins/kepu，以及 Codex ~/.codex/skills/kepu 与 ~/.agents/skills/kepu）",
    )
    parser.add_argument("--upgrade", action="store_true", help="覆盖升级已安装的同名插件/技能并清理本仓库旧版散装目录")
    parser.add_argument("--with-libtv", action="store_true", help="同时配置双端 LibTV Remote MCP（MAGI-2 视频生成连接）")
    args = parser.parse_args()

    if not args.workspace and not args.install_global:
        parser.error("请传入 --global 安装到本机全局，或指定项目目录（如 python3 install.py --global --upgrade）。")

    repo_root = Path(__file__).resolve().parent
    skill_src = repo_root / "skills" / SKILL_NAME
    if not skill_src.is_dir():
        raise RuntimeError(f"仓库缺少核心技能目录：{skill_src}")

    results: list[str] = []

    if args.workspace:
        ws = args.workspace.expanduser().resolve()
        if not ws.is_dir():
            parser.error(f"找不到项目目录：{ws}")
        ws_skills = ws / ".agents" / "skills"
        results.append(copy_clean_dir(skill_src, ws_skills / SKILL_NAME, upgrade=args.upgrade))
        if args.upgrade:
            for old_name in LEGACY_REPO_SKILLS:
                if remove_tree_or_link(ws_skills / old_name):
                    results.append(f"cleaned legacy workspace skill: {ws_skills / old_name}")

    if args.install_global:
        results.extend(install_antigravity_plugin(repo_root, upgrade=args.upgrade))
        home = Path.home()
        for optional_parent in (home / ".codex", home / ".agents"):
            if optional_parent.is_dir():
                s_root = optional_parent / "skills"
                results.append(copy_clean_dir(skill_src, s_root / SKILL_NAME, upgrade=args.upgrade))
                if args.upgrade:
                    for old_name in LEGACY_REPO_SKILLS:
                        if remove_tree_or_link(s_root / old_name):
                            results.append(f"cleaned legacy skill: {s_root / old_name}")

    for line in results:
        print(line)

    if args.with_libtv:
        libtv_script = skill_src / "scripts" / "libtv_setup.py"
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
