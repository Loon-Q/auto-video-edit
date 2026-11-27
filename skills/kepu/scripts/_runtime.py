#!/usr/bin/env python3
"""Cross-platform runtime & binary discovery for @kepu / @科普 (macOS + Windows)."""
from __future__ import annotations

import importlib
import os
from pathlib import Path
import shutil
import subprocess
import sys


def runtime_root() -> Path:
    custom = os.environ.get("KEPU_RUNTIME") or os.environ.get("PRODUCT_VIDEO_RUNTIME")
    if custom:
        return Path(custom).expanduser().resolve()
    kepu_rt = Path.home() / ".local" / "share" / "kepu-video"
    legacy_rt = Path.home() / ".local" / "share" / "product-video-edit"
    if kepu_rt.exists():
        return kepu_rt.resolve()
    if legacy_rt.exists():
        return legacy_rt.resolve()
    return kepu_rt.resolve()


def venv_dir() -> Path:
    return runtime_root() / "venv"


def venv_bin_dir() -> Path:
    return venv_dir() / ("Scripts" if os.name == "nt" else "bin")


def venv_python() -> Path | None:
    cand = venv_bin_dir() / ("python.exe" if os.name == "nt" else "python")
    return cand if cand.is_file() else None


def ensure_packages(*modules: str) -> None:
    """Ensure Python packages are importable; transparently re-exec into runtime venv if needed."""
    missing = []
    for mod in modules:
        try:
            importlib.import_module(mod)
        except ImportError:
            missing.append(mod)
    if not missing:
        return

    vp = venv_python()
    if vp and os.environ.get("_KEPU_REEXEC") != "1":
        try:
            same = Path(sys.executable).resolve() == vp.resolve()
        except OSError:
            same = False
        if not same:
            env = os.environ.copy()
            env["_KEPU_REEXEC"] = "1"
            env["PYTHONIOENCODING"] = "utf-8"
            if os.name == "nt":
                sys.exit(subprocess.call([str(vp), *sys.argv], env=env))
            os.execve(str(vp), [str(vp), *sys.argv], env)

    setup_script = Path(__file__).resolve().parent / "video_edit.py"
    mods_str = ", ".join(missing)
    sys.exit(
        f"[ERROR] 当前 Python 环境缺少依赖：{mods_str}\n"
        f"请先运行：python3 \"{setup_script}\" setup\n"
        f"（Windows PowerShell 使用：py -3 \"{setup_script}\" setup）"
    )


def search_path() -> str:
    root = runtime_root()
    extra = [
        str(root / "bin"),
        str(venv_bin_dir()),
        str(Path.home() / ".local" / "bin"),
    ]
    if sys.platform == "darwin":
        extra += ["/opt/homebrew/bin", "/usr/local/bin"]
    cur = os.environ.get("PATH", "")
    parts = [p for p in extra + cur.split(os.pathsep) if p]
    dedup: list[str] = []
    for p in parts:
        if p not in dedup:
            dedup.append(p)
    return os.pathsep.join(dedup)


def find_tool(name: str) -> str:
    env_override = os.environ.get(f"HYPERFRAMES_{name.upper()}_PATH")
    if env_override and Path(env_override).is_file():
        return str(Path(env_override).resolve())
    found = shutil.which(name, path=search_path())
    if found:
        return str(Path(found).resolve())
    sys.exit(
        f"[ERROR] 找不到命令行工具 `{name}`。\n"
        f"请确认已安装 `{name}` 并加入 PATH，或先运行 `video_edit.py setup` / `video_edit.py doctor` 检查环境。"
    )
