# G8 编码结果 · GLM-5.2（第三批盲编 · 19×4）

> 本文件为独立第二编码结果，依据 `00_任务_19x4盲编_给编码者.md` 第 2 节写死的读法判定。
> 编码者仅凭自身对公开来源的了解判定，**未重读一手文档、未联网、未使用任何 API key 或凭据文件**，
> **未阅读 `returns/` 下任何其它编码者的 md 文件**。

## 编码者标识与盲法声明

- 编码者标识：**GLM-5.2**
- 盲法声明：
  - 联网：**否**
  - 读过其它编码者的材料：**否**（仅阅读了用户直接给出的两份任务文件 `00_任务_19x4盲编_给编码者.md` 与 `01_空白编码表_19x4_给编码者.md`；未打开 `E:\workplace` 下任何稿件、补充材料或其它编码者结果；未联网；未使用任何 API key 或凭据文件）

## 19 行判定（ROW 格式）

```
ROW 1 | COCO | release=yes | protocol=no | yolo_dist=unknown | reported=yes | reason: COCO ships separate train2017/val2017/test2017 dirs (test structurally independent of train and val), but test-dev GT is withheld and server-gated (not locally evaluable); the MS paper + official leaderboard report test-dev results independent of val selection, while the ultralytics coco.yaml has no test key (practitioners report on val).
ROW 2 | PASCAL VOC | release=yes | protocol=yes | yolo_dist=unknown | reported=yes | reason: Per rule 4 using VOC2007 (the version official retrospective papers report): VOC2007 ships trainval/test as separate dirs with PUBLIC test labels (locally evaluable); the ultralytics VOC.yaml has no test key (its val key serves as VOC2007 test); the official paper reports VOC2007 test, independent of trainval selection.
ROW 3 | Objects365 | release=yes | protocol=no | yolo_dist=unknown | reported=unknown | reason: Objects365 releases train/val/test as separate dirs (test structurally independent), but test GT is withheld for the challenge (server-gated); the ultralytics config has no usable test key; I cannot confirm from memory whether the official paper's headline number is drawn from val (selection-contaminated) or from the held-out test.
ROW 4 | Open Images v7 | release=yes | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: OID ships train/val/test as separate dirs, but I cannot resolve from memory whether the official protocol's test is locally evaluable (Kaggle-server gating vs. publicly downloadable test-box CSVs are in tension), nor which half the official paper/leaderboard actually reports.
ROW 5 | DOTA v1.0 | release=yes | protocol=no | yolo_dist=unknown | reported=yes | reason: DOTA ships train/val/test as separate dirs, but test GT is withheld (server-gated); the ultralytics DOTAv1.yaml has no usable test key; the official paper/leaderboard report test-server results independent of val selection.
ROW 6 | DOTA v2.0 | release=yes | protocol=no | yolo_dist=unknown | reported=yes | reason: Same structure as DOTA v1.0 — separate test dir but server-gated GT; no usable test key in the mirror yaml; the official paper reports test results independent of val selection.
ROW 7 | VisDrone-DET | release=yes | protocol=yes | yolo_dist=unknown | reported=yes | reason: VisDrone releases train/val/test with public test annotations (locally evaluable); the ultralytics visdrone.yaml's test key is unconfirmed (treated as absent); the official paper reports test results independent of val selection.
ROW 8 | AI-TOD | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: The official README contains two mutually contradictory release statements (per the evidence pointer) and, as a blind coder who cannot re-read the primary document, I cannot resolve whether a separate held-out test with locally evaluable labels exists or which half the paper reports.
ROW 9 | UAVDT | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: The evidence pointers are flagged as unverified beyond two mirrors, and my independent memory of UAVDT's split is insufficient to confirm a separate held-out test, locally evaluable labels, or which half the official paper reports.
ROW 10 | xView | release=yes | protocol=no | yolo_dist=unknown | reported=yes | reason: xView ships train (labeled) and test (images only) as separate dirs (test structurally independent), but test GT is withheld for the challenge (server-gated); the ultralytics xView.yaml has no usable test key; the official challenge leaderboard reports test results independent of selection.
ROW 11 | DIOR | release=yes | protocol=yes | yolo_dist=unknown | reported=unknown | reason: DIOR ships train(11725)/test(11738) as separate dirs with public test labels (locally evaluable); the mirror DIOR-R yaml's test key is unconfirmed; with no dedicated val set, "independence from selection" is ill-defined, so I cannot confirm the reported test number is selection-independent.
ROW 12 | NWPU VHR-10 | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: The official release only distinguishes positive(650)/negative(150) image sets (per TorchGeo), with no official train/val/test split config; the original 2014 paper predates the held-out-test convention and reports no canonical benchmark number on a fixed test half.
ROW 13 | SHWD | release=yes | protocol=yes | yolo_dist=unknown | reported=unknown | reason: SHWD ships train/test with public test labels (open dataset, locally evaluable); the mirror Reflective_vests.yaml's test key is unconfirmed; with no dedicated val, I cannot confirm the README's reported number is independent of checkpoint selection.
ROW 14 | SFCHD | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: SFCHD has no widely documented public split configuration in my knowledge; I cannot determine its release structure, local-evaluability, or reported-number provenance without re-reading the first-party release file.
ROW 15 | MAFA | release=yes | protocol=yes | yolo_dist=unknown | reported=yes | reason: MAFA ships train/test with public test labels (locally evaluable); no ultralytics MAFA config exists; the CVPR LED paper reports test results independent of selection.
ROW 16 | Mendeley face-mask | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: I cannot reliably determine from memory whether this Mendeley-hosted record ships an official held-out test split; the "mirror generator" phrasing suggests split generation rather than a fixed official release, so all four units are unresolvable blind.
ROW 17 | WIDER FACE | release=yes | protocol=no | yolo_dist=unknown | reported=yes | reason: WIDER FACE ships train/val/test as separate dirs (test structurally independent), but the official site withholds test GT (server-gated, verified word by word); the ultralytics widerface.yaml has no test key; the CVPR paper reports test-server results independent of val selection.
ROW 18 | CrowdHuman | release=yes | protocol=yes | yolo_dist=unknown | reported=unknown | reason: CrowdHuman ships train/val/test with public test annotations (locally evaluable); the ultralytics crowdhuman.yaml's test key is unconfirmed; I cannot confirm from memory whether the official paper's headline number is drawn from the held-out test or from val.
ROW 19 | D-Fire (FireSmoke) | release=yes | protocol=yes | yolo_dist=unknown | reported=unknown | reason: D-Fire ships train/test with public test labels (locally evaluable); the mirror yaml's test key is unconfirmed; with no dedicated val, I cannot confirm the README's reported number is drawn from a test half independent of checkpoint selection.
```

