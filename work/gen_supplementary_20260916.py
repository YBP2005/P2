# -*- coding: utf-8 -*-
"""
r23 = G6：生成 `P2_补充材料.md`（真补充材料）。

设计原则：**不手抄**。每一个小节的正文都是**逐字嵌入已验证的来源文件**（带该文件的 md5 与路径），
这样"补充材料里的数与来源文件里的数"不可能不一致。
  S1 ← E:\\workplace\\split_units_19rows_20260916.md                （19×5 标记表 + 重算 + 交叉核对 + 四层级）
  S2 ← E:\\workplace\\审计文档更正与裁定_20260916.md 的 §2 取代块      （计数口径的更正记录）
  S3 ← E:\\workplace\\xframe_evidence_20260916.txt                  （5 框架 23 文件的逐行证据）
  S4 ← E:\\workplace\\xeval_analysis_20260916.txt                   （2×2 评估矩阵：验证 + 分解 + 兑现率）
  S5 ← D:\\deepseek\\...\\selection_premium_public_20260916.md 的样本与读法节（公开日志溢价；只读）
输出：E:\\workplace\\P2_补充材料.md
"""
import io, os, re, sys, hashlib

sys.stdout.reconfigure(encoding='utf-8')
BASE = r'E:\workplace'
OUT = os.path.join(BASE, 'P2_补充材料.md')


def load(p):
    if not os.path.exists(p):
        return None, None, None
    b = io.open(p, 'rb').read()
    return b.decode('utf-8'), hashlib.md5(b).hexdigest(), len(b)


def slice_between(text, start_pat, end_pat=None, inclusive_start=True):
    """按正则取一段（默认含起始行、不含结束行）。"""
    lines = text.split('\n')
    s = [k for k, l in enumerate(lines) if re.search(start_pat, l)]
    if not s:
        return None
    s = s[0]
    if end_pat is None:
        return '\n'.join(lines[s:])
    e = [k for k, l in enumerate(lines) if k > s and re.search(end_pat, l)]
    e = e[0] if e else len(lines)
    return '\n'.join(lines[s if inclusive_start else s + 1:e])


SRC = {}

# ---------- S1
t, h, n = load(os.path.join(BASE, 'split_units_19rows_20260916.md'))
if t is None:
    sys.exit('!! 缺 split_units_19rows_20260916.md')
SRC['S1'] = ('E:\\workplace\\split_units_19rows_20260916.md', h, n, t)

# ---------- S2（裁定书里"计数口径取代"那一段）
t2, h2, n2 = load(os.path.join(BASE, '审计文档更正与裁定_20260916.md'))
if t2 is None:
    sys.exit('!! 缺 审计文档更正与裁定_20260916.md')
seg = slice_between(t2, r'^> ### 本节（§2）的四个计数已被机械重算取代',
                    r'^\*\*前提\*\*：\(d-1\)')
if not seg or 'release（发布物层）' not in seg:
    sys.exit('!! 裁定书 §2 取代块抽取失败')
SRC['S2'] = ('E:\\workplace\\审计文档更正与裁定_20260916.md（§2 取代块）', h2, n2, seg)

# ---------- S3
t3, h3, n3 = load(os.path.join(BASE, 'xframe_evidence_20260916.txt'))
if t3 is None:
    sys.exit('!! 缺 xframe_evidence_20260916.txt')
SRC['S3'] = ('E:\\workplace\\xframe_evidence_20260916.txt', h3, n3, t3)

# ---------- S4
t4, h4, n4 = load(os.path.join(BASE, 'xeval_analysis_20260916.txt'))
if t4 is None:
    sys.exit('!! 缺 xeval_analysis_20260916.txt')
SRC['S4'] = ('E:\\workplace\\xeval_analysis_20260916.txt', h4, n4, t4)

# ---------- S5（D 盘，只读）
PUB = r'D:\deepseek\analysis\eval_validity\selection_premium_public_20260916.md'
t5, h5, n5 = load(PUB)
if t5 is None:
    print('!! 缺公开日志文件（D 盘只读），S5 将只留指针')
    SRC['S5'] = (PUB, 'NA', 0, '（本次未能读取该文件；S5 见正文 §5.5 与其证据指针）')
else:
    body = slice_between(t5, r'^## 样本', r'^## 变更记录')
    if not body or 'ayyappakorla' not in body:
        sys.exit('!! 公开日志样本节抽取失败')
    SRC['S5'] = (PUB, h5, n5, body)

TITLES = {
    'S1': ('S1 · 19 个公开基准 × 5 个计数单位的逐行标记表与机械重算',
           '正文 §3、§6；这是"多少基准有问题"这句话的**全部逐行依据**。'),
    'S2': ('S2 · 计数口径的更正记录（旧口径 → 重算口径）',
           '正文 §6.3；说明为什么同一事实曾有两套数、以及哪一套已作废。'),
    'S3': ('S3 · 跨框架配置审计的逐行证据（5 个框架 / 23 个官方文件）',
           '正文 §6.5；每个框架的 commit 固定点与逐行证据（判定在正文，证据在此）。'),
    'S4': ('S4 · 三分划协议上的 2×2 评估矩阵（41 run × {best,last} × {val,test}）',
           '正文 §8.6 与 §5.6；含归档复现验证、Δgap 的可分解化、以及选点获益的兑现率。'),
    'S5': ('S5 · 公开第三方日志上的选择溢价（样本与读法）',
           '正文 §5.5；每条日志的轮数、末轮、最优轮与溢价，以及四项限制。'),
}

buf = []
def emit(s=''):
    buf.append(s)


