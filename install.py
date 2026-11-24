#!/usr/bin/env python3
"""Copy the complete skill into a Codex or Antigravity project."""
import argparse
from pathlib import Path
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path, help="剪辑项目目录")
    args = parser.parse_args()
    workspace = args.workspace.expanduser().resolve()
    if not workspace.is_dir():
        parser.error(f"找不到项目目录：{workspace}")
    source = Path(__file__).resolve().parent / ".agents/skills/product-video-edit"
    destination = workspace / ".agents/skills/product-video-edit"
    if source == destination:
        print(f"项目已包含自动剪辑技能：{destination}")
        return
    if destination.exists() or destination.is_symlink():
        parser.error(f"目标已有技能：{destination}。先备份或移开旧版本。")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    print(f"已安装到：{destination}")


if __name__ == "__main__":
    main()
