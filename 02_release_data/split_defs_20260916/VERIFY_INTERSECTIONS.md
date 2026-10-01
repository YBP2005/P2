# 三分划"三个交集为 0"的本地复算（2026-09-16）

> **用途**：正文 §8.1 说"构建后**必须验证三个交集为 0**（按文件名求交）——这是该协议能被信任的前提"。
> 此前这句话只能靠 pod 上的转述；本轮从 **B 机（无卡模式）** 拉回划分定义与三份文件名清单，
> 因此这句话现在**可以在本地复算**。

**来源**：`split_defs_20260916/`（含 `SHA256SUMS.txt`）

```text
# three-way protocol: train = same label subset as the published runs; val = carve-out from the pool
# minus that subset (seed 42); test = the corpus's own held-out split. Built 2026-09-14T07:37:27Z.
path: /workspace/datasets/split_5_5
train: train/20_percent/images
val: carve_sfchd20/images
test: test/images
nc: 2
names: ['hat', 'person']
```

## 1. 三份清单的规模

| 划分 | 清单文件 | 文件数 |
|---|---|---|
| train/20_percent | `train_20_percent_images.txt` | **2413** |
| carve_sfchd20 (val) | `carve_sfchd20_images.txt` | **1000** |
| test | `test_images.txt` | **6033** |

合计 **9446** 个文件（train 2413 + carve 1000 + test 6033）——**任何重复都会让合计偏大**。

## 2. 三个两两交集（**都必须是 0**）

| 交集 | 大小 |
|---|---|
| train/20_percent ∩ carve_sfchd20 (val) | **0** |
| train/20_percent ∩ test | **0** |
| carve_sfchd20 (val) ∩ test | **0** |

**结论：三个交集**全部为 0** ⇒ §8.1 的前提成立**

## 3. 与归档数字的交叉核对

| 量 | 本次本地复算 | 归档记录 | 一致？ |
|---|---|---|---|
| test 划分文件数 | **6033** | 6033（B 机 `val()` 的扫描行） | ✓ |
| carve 划分文件数 | **1000** | 1000（earlier recon 只看到 aitod） | — |

## 4. 结论与限制

- ✅ **§8.1 的"三个交集为 0"现可在本地复算**，不需要 pod、不需要 GPU（拉回一次即可）。
- ⚠️ **仍未闭合的**：**重新训练**依然需要 6 个语料本体；本文件只让"划分定义与划分清单"这一层可核。
- 说明：本文件是**新增件**，不替代 `_xframe/` 与 `xeval_20260916/`，三者分别覆盖跨框架证据、GPU 评估矩阵、划分定义。

*由 `work/verify_split_defs_20260916.py` 生成；清单来源哈希见 `split_defs_20260916/SHA256SUMS.txt`。*
