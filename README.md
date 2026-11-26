# 自动剪辑与科技解说创作套件（Codex & Google Antigravity）

面向真人主持的**科技深度解说长视频（对标硅谷101）**与**产品测评/盘点视频**的开源全链路 AI 技能包。涵盖**从零写稿、已拍口播只删不改重写、全渠道真实史料检索与 8 帧无字幕体检、LibTV（`MAGI-2`）生成判断、语义气口粗剪、硅谷101 标准 OpenMotion 视效模板库及成片返修**。

- **跨平台零硬编码**：同时支持 **macOS** 与 **Windows PowerShell**，所有脚本自动寻址本机运行环境。
- **双端同源**：**OpenAI Codex** 与 **Google Antigravity（反重力）** 直接共用同一套技能、模板与 MCP 配置。

---

## 核心架构：全流程三块拼图

| 阶段 | 模块 | 解决什么核心问题 |
|---|---|---|
| **1. 动工前：写稿、重写、收集素材与生成判断** | [`wlj-script-rewrite`](.agents/skills/wlj-script-rewrite/SKILL.md) | <ul><li>**路径 A（新选题未拍）**：按硅谷101 黄金四拍冷开场 + 三章推进从零写零废话初稿，杜绝前后重复与有词无画面。</li><li>**路径 B（口播已拍完）**：台词**只删不改**，基于实录逐字转写 + 原音频 `±0.25s` 最安静 `80ms` 响度核准剪口。</li><li>**全渠道收集素材 + 硬字幕体检**：检索 YouTube 历史广告、Wikimedia 公有领域馆藏大图、B 站演示与一手报道原文；强制跑 **8 帧底部字幕高危区体检**并登记 `画面来源：XX` 清单。</li><li>**LibTV 生成判断与飞书交付**：逐镜判定真实素材 / 原理画布 / `MAGI-2` 生成，按本地 BGM 的 BPM 与动态起伏初配每章音乐，一键输出飞书原生表格供审定。</li></ul> |
| **2. 开剪后：4K 音画同源精剪、硅谷101 视效与四道核验** | [`product-video-edit`](.agents/skills/product-video-edit/SKILL.md) | <ul><li>**4K 音画同源原子切片与防跳帧**：`1600 samples/frame @ 48kHz / 30fps` 帧对齐切片（全片音画误差 `< 10ms`），NG 重录只取最后完整遍，紧凑语义气口（`0.06s–0.23s`），相邻补录镜头用 4K `1.0x ↔ 1.3x` 景别交替消除跳帧。</li><li>**硅谷101 V5.1 标准视效模板库**（[`templates/sv101/`](.agents/skills/product-video-edit/templates/sv101/)）：内置**零底纹阴影大字**、**全篇常驻 `42px` 章节条**、**演进节点树 `#sv-era-tree`**、**不透明标签逻辑分支树**、**`<canvas>` 声学波束场**、**多维结论三幕动态看板**与**章节间 `0.40s` 光学推镜模糊丝滑转场**。</li><li>**四道交付硬核验**：16 镜全片口播互相关音画同步校验、Studio Linter 零报错、24 帧关键画面抽检、`blackdetect` + `volumedetect` 核验。</li></ul> |
| **3. 商业隐喻生成管线：Nano Banana + LibTV `magi-2`** | `image-generator` + `guizang-magi2-skill` + `LibTV MCP` | 强制走 **Nano Banana / Imagen 先出风格统一的现代商业参考图 → LibTV `magi-2`（唯一锁定视频模型）生成现代商业隐喻视频**（如 `0101` 光纤代码水龙头、建筑光廊三棒转化、剧本撕裂化为金色 Token 粒子流，杜绝字面直译俗套画面），并支持静音代码动作灰盒帧级卡点重绘。 |

---

## 1. 一键安装与升级

克隆或下载本仓库后，推荐直接安装到**本机全局**（自动同步至 Antigravity `~/.gemini/config/skills`、Codex `~/.codex/skills` 及 `~/.agents/skills`，换任何新线程/新项目都不会回退旧版）：

