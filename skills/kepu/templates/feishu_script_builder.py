#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通用飞书重写脚本 XML 生成器（12 节标准结构，兼容 macOS 与 Windows）。

支持两种用法：
1. JSON 驱动（推荐）：将新一期的删减表、剪口实测、完整台词、分镜、LibTV 清单、素材与配乐写为 JSON：
   python3 feishu_script_builder.py --spec my_episode.json --out draft.xml
2. Python 范本复制修改：直接参考同目录完整实战范本 `example_ai_toy_v5_builder.py`（《AI对话玩具》V5 全文）。

前置步骤：先运行 `lark-cli docs +script --command init-draft ...` 拿到 `draft_path`，
生成 XML 后跑 `lark-cli docs +script --command parse` 校验通过，再执行 `lark-cli docs +create`。
"""
from __future__ import annotations

import argparse
from html import escape as E
import json
from pathlib import Path
import re


def rich(s: str) -> str:
    """轻量行内标记：~~删除~~ -> <del>，**加粗** -> <b>，其余自动 XML 转义。"""
    out: list[str] = []
    tokens = re.split(r"(~~.+?~~|\*\*.+?\*\*)", str(s))
    for t in tokens:
        if t.startswith("~~") and t.endswith("~~") and len(t) > 4:
            out.append(f"<del>{E(t[2:-2])}</del>")
        elif t.startswith("**") and t.endswith("**") and len(t) > 4:
            out.append(f"<b>{E(t[2:-2])}</b>")
        else:
            out.append(E(t))
    return "".join(out)


def cell(s: str, th: bool = False, bg: str | None = None) -> str:
    tag = "th" if th else "td"
    attr = f' background-color="{bg}"' if bg else ""
    paras = "".join(f"<p>{rich(x)}</p>" for x in str(s).split("\n"))
    return f"<{tag}{attr}>{paras}</{tag}>"


def table(headers: list[str], rows: list[list[str]], widths: list[int]) -> str:
    cols = "".join(f'<col width="{w}"/>' for w in widths)
    hdr = "<tr>" + "".join(cell(x, th=True, bg="light-gray") for x in headers) + "</tr>"
    body = "".join("<tr>" + "".join(cell(c) for c in r) + "</tr>" for r in rows)
    return f"<table><colgroup>{cols}</colgroup><thead>{hdr}</thead><tbody>{body}</tbody></table>"


def p(s: str) -> str:
    return f"<p>{rich(s)}</p>"


def ul(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{rich(x)}</li>" for x in items) + "</ul>"


def ol(items: list[str]) -> str:
    return "<ol>" + "".join(f"<li>{rich(x)}</li>" for x in items) + "</ol>"


def h(n: int, s: str) -> str:
    return f"<h{n}>{E(s)}</h{n}>"


def callout(lines: list[str], emoji: str = "💡", bg: str = "light-orange", border: str = "orange") -> str:
    return f'<callout emoji="{emoji}" background-color="{bg}" border-color="{border}">' + "".join(
        p(x) for x in lines
    ) + "</callout>"


def build_from_spec(spec: dict) -> str:
    X: list[str] = [f"<title>{E(spec['title'])}</title>"]

    # 1. 一页看懂
    if spec.get("overview"):
        ov = spec["overview"]
        X.append(h(1, ov.get("heading", "一页看懂")))
        if ov.get("callout"):
            X.append(callout(ov["callout"]))
        for note in ov.get("notes", []):
            X.append(p(note))

    # 2. 上一版为什么不行（可选：新片首次写脚本时可写“本期核心难点与破局”）
    if spec.get("root_causes"):
        rc = spec["root_causes"]
        X.append(h(1, rc.get("heading", "上一版为什么不行")))
        X.append(table(rc.get("headers", ["根因", "具体表现", "这一版怎么改"]), rc["rows"], rc.get("widths", [180, 320, 320])))

    # 3. 对标学什么
    if spec.get("benchmark"):
        bm = spec["benchmark"]
        X.append(h(1, bm.get("heading", "硅谷101 对标落点")))
        if bm.get("intro"):
            X.append(p(bm["intro"]))
        X.append(table(bm.get("headers", ["维度", "对标做法", "本期落点"]), bm["rows"], bm.get("widths", [130, 340, 350])))

    # 4. 视觉总纲
    if spec.get("visual_system"):
        vs = spec["visual_system"]
        X.append(h(1, vs.get("heading", "全新视觉总纲")))
        for sec in vs.get("sections", []):
            X.append(h(2, sec["title"]))
            if sec.get("ordered"):
                X.append(ol(sec["ordered"]))
            if sec.get("bullets"):
                X.append(ul(sec["bullets"]))
            if sec.get("paragraphs"):
                for para in sec["paragraphs"]:
                    X.append(p(para))
            if sec.get("table"):
                tb = sec["table"]
                X.append(table(tb["headers"], tb["rows"], tb["widths"]))

    # 5. 台词删减表 & 剪口实测
    if spec.get("deletions"):
        dl = spec["deletions"]
        X.append(h(1, dl.get("heading", "台词删减方案（只删不改不加）")))
        if dl.get("intro"):
            X.append(p(dl["intro"]))
        X.append(
            table(
                dl.get("headers", ["编号", "位置", "原话（删除线为删掉部分）", "为什么删", "省时"]),
                dl["rows"],
                dl.get("widths", [60, 70, 360, 260, 70]),
            )
        )
        if dl.get("kept"):
            X.append(h(2, "考虑过但保留的"))
            X.append(ul(dl["kept"]))
        if dl.get("cut_audit"):
            ca = dl["cut_audit"]
            X.append(h(2, ca.get("heading", "剪口实测（用原音频逐个核过）")))
            if ca.get("intro"):
                X.append(p(ca["intro"]))
            X.append(table(ca.get("headers", ["结果", "编号与说明"]), ca["rows"], ca.get("widths", [160, 660])))

    # 6. 删减后完整台词
    if spec.get("full_dialogue"):
        fd = spec["full_dialogue"]
        X.append(h(1, fd.get("heading", "删减后的完整台词（可直接通读）")))
        if fd.get("intro"):
            X.append(p(fd["intro"]))
        for ch in fd["chapters"]:
            X.append(h(2, ch["title"]))
            for para in ch["paragraphs"]:
                X.append(p(para))

    # 7. 全新分镜
    if spec.get("storyboard"):
        sb = spec["storyboard"]
        X.append(h(1, sb.get("heading", "全新分镜")))
        if sb.get("intro"):
            X.append(p(sb["intro"]))
        headers = sb.get("headers", ["镜号", "台词（删减后）", "画面", "字与排版", "声音", "素材"])
        widths = sb.get("widths", [52, 170, 260, 140, 110, 88])
        for ch in sb["chapters"]:
            X.append(h(2, ch["title"]))
            X.append(table(headers, ch["rows"], widths))

    # 8. LibTV 生成清单
    if spec.get("libtv"):
        lt = spec["libtv"]
        X.append(h(1, lt.get("heading", "LibTV 生成清单")))
        if lt.get("rules_rows"):
            X.append(h(2, "什么时候生成、什么时候不生成"))
            X.append(table(["判断", "规则", "本片对应"], lt["rules_rows"], [150, 360, 310]))
        if lt.get("shots_rows"):
            X.append(h(2, "生成镜头"))
            X.append(
                table(
                    ["编号", "用在", "方式", "提示词要点", "时长 / 花费"],
                    lt["shots_rows"],
                    [60, 130, 140, 400, 90],
                )
            )
        if lt.get("callout"):
            X.append(callout(lt["callout"], emoji="⚙️", bg="light-gray", border="gray"))

    # 9. 素材清单（网上来源优先，不补拍）
    if spec.get("materials"):
        mt = spec["materials"]
        X.append(h(1, mt.get("heading", "素材清单（真实史料与网源）")))
        for sec in mt.get("sections", []):
            X.append(h(2, sec["title"]))
            X.append(table(sec["headers"], sec["rows"], sec["widths"]))

    # 10. 音乐
    if spec.get("music"):
        mu = spec["music"]
        X.append(h(1, mu.get("heading", "音乐：每章一首（来自本地背景音目录）")))
        X.append(table(mu.get("headers", ["段落", "情绪", "首选 / 备选", "理由"]), mu["rows"], mu.get("widths", [90, 160, 230, 340])))
        if mu.get("note"):
            X.append(p(mu["note"]))

    # 11. 需要拍板的事（仅未定事项）
    if spec.get("decisions"):
        dc = spec["decisions"]
        X.append(h(1, dc.get("heading", "需要你拍板的事项")))
        X.append(ol(dc["items"]))

    # 12. 制作顺序与验收
    if spec.get("production_steps"):
        ps = spec["production_steps"]
        X.append(h(1, ps.get("heading", "制作顺序与验收")))
        X.append(ol(ps["items"]))

    return "".join(X)


def main() -> None:
    ap = argparse.ArgumentParser(description="根据 JSON 规格生成飞书脚本重写文档 XML。")
    ap.add_argument("--spec", required=True, help="单期脚本 JSON 路径")
    ap.add_argument("--out", default="draft.xml", help="输出飞书 XML 路径（默认：draft.xml）")
    a = ap.parse_args()

    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    xml_str = build_from_spec(spec)
    out_path = Path(a.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(xml_str, encoding="utf-8")
    print(f"[OK] written {out_path} ({len(xml_str)} chars)")


if __name__ == "__main__":
    main()
