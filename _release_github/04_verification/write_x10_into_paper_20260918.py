# -*- coding: utf-8 -*-
"""r51: two things the X10 pass produced.

(1) A real arithmetic defect in §9.  The text said "a near-matched control of 10 further runs
    was appended by amendment, making 80 as reported here".  The run directories are the
    primary record and they say otherwise: control C has ten seeds per arm across the three
    analysis roots ({42..48} from the later pull plus {49,50,51} from the earlier one) = 20
    runs, so the experiment contains **90 runs** (60 three pairs + 10 saturated + 20 control C).
    Corrected in the English form and in the Chinese governing draft.

(2) The X10 audit itself (val side), which the panel's GLM requested: for the four cells whose
    YAML aliases `val:`/`test:`, each run's own log measures the selection premium directly
    (p = max_e − final), and the paired difference d̄ = p_baseline − p_strategy is the part of
    a cell's Δ that is differential selection opportunity rather than the intervention:
    Δ ≈ Δ_reported + d̄.  Measured over all 90 runs: no verdict changes, but the saturated
    control's −1.490 pp becomes −0.529 pp — about two-thirds of the paper's most striking
    negative number is the bias §9.4 warns about, so it is stated rather than left standing.

Both go into the article, the supplement (as a note spanning S24–S27) and the Chinese draft.
"""
import hashlib
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
WORK = r'E:\workplace\work'
BASE = r'E:\workplace'
P4 = os.path.join(WORK, 'en_part4.md')
SUPD = os.path.join(WORK, 'sup_en_d.md')
ZH = os.path.join(BASE, '评测有效性稿_正文_v0.1.md')

# ---------------------------------------------------------------- (1) run arithmetic
OLD_RUNS = (u'and **a near-matched\ncontrol of 10 further runs was appended by amendment, '
            u'making 80 as reported here**.')
NEW_RUNS = (u'and the near-matched\n**control C** was appended by amendment and later extended to ten '
            u'seeds \u2014 **2 \u00d7 10 = 20 further\nruns** \u2014 for **90 runs in total** (70 registered + 20 '
            u'appended); the count is taken from the run\ndirectories themselves, ten seeds per arm in '
            u'every cell except the saturated control, which has five.')

# ---------------------------------------------------------------- (2) the X10 paragraph
X10 = u'''
**How much of these \u0394s is the alias itself \u2014 val side.** In the four cells whose config points
`val:` and `test:` at one directory, the metric watched during training **is** the reported
metric, so each run's own log measures the selection premium directly:
`p = max_e mAP50-95(e) \u2212 mAP50-95(final epoch)`. Paired across seeds within a cell,
`d\u0304 = mean[p_baseline \u2212 p_strategy]` is the part of that cell's \u0394 that is **differential
selection opportunity** rather than the intervention, so `\u0394 \u2248 \u0394_reported + d\u0304`.
Measured over all 90 runs (`work/x10_alias_audit_20260918.py`, reading every per-run
`results.csv`): **T1-a** `d\u0304 = +0.051 pp` [0.006, 0.099] \u2192 \u0394 + d\u0304 = **+0.198 pp** (still short of
the +0.30 criterion); **T1-c** `d\u0304 = +0.214` [0.086, 0.326] \u2192 **+3.941 pp** (still passes);
**control C** `d\u0304 = +0.406` [0.313, 0.498] \u2192 **+1.133 pp**; and the **saturated control**
`d\u0304 = +0.961 pp` [0.440, 1.674] \u2192 **\u22120.529 pp** \u2014 the baseline arm's own val-side premium is
2.505 pp against the strategy arm's 1.543, so **about two-thirds of that cell's \u22121.490 pp is
the bias \u00a79.4 warns about**, quantified. **T1-b is excluded by construction**: its YAML separates
the two keys, so its training-time metric is not the reported one and a val-side term cannot
bound a two-term bias. **No verdict changes; one magnitude does**, and we state the smaller
number rather than leave the more striking one standing.
'''

zh_run = (u'**70 run** = T1 三对 × 2 臂 × 10 种子（60）+ T2 饱和对照 2 臂 × 5 种子（10）；'
          u'另有**改良追加的近似匹配对照 C**，后扩到十种子（**2 × 10 = 20 run**），'
          u'故本实验**共 90 run**（70 登记 + 20 追加）。')