**macOS**
```sh
python3 install.py --global --upgrade --with-libtv
```

**Windows PowerShell**
```powershell
py -3 install.py --global --upgrade --with-libtv
```

若只需安装到某一个独立剪辑项目目录（写入 `<项目>/.agents/skills/`）：

```sh
# macOS
python3 install.py "/你的/剪辑项目" --upgrade

# Windows PowerShell
py -3 install.py "D:\剪辑项目" --upgrade
```

---

## 2. 准备本机运行环境（新电脑首次执行）

请先安装以下基础工具并确保在新终端的 `PATH` 中可用（推荐 Python 3.12）：

| 工具 | 用途 |
|---|---|
| [Python 3.11+](https://www.python.org/downloads/) | 安装器、实录逐字转写（`faster-whisper`）、原音频剪口测量、BGM 分析与粗剪入口 |
| [Git](https://git-scm.com/downloads)、[Node.js 22.18+（含 npm/npx）](https://nodejs.org/en/download) | 拉取构建固定版本 OpenMotion 及桥接 LibTV Remote MCP |
| [FFmpeg](https://ffmpeg.org/download.html)（含 `ffprobe`） | 音视频解码、气口剪切、8 帧无字幕体检总览图与成片质检 |
| [Google Chrome](https://www.google.com/chrome/) 或 Chromium | OpenMotion 预览与 1080p 渲染 |
| `lark-cli`（可选） | 将脚本与原生分镜表格一键创建/更新至飞书云文档 |

在仓库目录（或已安装技能的项目目录）运行初始化与自检：

**macOS**
```sh
python3 .agents/skills/product-video-edit/scripts/video_edit.py setup --with-libtv
python3 .agents/skills/product-video-edit/scripts/video_edit.py doctor
```

**Windows PowerShell**
```powershell
py -3 .agents/skills/product-video-edit/scripts/video_edit.py setup --with-libtv
py -3 .agents/skills/product-video-edit/scripts/video_edit.py doctor
```

`setup` 会在独立运行目录（默认 `~/.local/share/product-video-edit`，可用 `PRODUCT_VIDEO_RUNTIME` 自定义）自动安装 `numpy`、`faster-whisper`、`yt-dlp`，并构建固定版本 OpenMotion。首次使用 LibTV 工具时会自动在浏览器弹出授权登录。

---

## 3. 开箱即用提示词（直接复制给 Codex 或 Antigravity）

### 场景 1：新选题还没拍，从零写硅谷101级脚本、分镜与素材清单
> 用 `wlj-script-rewrite` 帮我从零写一期《选题名称》的科技解说脚本与分镜：对标硅谷101立住冷开场四拍与正文三章，确保每句台词都有真实画面或一手报道证据支撑；同步检索可用的真实史料/网源素材、判断哪些比喻镜头用 LibTV 生成，最后输出到飞书文档给我审。

### 场景 2：口播已经拍完，只删不改重写分镜、收集无字幕素材并交付飞书
> 用 `wlj-script-rewrite` 重写这期脚本与分镜：台词已拍完只做删减不改字，用原音频实测每个剪口响度；对标硅谷101重新设计逐镜画面与音乐，网上找齐真实史料并跑 8 帧无字幕体检登记来源，判断哪些镜头用 LibTV 生成，输出飞书文档给我审定，审定前先不要开剪。

### 场景 3：脚本已拍板，粗剪口播并用硅谷101标准视效模板制作成片
> 飞书脚本已拍板，用 `product-video-edit` 先按删减表剪出纯口播版给我试听；通过后套用 `templates/sv101/` 下的硅谷101标准视效模板，先做冷开场+第一章试剪定手感，配乐从我本地背景音目录按章节选。

---

## 4. 仓库结构与核心资产速览

```text
.agents/skills/
├── wlj-script-rewrite/                   # 【动工前】新写脚本 / 只删重写 / 素材体检 / 生成判断
│   ├── SKILL.md                          # 双路径（未拍新写 A / 已拍重写 B）不可跳步主流程
│   ├── references/
│   │   ├── user-preferences.md           # 协作铁律与 9 项已定默认规范（来源标、章节条、不补拍等）
│   │   ├── new-script-guide.md           # 开拍前从零写硅谷101级脚本规范与四项自检表
│   │   ├── cut-rules.md                  # 已拍台词只删不改规则与原音频 80ms 剪口响度标准
│   │   ├── visual-system.md              # 四级画面优先级、全片 3 种画面状态、字体色值与配乐规则
│   │   ├── sv101-rules.md                # 硅谷101 三期标杆原片量化实测与取舍
│   │   ├── sv101-vfx-spec.md             # 硅谷101 六大标准视效的精确像素/滤镜/缓动参数规范
│   │   ├── material-pipeline.md          # 五大找片渠道 + 8 帧底部字幕高危区体检 + 来源登记硬流程
│   │   ├── libtv-decision.md             # LibTV / MAGI-2 生成判断表与防重复扣费自检
│   │   └── lessons.md                    # 实战复盘：10 条被否定的错误做法对照表
│   ├── scripts/
│   │   ├── transcribe_words.py           # 实录逐字时间戳转写（自动寻址运行环境）
│   │   ├── phrase_time.py                # 候选删减省时计算 + 原音频 ±0.25s 剪口响度实测
│   │   ├── footage_inventory.py          # 自有实拍目录缩略图总览生成
│   │   ├── archival_search.py            # 多渠道检索（YouTube 老广告 / Wikimedia 馆藏大图 / Bilibili）
│   │   ├── broll_qc_manifest.py          # 外部视频 8 帧硬字幕体检图 + sources_manifest.json 登记校验
│   │   └── bgm_analyze.py                # 本地配乐目录 BPM 与 10 段响度起伏分析
│   └── templates/
│       ├── feishu_script_builder.py      # 通用 JSON -> 飞书 12 节原生表格 XML 生成器
│       ├── example_spec_minimal.json     # 飞书生成器最小结构示例
│       └── example_ai_toy_v5_builder.py  # 《AI对话玩具》V5 完整重写脚本与分镜实战范本
│
└── product-video-edit/                   # 【开剪后】语义气口粗剪 / 硅谷101视效模板 / OpenMotion 渲染返修
    ├── SKILL.md                          # 实剪、试剪定手感、质检与聊天返修流程
    ├── references/
    │   ├── shot-plan.md                  # 分镜对齐与 V5 制作执行规范
    │   └── local.md                      # 粗剪档位、OpenMotion 防 1 帧闪现铁律与三道交付检查
    ├── scripts/
    │   ├── video_edit.py                 # 跨平台统一入口（setup / doctor / rough / openmotion / libtv）
    │   ├── rough_cut.py                  # -38 dB 有效人声核收边与语义气口自动剪切
    │   ├── libtv_setup.py                # 软链安全版 guizang-magi2-skill 与双端 LibTV MCP 配置器
    │   └── openmotion_rpc.py             # OpenMotion 本地 stdio MCP 调用桥接
    └── templates/sv101/                  # 可直接复用的硅谷101质感 OpenMotion 组件模板
        ├── sv101-base.css                # 标准字体、#0E0F12 微十字网格、4:3 虚化补边、防闪帧锁与字幕层
        ├── xray-spotlight.html           # 实拍压暗 + 圆形聚光放大镜渐进点亮（对标《1nm》光刻机）
        ├── evidence-highlighter.html     # 报道/官网截图微推 + 橙色荧光笔横刷划重点（对标《苹果关税》）
        └── schematic-and-chrome.html     # 滚动年份翻牌器 + 0.3s黑场章节卡 + 4:6列要点 + 38px常驻章节条
```

---

## 开源许可

本仓库采用 [MIT License](LICENSE) 开源。通过 `--with-libtv` 按需拉取的第三方外部技能 [`op7418/guizang-magi2-skill`](https://github.com/op7418/guizang-magi2-skill) 遵循其原仓库的 `AGPL-3.0` 协议。
