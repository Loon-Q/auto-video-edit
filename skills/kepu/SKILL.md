---
name: kepu
description: >-
  【@kepu / @科普｜硅谷101级深度科技商业科普长视频端到端技能包】仅当用户明确输入 @kepu、@科普，或明确指定调用 @kepu / @科普 制作 5–15 分钟深度科技/商业解说长视频时激活。
  一套 100% 独立闭环工作流，端到端自动包办：新选题从零写硅谷101黄金四拍脚本、已拍口播只删不改重写分镜与原音频剪口实测、全渠道无字幕真实史料检索与 8 帧高危区体检、
  飞书原生表格文档交付审定、4K 原生音画同源原子切片粗剪（全片嘴型误差 <10ms）、Nano Banana 首帧参考图 + LibTV magi-2 现代商业隐喻视频生成、
  硅谷101 V5.1 标准 OpenMotion 分章精渲（00:00 起全篇常驻章节条、130 年演进时间线节点树、零底纹阴影花字、不透明问答分支树、Canvas 动态声学波束、
  多维结论三幕动态数据看板、章节间 0.40s 光学推镜模糊丝滑转场）及四道硬核质检导出。未点名 @kepu / @科普 时绝不抢触发，不与任何其他技能包联动。
---

# 硅谷101级深度科技商业科普 · 端到端独立技能包 (`@kepu` / `@科普`)

> **最高独立与防偷懒铁律（必读）**：
> 1. **100% 独立闭环**：本技能包自带从写稿、找史料、发飞书到 4K 精剪、商业隐喻生成、硅谷101视效模板与四道质检的全套规范与脚本，**不与任何外部其他视频技能产生联动、引用或规则混用**。
> 2. **严格点名触发**：仅在用户输入 `@kepu`、`@科普` 或明确指定使用本技能包时激活；未点名时保持静默，绝不干扰用户的其他创作任务。
> 3. **小白友好 · 自动识别阶段 · 仅 3 个拍板点**：用户无需记忆任何底层脚本或阶段术语，全程用大白话沟通，严格守住 **① 飞书审定脚本与分镜（审前绝不乱渲染、不花钱生成视频）→ ② 试听纯口播粗剪 / 首段手感 → ③ 验收桌面最终成片** 三个拍板节点。执行力必须拉满，严禁跳步缩水或只看命令返回 `0` 不看真实画面！

---

## 一、自动场景路由（根据用户给的一句话自动进对应阶段）

每次收到 `@科普` / `@kepu` 请求，先必读 [`references/user-preferences.md`](./references/user-preferences.md) 与 [`references/lessons.md`](./references/lessons.md)，再按用户当前手头材料自动走对应入口：

| 用户怎么说 / 手头有什么 | 自动进入哪个阶段 | 执行路径 |
|---|---|---|
| **场景 A｜只给选题，还没拍口播**<br>例：`@科普 帮我写一期《脑机接口》` | **阶段一（路径 A）：新选题从零写稿 + 史料收集 + 飞书审定** | 走下文 `步骤 A1 → A2 → A4 → A5 → A6 → 拍板点 ①` |
| **场景 B｜口播已拍完，要重写分镜且台词只删不改**<br>例：`@科普 口播拍好了，帮我删废话重做硅谷101分镜` | **阶段一（路径 B）：实录转写 + 剪口响度实测 + 重写分镜上飞书** | 走下文 `步骤 B1 → A2 → B3 → A4 → A5 → A6 → 拍板点 ①` |
| **场景 C｜飞书脚本已拍板（或直接要求开剪出片）**<br>例：`@科普 脚本过了，开始按最高标准做全片吧` | **阶段二 & 三：4K音画同源粗剪 → 商业隐喻生成 → 分章精渲 → 四道质检交片** | 走下文 `步骤 C1（拍板点 ②）→ C2 → C3 → C4 → C5（拍板点 ③）` |
| **场景 D｜看完成片提截图或口头修改意见**<br>例：`@科普 图3和转场这里改一下` | **阶段四：定位子工程局部精修重渲 + 无损重合成 + 二次质检** | 若用户说“先思考复核、先不着急改”，严格只做全量排查反思汇报，等口令再改；直接让改则走 `步骤 D1` |

---

## 二、阶段一：动工前 · 脚本创作/只删重写、无字幕史料体检与飞书审定