emit('# P2 补充材料（Supplementary Material）')
emit()
emit('> **本文是 P2（划分稿）的补充材料**，与正文 `评测有效性稿_正文_v0.1.md` 配套提交。')
emit('> **编号约定**：正文用 §n 指章节、S n 指本文小节。')
emit()
emit('## 0. 生成方式与可核性（**先读这一节**）')
emit()
emit('本文**不是手写的**：每一节的正文都是**逐字嵌入**下列**已验证来源文件**的内容，')
emit('故"本文里的数"与"来源文件里的数"**不可能不一致**。每个来源文件都记了 md5 与字节数，任何人可复核。')
emit()
emit('| 小节 | 内容 | 来源文件 | md5 | 字节 |')
emit('|---|---|---|---|---|')
for k in ('S1', 'S2', 'S3', 'S4', 'S5'):
    p, h, n, _ = SRC[k]
    emit('| **%s** | %s | `%s` | `%s` | %d |' % (k, TITLES[k][0], p, h, n))
emit()
emit('**生成脚本**：`work\\gen_supplementary_20260916.py`（纯本地、可复跑；S5 读 D 盘时只读）。')
emit('**复核入口**：见本文 §S7。')
emit()
emit('---')
emit()
for k in ('S1', 'S2', 'S3', 'S4', 'S5'):
    p, h, n, body = SRC[k]
    title, why = TITLES[k]
    emit('## %s' % title)
    emit()
    emit('> **用途**：%s' % why)
    emit('> **来源**：`%s`（md5 `%s`，%d 字节），以下内容**逐字嵌入，未改动**。' % (p, h, n))
    emit()
    emit('```text')
    emit(body.rstrip('\n'))
    emit('```')
    emit()
    emit('---')
    emit()

MM_MD5 = hashlib.md5(io.open(os.path.join(BASE, '多模型盲审清单_通用_20260915.md'), 'rb').read()).hexdigest() \
    if os.path.exists(os.path.join(BASE, '多模型盲审清单_通用_20260915.md')) else '(文件不在 E 盘)'
DSH_MD5 = hashlib.md5(io.open(os.path.join(BASE, 'DSH+本地+云端_工作方法指南.md'), 'rb').read()).hexdigest() \
    if os.path.exists(os.path.join(BASE, 'DSH+本地+云端_工作方法指南.md')) else '(文件不在 E 盘)'

emit('## S6 · 过程规程（共享工具；两篇共用，均不主张原创）')
emit()
emit('> **用途**：正文 §2.3 声明"本文与伴生论文共用同一套过程规程、且均不主张原创"。')
emit('> 本节把该声明**落到可核的名字与哈希上**（这是互引规则 ⑤b 的落实方式）。')
emit('> **形式决定（P2 侧）**：这两份规程是**项目内部件**，**不随本文发布其正文**——它们不是公开出版物，')
emit('> 且与本文的科学主张无直接关系。本文只声明"**用了同一套规程**"，并给出**文件名与 md5**，')
emit('> 使复核者能向作者索取同一份文件。**若审稿人要求，可随修订一并提供。**')
emit()
emit('| 规程（内部件） | md5 | 在本文中的作用 | 主张原创？ |')
emit('|---|---|---|---|')
emit('| `多模型盲审清单_通用_20260915.md` | `%s` | 外部模型分层复核；§10 的六项自陈缺陷中，"静默排除"与"取错列"两项由该复核发现 | **否**，两篇都不主张 |' % MM_MD5)
emit('| `DSH+本地+云端_工作方法指南.md` | `%s` | 本地/云端工作法：脚本化远端执行、补丁的全有或全无、审计锚点、每个数字带本地指针 | **否**，两篇都不主张 |' % DSH_MD5)
emit()
emit('**同一条约定也适用于审计锚点体系**：本文的 227 条锚点与伴生论文的 481 条锚点是**同一套**共享工具，')
emit('两篇都不把它写成方法学贡献。')
emit()
emit('**为什么不附正文**：① 两份都是**中文工作文档**，与本文的科学主张无直接关系；')
emit('② 附上会把"过程"读成"方法学贡献"，恰是本条规则要避免的；③ 给出 md5 已足以确认"两篇用的是同一份"。')
emit()
emit('---')
emit()

emit('## S7 · 复核入口（任何人可独立复算）')
emit()
emit('```powershell')
emit('# ① 正文锚点（209 条；须 ALL PASS）')
emit('python E:\\workplace\\work\\audit_anchors_fupaper.py')
emit()
emit('# ② S4 的 2×2 矩阵分析（读本次拉回的产物）')
emit('python E:\\workplace\\work\\xeval_analyze_20260916.py')
emit()
emit('# ③ §5.6 的机制检验（读 D 盘归档，只读）')
emit('python E:\\workplace\\work\\gap_mechanism_20260916.py')
emit()
emit('# ④ 本次拉回的产物完整性（sha256 + 字节数）')
emit('python E:\\workplace\\work\\verify_pulled.py')
emit('python E:\\workplace\\work\\verify_pulled.py E:\\workplace\\_xframe')
emit('```')
emit()
emit('**口径声明**：S1–S5 的来源文件各不相同，**不可混用**——S1/S2 是**配置层审计**（不下载数据集），')
emit('S3 是**官方配置/脚本的定点抽样**（5 框架、非普查），S4/S5 是**实测**（前者自有 run，后者他人日志）。')
emit('正文各处均按此区分强度。')
emit()

io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(buf) + '\n')
b = io.open(OUT, 'rb').read()
print('补充材料已写：%s' % OUT)
print('  md5 %s  size %d  lines %d' % (hashlib.md5(b).hexdigest(), len(b), b.decode('utf-8').count('\n') + 1))
for k in ('S1', 'S2', 'S3', 'S4', 'S5'):
    p, h, n, body = SRC[k]
    print('  %s 嵌入 %6d 字符  ← %s' % (k, len(body), os.path.basename(p)))
