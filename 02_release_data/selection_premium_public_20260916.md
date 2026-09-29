# 公开第三方日志上的"选择溢价"（2026-09-16）

**定义**（与我们在自己 run 上用的是同一套）：`premium = 最优轮 mAP50-95 − 末轮 mAP50-95`；
第二个读数为 `最优轮 − 末五轮均值`。Ultralytics 系日志报告的是 **best-validation checkpoint**，
所以这个差值正好是"在报告所用的划分上选点"所带来的成分。

**这一节能支持什么、不能支持什么**（写在前面，避免被读成更强的结论）：

- **能**：该成分在**他人发表的**日志里确实存在，并给出每条日志的量级；
- **不能**：不能给出**领域级**的量级分布——样本是 20 条、来自 6 个来源仓库，且多数未标注数据集与协议；也**不能**由此推出这些基准 `val` 与 `test` 同目录——
  日志里没有 yaml，那一条要靠 19 基准的别名审计，两者是**不同的证据**，必须分开陈述。

## 样本

| 文件 | 轮数 | 末轮 | 最优轮（位置） | 溢价 max−final | 溢价 max−末五轮均值 | 指标列名 |
|---|---|---|---|---|---|---|
| `aakashchalla12345678-yolov8n__unstated__yolov8n.csv` | 30 | 0.4861 | 0.4861 (ep 30) | **+0.00 pp** | **+0.26 pp** | `metrics/mAP50-95(B)` |
| `adityadgmath070-yolov8-fs-grafik-adamw-results6__unstated__yolov8.csv` | 100 | 0.4284 | 0.4284 (ep 100) | **+0.00 pp** | **+0.54 pp** | `metrics/mAP50-95(B)` |
| `adityadgmath070-yolov8-fs-grafik-adamw-results7__unstated__yolov8.csv` | 100 | 0.4403 | 0.4494 (ep 74) | **+0.91 pp** | **+0.79 pp** | `metrics/mAP50-95(B)` |
| `adityadgmath070-yolov8-fs-grafik-adamw-results8__unstated__yolov8.csv` | 100 | 0.4275 | 0.4511 (ep 30) | **+2.36 pp** | **+2.55 pp** | `metrics/mAP50-95(B)` |
| `adityadgmath070-yolov8-fs-grafik-sgd-results1__unstated__yolov8.csv` | 100 | 0.3151 | 0.3167 (ep 97) | **+0.16 pp** | **+0.17 pp** | `metrics/mAP50-95(B)` |
| `adityadgmath070-yolov8-fs-grafik-sgd-results2__unstated__yolov8.csv` | 100 | 0.4402 | 0.4459 (ep 65) | **+0.57 pp** | **+0.58 pp** | `metrics/mAP50-95(B)` |
| `adityadgmath070-yolov8-fs-grafik-sgd-results3__unstated__yolov8.csv` | 100 | 0.4515 | 0.4648 (ep 53) | **+1.33 pp** | **+1.33 pp** | `metrics/mAP50-95(B)` |
| `adityadgmath070-yolov8-fs-grafik-sgd-results4__unstated__yolov8.csv` | 100 | 0.4340 | 0.4458 (ep 84) | **+1.18 pp** | **+1.20 pp** | `metrics/mAP50-95(B)` |
| `ayyappakorla-yolov3-results__unstated__yolov3.csv` | 200 | 0.9011 | 0.9041 (ep 198) | **+0.31 pp** | **+0.20 pp** | `metrics/mAP_0.5:0.95` |
| `dhanduramesh-yolov11s__ppe-css-data__yolo11n.csv` | 1 | 0.4430 | 0.4430 (ep 1) | **+0.00 pp** | — | `metrics/mAP50-95(B)` |
| `ericmorning-pcb-yolo-comparison__pcb-components__yolo11.csv` | 145 | 0.4647 | 0.4863 (ep 115) | **+2.16 pp** | **+2.33 pp** | `metrics/mAP50-95(B)` |
| `ericmorning-pcb-yolo-comparison__pcb-components__yolo12.csv` | 150 | 0.4698 | 0.4853 (ep 132) | **+1.55 pp** | **+1.57 pp** | `metrics/mAP50-95(B)` |
| `ericmorning-pcb-yolo-comparison__pcb-components__yolov8.csv` | 93 | 0.4467 | 0.4621 (ep 63) | **+1.54 pp** | **+1.49 pp** | `metrics/mAP50-95(B)` |
| `ikram0703-yolov8-ema-Model1__unstated__yolov8.csv` | 123 | 0.6311 | 0.6385 (ep 98) | **+0.74 pp** | **+0.62 pp** | `metrics/mAP50-95(B)` |
| `ikram0703-yolov8-ema-Model2__unstated__yolov8.csv` | 131 | 0.6290 | 0.6301 (ep 106) | **+0.10 pp** | **+0.10 pp** | `metrics/mAP50-95(B)` |
| `ikram0703-yolov8-ema-Model3__unstated__yolov8.csv` | 81 | 0.6293 | 0.6435 (ep 56) | **+1.42 pp** | **+1.27 pp** | `metrics/mAP50-95(B)` |
| `ikram0703-yolov8-ema-Model4__unstated__yolov8.csv` | 182 | 0.6058 | 0.6071 (ep 157) | **+0.14 pp** | **+0.15 pp** | `metrics/mAP50-95(B)` |
| `ikram0703-yolov8-ema-Model5__unstated__yolov8.csv` | 109 | 0.6294 | 0.6363 (ep 84) | **+0.70 pp** | **+0.72 pp** | `metrics/mAP50-95(B)` |
| `kimmkless-yolodetector__train2-vehicle-5class__yolov8n.csv` | 100 | 0.4327 | 0.4327 (ep 100) | **+0.00 pp** | **+0.83 pp** | `metrics/mAP50-95(B)` |
| `kimmkless-yolodetector__train4-face-expression__yolov8n.csv` | 5 | 0.5803 | 0.5803 (ep 5) | **+0.00 pp** | **+12.94 pp** | `metrics/mAP50-95(B)` |
| `kimmkless-yolodetector__train8-plant-disease__yolov8n.csv` | 100 | 0.4745 | 0.5029 (ep 80) | **+2.84 pp** | **+2.82 pp** | `metrics/mAP50-95(B)` |
| `nhnthanhj-metrics-result-f1-yololight__unstated__yolo-light-seg.csv` | 47 | 0.6521 | 0.7086 (ep 42) | **+5.65 pp** | **+2.42 pp** | `metrics/mAP50-95(B)` |
| `nhnthanhj-metrics-result-f1-yolov8n__unstated__yolov8n-seg.csv` | 74 | 0.7093 | 0.7300 (ep 54) | **+2.07 pp** | **+2.10 pp** | `metrics/mAP50-95(B)` |
| `ottogalt-yolo-result__unstated__yolov8.csv` | 20 | 0.9595 | 0.9595 (ep 20) | **+0.00 pp** | **+0.56 pp** | `metrics/mAP50-95(B)` |