**铁律**：脚本与分镜未经用户在飞书拍板前，严禁擅自提交付费视频生成或渲染全片。

- **步骤 A1（仅未拍新选题）｜按硅谷101黄金结构从零写初稿**
  - 必读 [`references/new-script-guide.md`](./references/new-script-guide.md)：先锁死**全片唯一反差主命题**与**结尾回收的 3 个锚点**（不写旁支、同一底层机制绝不拆两章重复讲）。
  - 按「冷开场黄金四拍（实物极端反差 → 旧方案露馅骤停反问 → 2s 片名卡 → 目录式具象三连问）+ 正文三章 + 克制温暖尾声」撰稿，跑完四项自检（清空口头禅过渡词、确保每句都有可见实物或一手报道原文支撑）。

- **步骤 B1（仅已拍口播）｜以实录为准做逐字时间戳转写**
  - 运行 [`scripts/transcribe_words.py`](./scripts/transcribe_words.py) 对原始实拍音轨做逐字时间戳转写。实录与文稿不同处一律按实录写；**凡主播前两句说错后从头重录的 NG 废片，严禁掐头拼接，单独标记只取最后一次完整干净遍**。

- **步骤 A2｜盘点自有实拍 + 全渠道检索真实史料 + 8 帧无字幕体检**
  - 必读 [`references/material-pipeline.md`](./references/material-pipeline.md)：
    1. 若已有实拍目录，运行 [`scripts/footage_inventory.py`](./scripts/footage_inventory.py) 生成全量实拍缩略总览图并逐张审看（查清有哪些未用过的 4K B-roll，全片严禁重复使用同一条素材）。
    2. 运行 [`scripts/archival_search.py`](./scripts/archival_search.py)（`--source youtube | wikimedia | bilibili`）检索历史原版广告、馆藏实物影像、发布会与一手报道/官网截图。**缺通用画面一律先网上找干净源，不主动安排补拍。**
    3. 下载的外部视频入库前**必跑** [`scripts/broll_qc_manifest.py`](./scripts/broll_qc_manifest.py) 生成 **8 帧底部字幕高危区体检图**，亲眼看图剔除硬字幕/水印素材，并登记第三方 `画面来源：XX` 至 `sources_manifest.json`（`check` 返回 `0` 方可入库）。

- **步骤 B3（仅已拍口播）｜台词只删不改方案与原音频剪口响度实测**
  - 必读 [`references/cut-rules.md`](./references/cut-rules.md)：把候选删减写入 JSON，运行 [`scripts/phrase_time.py`](./scripts/phrase_time.py) 实测原音频每个剪口 `±0.25s` 内最安静 `80ms` 响度（`≤ -40 dB` 直接剪，`-40~-30 dB` 听验，`> -30 dB` 连读挪切点或换 take），并为每个剪口写明遮蔽方案（`1.0x ↔ 1.3x` 换景别 / 切 B-roll / 进章节卡）。

- **步骤 A4｜按硅谷101量化与视效工程标准逐镜写分镜**
  - 必读 [`references/visual-system.md`](./references/visual-system.md)、[`references/sv101-rules.md`](./references/sv101-rules.md)、[`references/sv101-vfx-spec.md`](./references/sv101-vfx-spec.md) 与 [`references/shot-plan.md`](./references/shot-plan.md)。
  - 每一句先回答“观众此刻该看到什么实物”，严格控制在 3 种画面状态（主持人自然全屏 / 全屏真实画面 / `#0E0F12` 原理画布，全片仅限一次 `4:6` 列要点同屏）。

- **步骤 A5｜现代商业隐喻生成清单与章节配乐分析**
  - 必读 [`references/libtv-decision.md`](./references/libtv-decision.md)：逐镜判定「真实史料 / 代码画布 / Nano Banana 高清剖面静帧 / Nano Banana 垫图 → LibTV `magi-2` 现代商业隐喻视频」（**视频生成硬锁定唯一模型 `magi-2`，严禁字面直译厨房水龙头或卡通机器人递棒等土味画面**）。
  - 运行 [`scripts/bgm_analyze.py`](./scripts/bgm_analyze.py) 扫描本地「背景音」目录 BPM 与起伏，按“开场快（`≥110 BPM`）、原理稳、尾声暖”初配每章音乐。

