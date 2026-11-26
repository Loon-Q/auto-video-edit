#!/usr/bin/env python3
"""跨平台多渠道真实史料与公开素材检索工具（YouTube / Bilibili / Wikimedia Commons）。

只列检索结果与元数据，不盲目批量下载；确认候选后再按需下载并跑 `broll_qc_manifest.py` 做无字幕体检。
兼容 macOS 与 Windows：
  python3 archival_search.py "Teddy Ruxpin commercial 1985" "Furby commercial 1998"
  python3 archival_search.py --source bilibili "BubblePal AI玩具" "小智ESP32"
  python3 archival_search.py --source wikimedia "Edison talking doll" "Thomas Edison phonograph 1878"

视频按片段下载示例：
  yt-dlp -f "bv*[height<=1080]+ba/b" --download-sections "*00:05-00:15" -o out.mp4 "https://www.youtube.com/watch?v=<id>"
"""
from __future__ import annotations

import argparse
import json
import subprocess
import urllib.parse
import urllib.request

from _runtime import find_tool


def search_ytdlp(prefix: str, queries: list[str], limit: int, timeout: int) -> None:
    ytdlp = find_tool("yt-dlp")
    for q in queries:
        print(f"== [{prefix}] {q}")
        res = subprocess.run(
            [
                ytdlp,
                "--socket-timeout",
                str(timeout),
                "--flat-playlist",
                "--print",
                "%(id)s | %(title)s | %(duration)ss | %(webpage_url)s",
                f"{prefix}{limit}:{q}",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        lines = [ln for ln in res.stdout.splitlines() if ln.strip()]
        for ln in lines[-limit:]:
            print("  ", ln)
        if res.returncode != 0 and not lines:
            err_tail = "\n".join(res.stderr.splitlines()[-3:])
            print(f"  [WARN] 检索未返回结果：{err_tail}")


def search_wikimedia(queries: list[str], limit: int, timeout: int) -> None:
    headers = {"User-Agent": "auto-video-edit-skill/2.0 (https://github.com/Loon-Q/auto-video-edit)"}
    for q in queries:
        print(f"== [wikimedia] {q}")
        params = urllib.parse.urlencode({
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrnamespace": "6",  # File: namespace
            "gsrsearch": q,
            "gsrlimit": str(limit),
            "prop": "imageinfo",
            "iiprop": "url|size|mime|extmetadata",
        })
        url = f"https://commons.wikimedia.org/w/api.php?{params}"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            print(f"  [WARN] Wikimedia 请求失败：{exc}")
            continue

        pages = list((data.get("query", {}).get("pages") or {}).values())
        if not pages:
            print("  (无匹配馆藏文件)")
            continue
        for pg in pages:
            title = pg.get("title", "")
            ii = (pg.get("imageinfo") or [{}])[0]
            w, h = ii.get("width", "?"), ii.get("height", "?")
            mime = ii.get("mime", "")
            file_url = ii.get("url", "")
            meta = ii.get("extmetadata") or {}
            lic = (meta.get("LicenseShortName") or {}).get("value", "unknown")
            print(f"   {title} | {w}x{h} ({mime}) | {lic}\n     -> {file_url}")


def main() -> None:
    ap = argparse.ArgumentParser(description="多渠道检索真实历史广告、馆藏图片与公开产品演示素材。")
    ap.add_argument("queries", nargs="+", help="检索关键词（可传多个）")
    ap.add_argument(
        "--source",
        choices=("youtube", "bilibili", "wikimedia"),
        default="youtube",
        help="检索源：youtube（默认，老广告/发布会）、bilibili（国内产品演示）、wikimedia（公有领域馆藏大图）",
    )
    ap.add_argument("--limit", type=int, default=5, help="每个关键词返回条数（默认：5）")
    ap.add_argument("--timeout", type=int, default=15, help="单次网络超时秒数（默认：15）")
    a = ap.parse_args()

    if a.source == "youtube":
        search_ytdlp("ytsearch", a.queries, a.limit, a.timeout)
    elif a.source == "bilibili":
        search_ytdlp("bilisearch", a.queries, a.limit, a.timeout)
    else:
        search_wikimedia(a.queries, a.limit, a.timeout)


if __name__ == "__main__":
    main()