> 「最优轮」读的是各日志自己的 **epoch 列**（表内 `ep` 即该列的值），不是行号；
> 本目录多数日志的 epoch 从 1 起、`ayyappakorla` 的 yolov3 从 **0** 起，两种都用列值，故可跨行比较。
**未纳入统计的日志**（轮数过少，不足以谈"选择"）：`aakashchalla12345678-yolov8n__unstated__yolov8n.csv`（30 轮）、`dhanduramesh-yolov11s__ppe-css-data__yolo11n.csv`（1 轮）、`kimmkless-yolodetector__train4-face-expression__yolov8n.csv`（5 轮）、`ottogalt-yolo-result__unstated__yolov8.csv`（20 轮）

## 读法

- 完整日志（≥40 轮）共 **20** 条，来自 **6** 个来源仓库；溢价中位数 **+1.04 pp**、最大 **+5.65 pp**、最小 **+0.00 pp**；**18/20** 条为正。
- 分布：+0.00、+0.00、+0.10、+0.14、+0.16、+0.31、+0.57、+0.70、+0.74、+0.91、+1.18、+1.33、+1.42、+1.54、+1.55、+2.07、+2.16、+2.36、+2.84、+5.65
- **最要紧的一点**：最大的一条溢价 **+5.65 pp** 出现在一条正常的公开发布日志里，而这类文献里被报告的效应常常只有 0.5–2 pp 量级——也就是说**选择成分可以与所报告的效应同量级甚至更大**。中位数 +1.04 pp 也已经不小。这解释了为什么"报告值在哪个划分上选出来"不是细节。
- 但样本仍小（20 条、6 个来源，且多数来源未标注数据集/协议），因此**只能**写成"该成分在他人发表日志中普遍存在且可量化"，**不能**给出领域级分布，也**不能**由此推出基准别名。

