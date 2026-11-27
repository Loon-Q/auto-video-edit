#!/usr/bin/env python3
"""外部视频无字幕/无水印 8 帧抽帧体检 & `画面来源：XX` 强制登记工具（兼容 macOS 与 Windows）。

子命令：
  1) inspect  : 扫描视频文件或目录，生成带底部字幕高危区参考线的 8 帧/条总览体检图，并初始化/更新 sources_manifest.json
  2) register : 看图核验后，登记某条素材的体检状态（clean / crop_bottom / rejected）与左上角来源文案
  3) check    : 开剪前校验清单——若仍有 unverified 素材，或第三方可用素材未填 source_label，返回非 0 阻断入库
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from _runtime import find_tool

VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".mkv", ".webm"}


def safe_label(text: str) -> str:
    return re.sub(r"[:'\"\\%;,\[\]]", " ", text)


def probe_clip(ffprobe: str, clip: Path) -> dict:
    res = subprocess.run(
        [
            ffprobe, "-v", "error", "-print_format", "json",
            "-show_format", "-show_streams", str(clip),
        ],
        capture_output=True, text=True, encoding="utf-8", check=True,
    )
    info = json.loads(res.stdout)
    streams = info.get("streams", [])
    v = next((s for s in streams if s.get("codec_type") == "video" and not s.get("disposition", {}).get("attached_pic")), {})
    has_audio = any(s.get("codec_type") == "audio" for s in streams)
    dur = float(info.get("format", {}).get("duration") or v.get("duration") or 0.0)
    return {
        "width": v.get("width"),
        "height": v.get("height"),
        "fps": v.get("r_frame_rate"),
        "duration": round(dur, 2),
        "has_audio": has_audio,
    }


def load_manifest(path: Path) -> dict:
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"version": 1, "rule": "第三方素材左上角 22px 白色 70% 不透明度显示 3.0s 后淡出；严禁带入原片硬字幕", "clips": {}}


def save_manifest(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def cmd_inspect(args: argparse.Namespace) -> int:
    ffmpeg = find_tool("ffmpeg")
    ffprobe = find_tool("ffprobe")
    target = Path(args.target).expanduser().resolve()
    if target.is_file():
        clips = [target]
        default_manifest = target.parent / "sources_manifest.json"
    elif target.is_dir():
        clips = sorted(p for p in target.iterdir() if p.is_file() and p.suffix.lower() in VIDEO_EXTS)
        default_manifest = target / "sources_manifest.json"
    else:
        sys.exit(f"[ERROR] 路径不存在：{target}")

    if not clips:
        sys.exit(f"[ERROR] 未找到视频文件：{target}")

    manifest_path = Path(args.manifest).expanduser().resolve() if args.manifest else default_manifest
    manifest = load_manifest(manifest_path)
    sheet_path = Path(args.sheet).expanduser().resolve()
    sheet_path.parent.mkdir(parents=True, exist_ok=True)

    tmp = Path(tempfile.mkdtemp(prefix="wlj-broll-qc-"))
    cols = 8
    cell_w, cell_h = 320, 180
    try:
        cells: list[Path] = []
        for row_idx, clip in enumerate(clips):
            meta = probe_clip(ffprobe, clip)
            dur = max(meta["duration"], 0.5)
            existing = manifest["clips"].get(clip.name, {})
            manifest["clips"][clip.name] = {
                "file": clip.name,
                "width": meta["width"],
                "height": meta["height"],
                "fps": meta["fps"],
                "duration": meta["duration"],
                "has_audio": meta["has_audio"],
                "status": existing.get("status", "unverified"),
                "is_third_party": existing.get("is_third_party", True),
                "source_label": existing.get("source_label", ""),
                "display_text": existing.get("display_text", ""),
                "shots": existing.get("shots", []),
                "notes": existing.get("notes", ""),
            }
            print(f"[{row_idx + 1:02d}/{len(clips):02d}] {clip.name} ({meta['width']}x{meta['height']}, {dur:.2f}s) -> status={manifest['clips'][clip.name]['status']}")

            for c_idx in range(cols):
                ts = round(dur * (c_idx + 0.5) / cols, 2)
                cell_img = tmp / f"r{row_idx:03d}_c{c_idx:02d}.jpg"
                hdr = safe_label(f"{clip.stem[:18]} @{ts:.1f}s" if c_idx == 0 else f"@{ts:.1f}s")
                # Red horizontal guide at y=140 (78% of 180px) marks the bottom 22% subtitle danger zone!
                base_vf = (
                    f"scale={cell_w}:{cell_h}:force_original_aspect_ratio=decrease,"
                    f"pad={cell_w}:{cell_h}:(ow-iw)/2:(oh-ih)/2:black,"
                    f"drawbox=x=0:y=140:w={cell_w}:h=2:color=red@0.75:t=fill"
                )
                txt_vf = f"{base_vf},drawtext=text='{hdr}':x=4:y=4:fontsize=13:fontcolor=yellow:box=1:boxcolor=black@0.75"
                r = subprocess.run(
                    [ffmpeg, "-v", "error", "-y", "-ss", str(ts), "-i", str(clip), "-frames:v", "1", "-vf", txt_vf, str(cell_img)],
                    capture_output=True,
                )
                if r.returncode != 0 or not cell_img.is_file():
                    subprocess.run(
                        [ffmpeg, "-v", "error", "-y", "-ss", "0", "-i", str(clip), "-frames:v", "1", "-vf", base_vf, str(cell_img)],
                        capture_output=True,
                    )
                if cell_img.is_file():
                    cells.append(cell_img)

        total_cells = len(cells)
        if total_cells == 1:
            shutil.copy2(cells[0], sheet_path)
        elif total_cells > 1:
            inputs = sum((["-i", str(p)] for p in cells), [])
            fc = "".join(f"[{i}:v]setsar=1[v{i}];" for i in range(total_cells)) + "".join(f"[v{i}]" for i in range(total_cells))
            layout = "|".join(f"{(i % cols) * cell_w}_{(i // cols) * cell_h}" for i in range(total_cells))
            subprocess.run(
                [
                    ffmpeg, "-v", "error", "-y", *inputs,
                    "-filter_complex", f"{fc}xstack=inputs={total_cells}:layout={layout}:fill=0x101216",
                    "-frames:v", "1", str(sheet_path),
                ],
                check=True,
            )

        save_manifest(manifest_path, manifest)
        print(f"[OK] 8帧字幕体检图已生成：{sheet_path}（红线以下为底部硬字幕高危区，请务必打开逐条核看）")
        print(f"[OK] 来源登记表已更新：{manifest_path}")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def cmd_register(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest).expanduser().resolve()
    manifest = load_manifest(manifest_path)
    name = Path(args.clip).name
    entry = manifest["clips"].setdefault(name, {"file": name})
    entry["status"] = args.status
    is_tp = not args.own
    entry["is_third_party"] = is_tp
    src_raw = (args.source or "").strip()
    if src_raw.startswith("画面来源：") or src_raw.startswith("画面来源:"):
        src_raw = re.sub(r"^画面来源[：:]\s*", "", src_raw)
    entry["source_label"] = src_raw if is_tp else ""
    entry["display_text"] = f"画面来源：{src_raw}" if (is_tp and src_raw) else ""
    if args.shots is not None:
        entry["shots"] = [s.strip() for s in args.shots.split(",") if s.strip()]
    if args.notes is not None:
        entry["notes"] = args.notes
    save_manifest(manifest_path, manifest)
    print(json.dumps(entry, ensure_ascii=False, indent=2))
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest).expanduser().resolve()
    if not manifest_path.is_file():
        sys.exit(f"[ERROR] 找不到来源登记表：{manifest_path}")
    manifest = load_manifest(manifest_path)
    clips = manifest.get("clips", {})
    if not clips:
        sys.exit(f"[ERROR] 来源登记表为空：{manifest_path}")

    problems: list[str] = []
    usable = 0
    for name, c in clips.items():
        st = c.get("status", "unverified")
        if st == "unverified":
            problems.append(f"{name}: 尚未看图核验 (status=unverified)")
        elif st in ("clean", "crop_bottom"):
            usable += 1
            if c.get("is_third_party", True) and not c.get("source_label"):
                problems.append(f"{name}: 第三方可用素材缺少来源标注 (--source)")
            if st == "crop_bottom" and not c.get("notes"):
                problems.append(f"{name}: status=crop_bottom 必须在 --notes 中注明底部裁切比例")

    if problems:
        print("[FAIL] 素材入库校验未通过：")
        for p in problems:
            print("  -", p)
        return 1

    print(f"[PASS] 全部素材已核验通过（共 {len(clips)} 条，可用 {usable} 条，弃用 {len(clips) - usable} 条）。")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description="外部素材 8 帧无字幕体检与 `画面来源：XX` 清单管理工具。")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_in = sub.add_parser("inspect", help="生成 8 帧/条字幕体检图并初始化/更新 sources_manifest.json")
    p_in.add_argument("target", help="视频文件或外部素材目录")
    p_in.add_argument("--sheet", required=True, help="输出体检总览图路径（.jpg / .png）")
    p_in.add_argument("--manifest", default=None, help="sources_manifest.json 路径（默认写在素材目录下）")

    p_reg = sub.add_parser("register", help="看图核验后登记素材状态与左上角来源文字")
    p_reg.add_argument("manifest", help="sources_manifest.json 路径")
    p_reg.add_argument("clip", help="视频文件名")
    p_reg.add_argument("--status", choices=("clean", "crop_bottom", "rejected"), required=True, help="体检结论")
    grp = p_reg.add_mutually_exclusive_group()
    grp.add_argument("--third-party", action="store_true", help="第三方素材（需标左上 22px 来源小字，默认）")
    grp.add_argument("--own", action="store_true", help="自有实拍 / 画布 / LibTV 生成（不标来源小字）")
    p_reg.add_argument("--source", default=None, help="来源名称，如 'Mattel (1985)' 或 'Fast Company (2015)'")
    p_reg.add_argument("--shots", default=None, help="使用该素材的镜号，逗号分隔，如 '1-8,1-9'")
    p_reg.add_argument("--notes", default=None, help="备注（crop_bottom 时必填裁切放大比例）")

    p_chk = sub.add_parser("check", help="开剪前校验清单是否全部完成无字幕核验与来源登记")
    p_chk.add_argument("manifest", help="sources_manifest.json 路径")

    args = ap.parse_args()
    if args.cmd == "inspect":
        sys.exit(cmd_inspect(args))
    if args.cmd == "register":
        sys.exit(cmd_register(args))
    sys.exit(cmd_check(args))


if __name__ == "__main__":
    main()