- **步骤 A6（拍板点 ①）｜一键生成飞书原生表格文档交付审定**
  - 使用 [`templates/feishu_script_builder.py`](./templates/feishu_script_builder.py)（参考完整范本 [`templates/example_ai_toy_v5_builder.py`](./templates/example_ai_toy_v5_builder.py)）生成 12 节完整飞书文档并回查表格与删除线，仅向用户确认 `2–3` 个未定关键拍板项。

---

## 三、阶段二 & 三：4K 音画同源精剪、商业隐喻生成、分章精渲与四道质检

飞书脚本审定通过后，必读 [`references/local.md`](./references/local.md) 与 [`references/sv101-vfx-spec.md`](./references/sv101-vfx-spec.md)，按以下 5 步把执行力拉到极致：

### 步骤 C1｜4K 原生音画同源原子切片与紧凑气口粗剪（拍板点 ②）
1. **严禁音画分家重切导致嘴型不同步**：口播音频与所有真人出镜 `<video>` 子片段必须从**同一条原始 4K 音画同步相机母带**按 `1600 samples/frame @ 48kHz / 30fps`（精确帧边界）同源切出，出镜视频统一加 `-g 15 -keyint_min 1 -bf 0` 短 GOP 编码（辅助工具见 [`scripts/video_edit.py`](./scripts/video_edit.py) 与 [`scripts/rough_cut.py`](./scripts/rough_cut.py)）。
2. **零 NG 半句拼接 + 紧凑自然气口 + 防跳帧**：
   - 重录句只用最后完整遍；同句内分句气口收紧至 `0.06–0.14s`（`2–4` 帧），句末换气 `0.20–0.23s`（`6–7` 帧），剔除句尾低头复位帧（提前切进章节卡或 B-roll）；
   - 分句补录的相邻真人出镜镜头必须做 **4K 原生 `1.0x` 全景 ↔ `1.3x` 光学近景交替**，彻底消除补录跳帧感。
3. 如用户需先确认口播节奏或前 30 秒手感，先交付试听/试看，确认后推进全片。

### 步骤 C2｜Nano Banana 商业垫图 + LibTV `magi-2` 视频 + 差异化音效库
1. **先用 Nano Banana / Imagen（`image-generator`）出图，绝不在 LibTV 里抽普通配图**：
   - 生成历史/硬件正面可辨识剖面复原图（杜绝看不懂的局部铁皮背板或圆窗手托图）及所有生成视频的 16:9 现代暗调商业参考首帧，生成后逐张 `read_file` 目视验收。
2. **调用 LibTV `magi-2`（`intent: "reference"`）生成现代商业隐喻视频**：
   - 把口播比喻转译为苹果/索尼商业片级视觉隐喻（如哑光黑总阀倾泻金色 `0101` 光纤代码流、暗调建筑光廊声波→发光文字板→声浪三棒转化、厚剧本撕裂化作金色神经元 Token 粒子流）；遇到 `wait_interrupted` 只调 `read_node` / `task_status` 查结果，**严禁重复提交扣双倍积分**。
   - 下载后统一转码为 `30fps` 短 GOP（`-g 15 -bf 0`），并定制匹配材质的差异化拟音与多变体 UI 打点音效（严禁单一音效重复刷屏）。

### 步骤 C3｜按章分段搭建硅谷101 V5.1 OpenMotion 工程
直接复用 [`templates/sv101/`](./templates/sv101/) 标准组件（`sv101-base.css`、`xray-spotlight.html`、`evidence-highlighter.html`、`schematic-and-chrome.html`），按章节拆分为独立子工程（`seg0`..`segN`）逐段精雕并跑通 `lint-project.mjs` **0 Error**：
- **全篇常驻章节条 & 演进节点树**：底部 `42px` `#sv-chapter-bar` 从 `00:00` 第 `0` 帧至尾帧全程 `opacity: 1` 常驻不隐藏（含 `导语` 与连续 `#FFA800` 进度线）；跨年代演进挂载右上 `#sv-era-tree` 节点树实时点亮。
- **花字零阴影底纹 & 无标点字幕 & 安全边距**：所有大号苍耳体花字强制 `text-shadow: none !important; filter: none !important;`，多字主副标题必加 `white-space: nowrap` 防折行孤字；左上来源小字锁定 `top: 38px; left: 48px`；风雅宋 `54px` 字幕去掉句尾标点、句中逗号改单空格。
- **自解释动态原理画布**：逻辑分支树必须配纯色不透明深底问答胶囊（`z-index` 高于 `<svg>` 严禁连线穿字）；声学/信号场用高清主体 + `<canvas>` 动态波束；超过 `3.0s` 的多维结论（如 `快·贵·难管`）拆成 `2.5s` 一幕的动态数据/安检门看板，严禁黑底死字干等。
- **零半途冻帧 & 纯 GPU 动画**：每条 `<video>` 真实时长必须严格大于 `data-duration`；定格解读在 `0ms` 定格帧同步触发去色与标注；GSAP 仅用 `x`/`y`/`scale`/`scaleX` 变换，禁用 `left`/`top`。

