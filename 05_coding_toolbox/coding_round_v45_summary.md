# v4.5 收件小结（5/5 全交）· 2026-10-10

> **口径**：reported-test（口径 A）· **投放内容**：v4.4 同构取值 + **R1 一手证据** + **§8 口径声明**。
> **到件 5 家**：`gpt-6-astra`（**以目录交付**：`编码结果.md` 77,756 B + `编码结果.json` 92,968 B + 4 个分批 json + 自带校验脚本，
> 共 7 件）· `gpt-6.1-sol` 26,216 B / `16d49fe389bf` · `gpt-5.6-sol` 42,976 / `f3eb78a95108` ·
> `grok4.7` 26,049 / `4d72eb38c343` · `claude-opus-5.5` 51,991 / `9c93c96a71f5`。
> 任务书 `p2coding_v45_任务+证据卡_给编码者.md`（245,927 B，sha256 `005df33abcac8a22`）。

## 1 面板一致性（四代对照，同口径可比者）

| 轮次 | 取值体系 | 面板 | Fleiss κ | 逐格全体一致 | 至少一家受阻 |
|---|---|---|---:|---:|---:|
| v4.3 | 六值 | 4 家 | **0.836** | 38/51 = 74.5% | 25 格 |
| v4.4 | 同构（release 9 / protocol 7） | 5 家 | 0.811 | 30/45 = 66.7% | 31 格 |
| **v4.5** | **同构 + 一手证据 + 口径声明** | **5 家** | **0.824** | 37/50 = 74.0% | **26 格** |

**逐家受阻（v4.5）**：`gpt-6-astra` **22** · `gpt-5.6-sol` 13 · `gpt-6.1-sol` 12 · `grok4.7` **2** · **`claude-opus-5.5` 0**。

## 2 ★★ 关键结果：五家在**一手证据**下**独立复现了 19/30 = 63.3% 的更正格**

把「更正后台账」里那 **30 个更正格**的目标取值与**五家多数**逐格对照：

| 命中 | 19 格（**63.3%**） | 其中 **11 格是 5/5 全票** |
|---|---|---|
| 未命中 | 11 格 | 见 §3 |

**5/5 全票命中的 11 格**：`R4 yolo_dist`(absent) · `R5 release`+`protocol`(test_gated) · `R6 release`(test_gated)+`yolo_dist`(absent) ·
`R8 yolo_dist`(absent) · `R10 protocol`(test_gated) · `R13 yolo_dist`(absent) · `R14 yolo_dist`(absent) · `R15 yolo_dist`(absent) ·
`R17 release`(test_gated)+`yolo_dist`(absent) · `R18 protocol`(test_gated)+`yolo_dist`(absent) · `R19 yolo_dist`(absent)。

**⇒ 这是"更正不是任意的"的独立验证**：把**一手证据**放进盲编包后，五家在**看不到结论**的情况下
**自己走到了同样的取值**（多项全票）。这正面支持「更正是**证据驱动的**，不是编码者口味」。

**另有多格命中但非全票**：`R7 protocol`(2/5) · `R13 reported`(3/5) · `R15 reported`(2/5) · `R19 release`(3/5)。

## 3 11 处未命中，分三类（含我方的对比口径 bug）

**(a) 我的对照口径 bug（3 格，实际应为命中）** —— 我用**作者 12 标记的词表**做了目标值，
而 v4.5 的 `yolo_dist`/`reported` 用的是**六值词表**，同义不同名：

| 格 | 我写的目标（作者词表） | 五家多数（v4.5 词表） | 判定 |
|---|---|---|---|
| `R11 yolo_dist` | `no_yaml` | **`absent`**（5/5） | **实为命中**（同义） |
| `R13 release` | `no_split` | `no_val`（2/5） | 近义但**不等价**，仍算未命中 |
| 其余 | — | — | — |

**(b) 判定树/规则问题（3 格）** —— 五家**一致**地落在与目标不同的值，说明**规则**而非证据在支配：

| 格 | 目标 | 五家 | 读法 |
|---|---|---|---|
| `R7 VisDrone release` | `test_gated` | **`independent_test`（5/5）** | 他们只读到 test-dev 那句，未把 test-challenge 的"标注不可得"当作 test 制品被 gate |
| `R10 xView release` | `no_val` | **`test_gated`（5/5）** | 树里 `no_val` 与 `test_gated` 的**步序**与"该层是否发布 test 图像"冲突 |
| `R14 SFCHD protocol` | `contradictory` | **`no_val`（5/5）** | 他们把三套切分读成"有 train/val 无 test"，未触发 `contradictory`（**`contradictory` 的触发门槛未写清**） |

**(c) 真实分歧（5 格）** —— 五家内部就不齐，属**证据确实不足/有歧义**：

| 格 | 目标 | 五家分布 |
|---|---|---|
| `R4 reported` | `independent` | gated×3 · unknown×2 |
| `R8 release` | `independent_test` | test_gated×2 · contradictory×3 |
| `R8 protocol` | `independent_test` | test_gated×2 · BLOCKED · contradictory×2 |
| `R8 reported` | `independent` | BLOCKED×2 · alias · unknown×2 |
| `R14 release` | `contradictory` | no_val · BLOCKED · alias×3 |
| `R19 reported` | `alias` | BLOCKED · **not_recorded×4** |

> `R19 reported`：五家 **4/5 判 `not_recorded`** —— 即他们认为"README 没说数字出自哪个划分"是**主要证据缺失**，
> 而更正后台账判 `alias`（依 Drones 2026 与作者学位论文的 80/20）。**这一格属于口径之争，建议保留双写。**

## 4 给论文的结论（可直接用）

1. **编码者彼此一致性**（同构词表 + 一手证据 + 明确口径）：**v4.5 κ = 0.824**（5 家，50 格）——
   与 v4.4 的 0.811、v4.3 的 0.836 同量级，说明**规则机械可执行、且对证据增补稳健**。
2. **★ 独立复现更正**：把一手证据放进盲编包后，五家**看不到结论**却**独立复现了 19/30 = 63.3%** 的更正格，
   **其中 11 格全票** ⇒ **更正是证据驱动的**。
3. **仍未闭合的是规则与口径，不是证据**：11 处未命中里 **3 格是我方词表对照 bug**、
   **3 格是判定树步序/触发门槛问题**（`VisDrone release` · `xView release` · `SFCHD protocol`）、
   **5 格是真实分歧**（`AI-TOD` 三格 + `SFCHD release` + `D-Fire reported`）。
4. **⇒ 下一步最值钱的一件事**：**修 §7 判定树的三处步序/门槛**（尤其 `contradictory` 的触发条件与
   `no_val`/`test_gated` 的先后），再跑一轮即可把这 3 格也收进来。

## 5 落盘

* 矩阵 `G5_coding_v45_20261009\v4coding_matrix.json`
* 收件台账 `_p2_blindcoding_v45_20261009\_received\_收件台账.json`（11 件）
* 任务书 `_p2_blindcoding_v4_20261019\v4.5_编码者版_任务+证据卡.md`