## 歧义说明（规则本身仍有两种读法之处）

1. **Row 4（Open Images v7），`protocol` 单元**：两种读法——(a) "官方协议经 Kaggle 服务器门控测试"⇒ `protocol=no`；(b) "测试框标注 CSV 可公开下载，故测试可本地自评"⇒ `protocol=yes`。当"服务器门控"与"测试 GT 实际公开"并存时，规则未写明应以哪一条为准，我无法消解，故记 `unknown`。同族的 xView / WIDER FACE / DOTA 测试 GT 明确扣留，无此张力，故判 `no`。

2. **Row 8（AI-TOD）、Row 9（UAVDT）**：证据指针本身标注了一手源不可靠（README 自相矛盾 / 镜像不可验证）。作为盲编者无法重读一手文档，只能记 `unknown`；非盲、有一手访问权限的编码者可能给出更硬的 `yes/no`。这一点本身可能造成本批与有原文访问权批次之间的系统性 κ 偏低，建议论文注明。

3. **只有 train/test、无独立 val 的基准（Row 11 DIOR、Row 13 SHWD、Row 19 D-Fire），`reported` 单元**：当不存在独立的选择半区时，"与检查点选择相互独立"这一判据本身欠定义——单次 train→test 直接报告读作 `yes`，而任何超参调优读作 `no`。规则未给出门控判据，故我统一记 `unknown`；若协调者另给一条"无 val 即默认 selection 不可证⇒unknown"的写死读法，这三行可机械统一。

## 汇总统计（自查）

- 共 19 行 × 4 单元 = 76 个判定。
- `yes`：release 13、protocol 8、reported 8。
- `no`：release 0、protocol 6、reported 0。
- `unknown`：release 6、protocol 5、reported 11。

其中 `release` 全程无 `no`：依规则第 3 条，无切分件或无 test 键统一记 `unknown` 而非 `no`，且本批凡有独立 test 目录者（即使标注扣留）均记 `yes`，故 `release` 一列不出现 `no`。
