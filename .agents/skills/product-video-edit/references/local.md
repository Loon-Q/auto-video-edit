# 本机制作、OpenMotion 与交付

技能仓库首页 README 提供 Codex 和 Antigravity 安装方法。已安装技能中，下面的 `video_edit.py` 都指本技能 `scripts/video_edit.py` 的实际路径。macOS 用 `python3`，Windows PowerShell 用 `py -3`。

## 环境检查与一键安装

```sh
python3 video_edit.py setup
python3 video_edit.py doctor
# 如需启用 LibTV (MAGI-2 / Seedream) 视频与贴纸生成：
python3 video_edit.py libtv
```

`setup` 会在本机独立运行目录（默认 `~/.local/share/product-video-edit`，可用环境变量 `PRODUCT_VIDEO_RUNTIME` 自定义）中自动配置 Python 虚拟环境（含 `numpy`、`faster-whisper`、`yt-dlp`；加 `--with-stickers` 额外安装 `pillow`、`scipy` 供刀版白边贴纸脚本使用），并拉取构建固定版本的 OpenMotion。同仓库 `wlj-script-rewrite` 下的全部脚本会自动识别并复用该运行环境。

## 口播粗剪

```sh
python3 video_edit.py rough analyze "真人实拍Aroll.mp4" -o "暂停分析.json"
python3 video_edit.py rough cut "真人实拍Aroll.mp4" "暂停复核.json" -o "纯口播粗剪.mp4"
```

两条粗剪命令之间对照台词、转写和实际试听复核。分析文件里的 `pauses[].label` 不可照搬分条录制时的原始停顿时长，必须按**实际台词语义结构**逐条标注气口：
- 起止留白：开口前 `0.06s`，句末收尾 `0.16s`；每条分录的有声区间按 `-38 dB` 人声核收紧首尾静音拖尾（起音留 `0.03s`、尾音留 `0.05s`），避免叠加出多余顿感。
- 句间气口档位：`splice`（删口癖/句内拼）`0.04s`；`seamless`（同口气顺接 / 强反差紧顶 / 排比连问）`0.08s`；`flow`（流畅句转 / 悬念小顿）`0.13s`；`turn`（轻段转 / 进总纲 / 故事展开）`0.18s`；`chapter`（真正换景 / 换大章节）`0.26s`；普通 `comma` `0.12s`、`period` `0.16s`、`paragraph` `0.22s`，≤`0.22s` 句内自然停顿保留。
- 将核准的场记口令、重吸气声、衣料摩擦声、重复段、误读和无效前后段用源时间区间写入 `drops`，确认有声区间、停顿条目和拼接边界一致。精听粗剪确认对话流畅后再做视觉卡点。粗剪规则参考 [AI Talking Head Edit](https://github.com/moluyao/ai-talking-head-edit) 并按本团队实测口播节奏固化。

## OpenMotion 与防坑铁律

- `python3 video_edit.py openmotion studio "该视频的工作区"` 返回本机 Studio 地址。每条片使用自己的工作区，复用当前项目已有的工程。
- 没有原生 OpenMotion 工具时，用 `python3 video_edit.py openmotion call "该视频的工作区" get_project 参数.json` 调本机 MCP。用 `python3 video_edit.py openmotion tools "该视频的工作区"` 查看参数结构，Studio 启动结果中的 `authoringGuide` 指向该版本的合成指南。支持 stdio 的宿主也可使用 `python3 video_edit.py openmotion mcp "该视频的工作区"`。
- **根治单帧闪现铁律（必守）**：Hyperframes 激活 `<video>` 节点时会强制设置 `visibility: visible`，直接穿透父容器的 `visibility: hidden`。因此：
  1. 所有未出场的镜头容器在 CSS 中必须默认写死 `opacity: 0; isolation: isolate`（建立独立层叠上下文，防止子元素 `z-index` 穿插到上一段主持人和背景之间）；
  2. 任何 `<video>` 的 `data-start` 必须严格等于或晚于其容器 GSAP 淡入动画的起始时间，严禁提前 `0.01~0.02s`。
- **macOS 1080p 渲染防底部裁切**：在 macOS 上调用 `hyperframes render` 导出 1080p MP4 时，务必加上 `--experimental-fast-capture=false`（若运行目录存在 `shared/hyperframes-capture-fix.mjs`，一并通过 `NODE_OPTIONS` 挂载），避免系统 Headless Chrome 出现底部 86px 裁切。

## 交付检查

导出成片后不可只看命令返回 0，必须完成三项实测：
1. **抽帧目视核对**：按关键切镜点和跨幕接缝导出缩略网格图，逐镜核对画面与台词一致、花字无提前剧透、外部素材无原字幕穿帮、无单帧跳闪；
2. **黑帧与响度检测**：运行 `ffmpeg -i out.mp4 -vf blackdetect=d=0.05:pix_th=0.10 -af volumedetect -f null -`，确认零意外黑帧、口播与 BGM 响度平衡（整体均值约 `-15 ~ -16 dB`，历史原声窗口零 BGM 串音）；
3. **播放与工程归档**：提高播放兼容性可用 `+faststart` 封装 H.264 `yuv420p` / AAC 48kHz MP4，并保留可编辑 OpenMotion 工程。旧原生工程 ZIP 导入后若打开卡住，可将目标工程 `projects/工程ID/` 内容单独打包至 ZIP 根目录后导入。
