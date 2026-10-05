# -*- coding: utf-8 -*-
"""盲态隔离核验器（2026-10-04 新增，r232）。

**要防的事**：盲审模型只能看到「任务件 + 盲审包（+ 两份可选辅助目录）」。
若这些材料里出现 **① 其它评审者的痕迹 ② 其它轮次的材料 ③ 他评分数/档位 ④ 上一轮的"改动清单"**，
盲态就被破坏，本轮分数也失去可比性。

**实测发现并已修的四处泄漏**（都在**任务件**里，包本身干净）：
  1. §0「本轮改了什么」6 条清单 —— 直接描述上一轮版本的样貌（甚至写"正文**原先**称…"）；
  2. §0 的"上一轮包"印的是**本轮包自己的 md5**（脚本全局替换误伤）；
  3. §2 透露"**上一轮出现过自报 79.0、分项之和 81.5**" —— **他评分数**；
  4. §0a 称三脚本"仍带明文口令" —— **事实过时**（实测复现仓库无明文口令）。

用法：
    python -X utf8 work/verify_blind_isolation_20261014.py            # 核验（默认下一轮的件）
    python -X utf8 work/verify_blind_isolation_20261014.py --date 20261013
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

DATE = '20261015'
if '--date' in sys.argv:
    DATE = sys.argv[sys.argv.index('--date') + 1]
TAG = 'p2r%d' % (int(DATE[-2:]) - 5) if False else 'p2r20'

CAND = [
    r'E:\WorkBuddy\盲审P2\P2盲审包_全量_%s.md' % DATE,
    r'E:\WorkBuddy\盲审P2\P2盲审任务_说明与输出格式_%s.md' % DATE,
    os.path.join(r'E:\workplace\_p2_blind_extras_20261002', 'P2盲审任务_说明与输出格式_%s.md' % DATE),
]

# (名称, 正则, 说明, 是否允许少量命中)
RULES = [
    ('其它评审者模型名',
     r'(?i)\b(gemini|grok|qwen|kimi|claude|deepseek|glm-?\d|hy4|space[-_ ]?bunny|gpt-?\d|astra|step-?\d)\b',
     '材料里出现了模型名 ⇒ 可能是他评痕迹（附录/细则里的中性用词请人工确认）', 0),
    ('他评产物名',
     r'_review_|distill_|评审件|归档清单|consensus_ledger|intake_ledger',
     '材料里出现了评审产物名 ⇒ 他评痕迹', 0),
    ('其它轮次材料',
     r'(上一轮|前一轮|再上一轮|round R\d|本轮改了什么|与上一版相比|previous round)',
     '材料提到了其它轮次 ⇒ 破坏了盲态（应只讲"本轮"）', 0),
    ('他评分数/档位泄露',
     r'(上一轮出现过自报|别的评审者.{0,8}(分|分项)|出现过自报\s*\d|其它评审者.{0,8}(分数|评价))',
     '材料透露了其他评审者的自报分/评价 ⇒ 严重', 0),
    ('明文口令（过时/错误陈述）',
     r'明文(服务)?口令|plaintext\s+(service\s+)?password',
     '若复现仓库已无明文口令，则这句是**错误陈述**，会误导评审', 0),
    ('指向他评目录的路径',
     r'(G5_review_|\\<你的模型目录>\\.{0,40}\.md).{0,0}',
     '材料里给出了可能读到他人输出的路径模式（`<你的模型目录>` 自身是允许的）', 0),
]


def main():
    bad = 0
    print('=' * 96)
    print('盲态隔离核验（%s）' % DATE)
    print('=' * 96)
    found = [p for p in CAND if os.path.exists(p)]
    if not found:
        print('未找到本轮的件（%s）⇒ 无可核对象。' % ', '.join(os.path.basename(p) for p in CAND))
        return 0
    for p in found:
        s = io.open(p, encoding='utf-8').read()
        print('\n--- %s（%d B）---' % (os.path.basename(p), len(s.encode())))
        for name, pat, why, allow in RULES:
            ms = re.findall(pat, s)
            # 允许项：① `<你的模型目录>`（说明输出位置）；② 输出文件名模板 `<tag>_review_<标识>_<日期>.md`
            #   —— 这两者必须给出，不构成泄漏。除此之外的 `_review_` 一律算痕迹。
            _keep = []
            for m in ms:
                mm = m if isinstance(m, str) else str(m)
                if '你的模型目录' in mm:
                    continue
                _keep.append(m)
            ms = [m for m in _keep
                  if not (str(m) == '_review_' and re.search(r'@?p2r\d+_review_<评审者标识>', s))]
            ok = len(ms) <= allow
            print('  %s %-16s %d 处 %s' % ('OK  ' if ok else 'FAIL', name, len(ms),
                                           '' if ok else '(%s)' % why))
            if not ok:
                bad += 1
                for m in ms[:4]:
                    print('       命中：%s' % str(m)[:80])
    # 附：给评审的可达面（只列，不判）
    for d in (r'E:\WorkBuddy\盲审P2\复现仓库', r'E:\WorkBuddy\盲审P2\参考文献'):
        if os.path.isdir(d):
            n = sum(len(f) for _, _, f in os.walk(d))
            print('\n  辅助目录 %s：%d 件（评审可读，非评审对象）' % (os.path.basename(d), n))
    print('\n%s' % ('ISOLATION: OK —— 未发现跨轮/他评痕迹' if not bad
                    else 'ISOLATION: %d 项可疑（见上）' % bad))
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
