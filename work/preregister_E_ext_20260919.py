# -*- coding: utf-8 -*-
"""Item 2 pre-registration: write the E = 50 / 400 extension's criteria into the plan document
BEFORE any run starts.  (Discipline: the criterion exists on disk, dated, before the verdict.)"""
import io
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
W = r'E:\workplace'
DOC = os.path.join(W, 'P2_GPU实验方案_20260919.md')
LOG = os.path.join(W, '变更日志.md')

SEC = """

---

## §E-扩展（r54j，2026-09-19）：轮数预算 E = 50 / 400 —— **判据先写在这里，然后才开跑**

**动机**：§13.1 / 理论文档 §7 现有的合成结论是"选择偏差随**选择噪声的绝对量**与**选择机会的次数**走，
而不取决于 val 与 test 是否同一个文件"。G3 只测了 E = 100 与 200 两点（溢价 +0.289 pp，t = 4.96，p = 7.8×10⁻⁴），
两点不足以区分"随 ln E 增长"与"阶跃"。同时，被**否证并撤回**的那条预言（溢价 ∝ σ√(2 ln E)，回归斜率
0.026 ± 0.222，p = 0.82，n = 101）需要一个**直接的四点设计**来正面检验。本扩展就是这最后一个 GPU 项。

**设计（与 G3 逐项相同，只改 `--epochs`）**：

| 项 | 值 |
|---|---|
| 数据 | `/root/datasets_mask/dota15_yolo/dota15_20p.yaml`（nc = 16；train 282 图；`val:` 与 `test:` 都指向 `images/val`，458 图 —— 别名配置，与 G3 完全一致） |
| 预训练 | `/workspace/weights/dota15_pretrain.pt` |
| 训练脚本 | `/workspace/train_obj.py`（md5 `316e074050dde23cde33e4a223ec46a8`，未改动） |
| 损失 | `--loss shapeiou` |
| 两臂 | base（默认 lr = 0.001）与 `--lr 0.005` |
| 种子 | 42–46（`--shuffle-seed`） |
| 预算 | **E = 50**（先跑）与 **E = 400** |
| 规模 | 5 种子 × 2 臂 × 2 预算 = **20 次训练**；对照 G3 的 20 次（E = 100/200） |
| 单价（实测） | 100 轮 ≈ 12 min、200 轮 ≈ 20 min ⇒ E = 50 ≈ 6 min、E = 400 ≈ 40 min ⇒ 合计 ≈ **7.7 h** |
| 保存周期 | `save_period = 5`（`train_obj.py` 内写死，不改为的是协议同一；E = 400 每 run ≈ 82 个权重 ≈ 0.82 GB，10 run ≈ 8.2 GB，磁盘余量 16 GB，队列内置 **< 4 GB 即 ABORT** 的看门狗） |
| 判据读取 | 溢价只读每个 run 的 `results.csv`（**逐 epoch**，与保存周期无关）：`premium = max_e V(e) − V(末轮)`，V = val 的 mAP50-95 ×100 |

**判据（现在写死，跑完照此判定，不修改）**：

- **C1（主判据，方向）**：溢价随 E 单调不减，且把每个 run 的溢价对 **ln E** 回归，斜率 > 0 且 **p < 0.05**
  （每预算 n = 10：5 种子 × 2 臂；四预算合计 n = 40）。判 met / not met。
- **C2（正面检验已撤回的那条预言）**：若溢价 ∝ σ√(2 ln E)，则 `premium(400) / premium(100)` 应落在
  **√(ln400/ln100) = 1.141 的 ±25 %**，即 **[0.86, 1.43]**。落在带内 ⇒ 该缩放**复活**（须重新审视撤回）；
  落在带外 ⇒ 现有结论"溢价水平由 val 曲线的形状决定、而非其抖动"成立。
  （G2 的同类检验用的就是带判据：WC 比 1.19 vs √3 → magnitude not met。）
- **C3（形状对照，G1 的教训前置）**：峰值相对位置 ê/E 的均值，|ê/E(400) − ê/E(100)| ≤ **0.05**；
  超出即宣布"本轮比较被形状混淆"，**不得**当作 E 效应报告。
- **C4（次级，Prop 4 不等式）**：在两个新预算上 WC = prem_val − prem_test > 0；
  兑现率（prem_test / prem_val）**不得**随 E 上升。小数结果照算，不做合格判定。
- **C5（设计同一性）**：数据 YAML / 预训练 / 种子 / 两臂 / 训练脚本 md5 与 G3 逐项相同，**唯一差别是 `--epochs`**；
  `save_period` 的取值只影响权重落盘数量，不影响任何判据量（C1 读逐 epoch 的 results.csv）。

**真阴性怎么写**：三条判据里任何一条 not met，都照原样写进 §13.1 与理论文档，并把"这说明什么"写清楚
（例如 C1 not met ⇒ "选择机会次数不改变溢价水平"；C2 落带外 ⇒ 撤回的那条预言**维持撤回**）。

**产物与留档**：`/workspace/g3ext_20260919/`（`ext.log`、`ext_manifest.jsonl`、`g3ext.DONE` / `g3ext.ABORT`），
权重在 `/workspace/runs/g3ext_e{50,400}_{base,lr005}_s{42..46}n/`；
分析脚本 `work/g3ext_verdict_20260919.py`（照 G3 同一口径），结果 CSV 拉回本地留档。
"""

t = io.open(DOC, encoding='utf-8').read() if os.path.exists(DOC) else '# P2 GPU 实验方案\n'
if '§E-扩展（r54j' in t:
    print('判据已存在，跳过')
else:
    io.open(DOC, 'a', encoding='utf-8', newline='\n').write(SEC)
    print('已把判据写入 %s（%d 字符）' % (os.path.basename(DOC), len(SEC)))

NOTE = """

### ⑫ r54j：E = 50 / 400 扩展实验开工（**判据先落盘**）

用户给了 B 机（`cpod-1uearmsfxbj2:25046`，GPU 已恢复）。上机勘察发现：B 机是**刚重启的容器**，
`/workspace/g1pp_g3_20260919/runs`、`g3.log`、conda env 都在，但 `/workspace/dota15_20p.yaml` 与
`/workspace/g2_val_*.yaml` 不在了——**真正在用的是 `/root/datasets_mask/dota15_yolo/dota15_20p.yaml`**
（我早先查错了路径，一度以为环境丢了）。核对结果：数据 YAML（nc = 16、val == test 别名、282/458 图）、
`dota15_pretrain.pt`、torch 2.4.0+cu121 / ultralytics 8.4.120、RTX 4090、外网**全部完好**；
G2/G3/G4 的逐 run `results.csv` 本地已有副本，证据链未受影响。唯一硬约束是**磁盘只剩 16 GB**。

判据（C1–C5）已写入 `P2_GPU实验方案_20260919.md` §E-扩展；队列 `g3ext_20260919.py` 内置上机前检、
失败即停（任一无 `weights/last.pt` 即 `g3ext.ABORT`）、**磁盘 < 4 GB 即 ABORT** 的看门狗，
以及 E = 50 先跑（约 1 h 出早期信号）、E = 400 后跑（约 6.7 h）的顺序。
"""
t2 = io.open(LOG, encoding='utf-8').read()
if '⑫ r54j' in t2:
    print('日志已存在，跳过')
else:
    io.open(LOG, 'a', encoding='utf-8', newline='\n').write(NOTE)
    print('已写入变更日志 ⑫ r54j')
