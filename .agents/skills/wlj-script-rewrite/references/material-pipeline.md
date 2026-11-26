# 全渠道真实素材收集、无字幕体检与来源登记硬流程

硅谷101 质感的底气来自**高密度的真实画面与一手原文证据**，而不是靠后期硬画卡片。同时，栏目已定规则要求**不主动安排低效补拍、严禁带入外部原视频硬字幕/水印、第三方画面左上角标 22px 来源小字并在 3 秒后淡出**。所有外部素材从检索到进入剪辑工程，必须走完以下标准闭环。

---

## 一、五大标准找片渠道（替代盲搜与现场补拍）

| 素材类别 | 首选检索渠道与工具 | 关键词公式与实操要点 |
|---|---|---|
| **1. 历史老广告 / 馆藏实物运转 / 早期发布会** | `archival_search.py --source youtube` | 用英文搜原始年份与厂商：`"<Product>" commercial <Year>`、`"<Product>" Toy Fair / CES demo <Year>`、`"<Museum>" "<Object>"`。优先选无后人解说字幕的原始转录带。 |
| **2. 公有领域馆藏高清图 / 人物老照片 / 专利插图** | `archival_search.py --source wikimedia` | 检索 Wikimedia Commons 公有领域或 CC 馆藏原图（如 `Edison phonograph doll 1890`），直接拿原始高分辨率大图，不搜模糊网图。 |
| **3. 权威报道 / 官方发布页 / 芯片规格书（证据卡）** | 浏览器打开一手原网页高清截图 | 找事件源头页面（如 OpenAI Blog、Apple Newsroom、乐鑫 Espressif 官网、Forbes / Fast Company / Reuters 原文），截 `≥ 1920px` 宽的正文核心段，供荧光笔高亮模板 `evidence-highlighter.html` 使用。 |
| **4. 国内/现代竞品官方演示与开源架构** | 产品官网宣传片、`archival_search.py --source bilibili`、GitHub 仓库 | 官网首屏背景视频往往是无字幕高码率裸片；B 站优先找品牌官方号无花字演示段。 |
| **5. 家常具象动作与通用行业空镜** | 厂商公开 Press Kit、免版税高清素材库（Pexels / Pixabay）、YouTube 实拍 | 水龙头开关慢动作、拔路由器电源、数据中心机房冷通道、客厅环境等通用镜头一律网上找干净实拍，不折腾现场补拍。 |

---

## 二、外部素材入库三道硬门槛（必跑 `broll_qc_manifest.py`）

> **铁律**：任何下载回来的外部视频，未经抽帧目视核验确认“无硬字幕、无台标遮挡”，**严禁**写进工程！

### 第 1 步：批量生成 8 帧字幕高危区体检图
把下载好的候选素材放入项目外部素材目录（如 `03_历史与资料素材/`），运行：

```sh
python3 scripts/broll_qc_manifest.py inspect "03_历史与资料素材" \
  --sheet "03_历史与资料素材/_broll_qc_sheet.jpg" \
  --manifest "03_历史与资料素材/sources_manifest.json"
```

脚本会对每条视频探测分辨率/帧率/音轨，并均匀抽取 **8 帧**拼成总览图（每帧在高度 `78%` 处画有一条红色参考线标出底部字幕高危区），同时初始化 `sources_manifest.json`（初始状态为 `unverified`）。

### 第 2 步：逐条看图判定（绝不跳步）
必须打开 `_broll_qc_sheet.jpg` 逐行目视检查全部 8 帧：
- **`clean`（直接可用）**：全程无原视频字幕、无居中水印、画质清晰。
- **`crop_bottom`（裁底可用）**：仅最底部边缘带小字幕，且主体靠上，可通过放大 `1.12–1.18x` 上移构图完全裁出画外而不伤主体（需在 `notes` 写明裁切比例，且在成片抽帧时二次复核）。
- **`rejected`（立即弃用）**：字幕压在主体上（如此前压在底部的日文字幕 EMO 片段）、满屏花字或严重糊片——当场标 `rejected` 并换源，绝不凑合使用。

### 第 3 步：登记来源文案并锁定清单
检查通过后，把每条素材的判定结果与精确的左上角来源文案写回 `sources_manifest.json`：

```sh
# 第三方素材（自动生成 "画面来源：Mattel (1985)"，左上 22px 显示 3 秒淡出）
python3 scripts/broll_qc_manifest.py register "03_历史与资料素材/sources_manifest.json" \
  "03A_TeddyRuxpin_1985.mp4" --status clean --third-party --source "Worlds of Wonder (1985)" --shots "1-8,1-9,1-11"

# 自有实拍或 LibTV 生成（标记 --own，不显示左上来源小字）
python3 scripts/broll_qc_manifest.py register "03_历史与资料素材/sources_manifest.json" \
  "G1_actor_freeze.mp4" --status clean --own --shots "2-5"

# 开剪前一键校验是否还有漏检或漏填来源的第三方素材（返回 0 才允许进工程）
python3 scripts/broll_qc_manifest.py check "03_历史与资料素材/sources_manifest.json"
```

---

## 三、入库文件命名约定

统一采用 `序号或镜号_主体简名_年份或来源.扩展名`，做到看文件名就知用途：
- 历史史料：`01_EdisonDoll_RealPlay_1890.mp4`、`03_TeddyRuxpin_Ad_1985.mp4`
- 证据截图：`EV01_FastCompany_8000Lines_2015.png`、`EV02_OpenAI_ChatGPT_20221130.png`
- 现代产品与通用空镜：`MOD01_Loona_Clean.mp4`、`ENV01_DataCenter_Rack.mp4`
- LibTV 生成镜头：`G1_Actor_StageFreeze.mp4`、`G3_RelayRace_Magi2.mp4`
