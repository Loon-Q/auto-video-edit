# 本机制作、OpenMotion 与交付

技能仓库首页 README 提供 Codex 和 Antigravity 安装方法。已安装技能中，下面的 `video_edit.py` 都指本技能 `scripts/video_edit.py` 的实际路径。macOS 用 `python3`，Windows PowerShell 用 `py -3`。

## 口播粗剪

```sh
python3 video_edit.py doctor
python3 video_edit.py rough analyze "真人实拍Aroll.mp4" -o "暂停分析.json"
python3 video_edit.py rough cut "真人实拍Aroll.mp4" "暂停复核.json" -o "纯口播粗剪.mp4"
```

两条粗剪命令之间对照台词、转写和实际试听复核。分析文件里的 `pauses[].label` 是程序按时长给的建议。将核准的重复段、误读和无效前后段用源时间区间写入 `drops`，确认有声区间、停顿条目和拼接边界一致。精听粗剪后再做视觉卡点。粗剪规则参考 [AI Talking Head Edit](https://github.com/moluyao/ai-talking-head-edit)，该脚本沿用团队实测的本机实现。

## OpenMotion

- 首次运行 `python3 video_edit.py setup`，默认运行目录为用户家目录的 `.local/share/product-video-edit`。可用 `PRODUCT_VIDEO_RUNTIME` 选择独立运行目录。在 PATH 或该运行目录的 `bin` 中找到 FFmpeg、FFprobe；Chrome 在自定义位置时设置 `HYPERFRAMES_BROWSER_PATH`。
- `python3 video_edit.py openmotion studio "该视频的工作区"` 返回本机 Studio 地址。每条片使用自己的工作区，复用当前项目已有的工程。
- 没有原生 OpenMotion 工具时，用 `python3 video_edit.py openmotion call "该视频的工作区" get_project 参数.json` 调本机 MCP。用 `python3 video_edit.py openmotion tools "该视频的工作区"` 查看参数结构，Studio 启动结果中的 `authoringGuide` 指向该版本的合成指南。支持 stdio 的宿主也可使用 `python3 video_edit.py openmotion mcp "该视频的工作区"`。按明确项目 ID 查询、保存、渲染和导出。版本和修订值从当前工程读取，冲突时重新读。导入后先打开指定工程的后台预览再请求导出。
- 按镜头任务选 OpenMotion 的画幅变化、分层、遮罩和转场方案。用户选择在 Studio 看时可用「评论此刻」和「画笔标注」。聊天里的截图和台词也能完成返修。在用户说先收意见时记录，等指示后动手。

## 交付检查

实际核对成片时长、音视频、首尾和修改点，抽查花字与口播、产品数量、人物分层、演示动作和原声。如果需要，提高播放兼容性可用 faststart 重新封装 H.264/AAC MP4。用 OpenMotion 工程导出保存可编辑 ZIP。

旧原生工程 ZIP 导入后如果打开或导出卡住，可以把包内目标工程的 `projects/工程ID/` 内容单独打包，使 `index.html`、`assets/` 和同级配置位于 ZIP 根目录。作为独立工程导入，按新项目 ID 打开预览并导出。
