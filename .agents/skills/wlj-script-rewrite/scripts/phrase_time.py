#!/usr/bin/env python3
"""计算候选删减的时间、省时，并用真实音频复核剪口气口（兼容 macOS 与 Windows）。

用法：
  python3 phrase_time.py transcript.json deletions.json [--report out.json]
  py -3 phrase_time.py transcript.json deletions.json --report out.json

deletions.json 示例：
  [{"id": "D01", "seg": "act0", "phrase": "它们的价格差了二三十倍"}, ...]
phrase 用转写里的写法（转写有错字时照抄错字）；nth 可选，指第几次出现。

注意：Whisper 的字级时间在句与句之间常常是连续的（间隙显示 0），不代表没有气口。
所以本脚本额外读取原音频，在每个剪口 ±0.25s 内找最安静的 80ms，报告其响度：
  ≤ -40 dB 可以直接剪；-40 ~ -30 dB 需听验；> -30 dB 是连读，需挪切点 / 换 take / 退一步或保留。
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess

from _runtime import ensure_packages, find_tool

ensure_packages("numpy")

import numpy as np  # noqa: E402

PUNCT = r"[\s,，。、？?！!：:；;…“”\"'—\-]"


def verdict(db: float | None) -> str:
    if db is None:
        return "无音频"
    if db <= -40:
        return "可直接剪"
    if db <= -30:
        return "需听验"
    return "连读⚠"


def main() -> None:
    ap = argparse.ArgumentParser(description="计算候选删减起止时间、省时与原音频剪口响度。")
    ap.add_argument("transcript", help="transcribe_words.py 生成的 JSON")
    ap.add_argument("deletions", help="候选删减列表 JSON")
    ap.add_argument("--report", help="可选：输出详细复核报告 JSON 路径")
    a = ap.parse_args()

    T = json.loads(Path(a.transcript).read_text(encoding="utf-8"))
    deletions = json.loads(Path(a.deletions).read_text(encoding="utf-8"))

    needs_ffmpeg = any(isinstance(v, dict) and v.get("audio") for v in T.values())
    ffmpeg = find_tool("ffmpeg") if needs_ffmpeg else None

    maps: dict[str, tuple[list[tuple[str, float, float]], float]] = {}
    audio: dict[str, np.ndarray] = {}
    for k, v in T.items():
        rows = v["rows"] if isinstance(v, dict) and "rows" in v else v
        off = float(v.get("offset", 0.0)) if isinstance(v, dict) else 0.0
        chars: list[tuple[str, float, float]] = []
        for r in rows:
            for s, e, w in r["w"]:
                w2 = re.sub(PUNCT, "", w)
                for i, ch in enumerate(w2):
                    chars.append((ch, s + (e - s) * i / len(w2), s + (e - s) * (i + 1) / len(w2)))
        maps[k] = (chars, off)

        audio_path = v.get("audio") if isinstance(v, dict) else None
        if audio_path and ffmpeg and Path(audio_path).is_file():
            raw = subprocess.run(
                [ffmpeg, "-v", "error", "-i", str(audio_path), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                capture_output=True,
                check=True,
            ).stdout
            audio[k] = np.frombuffer(raw, dtype=np.float32)

    def quietest(seg: str, t: float, sr: int = 16000, rad: float = 0.25, win: float = 0.08) -> tuple[float | None, float | None]:
        x = audio.get(seg)
        if x is None or len(x) == 0:
            return None, None
        a0, a1 = max(0, int((t - rad) * sr)), min(len(x), int((t + rad) * sr))
        w = int(win * sr)
        best: float | None = None
        bt = t
        for i in range(a0, max(a0 + 1, a1 - w), int(0.01 * sr)):
            db = float(20 * np.log10(np.sqrt((x[i : i + w] ** 2).mean() + 1e-12)))
            if best is None or db < best:
                best, bt = db, (i + w / 2) / sr
        return (round(best, 1) if best is not None else None), round(bt, 2)

    res = []
    total = 0.0
    for d in deletions:
        seg = d["seg"]
        if seg not in maps:
            print(d["id"], f"SEG NOT FOUND ({seg}):", d["phrase"])
            continue
        chars, off = maps[seg]
        txt = "".join(c[0] for c in chars)
        p = re.sub(PUNCT, "", d["phrase"])
        idx = -1
        for _ in range(d.get("nth", 1)):
            idx = txt.find(p, idx + 1)
        if idx < 0:
            print(d["id"], "NOT FOUND:", d["phrase"])
            continue
        s, e = chars[idx][1], chars[idx + len(p) - 1][2]
        nxt = chars[idx + len(p)][1] if idx + len(p) < len(chars) else e
        save = nxt - s
        total += save
        in_db, in_t = quietest(seg, s)
        out_db, out_t = quietest(seg, e)
        r = {
            **d,
            "global_start": round(s + off, 2),
            "global_end": round(e + off, 2),
            "save": round(save, 2),
            "cut_in": {"t": in_t, "db": in_db, "verdict": verdict(in_db)},
            "cut_out": {"t": out_t, "db": out_db, "verdict": verdict(out_db)},
            "ctx": txt[max(0, idx - 6) : idx] + "【" + p + "】" + txt[idx + len(p) : idx + len(p) + 6],
        }
        print(
            f'{d["id"]} {r["global_start"]:7.2f}-{r["global_end"]:7.2f} 省≈{save:4.2f}s '
            f'入口{in_db}dB[{verdict(in_db)}] 出口{out_db}dB[{verdict(out_db)}] {r["ctx"]}'
        )
        res.append(r)

    print(f"合计省时 ≈ {total:.1f}s")
    if a.report:
        report_path = Path(a.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
