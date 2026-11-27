#!/usr/bin/env python3
"""分析本地 BGM 文件夹：时长、估算 BPM、10 段响度起伏。用于按章节初配曲目。

用法（兼容 macOS 与 Windows）：
  python3 bgm_analyze.py "<本地背景音目录>" [--json out.json]
  py -3 bgm_analyze.py "D:\\素材\\背景音"

结果是机器估算，动工前仍需把候选剪成 15 秒 A/B 小样给用户试听。
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

from _runtime import ensure_packages, find_tool

ensure_packages("numpy")

import numpy as np  # noqa: E402


def default_bgm_dir() -> Path:
    return Path.home() / "Desktop" / "背景音"


def main() -> None:
    ap = argparse.ArgumentParser(description="分析本地配乐目录的时长、估算 BPM 与 10 段动态起伏。")
    ap.add_argument("folder", nargs="?", default=None, help="本地背景音乐目录（默认尝试 ~/Desktop/背景音）")
    ap.add_argument("--json", dest="json_out", default=None, help="可选：导出 JSON 分析结果路径")
    a = ap.parse_args()

    folder = Path(a.folder).expanduser() if a.folder else default_bgm_dir()
    if not folder.is_dir():
        raise SystemExit(f"[ERROR] 找不到配乐目录：{folder}\n请显式传入你的本地背景音目录路径。")

    ffmpeg = find_tool("ffmpeg")
    tracks = sorted(
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in (".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg")
    )
    if not tracks:
        raise SystemExit(f"[ERROR] 目录中没有音频文件：{folder}")

    print(f"{'曲目':<18}{'时长s':>7}{'BPM':>7}{'起伏dB':>8}  10段响度")
    records = {}
    sr, hop, win = 11025, 256, 1024
    fps = sr / hop

    for f in tracks:
        raw = subprocess.run(
            [ffmpeg, "-v", "error", "-i", str(f), "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
            capture_output=True,
            check=True,
        ).stdout
        x = np.frombuffer(raw, dtype=np.float32)
        n = len(x) // hop
        if n < 20:
            continue
        rms = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1) + 1e-12)
        prof = [round(float(20 * np.log10(s.mean() + 1e-9)), 1) for s in np.array_split(rms, 10)]
        S = np.log1p(
            np.array([np.abs(np.fft.rfft(x[i : i + win] * np.hanning(win))) for i in range(0, len(x) - win, hop)])
        )
        flux = np.maximum(0.0, np.diff(S, axis=0)).sum(1)
        flux = flux - flux.mean()
        ac = np.correlate(flux, flux, mode="full")[len(flux) - 1 :]
        lags = np.arange(len(ac))
        m = (lags > fps * 60 / 180) & (lags < fps * 60 / 60)
        bpm = float(60 * fps / lags[m][int(np.argmax(ac[m]))])
        dur = round(len(x) / sr, 1)
        dyn = round(max(prof) - min(prof), 1)
        records[f.name] = {"dur": dur, "bpm": round(bpm, 1), "dyn_range": dyn, "loud_profile_dB": prof}
        print(f"{f.name:<18}{dur:7.1f}{bpm:7.1f}{dyn:8.1f}  " + " ".join(f"{v:.0f}" for v in prof))

    if a.json_out:
        out_p = Path(a.json_out)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
