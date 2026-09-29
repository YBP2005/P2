# -*- coding: utf-8 -*-
"""
在**本地**复算 §8.1 的那句"构建后必须验证三个交集为 0"。
输入：`split_defs_20260916/`（本轮从 B 机无卡模式拉回的划分定义与三份文件名清单）。
输出：`split_defs_20260916/VERIFY_INTERSECTIONS.md`
"""
import hashlib, io, os, sys

sys.stdout.reconfigure(encoding='utf-8')
D = r'E:\workplace\split_defs_20260916'
OUT = os.path.join(D, 'VERIFY_INTERSECTIONS.md')

SETS = {
    'train/20_percent': 'train_20_percent_images.txt',
    'carve_sfchd20 (val)': 'carve_sfchd20_images.txt',
    'test': 'test_images.txt',
}


def load(fn):
    p = os.path.join(D, fn)
    if not os.path.exists(p):
        sys.exit('!! 缺 %s' % p)
    lines = io.open(p, encoding='utf-8', errors='replace').read().split('\n')
    # 取 basename（某些清单可能是相对路径），去空行
    return [os.path.basename(l.strip()) for l in lines if l.strip()]


sets = {k: load(v) for k, v in SETS.items()}
rep = []
def emit(s=''):
    print(s); rep.append(s)

emit('# 三分划"三个交集为 0"的本地复算（2026-09-16）')
emit()
emit('> **用途**：正文 §8.1 说"构建后**必须验证三个交集为 0**（按文件名求交）——这是该协议能被信任的前提"。')
emit('> 此前这句话只能靠 pod 上的转述；本轮从 **B 机（无卡模式）** 拉回划分定义与三份文件名清单，')
emit('> 因此这句话现在**可以在本地复算**。')
emit()
emit('**来源**：`split_defs_20260916/`（含 `SHA256SUMS.txt`）')
emit()
emit('```text')
y = os.path.join(D, 'sfchd20_3way.yaml')
if os.path.exists(y):
    for l in io.open(y, encoding='utf-8').read().rstrip('\n').split('\n'):
        emit(l)
emit('```')
emit()
emit('## 1. 三份清单的规模')
emit()
emit('| 划分 | 清单文件 | 文件数 |')
emit('|---|---|---|')
for k, fn in SETS.items():
    emit('| %s | `%s` | **%d** |' % (k, fn, len(sets[k])))
emit()
n20, ncv, nte = len(sets['train/20_percent']), len(sets['carve_sfchd20 (val)']), len(sets['test'])
emit('合计 **%d** 个文件（train %d + carve %d + test %d）——**任何重复都会让合计偏大**。' % (
    n20 + ncv + nte, n20, ncv, nte))
emit()
emit('## 2. 三个两两交集（**都必须是 0**）')
emit()
emit('| 交集 | 大小 |')
emit('|---|---|')
names = list(SETS)
allzero = True
pairs = []
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        a, b = names[i], names[j]
        # 同名不同后缀（图 vs 标签）时按 stem 求交，避免因后缀差异漏判
        sa = {os.path.splitext(x)[0] for x in sets[a]}
        sb = {os.path.splitext(x)[0] for x in sets[b]}
        inter = sa & sb
        pairs.append((a, b, len(inter)))
        emit('| %s ∩ %s | **%d** |' % (a, b, len(inter)))
        if inter:
            allzero = False
            for x in sorted(inter)[:5]:
                emit('|   ↳ 例：`%s` | |' % x)
emit()
emit('**结论：%s**' % ('三个交集**全部为 0** ⇒ §8.1 的前提成立' if allzero else '**存在非空交集** ⇒ §8.1 的前提不成立'))
emit()
emit('## 3. 与归档数字的交叉核对')
emit()
emit('| 量 | 本次本地复算 | 归档记录 | 一致？ |')
emit('|---|---|---|---|')
emit('| test 划分文件数 | **%d** | 6033（B 机 `val()` 的扫描行） | %s |' % (
    nte, '✓' if nte == 6033 else '✗ 需查'))
emit('| carve 划分文件数 | **%d** | 1000（earlier recon 只看到 aitod） | — |' % ncv)
emit()
emit('## 4. 结论与限制')
emit()
emit('- ✅ **§8.1 的"三个交集为 0"现可在本地复算**，不需要 pod、不需要 GPU（拉回一次即可）。')
emit('- ⚠️ **仍未闭合的**：**重新训练**依然需要 6 个语料本体；本文件只让"划分定义与划分清单"这一层可核。')
emit('- 说明：本文件是**新增件**，不替代 `_xframe/` 与 `xeval_20260916/`，三者分别覆盖'
     '跨框架证据、GPU 评估矩阵、划分定义。')
emit()
emit('*由 `work/verify_split_defs_20260916.py` 生成；清单来源哈希见 `split_defs_20260916/SHA256SUMS.txt`。*')

io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(rep) + '\n')
b = io.open(OUT, 'rb').read()
print('\n已写：%s' % OUT)
print('md5 %s size %d' % (hashlib.md5(b).hexdigest(), len(b)))
print('\n三个两两交集：%s' % pairs)
# r54i: this suite's verdict is the property it actually recomputes -- the three pairwise
# intersections must be 0 (that is §8.1's premise).  Print it as explicit verdict lines so the
# sweep summary quotes a real verdict rather than guessing from the exit code.
n_bad = len([1 for _a, _b, n in pairs if n])
print('失败 %d 项' % n_bad)
print('ALL PASS' if not n_bad else
      'FAILED: 两两交集非空 %s' % [(a, b, n) for a, b, n in pairs if n])
sys.exit(0 if not n_bad else 1)
