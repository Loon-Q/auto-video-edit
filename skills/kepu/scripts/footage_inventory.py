#!/usr/bin/env python3
"""给实拍素材目录出一张缩略总览图（每条取第 2 秒一帧，带编号与文件名），供看图盘点。

用法（兼容 macOS 与 Windows）：
  python3 footage_inventory.py <素材目录> <输出.jpg> [--recursive] [--cols 6]
  py -3 footage_inventory.py "D:\\项目\\02_实拍素材" inv_v1.jpg --recursive

注意：看图工具可能缓存同名文件，重出时请换输出文件名。
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from _runtime import find_tool


def safe_drawtext_label(raw: str) -> str:
    return re.sub(r"[:'\"\\%;,\[\]]", " ", raw)


def main() -> None:
    ap = argparse.ArgumentParser(description="生成实拍视频目录的缩略图总览表。")
    ap.add_argument("folder", help="视频素材目录")
    ap.add_argument("out", help="输出总览图路径（.jpg / .png）")
    ap.add_argument("--recursive", action="store_true", help="递归扫描子目录")
    ap.add_argument("--cols", type=int, default=6, help="每行列数（默认：6）")
    ap.add_argument("--at", type=float, default=2.0, help="抽取第几秒的画面（默认：2.0）")
    a = ap.parse_args()

    ffmpeg = find_tool("ffmpeg")
    folder = Path(a.folder)
    if not folder.is_dir():
        raise SystemExit(f"[ERROR] 素材目录不存在：{folder}")

    pat = "**/*" if a.recursive else "*"
    files = sorted(
        p for p in folder.glob(pat)
        if p.is_file() and p.suffix.lower() in (".mp4", ".mov", ".m4v", ".mkv")
    )
    if not files:
        raise SystemExit(f"[ERROR] 在 {folder} 中未找到视频文件。")

    out_path = Path(a.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="wlj-inv-"))
    try:
        thumbs: list[Path] = []
        for i, f in enumerate(files, 1):
            t = tmp / f"{i:03d}.jpg"
            label = safe_drawtext_label(f"{i:02d} {f.stem}")
            base_vf = "scale=480:270:force_original_aspect_ratio=decrease,pad=480:270:(ow-iw)/2:(oh-ih)/2:black"
            text_vf = (
                f"{base_vf},"
                f"drawtext=text='{label}':x=6:y=6:fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.7"
            )
            # Try with drawtext first; fall back cleanly if FFmpeg build lacks libfreetype
            res = subprocess.run(
                [ffmpeg, "-v", "error", "-y", "-ss", str(a.at), "-i", str(f), "-frames:v", "1", "-vf", text_vf, str(t)],
                capture_output=True,
            )
            if res.returncode != 0 or not t.is_file():
                subprocess.run(
                    [ffmpeg, "-v", "error", "-y", "-ss", "0", "-i", str(f), "-frames:v", "1", "-vf", base_vf, str(t)],
                    capture_output=True,
                )
            if t.is_file():
                thumbs.append(t)
                print(f"{i:02d}  {f}")

        if not thumbs:
            raise SystemExit("[ERROR] 未能从视频提取任何缩略帧。")

        n, c = len(thumbs), max(1, a.cols)
        if n == 1:
            shutil.copy2(thumbs[0], out_path)
        else:
            inputs = sum((["-i", str(t)] for t in thumbs), [])
            fc = "".join(f"[{i}:v]setsar=1[v{i}];" for i in range(n)) + "".join(f"[v{i}]" for i in range(n))
            layout = "|".join(f"{(i % c) * 480}_{(i // c) * 270}" for i in range(n))
            subprocess.run(
                [
                    ffmpeg, "-v", "error", "-y", *inputs,
                    "-filter_complex", f"{fc}xstack=inputs={n}:layout={layout}:fill=black",
                    "-frames:v", "1", str(out_path),
                ],
                check=True,
            )
        print("→", out_path)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
