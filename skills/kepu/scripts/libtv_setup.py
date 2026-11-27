#!/usr/bin/env python3
"""Cross-platform installer & symlink-safe fixer for guizang-magi2-skill + LibTV Remote MCP.

Supports Google Antigravity and OpenAI Codex on macOS and Windows:
  1. Clones or updates https://github.com/op7418/guizang-magi2-skill into target skill directory(ies)
  2. Writes ~/.gemini/config/plugins/libtv/{plugin.json, mcp_config.json, assets/libtv-icon.svg}
  3. Avoids the symlink `npx -> npx-cli.js` trap by anchoring on the real `node` bin directory
     and injecting complete GUI-safe PATH entries (macOS + Windows)
  4. Preserves any previously configured OAuth callback port (default 5285) so ~/.mcp-auth tokens stay valid
  5. Sets `timeoutSeconds: 1200` (20 min) for MAGI-2 1080p renders
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

LIBTV_MCP_URL = "https://mcp.liblib.tv/mcp"
GUIZANG_REPO = "https://github.com/op7418/guizang-magi2-skill.git"

LIBTV_ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 48 48" fill="none">
  <rect width="48" height="48" rx="10" fill="#000" />
  <g transform="translate(11.397 15.692)" fill="#fff">
    <path d="M16.5757 16.616H0L0.832729 12.1982H17.6504L16.5757 16.616Z" />
    <path d="M0 16.616L2.31411 4.34598H6.76176L4.4459 16.616H0Z" />
    <path d="M8.26945 0H25.2063L24.3736 4.41609H7.54366L8.26945 0Z" />
    <path d="M25.2062 0L22.8921 12.27L18.3796 12.2718L20.7604 0H25.2062Z" />
  </g>
</svg>
"""


def candidate_node_bins() -> list[Path]:
    home = Path.home()
    dirs: list[Path] = []
    if os.name == "nt":
        for key in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA", "APPDATA"):
            val = os.environ.get(key)
            if val:
                dirs.append(Path(val) / "nodejs")
        dirs += [home / ".volta" / "bin", home / ".fnm" / "current" / "bin"]
    else:
        dirs += [
            home / ".local" / "share" / "node" / "bin",
            home / ".local" / "bin",
            Path("/opt/homebrew/bin"),
            Path("/usr/local/bin"),
            home / ".volta" / "bin",
            home / ".fnm" / "current" / "bin",
        ]
        nvm_dir = home / ".nvm" / "versions" / "node"
        if nvm_dir.is_dir():
            for v in sorted(nvm_dir.iterdir(), reverse=True):
                dirs.insert(0, v / "bin")
    return dirs


def find_node_and_npx() -> tuple[str, list[str]]:
    """Return a symlink-safe npx executable path and ordered PATH directories containing `node`."""
    npx_name = "npx.cmd" if os.name == "nt" else "npx"
    node_name = "node.exe" if os.name == "nt" else "node"

    search_dirs = [str(d) for d in candidate_node_bins() if d.is_dir()]
    merged_path = os.pathsep.join(search_dirs + [os.environ.get("PATH", "")])

    found_node = shutil.which(node_name, path=merged_path) or shutil.which("node", path=merged_path)
    found_npx = shutil.which(npx_name, path=merged_path) or shutil.which("npx", path=merged_path)

    path_Front: list[str] = []
    npx_cmd: str | None = None

    if found_node:
        # `node` itself is a real binary, so resolving it yields the true bin dir (never npm/bin/npx-cli.js!)
        real_node_bin = Path(found_node).resolve().parent
        orig_node_bin = Path(os.path.abspath(found_node)).parent
        for d in (real_node_bin, orig_node_bin):
            if str(d) not in path_Front:
                path_Front.append(str(d))
        sibling_npx = real_node_bin / npx_name
        if sibling_npx.exists():
            npx_cmd = str(sibling_npx)

    if not npx_cmd and found_npx:
        # Keep the bin wrapper path without resolving into node_modules/npm/bin/npx-cli.js
        abs_npx = Path(os.path.abspath(found_npx))
        npx_cmd = str(abs_npx)
        if str(abs_npx.parent) not in path_Front:
            path_Front.append(str(abs_npx.parent))

    if not npx_cmd:
        npx_cmd = npx_name

    return npx_cmd, path_Front


