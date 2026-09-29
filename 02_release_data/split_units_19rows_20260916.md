# 19 行 × 5 列单位标记表（副论文前置件）

> 由 `analysis\work\recompute_split_units_20260916.py` 生成；所有百分比由本表标记机械重算，无硬编码。
> 建立 2026-09-16。已施加 (h-1) 裁定（D-Fire 归干净）。

## 三种单位（正文须写明用哪一条）

| 单位 | 定义 |
|---|---|
| **release** | 基准自身发布物层：官方分划产物/脚本是否提供独立留出 test |
| **protocol** | 官方协议层：官方声明的划分，且该 test 是否本地可自评 |
| **yolo_dist** | 通用 YOLO 分发包层（＝审计 §1 表第 4 列所测的那一列） |
| **reported** | 实际报告层：文献报告的数字来自哪个划分、是否独立于选点 |

证据标记：(A) 审计明文｜(D) 由审计事实推导｜(?) 审计未表态

## 标记表

| # | benchmark | release | protocol | yolo_dist | reported | 证据类别 | 置信度 |
|---|---|---|---|---|---|---|---|
| 1 | COCO | `n_a(A)` | `independent_test(A)` | `clean(A)` | `clean(A)` | 官方计数 + mirror yaml | high |
| 2 | PASCAL VOC | `n_a(A)` | `test_gated(A)` | `alias(A)` | `alias(A)` | mirror VOC.yaml（两键逐行引用） | high |
| 3 | Objects365 | `no_test(A)` | `no_test(A)` | `no_test_key(A)` | `alias(D)` | mirror yaml + Ultralytics docs | high |
| 4 | Open Images v7 | `independent_test(A)` | `independent_test(A)` | `no_test_key(A)` | `alias(D)` | 官方 facts page + mirror yaml | high |
| 5 | DOTA v1.0 | `independent_test(A)` | `independent_test(A)` | `clean(A)` | `clean(A)` | 官方下载页 + mirror DOTAv1.yaml | high |
| 6 | DOTA v2.0 | `independent_test(A)` | `test_gated(A)` | `clean(A)` | `alias(D)` | 官方/mirror 文档 | high |
| 7 | VisDrone-DET | `independent_test(A)` | `independent_test(A)` | `clean(A)` | `clean(A)` | mirror + converter | high |
| 8 | AI-TOD | `contradictory(A)` | `contradictory(A)` | `unknown(A)` | `unknown(?)` | 官方 README（含两条互相矛盾的发布声明） | low |
| 9 | UAVDT | `no_val(A)` | `no_val(A)` | `unknown(A)` | `alias(A)` | 官方论文 + 两个 mirror（审计称 unverified beyond these two） | medium |
| 10 | xView | `no_test(A)` | `no_test(A)` | `no_test_key(A)` | `alias(A)` | mirror xView.yaml | low |
| 11 | DIOR | `independent_test(A)` | `independent_test(A)` | `no_test_key(A)` | `unknown(?)` | 官方描述（无计数）+ mirror DIOR-R yaml | low |
| 12 | NWPU VHR-10 | `no_split(A)` | `no_split(A)` | `unknown(A)` | `alias(A)` | 官方 TorchGeo（split 指 positive/negative） | high |
| 13 | SHWD | `no_yaml(A)` | `no_val(A)` | `train_val_alias(A)` | `alias(A)` | 官方 README + mirror Reflective_vests.yaml | medium |
| 14 | SFCHD | `alias(A)` | `no_val(A)` | `alias(A)` | `alias(A)` | 官方一方发布物（机器比对 _ev_sfchd_check2.py） | highest |
| 15 | MAFA | `no_val(A)` | `no_val(A)` | `unknown(?)` | `alias(A)` | 官方 CVPR PDF（pypdf 抽取） | high |
| 16 | Mendeley face-mask | `no_split(A)` | `no_split(A)` | `alias(D)` | `unknown(?)` | 官方数据记录 + mirror generator | lowest |
| 17 | WIDER FACE | `independent_test(A)` | `test_gated(A)` | `no_test_key(A)` | `alias(A)` | 官方站点（GT 不发布逐字核实）+ mirror | high |
| 18 | CrowdHuman | `test_gated(A)` | `alias(A)` | `no_test_key(A)` | `alias(A)` | 官方论文 + mirror | high |
| 19 | D-Fire (FireSmoke) | `independent_test(A)` | `independent_test(A)` | `clean(A)` | `unknown(?)` | 官方 README | medium |

## 重算结果

| 单位 | alias/非独立 | 可判定行中 | unknown |
|---|---|---|---|
| release（基准自身发布物层） | **10/19 = 52.6%** | 10/19 = 52.6% | 0 |
| protocol（官方协议层） | **13/19 = 68.4%** | 13/19 = 68.4% | 0 |
| yolo（通用 YOLO 分发包层（yolo_dist）） | **4/19 = 21.1%** | 4/15 = 26.7% | 4 |
| reported（实际报告层） | **12/19 = 63.2%** | 12/15 = 80.0% | 4 |

## 与审计已发表数字的交叉核对

- 审计 3a「字面 `val == test` **2/19**」→ 本表「分发包 config 两键同路径」(A 证源) 得 **2/19**，**复现 ✓**
  - 另 1 行 alias 由**生成器**造成（Mendeley face-mask），非分发包 config，不计入 3a 口径
- 审计「**14/19**」→ 本表 `reported` 得 **12/19**（差 -2）
- 审计「**5/19** clean」→ 本表 `reported=clean` 得 **3/19**（差 -2）
- 审计「12/19」为两行手调所得，**非**一致单位重算；本表按一致规则重算，数值不必相同

## 供正文采用的一组自洽数

- 字面 `val == test`（通用分发包 config，A 证源）：**2/19 = 11%** — PASCAL VOC, SFCHD
- 生成器制造的 train/val 同源：**1/19**（Mendeley face-mask），**口径不同，须单独表述**
- 官方协议层非独立：**13/19 = 68%**
- 实际报告层非独立：**12/19 = 63%**（unknown 4 行）
- 实际报告层干净：**3/19 = 16%**

## "same directory" 的四层级（解 (g0)）

- **L1** 通用分发包字面 `val==test`：2 行 — PASCAL VOC, SFCHD
- **L2** 分发包 `train==val`（F-C）：1 行 — SHWD
- **L3** 分发包干净但报告层非独立：9 行 — Objects365, Open Images v7, DOTA v2.0, UAVDT, xView, NWPU VHR-10, MAFA, WIDER FACE, CrowdHuman
- **L4** 其余：7 行

## 已施加的更正

- **(h-1) D-Fire / FireSmoke 族**：族行 "mixed" 判据取自一条 SHWD 血统的 config（A:59 引 Reflective_vests.yaml；A:52 注明其基于 SHWD）。属 FireSmoke/D-Fire 的三个副本全部 distinct。据 3a 明文采用的"发布物层"单位，D-Fire 归干净组。
- **(d-1) AI-TOD / DOTA 不对称**：审计对含 trainval 的 AI-TOD 标 F-C，对同样含 trainval 的 DOTA v1/v2 未标。本表统一采用"发布物/协议层"单位：trainval 属用户协议注意事项，不作判决依据；两处均不改判，但 AI-TOD 因 v2 发布声明自相矛盾而为 contradictory。

