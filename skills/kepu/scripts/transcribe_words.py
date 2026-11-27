#!/usr/bin/env python3
"""逐字转写（带字级时间戳）。以实录为准写脚本时使用。

自动发现本机 kepu 运行环境（无需手动指定 venv 路径，兼容 macOS 与 Windows）：
  python3 transcribe_words.py --out transcript.json act0.wav:0 act1.wav:54.0 act2.wav:127.53
  py -3 transcribe_words.py --out transcript.json "D:\\素材\\act0.wav:0"

每个输入写成 `音频或视频路径:全片偏移秒`（省略 `:偏移` 时默认为 `0`），偏移用来把分段时间换算成全片时间。
输出：JSON（段落 + 原音频绝对路径 + 字级时间）与同名 .txt（便于通读）。
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import wave

from _runtime import ensure_packages, find_tool

ensure_packages("numpy", "faster_whisper")

import numpy as np  # noqa: E402
from faster_whisper import WhisperModel  # noqa: E402

PROMPT_DEFAULT = "以下是普通话的句子，使用简体中文。"
OFFSET_SUFFIX_RE = re.compile(r"^(.*):([+-]?\d+(?:\.\d+)?)$")


def parse_input_item(item: str) -> tuple[Path, float]:
    m = OFFSET_SUFFIX_RE.match(item)
    if m and len(m.group(1)) > 1:  # Avoid splitting Windows drive letter like "D:0"
        return Path(m.group(1)), float(m.group(2))
    return Path(item), 0.0


def load_whisper(model_name: str) -> WhisperModel:
    try:
        return WhisperModel(model_name, device="cpu", compute_type="int8", local_files_only=True)
    except Exception:
        return WhisperModel(model_name, device="cpu", compute_type="int8", local_files_only=False)


def main() -> None:
    ap = argparse.ArgumentParser(description="逐字转写（带字级时间戳），支持 macOS 与 Windows。")
    ap.add_argument("inputs", nargs="+", help="audio_or_video[:offset_seconds]")
    ap.add_argument("--out", required=True, help="输出 JSON 路径（同时生成同名 .txt）")
    ap.add_argument("--model", default="small", help="Whisper 模型名（默认：small）")
    ap.add_argument("--prompt", default=PROMPT_DEFAULT, help="可追加专有名词，提高识别率")
    a = ap.parse_args()

    ffmpeg = find_tool("ffmpeg")
    model = load_whisper(a.model)
    out_path = Path(a.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    out: dict = {}
    lines: list[str] = []
    for item in a.inputs:
        src_path, off = parse_input_item(item)
        if not src_path.is_file():
            raise SystemExit(f"[ERROR] 找不到输入音视频文件：{src_path}")
        key = src_path.stem
        tmp = out_path.with_suffix(f".{key}.16k.wav")
        try:
            subprocess.run(
                [ffmpeg, "-y", "-v", "error", "-i", str(src_path), "-ac", "1", "-ar", "16000", str(tmp)],
                check=True,
            )
            with wave.open(str(tmp), "rb") as w:
                x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
        finally:
            tmp.unlink(missing_ok=True)

        segs, _ = model.transcribe(
            x, language="zh", initial_prompt=a.prompt, word_timestamps=True, beam_size=5
        )
        rows = []
        for s in segs:
            rows.append({
                "s": round(s.start, 2),
                "e": round(s.end, 2),
                "gs": round(s.start + off, 2),
                "t": s.text.strip(),
                "w": [[round(w.start, 2), round(w.end, 2), w.word] for w in (s.words or [])],
            })
        out[key] = {"offset": off, "audio": str(src_path.resolve()), "rows": rows}
        lines.append(f"===== {key} (offset {off}) =====")
        lines += [f"[{r['s']:7.2f}-{r['e']:7.2f} | G {r['gs']:7.2f}] {r['t']}" for r in rows]

    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    out_path.with_suffix(".txt").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
