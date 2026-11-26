# 自动剪辑技能套件（Codex & Google Antigravity）

面向真人主持的科技解说长视频（如《未来陪伴局》，对标硅谷101）与产品测评/盘点视频的全链路技能包，**macOS 与 Windows 跨平台通用，Codex 与 Google Antigravity（反重力）共用同一套配置**。

## 套件构成（双技能闭环 + LibTV 联动）

| 阶段 | 技能名 | 职责 |
|---|---|---|
| **阶段一：动工前重写脚本与生成判断** | [`wlj-script-rewrite`](.agents/skills/wlj-script-rewrite/SKILL.md) | 针对已拍完口播的片子：**台词只删不改**（基于实录逐字转写 + 原音频 `±0.25s` 最安静 `80ms` 响度实测剪口）；按硅谷101 双速引擎与 **3 种画面状态**重新设计逐镜分镜；按「真实画面 > 真实史料 > 原理画布 > LibTV 生成」逐镜判断哪些镜头用 `MAGI-2` 生成；按本地配乐 BPM 与动态起伏初配每章 BGM；最终输出原生可编辑表格到飞书云文档供审定。 |
| **阶段二：粗剪、包装与成片返修** | [`product-video-edit`](.agents/skills/product-video-edit/SKILL.md) | 剧本审定后执行：`-38 dB` 有效人声核收边 + 语义气口档位粗剪；先剪冷开场/开头试剪定手感；调用 OpenMotion 完成全片分层、前景白边贴纸、防 1 帧闪现渲染与跨幕拼接；交付前强制执行抽帧对照、`blackdetect` 零意外黑帧与 `volumedetect` 响度核验；支持聊天截图与口头意见快速返修。 |
| **可选联动：AI 视频与贴纸工厂** | `guizang-magi2-skill` + `LibTV MCP` | 一键拉取并修复 Antigravity / Codex 上的 LibTV Remote MCP（解决桌面端软链 `npx` 找不到 `node` 及长视频 60s 超时断连问题），支持 **Code to Video**（静音代码动作灰盒 → `MAGI-2` 全能参考精准卡点重绘）与刀版白边贴纸烘焙。 |

---

## 1. 安装与升级技能包

克隆或下载本仓库后，可安装到**单个剪辑项目**，或直接安装到**本机全局**（同时写入 Antigravity `~/.gemini/config/skills/` 与 Codex `~/.codex/skills/`）。已有旧版时加上 `--upgrade` 即可无损覆盖升级；加上 `--with-libtv` 可顺带配好 `guizang-magi2-skill` 与 LibTV MCP。

### 安装到本机全局（推荐，所有项目直接可用）

**macOS**
```sh
python3 install.py --global --upgrade --with-libtv
```

**Windows PowerShell**
```powershell
py -3 install.py --global --upgrade --with-libtv
```

### 安装到单个剪辑项目目录

**macOS**
```sh
python3 install.py "/你的/剪辑项目" --upgrade
```

**Windows PowerShell**
```powershell
py -3 install.py "D:\剪辑项目" --upgrade
```

---

## 2. 新电脑准备运行环境

请先准备以下基础工具并确保在新终端的 `PATH` 中可用（推荐 Python 3.12）：

