# `t1d_valext_20261002/` —— T1-d 的 `val` 侧补齐（2026-10-02）

**这是什么**：`t1d_dotatod15_{base100,lr005_100ep}_s42–51n` 共 **20 个 run** 的 `results.csv`，
**逐字节来自 A 机（`cpod-1u20pv1vhj4v:24581`）`/workspace/runs/<run>/results.csv`**（用 `work/gpu_ssh.py --profile a --get` 取回，未做任何修改）。

**为什么要它**：`P2_T1_registered-replication_long.csv` / `release_T1_registered-replication_summary.csv` 里
`T1-d` 的 `val` 侧长期只有 **n = 7**（seed 42–48），正文 Declarations 因此把该批 `val` 侧列为"三处不可复算例外"之一。
2026-10-02 实测：**20 个 run 的 `results.csv` 都还在 A 机上**（各 101 行 = 100 epoch + 表头），
`val` 曲线本来就在里面 ⇒ 补齐后 **n = 10**，且**不需要 `epoch*.pt`、不需要重训**。

**阳性对照（跑前做的）**：用这批曲线复算 n = 7 的配对臂差 = 均值 **−0.4043 pp**、t = **−5.893**、**p = 0.00106**、
95 % CI **[−0.5722, −0.2364]** —— 与已印值**逐位一致**（14/14 个 per-run 值也对上）；脚本 `work/p2_t1d_val_n10_20261002.py`。

**补齐后的读数（n = 10）**：均值 **−0.4056 pp**、SD 0.1564、**0+/10−**、t = **−8.201**、**p = 1.8148×10⁻⁵**、
95 % CI **[−0.5175, −0.2937]**。

**⚠ 一条陷阱**：本地 B 归档 tar（`b_artifacts_20260930.tgz`）里的 `t1d_*` 是**同名不同数据**（14 个 `val` 值里 8 个不符，
例 base s43：A **+0.865** vs B **+0.924**）⇒ **本目录的 `results.csv` 才是已印值的来源**，不要用 B 归档那份。
