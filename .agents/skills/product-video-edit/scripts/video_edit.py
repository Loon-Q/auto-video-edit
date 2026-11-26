#!/usr/bin/env python3
"""Local setup, rough cutting, LibTV integration, and native OpenMotion commands on macOS and Windows."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import venv

from libtv_setup import configure_libtv
from openmotion_rpc import run_mcp


ROOT = Path(os.environ.get("PRODUCT_VIDEO_RUNTIME") or Path.home() / ".local/share/product-video-edit").resolve()
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "openmotion"
UPSTREAM = "https://github.com/nexu-io/openmotion.git"
REVISION = "a44c714d0e702f3b9b02be8a7512bbf278c6294b"
MIN_NODE = (22, 18, 0)
CORE_PIP_PACKAGES = ("numpy==2.3.5", "faster-whisper", "yt-dlp")
STICKER_PIP_PACKAGES = ("pillow", "scipy")


def venv_bin_dir():
    return ROOT / "venv" / ("Scripts" if os.name == "nt" else "bin")


def media_env():
    env = os.environ.copy()
    extra_dirs = [str(ROOT / "bin"), str(venv_bin_dir()), str(Path.home() / ".local" / "bin")]
    if sys.platform == "darwin":
        extra_dirs += [str(Path.home() / ".local/share/node/bin"), "/opt/homebrew/bin", "/usr/local/bin"]
    env["PATH"] = os.pathsep.join(extra_dirs + [env.get("PATH", "")])
    env["OPENMOTION_TELEMETRY"] = "0"
    env["PYTHONIOENCODING"] = "utf-8"
    for binary_name in ("ffmpeg", "ffprobe"):
        found = shutil.which(binary_name, path=env["PATH"])
        if found:
            env["HYPERFRAMES_" + binary_name.upper() + "_PATH"] = str(Path(found).resolve())
    chrome_var = env.get("HYPERFRAMES_BROWSER_PATH") or env.get("MOTION_BROWSER_PATH")
    candidates = ["google-chrome", "chromium", "chromium-browser", "chrome"]
    guesses = [Path(p) for p in (shutil.which(n, path=env["PATH"]) for n in candidates) if p]
    if sys.platform == "darwin":
        guesses += [root / "Google Chrome.app/Contents/MacOS/Google Chrome"
                    for root in (Path("/Applications"), Path.home() / "Applications")]
    if os.name == "nt":
        guesses += [Path(env[key]) / "Google/Chrome/Application/chrome.exe"
                    for key in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA") if env.get(key)]
    if chrome_var:
        guesses.insert(0, Path(chrome_var))
    chrome = next((p.resolve() for p in guesses if p.is_file()), None)
    if chrome:
        env["HYPERFRAMES_BROWSER_PATH"] = str(chrome)
        env["MOTION_BROWSER_PATH"] = str(chrome)
    return env


def binary(name, env):
    path = shutil.which(name, path=env["PATH"])
    if not path:
        raise RuntimeError(f"找不到 {name}。安装后打开新终端，再运行 doctor。")
    return path


def output(args, env, cwd=None):
    return subprocess.check_output(args, env=env, cwd=cwd, text=True, encoding="utf-8").strip()


def node_command(env):
    node = binary("node", env)
    version = output([node, "--version"], env).lstrip("v").split("-")[0]
    if tuple(map(int, version.split("."))) < MIN_NODE:
        raise RuntimeError(f"需要 Node.js 22.18+，当前为 {version}。")
    return node


def video_python():
    relative = "Scripts/python.exe" if os.name == "nt" else "bin/python"
    path = ROOT / "venv" / relative
    return str(path) if path.is_file() else sys.executable


def module_ready(mod_name, env):
    return subprocess.run(
        [video_python(), "-c", f"import {mod_name}"], env=env, capture_output=True
    ).returncode == 0


def require_media(env):
    missing = [x for x in ("FFMPEG", "FFPROBE", "BROWSER") if not env.get("HYPERFRAMES_" + x + "_PATH")]
    if missing:
        raise RuntimeError("还缺少 " + "、".join(missing) + "。请看安装说明并运行 doctor。")


def source_ready():
    return (SOURCE / "mcp.ts").is_file() and (SOURCE / "studio/build/index.html").is_file() and (SOURCE / "node_modules").is_dir()


def detect_guizang_skill():
    candidates = [
        HERE.parent.parent / "guizang-magi2-skill" / "SKILL.md",
        Path.home() / ".gemini" / "config" / "skills" / "guizang-magi2-skill" / "SKILL.md",
        Path.home() / ".codex" / "skills" / "guizang-magi2-skill" / "SKILL.md",
    ]
    found = next((p.parent for p in candidates if p.is_file()), None)
    return str(found) if found else None


def detect_libtv_mcp():
    agy_cfg = Path.home() / ".gemini" / "config" / "plugins" / "libtv" / "mcp_config.json"
    return str(agy_cfg) if agy_cfg.is_file() else None


def doctor(env):
    try:
        node = output([node_command(env), "--version"], env)
    except (RuntimeError, subprocess.CalledProcessError):
        node = None
    states = {
        "python": sys.version.split()[0],
        "venv_python": video_python(),
        "numpy": module_ready("numpy", env),
        "faster_whisper": module_ready("faster_whisper", env),
        "yt_dlp": bool(shutil.which("yt-dlp", path=env["PATH"])) or module_ready("yt_dlp", env),
        "lark_cli": shutil.which("lark-cli", path=env["PATH"]),
        "git": shutil.which("git", path=env["PATH"]),
        "node": node,
        "npm": shutil.which("npm", path=env["PATH"]),
        "ffmpeg": env.get("HYPERFRAMES_FFMPEG_PATH"),
        "ffprobe": env.get("HYPERFRAMES_FFPROBE_PATH"),
        "chrome": env.get("HYPERFRAMES_BROWSER_PATH"),
        "openmotion": str(SOURCE) if source_ready() else None,
        "guizang_magi2_skill": detect_guizang_skill(),
        "libtv_mcp": detect_libtv_mcp(),
    }
    print(json.dumps(states, ensure_ascii=False, indent=2))
    core_keys = ("numpy", "faster_whisper", "yt_dlp", "node", "ffmpeg", "ffprobe", "chrome", "openmotion")
    return 0 if all(states[k] for k in core_keys) else 1


def setup(env, with_stickers=False, with_libtv=False):
    node_command(env)
    require_media(env)
    git = binary("git", env)
    npm = binary("npm", env)
    ROOT.mkdir(parents=True, exist_ok=True)

    if not Path(video_python()).is_file() or Path(video_python()).resolve() == Path(sys.executable).resolve():
        if not (ROOT / "venv").is_dir():
            venv.EnvBuilder(with_pip=True).create(ROOT / "venv")

    needed_mods = [("numpy", "numpy==2.3.5"), ("faster_whisper", "faster-whisper"), ("yt_dlp", "yt-dlp")]
    if with_stickers:
        needed_mods += [("PIL", "pillow"), ("scipy", "scipy")]
    missing_pkgs = [pkg for mod, pkg in needed_mods if not module_ready(mod, env)]
    if missing_pkgs:
        subprocess.run([video_python(), "-m", "pip", "install", *missing_pkgs], env=env, check=True)

    if SOURCE.exists():
        actual = output([git, "rev-parse", "HEAD"], env, SOURCE)
        if actual != REVISION:
            raise RuntimeError(f"{SOURCE} 有另一个 OpenMotion 版本。请为本包选择独立的 PRODUCT_VIDEO_RUNTIME。")
    if not source_ready():
        build_env = {**env, "GIT_LFS_SKIP_SMUDGE": "1"}
        with tempfile.TemporaryDirectory(prefix="openmotion-setup-", dir=ROOT) as temp:
            checkout = Path(temp) if not SOURCE.exists() else SOURCE
            if checkout != SOURCE:
                for args in (
                    ["init", "--quiet"],
                    ["remote", "add", "origin", UPSTREAM],
                    ["fetch", "--depth", "1", "origin", REVISION],
                    ["-c", "filter.lfs.required=false", "checkout", "--detach", "FETCH_HEAD"],
                ):
                    subprocess.run([git, *args], cwd=checkout, env=build_env, check=True)
            for args in (["ci"], ["run", "build:studio"]):
                subprocess.run([npm, *args], cwd=checkout, env=build_env, check=True)
            if checkout != SOURCE:
                checkout.rename(SOURCE)

    if with_libtv:
        targets = [Path.home() / ".gemini" / "config" / "skills" / "guizang-magi2-skill"]
        if (Path.home() / ".codex" / "skills").is_dir():
            targets.append(Path.home() / ".codex" / "skills" / "guizang-magi2-skill")
        configure_libtv(skill_targets=targets, apply_codex=True)

    return doctor(env)


def openmotion(args, env):
    if not source_ready():
        raise RuntimeError("OpenMotion 还需要安装，请先运行 setup。")
    require_media(env)
    env["MOTION_DATA_DIR"] = str(args.workspace.resolve())
    entry = "preview.ts" if args.mode == "studio" else "mcp.ts"
    command = [node_command(env), "--experimental-strip-types", entry]
    if args.mode == "tools":
        listing = run_mcp(command, SOURCE, env)
        print(json.dumps(listing, ensure_ascii=False, indent=2))
        return 0
    if args.mode != "call":
        return subprocess.call(command, cwd=SOURCE, env=env)
    if len(args.tool_args) != 2:
        raise ValueError("用法：openmotion call 工作区 工具名 参数.json")
    name, path = args.tool_args
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("工具参数必须是 JSON 对象")
    result = run_mcp(command, SOURCE, env, name, payload)
    print(json.dumps(result.get("structuredContent", result), ensure_ascii=False, indent=2))
    return int(bool(result.get("isError")))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor")

    setup_p = commands.add_parser("setup")
    setup_p.add_argument("--with-stickers", action="store_true", help="同时安装刀版白边贴纸所需的 pillow 与 scipy")
    setup_p.add_argument("--with-libtv", action="store_true", help="同时拉取 guizang-magi2-skill 并配置 LibTV MCP")

    libtv_p = commands.add_parser("libtv")
    libtv_p.add_argument("libtv_args", nargs=argparse.REMAINDER)

    rough = commands.add_parser("rough")
    rough.add_argument("rough_args", nargs=argparse.REMAINDER)

    motion = commands.add_parser("openmotion")
    motion.add_argument("mode", choices=("studio", "mcp", "tools", "call"))
    motion.add_argument("workspace", type=Path)
    motion.add_argument("tool_args", nargs=argparse.REMAINDER)

    args = parser.parse_args()
    env = media_env()
    if args.command == "doctor":
        return doctor(env)
    if args.command == "setup":
        return setup(env, with_stickers=args.with_stickers, with_libtv=args.with_libtv)
    if args.command == "libtv":
        return subprocess.call([sys.executable, str(HERE / "libtv_setup.py"), *args.libtv_args], env=env)
    if args.command == "rough":
        for tool in ("ffmpeg", "ffprobe"):
            binary(tool, env)
        return subprocess.call([video_python(), str(HERE / "rough_cut.py"), *args.rough_args], env=env)
    return openmotion(args, env)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))