def build_clean_path(front_dirs: list[str]) -> str:
    custom = os.environ.get("KEPU_RUNTIME") or os.environ.get("PRODUCT_VIDEO_RUNTIME")
    legacy_rt = Path.home() / ".local" / "share" / "product-video-edit"
    kepu_rt = Path.home() / ".local" / "share" / "kepu-video"
    runtime_root = Path(custom) if custom else (kepu_rt if kepu_rt.exists() else (legacy_rt if legacy_rt.exists() else kepu_rt))
    extra = list(front_dirs) + [str(runtime_root / "bin")]
    if os.name == "nt":
        sys_entries = [p for p in os.environ.get("PATH", "").split(os.pathsep) if p]
        extra += sys_entries
    else:
        extra += [
            str(Path.home() / ".local" / "bin"),
            "/opt/homebrew/bin",
            "/usr/local/bin",
            "/usr/bin",
            "/bin",
        ]
    dedup: list[str] = []
    for d in extra:
        if d and d not in dedup:
            dedup.append(d)
    return os.pathsep.join(dedup)


def read_existing_port(mcp_cfg_path: Path) -> str | None:
    if not mcp_cfg_path.is_file():
        return None
    try:
        cfg = json.loads(mcp_cfg_path.read_text(encoding="utf-8"))
        srv_args = cfg.get("mcpServers", {}).get("libtv", {}).get("args", [])
        for tok in srv_args:
            if str(tok).isdigit():
                return str(tok)
    except Exception:
        return None
    return None


def sync_guizang_skill(targets: list[Path], git_bin: str) -> list[str]:
    synced: list[str] = []
    for dest in targets:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if (dest / ".git").exists():
            subprocess.run([git_bin, "-C", str(dest), "pull", "--ff-only", "--quiet"], check=False)
            synced.append(f"updated: {dest}")
        elif (dest / "SKILL.md").is_file():
            synced.append(f"kept existing: {dest}")
        else:
            if dest.exists():
                shutil.rmtree(dest)
            subprocess.run([git_bin, "clone", "--depth", "1", GUIZANG_REPO, str(dest)], check=True)
            synced.append(f"cloned: {dest}")
    return synced