## 可核性

- **字节级可核**：每一条日志的 **SHA-256 与字节数**见同目录 `SHA256SUMS.txt`（取回日期 2026-09-16）。
  任何人可比对"被分析的字节"与"流通的字节"是否一致。
- **来源已补**：同目录 `PROVENANCE.md` 现已写出。全部 24 个文件**都**由内容哈希或唯一字节数匹配到**具体来源路径**（8 个 Kaggle dataset + 1 个 GitHub repo，固定于 commit `2417aff0457c`），未溯源条目 0。映射不是按文件名相似度猜的：脚本把 `_work\kg\*.zip` 里**每个条目**都哈希一遍，再与本地文件的 sha256 对撞。复核：`python analysis\work\build_provenance.py`。
- **仍**不可由本目录推出的两件事（见 `PROVENANCE.md` §4）：① Kaggle 侧的**确切下载版本**；
  ② 这些基准的 `val`/`test` 是否同目录（日志不带 yaml）。

## 还差什么（写进正文时应同时说明）

1. **样本量**：20 条、6 个来源——足以说明该成分在他人日志中存在并给出量级，但不足以给出领域级分布；要谈分布需要几十条以上可溯源日志。
2. **协议未知**：公开日志不带 yaml，因此无法判断该 run 的 `val` 与 `test` 是否同一目录；
   所以"溢价存在"与"基准别名"是两个独立命题，不能互相代替。
3. **端点约定**：日志只给逐 epoch 验证值；公开仓库通常不记录"报告的是哪一轮"，
   因此溢价是**上界**读法（假设报告的就是 best）。
4. **列名口径**：本表同时接受 Ultralytics 新拼写 `metrics/mAP50-95(B)` 与 YOLOv5/v3 旧拼写
   `metrics/mAP_0.5:0.95`（逐行标出用的是哪一个）。两种拼写指的是同一个量，但**列名不同**——
   任何"用列名去筛日志"的脚本都会漏掉另一支，这是本条的目的：让口径差异可见。

## 变更记录

- **2026-09-16 19:2x 修正（影响数字）**：首版只用 `mAP50-95` 这一种子串去认列名，
  于是 YOLOv5/v3 旧拼写的 `ayyappakorla-yolov3-results__unstated__yolov3.csv` 被 `read_log` 判为 None
  并**静默消失**（连"轮数过少"那一行都没进）。它实际是一条 200 轮的完整日志，溢价 **+0.31 pp**。
  修正后：样本 **19 → 20 条**、来源 **5 → 6 个**、中位数 **+1.18 → +1.04 pp**、正例 **18/20**。同时加了"未能解析的日志必须列出"这一节，使同类静默丢弃不再可能。
- **2026-09-16 19:10 更正**：三条 `kimmkless` 行原写作 `__train2__` / `__train4__` / `__train8__`，
  那是取回时的临时名；目录里实际是带任务名的 `__train2-vehicle-5class__` / `__train4-face-expression__` /
  `__train8-plant-disease__`。对应关系由**字节数**（12668/811/12718，与 `PROVENANCE.md` §1 的 GitHub tree 一致）确认。
  本版起，表内文件名恒为**目录里的真实文件名**，并由 `work\check_premium_filenames.py` 逐名验证存在性。

---

生成脚本：`analysis/work/selection_premium_public.py`（纯本地、无网络）。每条日志的来源仓库以文件名前缀标识；
确切来源（来源引用、源内路径、许可、固定点）见同目录 `PROVENANCE.md`。
生成时间：2026-09-16 19:16