### 步骤 C4｜`48kHz` 整数采样全局母带与 `0.40s` 光学丝滑合片
- **告别章节间黑屏硬拼**：每章末尾 `0.40s`（`12` 帧）对 `#seam-stage` 施加光学推镜模糊（`scale: 1.0 → 1.10 + blur`），下章开头 `0.40s` 收清进入（`#sv-chapter-bar` 留在外层稳立不动），用 `ffmpeg xfade=transition=fade:duration=0.40` 无缝融合。
- 在 NumPy 中按 `48,000 Hz` 精确整数采样点（`G_k * 48000`）拼合全局连续母带，叠加配乐余弦交叉淡化与 `-0.22s` J-cut 丝滑转场声，确保全片 **0.000ms 累积音画漂移**。

### 步骤 C5｜出片前四道强制硬核质检门禁（拍板点 ③）
每次导出成片到项目 `06_成片导出/` 后，**四项全过才准交付用户**：
1. **全片出镜口播波形互相关实测**：抽测各章全部真人出镜镜头对比 4K 原相机音轨，最大偏差必须 **`< 10 ms`**；
2. **Studio Linter 复核**：全部子工程 `lint-project.mjs` `errorCount == 0`；
3. **24 帧高分质检总览图亲眼核验**：用 `read_file` 逐帧检查花字零底纹、标题零折行孤字、分支树零穿字、左上来源标零裁切、章节转场丝滑零黑屏；
4. **`blackdetect` 与 `volumedetect` 实测**：中段零意外黑屏，整体响度均值约 `-15 ~ -16 dB`、峰值不削波。

---

## 四、阶段四：对话审片返修与经验沉淀（步骤 D1）

- 支持截图圈选、秒点或大白话口头意见：精确定位对应章节子工程修改重渲并无损重合成全片，改完重新跑通抽帧与同步核验再交付。
- 每完成一轮新经验沉淀，同步更新本技能 `references/` 并执行仓库根目录 `python3 install.py --global --upgrade` 保持本机与 GitHub 一致。

---

## 五、内置工具脚本速查（均位于本技能 `scripts/` 与 `templates/`）

```sh
# 1) 环境初始化与健康自检（自动复用已装环境，支持 macOS 与 Windows）
python3 scripts/video_edit.py setup --with-libtv
python3 scripts/video_edit.py doctor

# 2) 实录逐字时间戳转写 & 台词删减剪口 ±0.25s 原音频响度实测
python3 scripts/transcribe_words.py "02_实拍素材/Aroll.mp4" -o aroll_words.json
python3 scripts/phrase_time.py cuts.json aroll_words.json "02_实拍素材/Aroll.mp4"

# 3) 实拍缩略盘点、多渠道史料检索与外部视频 8 帧无字幕高危区体检
python3 scripts/footage_inventory.py "02_实拍素材" -o footage_sheet.jpg
python3 scripts/archival_search.py --source youtube "Edison talking doll 1890"
python3 scripts/broll_qc_manifest.py inspect "03_历史与资料素材" --sheet _qc.jpg --manifest sources_manifest.json
python3 scripts/broll_qc_manifest.py check "03_历史与资料素材/sources_manifest.json"

# 4) 本地背景音乐 BPM 与响度起伏分析 & 飞书 12 节原生表格构建
python3 scripts/bgm_analyze.py "~/Desktop/背景音"
python3 templates/feishu_script_builder.py --spec episode.json --out draft.xml
```
