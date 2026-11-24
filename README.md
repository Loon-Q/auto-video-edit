# 自动剪辑

给 Codex 和 Google Antigravity（反重力）用的真人产品视频剪辑技能。包含审素材、自写制作分镜、剪口播、开头 30 秒试剪、OpenMotion 全片及聊天返修流程。技能名为 `product-video-edit`。

## 1. 安装到剪辑项目

从 GitHub 登录并下载 ZIP 后解压，或用 Git 克隆。若直接在解压后的仓库目录里工作，Codex 和 Antigravity 会读取其中的 `.agents/skills/product-video-edit/`。如果要放到另一条片的项目里，在本仓库目录运行下面对应的命令，把路径改为已有的剪辑项目目录。

**macOS**

```sh
python3 install.py "/你的/剪辑项目"
```

**Windows PowerShell**

```powershell
py -3 install.py "D:\剪辑项目"
```

也可以手动把 `.agents/skills/product-video-edit` 整个文件夹复制到剪辑项目下的 `.agents/skills/`。用 Codex 或 Antigravity 打开**剪辑项目目录**并新开会话。两款软件打开同一个目录时共用同一份项目技能。[Codex 技能目录](https://developers.openai.com/api/reference/cli) · [Antigravity 技能目录](https://antigravity.google/docs/skills)

## 2. 新电脑准备运行环境

准备这些工具，安装后打开新终端，让它们能从 PATH 找到。推荐 Python 3.12。

| 工具 | 用途 |
|---|---|
| [Python 3.11+](https://www.python.org/downloads/) | 安装助手、粗剪和本机运行入口 |
| [Git](https://git-scm.com/downloads)、[Node.js 22.18+（随附 npm）](https://nodejs.org/en/download) | 下载和构建固定版本的 OpenMotion |
| [FFmpeg](https://ffmpeg.org/download.html)（含 `ffprobe`） | 口播分析、剪切与视频导出 |
| [Google Chrome](https://www.google.com/chrome/) 或 Chromium | OpenMotion 预览和渲染 |

已有 Homebrew 的 Mac 可以用 `brew install python git node ffmpeg`，Chrome 可从官网安装。Windows 安装完 Python 后先检查 `py -3 --version`，并确认 `git`、`node`、`npm`、`ffmpeg` 和 `ffprobe` 能在新终端运行。

在**剪辑项目目录**执行对应的两行。

**macOS**

```sh
python3 .agents/skills/product-video-edit/scripts/video_edit.py setup
python3 .agents/skills/product-video-edit/scripts/video_edit.py doctor
```

**Windows PowerShell**

```powershell
py -3 .agents/skills/product-video-edit/scripts/video_edit.py setup
py -3 .agents/skills/product-video-edit/scripts/video_edit.py doctor
```

`setup` 安装粗剪依赖并下载、构建已经固定提交的 OpenMotion 源码。初次运行需要联网。OpenMotion 和运行环境保存在当前用户的独立目录。两个编辑器都能通过终端入口调用 OpenMotion，同一工程也可在本机 Studio 打开审片。[OpenMotion 源码安装说明](https://github.com/nexu-io/openmotion/blob/a44c714d0e702f3b9b02be8a7512bbf278c6294b/docs/install.md)

## 3. 开始第一条片

把大纲、原始素材、真人口播和可用配乐放到自己的项目里。告诉 Codex 或 Antigravity：

> 用 product-video-edit。先看同事给的台词大纲和原素材，重写我们的制作分镜，粗剪口播，然后做开头 30 秒。背景音乐从我给的本地目录选。

也可以直接说「先检查自动剪辑技能的本机环境，照仓库 README 补齐依赖」。预览后在对话里发截图、指出一句台词或说要改的画面，就能进入返修。

技能目录里有[制作分镜模板](.agents/skills/product-video-edit/references/shot-plan.md)和[本机剪辑命令](.agents/skills/product-video-edit/references/local.md)。
