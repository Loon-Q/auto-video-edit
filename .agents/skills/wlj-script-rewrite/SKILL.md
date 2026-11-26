---
name: wlj-script-rewrite
description: 为《未来陪伴局》这类真人主持的科技解说长视频（对标硅谷101）重写脚本与分镜：台词已拍完时只删不改、按实录逐字稿和真实气口出删减方案；按“真实画面 > 真实史料 > 原理画布 > LibTV 生成”重新设计逐镜画面、排版、音乐与剪辑节奏；判断哪些镜头该用 LibTV / MAGI-2 生成；最后输出到飞书文档供审定。用户说“重写脚本/分镜”“台词只能删”“对标硅谷101”“哪些镜头用 LibTV 生成”“脚本和画面对不上”时先读本技能。
---

# 科技解说脚本重写（台词只删 · 分镜重做 · 生成判断）

本技能管“动工前”：把已拍完的口播变成一份能直接开剪的脚本。剪辑与渲染交给 `product-video-edit` 和 OpenMotion；MAGI-2 提示词与 LibTV 调用细节交给 `guizang-magi2-skill`。

## 何时用

- 台词已经拍完，用户要“重新写脚本 / 分镜”，且台词**只能删减，不能改字、不能加字**。
- 用户对上一版成片不满意（画面对不上台词、像 PPT、节奏平），要求推倒重来。
- 需要决定哪些镜头用 LibTV 生成、哪些用真实素材。

## 流程（不可跳步）

0. **先读 [用户偏好与已定默认](references/user-preferences.md)。** 里面已定的事项（来源小字、章节条、不补拍、真实史料等）直接按默认执行，不再重复问。脚本审定前不剪、不渲染、不生成。
1. **以实录为准，不以打印稿为准。** 用 [`scripts/transcribe_words.py`](scripts/transcribe_words.py) 对“当前已选 take 的纯口播轨”做逐字转写（带字级时间戳）。实录与稿子不同的地方按实录写；发现残留口误、重说、说错的句子单独记下。
2. **盘点全部素材。** 用 [`scripts/footage_inventory.py`](scripts/footage_inventory.py) 给实拍目录出缩略总览图，逐张看清每条素材是什么、能撑哪句话；同一句是否有多条 take（剪口不顺时可换 take）。用 [`scripts/archival_search.py`](scripts/archival_search.py)（兼容旧入口 `archival_search.sh`）搜真实史料（老广告、实物影像、发布会、报道原文）和通用画面（家常动作、数据中心等）。**实拍缺的画面一律先网上找，不安排补拍。**
3. **出删减方案。** 规则见 [删减规则](references/cut-rules.md)。把候选删减写成 JSON，用 [`scripts/phrase_time.py`](scripts/phrase_time.py)（自动调用本机 `product-video-edit` 运行环境）算每处的时间、省时，并读原音频测剪口响度：≤ -40 dB 直接剪，-40～-30 dB 需听验，> -30 dB 连读——连读时挪切点（如保留连接词“而”“但”）、换 take，或给出退一步的较小删法。
4. **定视觉总纲，再逐镜写分镜。** 先读 [视觉总纲](references/visual-system.md) 和 [硅谷101 量化标准](references/sv101-rules.md)。每一句先回答“观众此刻该看到什么实物”，再选三种画面状态之一。分镜每行写：镜号 / 台词（删减后）/ 画面 / 字与排版 / 声音 / 素材来源。
5. **逐镜判断要不要生成。** 按 [LibTV 生成判断](references/libtv-decision.md)。生成镜头附提示词要点、方式（文生 / 全能参考 / 代码灰盒）与预估花费；历史段落坚持真实史料。
6. **配乐按章节选曲。** 用 [`scripts/bgm_analyze.py`](scripts/bgm_analyze.py) 分析用户本地“背景音”文件夹的 BPM 与起伏，按“开场快、原理段稳、尾声慢”初配，并承诺动工前出 A/B 试听小样。
7. **输出到飞书文档。** 按 `lark-doc` 创建工作流；用 [`templates/feishu_script_builder.py`](templates/feishu_script_builder.py)（支持传入结构化 `--spec episode.json --out draft.xml`，完整单期实战范本见 [`templates/example_ai_toy_v5_builder.py`](templates/example_ai_toy_v5_builder.py)）把数据（删减表、剪口实测、完整台词、分镜、生成清单、素材、音乐、拍板项）生成 XML，`parse` 通过后 `docs +create`，再 `+fetch` 回查表格数和删除线数。
8. **交付时只问真正需要用户拍板的 2–3 件事**，且只问 `user-preferences.md` 里还没定的；用户答复后立刻写回 `user-preferences.md`。
9. **用户没说开剪就停在脚本。** 交付飞书文档后等用户审；用户说“先不要剪 / 不要执行”时，只补经验到本技能。

## 文档结构（固定顺序）

一页看懂 → 上一版为什么不行 → 对标学什么 → 视觉总纲（含来源小字与章节条规格）→ 台词删减表 → 剪口实测 → 删减后完整台词 → 逐章分镜 → LibTV 生成清单 → 素材清单（网上来源）→ 音乐 → 拍板项（仅未定事项）→ 制作顺序与验收。

## 本技能的硬性提醒

- 用户自己定下的审美（字体、主色、禁用元素）保留；上一版由模型发明的版式、组件、配乐一律不继承。
- 不在分镜里写台词没提过的英文标签、编号角标、胶囊框、装饰线。
- 每个删减剪口都要有遮法：换景别（4K 素材 1.0 / 1.3 两档）、切 B-roll、或切进章节卡 / 片名卡。
- 案例与经验沉淀：每做完一期，把新的有效做法补进 `references/`，把被用户否定的做法写进 [失败教训](references/lessons.md)。