def configure_libtv(
    skill_targets: list[Path] | None = None,
    plugin_dir: Path | None = None,
    proxy: str | None = None,
    no_proxy: bool = True,
    port: str | None = None,
    timeout_sec: int = 1200,
    apply_codex: bool = False,
) -> dict:
    git_bin = shutil.which("git")
    synced_skills: list[str] = []
    if skill_targets:
        if not git_bin:
            raise RuntimeError("找不到 git，无法拉取 guizang-magi2-skill。")
        synced_skills = sync_guizang_skill(skill_targets, git_bin)

    target_plugin = (plugin_dir or (Path.home() / ".gemini" / "config" / "plugins" / "libtv")).expanduser().resolve()
    mcp_cfg_path = target_plugin / "mcp_config.json"

    chosen_port = port if port is not None else (read_existing_port(mcp_cfg_path) or "5285")
    npx_cmd, front_dirs = find_node_and_npx()
    clean_path = build_clean_path(front_dirs)

    proxy_url: str | None = None
    if not no_proxy:
        proxy_url = proxy.strip() if proxy else None
        if not proxy_url:
            for k in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy"):
                v = os.environ.get(k, "").strip()
                if v:
                    proxy_url = v
                    break

    env_map: dict[str, str] = {"PATH": clean_path}
    if proxy_url:
        env_map["NODE_USE_ENV_PROXY"] = "1"
        env_map["HTTPS_PROXY"] = proxy_url
        env_map["HTTP_PROXY"] = proxy_url

    args_list = ["-y", "mcp-remote", LIBTV_MCP_URL]
    if chosen_port:
        args_list.append(str(chosen_port))

    plugin_manifest = {
        "name": "libtv",
        "displayName": "LibTV",
        "version": "1.0.0",
        "description": "LibTV 视觉创作插件：连接 LibTV Remote MCP，调用 MAGI-2 与 Seedream 生成视频与透明底素材、编排多模态画布节点。",
        "author": {"name": "LiblibAI", "url": "https://www.liblib.tv"},
        "homepage": "https://www.liblib.tv",
        "repository": "https://github.com/liblib-ai/marketplace",
        "logo": "assets/libtv-icon.svg",
        "suggestedPrompts": [
            "查看我在 LibTV 中的项目和可用视频模型",
            "用 MAGI-2 全能参考模式结合画布节点生成一段 10 秒视频",
            "用 Code to Video 静音动作灰盒配合设定图生成一段精准卡点视频",
        ],
    }
    mcp_cfg = {
        "mcpServers": {
            "libtv": {
                "command": npx_cmd,
                "args": args_list,
                "env": env_map,
                "timeoutSeconds": timeout_sec,
            }
        }
    }

    (target_plugin / "assets").mkdir(parents=True, exist_ok=True)
    (target_plugin / "plugin.json").write_text(
        json.dumps(plugin_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    mcp_cfg_path.write_text(json.dumps(mcp_cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (target_plugin / "assets" / "libtv-icon.svg").write_text(LIBTV_ICON_SVG, encoding="utf-8")

    codex_status = f"codex mcp add libtv --url {LIBTV_MCP_URL}"
    if apply_codex:
        codex_bin = shutil.which("codex", path=clean_path)
        if codex_bin:
            res = subprocess.run([codex_bin, "mcp", "add", "libtv", "--url", LIBTV_MCP_URL], capture_output=True, text=True)
            codex_status = "configured" if res.returncode == 0 else (res.stderr.strip() or res.stdout.strip())

    return {
        "skills": synced_skills,
        "antigravity_plugin": str(target_plugin),
        "npx": npx_cmd,
        "callback_port": chosen_port,
        "timeoutSeconds": timeout_sec,
        "proxy": proxy_url or "direct",
        "codex_mcp": codex_status,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="一键拉取 guizang-magi2-skill 并配置 Antigravity / Codex 的 LibTV MCP。")
    ap.add_argument("--workspace", type=Path, default=None, help="可选：同时安装到指定剪辑项目的 .agents/skills/")
    ap.add_argument("--no-global-skill", action="store_true", help="不安装到 ~/.gemini/config/skills 与 ~/.codex/skills")
    ap.add_argument("--proxy", default=None, help="显式指定代理地址（如 http://127.0.0.1:7890）；默认国内直连更快更稳")
    ap.add_argument("--use-shell-proxy", action="store_true", help="读取当前终端环境变量中的代理")
    ap.add_argument("--port", default=None, help="OAuth 本地回调端口（默认保留已有配置或使用 5285）")
    ap.add_argument("--apply-codex", action="store_true", help="若本机已装 codex CLI，自动执行 codex mcp add")
    a = ap.parse_args()

    targets: list[Path] = []
    if a.workspace:
        targets.append(a.workspace.expanduser().resolve() / ".agents" / "skills" / "guizang-magi2-skill")
    if not a.no_global_skill:
        targets.append(Path.home() / ".gemini" / "config" / "skills" / "guizang-magi2-skill")
        codex_root = Path.home() / ".codex" / "skills"
        if codex_root.is_dir():
            targets.append(codex_root / "guizang-magi2-skill")

    info = configure_libtv(
        skill_targets=targets,
        proxy=a.proxy,
        no_proxy=not (bool(a.proxy) or a.use_shell_proxy),
        port=a.port,
        apply_codex=a.apply_codex,
    )
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.exit(f"[ERROR] {exc}")