| 工具 | 用途 |
|---|---|
| [Python 3.11+](https://www.python.org/downloads/) | 安装器、实录逐字转写（`faster-whisper`）、剪口响度检测、BGM 分析与粗剪入口 |
| [Git](https://git-scm.com/downloads)、[Node.js 22.18+（含 npm/npx）](https://nodejs.org/en/download) | 拉取构建固定版本 OpenMotion 及桥接 LibTV Remote MCP |
| [FFmpeg](https://ffmpeg.org/download.html)（含 `ffprobe`） | 音视频解码、气口剪切、素材缩略总览图与成片质检 |
| [Google Chrome](https://www.google.com/chrome/) 或 Chromium | OpenMotion 预览与 1080p 渲染 |
| `lark-cli`（可选） | 将重写后的脚本与原生分镜表格一键发布到飞书云文档 |

在仓库目录（或已安装技能的剪辑项目目录）执行环境初始化与自检：

**macOS**
```sh
python3 .agents/skills/product-video-edit/scripts/video_edit.py setup --with-stickers --with-libtv
python3 .agents/skills/product-video-edit/scripts/video_edit.py doctor
```

**Windows PowerShell**
```powershell
py -3 .agents/skills/product-video-edit/scripts/video_edit.py setup --with-stickers --with-libtv
py -3 .agents/skills/product-video-edit/scripts/video_edit.py doctor
```

`setup` 会在当前用户的独立运行目录（默认 `~/.local/share/product-video-edit`，可通过 `PRODUCT_VIDEO_RUNTIME` 自定义）自动安装 `numpy`、`faster-whisper`、`yt-dlp`（加 `--with-stickers` 额外安装 `pillow`、`scipy`），并拉取构建固定版本的 OpenMotion。`wlj-script-rewrite` 下的所有脚本均会自动寻址复用该运行环境，零硬编码路径。

---

## 3. 标准使用方式（直接发给 Codex 或 Antigravity）

### 场景 A：口播已拍完，从头重写脚本、重做分镜并判断哪些镜头用 LibTV 生成
> 用 `wlj-script-rewrite` 重写这期脚本与分镜：台词已拍完只做删减不改字，用原音频核准每个剪口；对标硅谷101重新设计逐镜画面、音乐与剪辑节奏，判断哪些镜头需要调用 LibTV 生成，最后输出到飞书文档给我审定，先不要开剪。

### 场景 B：脚本审定通过后，粗剪口播并做开头试剪 / 全片制作
> 脚本已确认，用 `product-video-edit` 按删减表先出纯口播粗剪版给我听；通过后先做冷开场+第一章试剪定手感，背景音乐从我给的本地目录按章节选。

---

## 4. 仓库目录速览

- [`.agents/skills/wlj-script-rewrite/`](.agents/skills/wlj-script-rewrite/)
  - [`SKILL.md`](.agents/skills/wlj-script-rewrite/SKILL.md)：0–9 步脚本重写主流程与 12 节飞书文档结构
  - `references/`：
    - [`user-preferences.md`](.agents/skills/wlj-script-rewrite/references/user-preferences.md)：协作方式与 9 项已定默认规范（来源小字、常驻章节条、不补拍等）
    - [`cut-rules.md`](.agents/skills/wlj-script-rewrite/references/cut-rules.md)：只删不改规则与原音频 `80ms` 剪口响度判定标准
    - [`visual-system.md`](.agents/skills/wlj-script-rewrite/references/visual-system.md)：四级画面优先级、全片 3 种画面状态、字体色值、年份滚动与配乐规则
    - [`sv101-rules.md`](.agents/skills/wlj-script-rewrite/references/sv101-rules.md)：硅谷101 三期标杆量化实测与取舍
    - [`libtv-decision.md`](.agents/skills/wlj-script-rewrite/references/libtv-decision.md)：LibTV / MAGI-2 生成判断表与防翻车自检
    - [`lessons.md`](.agents/skills/wlj-script-rewrite/references/lessons.md)：过往被否定的 10 条失败教训对照表
  - `scripts/`：`transcribe_words.py`（逐字时间戳转写）、`phrase_time.py`（删减省时与原音频剪口响度实测）、`footage_inventory.py`（实拍缩略总览图）、`bgm_analyze.py`（本地配乐 BPM 与起伏分析）、`archival_search.py`（真实史料与公开网源检索）
  - `templates/`：`feishu_script_builder.py`（通用 JSON 驱动飞书 XML 生成器）、`example_ai_toy_v5_builder.py`（《AI对话玩具》V5 完整实战范本）
- [`.agents/skills/product-video-edit/`](.agents/skills/product-video-edit/)
  - [`SKILL.md`](.agents/skills/product-video-edit/SKILL.md)、[`references/shot-plan.md`](.agents/skills/product-video-edit/references/shot-plan.md)、[`references/local.md`](.agents/skills/product-video-edit/references/local.md)
  - `scripts/`：`video_edit.py`（统一环境/粗剪/OpenMotion/LibTV 入口）、`rough_cut.py`（`-38 dB` 语义气口粗剪）、`openmotion_rpc.py`、`libtv_setup.py`（软链安全版双端 LibTV 配置）
