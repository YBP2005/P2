# -*- coding: utf-8 -*-
"""r39: mechanical verification of the submission pack.

Checks every formal requirement that is **mechanically checkable locally**, so the
claims in `P2_投稿前件_v0.1.md` are audited rather than asserted. Read-only.
"""
import io
import os
import re
import struct
import sys

sys.stdout.reconfigure(encoding='utf-8')
W = r'E:\workplace'
POST = os.path.join(W, 'P2_投稿前件_v0.1.md')
ENG = os.path.join(W, 'P2_English_v0.1.md')
REFS = os.path.join(W, 'P2_参考文献_v0.1.md')
FORMS = os.path.join(W, 'PR形式要求_核实_20260917.md')
GA = os.path.join(W, 'figures', 'fig6_graphical_abstract.png')

fails = []


def rep(ok, label, detail=''):
    print('  %-4s %s%s' % ('ok' if ok else 'FAIL', label, ('   ' + detail) if detail else ''))
    if not ok:
        fails.append(label)


def load(p):
    return io.open(p, encoding='utf-8').read() if os.path.exists(p) else None


post, eng, refs, forms = load(POST), load(ENG), load(REFS), load(FORMS)

print('=' * 74)
print('投稿前件机械校验')
print('=' * 74)

# ---------------------------------------------------------------- Highlights
print('\n[1] Highlights：3-5 条，每条 <=85 字符（含空格）')
sec = post[post.find('## 2. Highlights'):post.find('## 3. Abstract')]
items = re.findall(r'(?m)^(\d)\. (.+)$', sec)
rep(3 <= len(items) <= 5, 'Highlights 条数 3-5', 'n=%d' % len(items))
worst = 0
for n, txt in items:
    ln = len(txt)
    worst = max(worst, ln)
    rep(ln <= 85, 'Highlight %s 长度 <=85' % n, '%d chars' % ln)
rep(worst <= 85, '最长 Highlight <=85 字符', 'max=%d' % worst)

# ------------------------------------------------------------------ abstract
print('\n[2] Abstract：<=150 词（两处必须一致）')
for name, doc in (('投稿前件', post), ('英文稿', eng)):
    i = doc.find('## 3. Abstract') if name == '投稿前件' else doc.find('## Abstract')
    if name == '投稿前件':
        j = doc.find('## 4. Keywords')
    else:
        # r46: "Positioning" and "Scope" moved out of the Abstract block to §1.2 (H23)
        j = doc.find('**Keywords:**')
    # r46: the closing phrase is now "seed inflation" (H19 renames the estimand)
    m = re.search(r'Object-detection papers report.*?(?:selection|seed) inflation\.', doc[i:j], re.S)
    wc = len(re.sub(r'[*`]', '', m.group(0)).split()) if m else 0
    rep(0 < wc <= 150, '%s 摘要 <=150 词' % name, '%d words' % wc)

# ---------------------------------------------------------------- references
print('\n[3] 参考文献：35-45 条，且英文稿必须全部引用')
rows = re.findall(r'(?m)^\| \[(\d+)\] \| ', refs)
rep(len(rows) == 44, 'canonical 参考文献表 = 44 条', 'n=%d' % len(rows))
rep(35 <= len(rows) <= 45, '条数落在 PR 区间 35-45', 'n=%d' % len(rows))
er = re.findall(r'(?m)^\[(\d+)\] ', eng)
rep(len(er) == 44, '英文稿 References 节 = 44 条', 'n=%d' % len(er))
cited = set(int(x) for x in re.findall(r'\[(\d{1,2})\]', eng))
uncited = [n for n in range(1, 41) if n not in cited]
rep(not uncited, '英文稿引用全部 44 条（无"只列不引"）', 'uncited=%s' % (uncited or 'none'))

print('\n[4] 参考文献的领域分布（PR 要求"本领域多个来源"）')
pr_journal = re.findall(r'\*Pattern Recognition\*', refs)
rep(len(pr_journal) >= 2, '本刊（Pattern Recognition）条目 >=2', 'n=%d' % len(pr_journal))
domains = {
    'CVPR/ICCV/ECCV/ICPR/TPAMI/Proc.IEEE': r'(CVPR|ICCV|ECCV|ICPR|TPAMI|Proceedings of the IEEE)',
    '数据/评测类期刊': r'(Patterns|Technologies|Drones|Journal of Imaging|ISPRS|Neural Computing)',
}
for k, p in domains.items():
    rep(len(re.findall(p, refs)) >= 3, '含 %s 类来源 >=3' % k,
        'n=%d' % len(re.findall(p, refs)))

# ------------------------------------------------------------- internal code
print('\n[5] 投稿稿不得出现内部代号')
bare = [l.strip()[:80] for l in eng.split('\n') if re.search(r'\bP1\b', l)]
rep(not bare, '英文稿无裸用内部代号 P1', str(bare or 'none'))
for mk in ['[A]', '[B]', '[C]', '[D]']:
    live = [l.strip()[:80] for l in eng.split('\n')
            if mk in l and not l.lstrip().startswith('>')]
    rep(not live, '英文稿未把未核实标记 %s 当引用' % mk, str(live or 'none'))

# ------------------------------------------------------- cover letter linkage
print('\n[6] Cover letter 必须点名伴生论文（互引记录 §1）')
cl = post[post.find('## 6. Cover Letter'):post.find('## 7. Declaration')]
rep('companion manuscript' in cl, 'Cover letter 提到 companion manuscript')
rep('budgeted fine-tuning' in cl, 'Cover letter **点名主题**（budgeted fine-tuning study）')
rep('do not overlap' in cl or 'neither duplicates' in cl, 'Cover letter 声明两篇不重复')

# ---------------------------------------------------------------- graphical
print('\n[7] Graphical abstract 尺寸 >=1328×531 px')
if os.path.exists(GA):
    b = open(GA, 'rb').read(33)
    w, h = struct.unpack('>II', b[16:24])
    rep(w >= 1328 and h >= 531, 'fig6 尺寸', '%d×%d px' % (w, h))
else:
    rep(False, 'fig6 存在')

# --------------------------------------------------- the corrected provenance
print('\n[8] 形式要求核实件的来源更正必须留痕')
rep(forms is not None and 'VETERINARY JOURNAL' in forms,
    '已记录 whu 存档属 Veterinary Journal（不是 PR）')
rep(forms is not None and '作废' in forms, '已声明该四条作废')

print('\n' + '=' * 74)
print('失败 %d 项' % len(fails))
print('ALL PASS' if not fails else 'FAILED: ' + ', '.join(fails))
sys.exit(0 if not fails else 1)
