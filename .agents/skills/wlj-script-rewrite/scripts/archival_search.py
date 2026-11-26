#!/usr/bin/env python3
"""跨平台检索真实史料与公开视频素材（老广告、实物影像、发布会演示、通用场景）。

只列检索结果，不自动下载；确认后再用 yt-dlp 下载所需片段。兼容 macOS 与 Windows：
  python3 archival_search.py "Teddy Ruxpin commercial 1985" "Furby commercial 1998"
  py -3 archival_search.py "Teddy Ruxpin commercial 1985" --limit 5

下载片段示例：
  yt-dlp -f "bv*[height<=1080]+ba/b" --download-sections "*00:05-00:15" -o out.mp4 "https://www.youtube.com/watch?v=<id>"
注意：逐条检查是否带原字幕 / 水印，带字幕的弃用或裁掉。
"""
from __future__ import annotations

import argparse
import subprocess

from _runtime import find_tool


def main() -> None:
    ap = argparse.ArgumentParser(description="检索 YouTube 上的真实历史广告、实物影像与公开演示视频。")
    ap.add_argument("queries", nargs="+", help="检索关键词（可传多个）")
    ap.add_argument("--limit", type=int, default=5, help="每个关键词返回条数（默认：5）")
    ap.add_argument("--timeout", type=int, default=15, help="单次连接超时秒数（默认：15）")
    a = ap.parse_args()

    ytdlp = find_tool("yt-dlp")
    for q in a.queries:
        print(f"== {q}")
        res = subprocess.run(
            [
                ytdlp,
                "--socket-timeout",
                str(a.timeout),
                "--flat-playlist",
                "--print",
                "%(id)s | %(title)s | %(duration)ss",
                f"ytsearch{a.limit}:{q}",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        lines = [ln for ln in res.stdout.splitlines() if ln.strip()]
        for ln in lines[-a.limit :]:
            print(ln)
        if res.returncode != 0 and not lines:
            err_tail = "\n".join(res.stderr.splitlines()[-3:])
            print(f"[WARN] 检索失败：{err_tail}")


if __name__ == "__main__":
    main()
