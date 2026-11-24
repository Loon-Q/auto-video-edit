#!/usr/bin/env python3
"""Local setup, rough cutting, and native OpenMotion commands on macOS and Windows."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import venv

from openmotion_rpc import run_mcp


ROOT = Path(os.environ.get("PRODUCT_VIDEO_RUNTIME") or Path.home() / ".local/share/product-video-edit").resolve()
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "openmotion"
UPSTREAM = "https://github.com/nexu-io/openmotion.git"
REVISION = "a44c714d0e702f3b9b02be8a7512bbf278c6294b"
MIN_NODE = (22, 18, 0)


def media_env():
    env = os.environ.copy()
    env["PATH"] = str(ROOT / "bin") + os.pathsep + env.get("PATH", "")
    env["OPENMOTION_TELEMETRY"] = "0"
    env["PYTHONIOENCODING"] = "utf-8"
    for binary in ("ffmpeg", "ffprobe"):
        found = shutil.which(binary, path=env["PATH"])
        if found:
            env["HYPERFRAMES_" + binary.upper() + "_PATH"] = str(Path(found).resolve())
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


def numpy_ready(env):
    return subprocess.run([video_python(), "-c", "import numpy"], env=env, capture_output=True).returncode == 0


def require_media(env):
    missing = [x for x in ("FFMPEG", "FFPROBE", "BROWSER") if not env.get("HYPERFRAMES_" + x + "_PATH")]
    if missing:
        raise RuntimeError("还缺少 " + "、".join(missing) + "。请看安装说明并运行 doctor。")


def source_ready():
    return (SOURCE / "mcp.ts").is_file() and (SOURCE / "studio/build/index.html").is_file() and (SOURCE / "node_modules").is_dir()


def doctor(env):
    try:
        node = output([node_command(env), "--version"], env)
    except (RuntimeError, subprocess.CalledProcessError):
        node = None
    states = {
        "python": sys.version.split()[0],
        "numpy": numpy_ready(env),
        "git": shutil.which("git", path=env["PATH"]),
        "node": node,
        "npm": shutil.which("npm", path=env["PATH"]),
        "ffmpeg": env.get("HYPERFRAMES_FFMPEG_PATH"),
        "ffprobe": env.get("HYPERFRAMES_FFPROBE_PATH"),
        "chrome": env.get("HYPERFRAMES_BROWSER_PATH"),
        "openmotion": str(SOURCE) if source_ready() else None,
    }
    print(json.dumps(states, ensure_ascii=False, indent=2))
    return 0 if all(states[k] for k in ("numpy", "node", "ffmpeg", "ffprobe", "chrome", "openmotion")) else 1


def setup(env):
    node_command(env)
    require_media(env)
    git = binary("git", env)
    npm = binary("npm", env)
    ROOT.mkdir(parents=True, exist_ok=True)
    if not numpy_ready(env):
        venv.EnvBuilder(with_pip=True).create(ROOT / "venv")
        subprocess.run([video_python(), "-m", "pip", "install", "numpy==2.3.5"], env=env, check=True)

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
    commands.add_parser("setup")
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
        return setup(env)
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