ZH_X10 = (u'\n**这些 Δ 里有多少是别名本身（val 侧）**：四个格（T1-a、T1-c、饱和对照、对照 C）的配置把 '
          u'`val:`/`test:` 指向同一目录，故训练期看到的量**就是**上报量，每个 run 自己的日志直接量出选择溢价 '
          u'`p = max_e mAP50-95(e) − mAP50-95(末轮)`；按种子配对得 `d̄ = mean[p_基线 − p_策略]`，'
          u'`Δ ≈ Δ_reported + d̄`。全部 90 个 run 实测（`work/x10_alias_audit_20260918.py`）：'
          u'**T1-a** d̄ = +0.051 pp [+0.006, +0.099] → **+0.198**（仍不足 +0.30 判据）；'
          u'**T1-c** d̄ = +0.214 [+0.086, +0.326] → **+3.941**（仍通过）；'
          u'**对照 C** d̄ = +0.406 [+0.313, +0.498] → **+1.133**；'
          u'**饱和对照** d̄ = +0.961 [+0.440, +1.674] → **−0.529**——基线臂自身的 val 侧溢价 2.505 pp、'
          u'策略臂 1.543 pp，故该格 −1.490 pp 中**约三分之二是 §9.4 所警告的偏差**。'
          u'**T1-b 依构造不适用**（其 yaml 两键分离）。**裁定无一改变，但有一个量级要改**，我们写出较小的那个数。\n')

# ---------------------------------------------------------------- apply
staged = []

# -- en_part4: run count + X10 paragraph (insert before §9.4)
t4 = io.open(P4, encoding='utf-8').read()
assert t4.count(OLD_RUNS) == 1, 'run-count sentence not found once'
n4 = t4.replace(OLD_RUNS, NEW_RUNS)
anchor94 = u'### 9.4 What this section has to do with the paper\'s subject'
assert n4.count(anchor94) == 1
n4 = n4.replace(anchor94, X10.strip() + u'\n\n' + anchor94)
staged.append((P4, 'r51_x10', t4, n4))

# -- supplement: a note spanning S24-S27, placed right after the §S8 index table
ts = io.open(SUPD, encoding='utf-8').read()
last_row = (u'| **Table S27** | 9.4 \u2b50 What this section has to do with the paper\'s subject | '
            u'Registered pair, data YAML, `val`, `test`, Split | 5 |\n')
assert ts.count(last_row) == 1, 'the S8 index last row was not found once'
SUP_NOTE = (
    u'\n> **Two notes spanning S24\u2013S27 (added 2026-09-18).** \u2460 The experiment contains\n'
    u'> **90 runs**: three registered pairs 3 \u00d7 2 \u00d7 10 = 60, the saturated control 2 \u00d7 5 = 10\n'
    u'> (the registered set is 70), and the control appended by amendment 2 \u00d7 10 = 20 \u2014 counted\n'
    u'> from the run directories, ten seeds per arm in every cell but the saturated control.\n'
    u'> \u2461 **Val-side alias bias**, `\u0394 \u2248 \u0394_reported + d\u0304` with `d\u0304 = mean[p_baseline \u2212 p_strategy]`\n'
    u'> and `p = max_e \u2212 final` from each run\u2019s own log: T1-a **+0.051** [0.006, 0.099], T1-c\n'
    u'> **+0.214** [0.086, 0.326], control C **+0.406** [0.313, 0.498], saturated control\n'
    u'> **+0.961** [0.440, 1.674] (\u0394 + d\u0304 = \u22120.529). T1-b is excluded by construction \u2014 its YAML\n'
    u'> separates the keys. Script `work/x10_alias_audit_20260918.py`. **No verdict changes.**\n')
ts2 = ts.replace(last_row, last_row + SUP_NOTE, 1)
staged.append((SUPD, 'r51_x10', ts, ts2))

# -- Chinese governing draft
tz = io.open(ZH, encoding='utf-8').read()
mz = re.search(r'\*\*70 run\*\*[^\n]*', tz)
assert mz, 'the Chinese run sentence was not found'
tz2 = tz[:mz.start()] + zh_run + tz[mz.end():]
kz = tz2.find(u'### 9.4')
assert kz > 0
tz2 = tz2[:kz] + ZH_X10.strip() + u'\n\n' + tz2[kz:]
staged.append((ZH, 'r51_x10', tz, tz2))

for path, tag, txt, new in staged:
    assert new != txt, 'no-op edit in %s' % os.path.basename(path)
    io.open(path + '.bak_before_%s_20260918' % tag, 'w', encoding='utf-8',
            newline='\n').write(txt)
    io.open(path, 'w', encoding='utf-8', newline='\n').write(new)
    print('%-24s md5 %s -> %s' % (os.path.basename(path),
                                  hashlib.md5(txt.encode('utf-8')).hexdigest()[:12],
                                  hashlib.md5(new.encode('utf-8')).hexdigest()[:12]))
# verify the new facts are present and the old count is gone
back4 = io.open(P4, encoding='utf-8').read()
assert u'90 runs in total' in back4 and u'making 80' not in back4
assert u'\u22120.529' in back4 and u'+0.198' in back4
print('OK 运行数已改为 90；X10 的 val 侧别名偏差段落已写入三份文件')
