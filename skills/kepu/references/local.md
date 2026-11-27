# 本机制作、分段精制、OpenMotion 渲染与四道交付核验（V5.1）

技能仓库首页 README 提供 Codex 和 Antigravity 安装方法。下面的 `video_edit.py` 指本技能 `scripts/video_edit.py` 的实际路径。macOS 用 `python3`，Windows PowerShell 用 `py -3`。

## 环境检查与一键安装

```sh
python3 video_edit.py setup
python3 video_edit.py doctor
# 如需启用 LibTV (magi-2) 视频生成桥接：
python3 video_edit.py libtv
```

`setup` 会在本机独立运行目录（默认 `~/.local/share/product-video-edit`）自动配置 Python 虚拟环境（含 `numpy`、`faster-whisper`、`yt-dlp`）并拉取构建固定版本的 OpenMotion。

## 4K 音画同源切片与紧凑气口标准

1. **严禁音画分家重切导致嘴型不同步**：
   - 真人出镜镜头与口播母带必须从**同一条原始 4K 音画同步相机文件**中，按 `1600 samples/frame @ 48kHz / 30fps`（每帧精确 `0.033333s`）同源切出，视频子片段加 `-g 15 -keyint_min 1 -bf 0` 短 GOP 编码，确保 Hyperframes 逐帧 seek 零偏差。
2. **NG 废片零拼句 + 紧凑语义气口**：
   - 遇到主播说错重录，**只取最后一次完整干净的 take**，绝不把前遍废片的前两句拼到重录后半句上。
   - 按写作连贯度收紧气口：同句分句 `0.06–0.14s`（`2–4` 帧），句末换气 `0.20–0.23s`（`6–7` 帧），剔除分条录制原始长静音与句尾低头复位帧；相邻补录真人镜用 4K `1.0x ↔ 1.3x` 景别交替消除跳帧。

## 分段 OpenMotion 精制与防坑铁律

- **分段工程 + 丝滑合片架构**：5–10 分钟长片优先按章节拆分为 `seg0`..`segN` 独立工程分别通过 `lint-project.mjs` 并渲染，避免单工程过大导致注意力稀释；章尾留 `0.40s` `#seam-stage` 光学推镜模糊（`scale: 1.0 → 1.10 + blur`），章首留 `0.40s` 收清进入，最外层 `#sv-chapter-bar` 贴底常驻不动。
- **合成全局整数采样母带**：以 `48,000 Hz` 整数采样点（`int(round(G_k * 48000))`）在 NumPy 中精确摆放各章音轨（`G_k` 每次递减 `0.40s` `xfade` 重叠量），叠加 `-0.22s` J-cut 丝滑转场声与余弦交叉淡化，保证全片 6–15 分钟**零毫秒累积漂移**且无静音断层。
- **OpenMotion Linter 零报错三铁律**：
  1. 未出场镜头层 `.sv-layer` 默认写死 `opacity: 0; visibility: hidden; isolation: isolate;`；`<video data-start>` 绝不早于容器出现帧，且物理视频时长严格大于 `data-duration`（零半途冻帧）。
  2. GSAP 动画**一律使用纯 GPU Transform（`x`、`y`、`scale`、`scaleX`、`opacity`）**，严禁 tween `left`、`top`、`width` 触发布局像素取整抖动（`gsap_non_transform_motion`）。
  3. 所有自定字体（`CangEr`、`Song`、`Sans`）必须在 CSS 顶部写明 `@font-face` 本地路径，且每个 `<audio>`/`<video>` 必填唯一 `id` 与 `data-hf-id`。
- **macOS 渲染命令**：挂载 `NODE_OPTIONS="--import file://$RUNTIME/openmotion/shared/hyperframes-capture-fix.mjs"` 调用 `hyperframes render -q looks`。

## 四道硬核交付检查（缺一不可）

导出成片后严禁只看命令返回 `0`，必须全部跑通：
1. **全片出镜嘴型互相关实测**：抽取各章全部主持人出镜片段，与 4K 原始相机音轨做波形互相关（`np.correlate`），确认全片最大音画偏差 **`< 10 ms`**（远小于 1 帧 `33.3 ms`）。
2. **24 帧关键画面目视抽检**：用 `read_file` 亲自查看合成后的高分缩略总览图，逐帧确认：花字零黑色底纹阴影、长标题零折行孤字、逻辑树不透明标签零穿字、左上来源标无裁切、章节接缝丝滑无黑屏、6 支商业隐喻视频质感统一。
3. **黑帧与响度检测**：运行 `ffmpeg -i out.mp4 -vf blackdetect=d=0.08:pix_th=0.05 -af volumedetect -f null -`，确认章节间零意外黑屏、整体响度均值约 `-15 ~ -16 dB`、峰值不削波。
4. **工程与双端技能同步**：封装 `+faststart` H.264 `yuv420p` / AAC 48kHz MP4，保留可编辑 OpenMotion 工程；若本轮沉淀了新规范，运行仓库 `python3 install.py --global --upgrade` 同步至本机全局并推送到 GitHub。
