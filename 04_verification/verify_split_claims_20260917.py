# -*- coding: utf-8 -*-
"""r48: recompute the paper's central split table from the archived configuration files.

The shared lessons library's 02 §3 asks for it: any assertion *about* the material must be
verified by recomputing from the material, not by reading the sentence again.  This paper's
headline table states, per three-way pair, whether the published protocol's dataset config
points `val:` and `test:` at the same directory — and those config files have been archived
locally (pulled from both pods on 2026-09-16, `eval_validity/yamls/`, with a MANIFEST).

So: parse the four YAMLs, recompute "same directory" from the two keys, and compare with the
row the article and the supplementary print.  Also recompute the MANIFEST's own summary count
("28 yamls, 8 with val == test") — a label stating a count about content, which the library's
02 §6 says must be recomputed rather than trusted.

The archive lives outside this workspace (D:), so its path is declared here explicitly and
the check FAILS LOUDLY if it is absent, rather than silently skipping.
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
W = r'E:\workplace'
ARCHIVE_YAMLS = r'D:\deepseek\analysis\eval_validity\yamls'   # read-only, never written
ART = os.path.join(W, 'P2_English_v0.1.md')
SUP = os.path.join(W, 'P2_Supplementary_English_v0.1.md')

# pair label -> (yaml file the paper names, local copy in the archive)
PAIRS = [
    ('T1-a dota15\u2192aitod', 'aitod_20p.yaml',
     'A__root__datasets__AI-TOD_yolo__aitod_20p.yaml'),
    ('T1-b aitod\u2192visdrone', 'visdrone_20p.yaml',
     'A__root__datasets_mask__visdrone__visdrone_20p.yaml'),
    ('T1-c visdrone\u2192dota15', 'dota15_20p.yaml',
     'A__root__datasets_mask__dota15_yolo__dota15_20p.yaml'),
    ('T2 mask\u2192mendeley', 'mende_20p.yaml',
     'A__root__datasets_mask__mendeley_yolo__mende_20p.yaml'),
]


def keys(path):
    """Read the `val:` / `test:` values from a dataset yaml (no yaml dependency needed)."""
    val = test = None
    for line in io.open(path, encoding='utf-8', errors='replace'):
        m = re.match(r'\s*val\s*:\s*(\S+)\s*$', line)
        if m:
            val = m.group(1)
            continue
        m = re.match(r'\s*test\s*:\s*(\S+)\s*$', line)
        if m:
            test = m.group(1)
    return val, test


def main():
    fails = []
    print('=' * 78)
    print('重算型核验：正文/补充材料的分划表 vs 归档的 yaml 配置')
    print('  归档位置（只读）：%s' % ARCHIVE_YAMLS)
    print('=' * 78)
    if not os.path.isdir(ARCHIVE_YAMLS):
        sys.exit('!! 归档目录不存在 —— 本核验无法运行（不得静默跳过）：%s' % ARCHIVE_YAMLS)

    art = io.open(ART, encoding='utf-8').read()
    sup = io.open(SUP, encoding='utf-8').read()

    print('\n[1] 四对语料：yaml 实测 vs 文中声明')
    for pair, named, local in PAIRS:
        p = os.path.join(ARCHIVE_YAMLS, local)
        if not os.path.exists(p):
            print('   FAIL %-22s 归档缺 %s' % (pair, local))
            fails.append('%s: archive missing %s' % (pair, local))
            continue
        val, test = keys(p)
        same = (val == test)
        measured = 'same directory' if same else 'separated'
        # what does the document say about this pair?
        rows = [l for l in (art + '\n' + sup).split('\n')
                if l.strip().startswith('| ' + pair)]
        stated = None
        for r in rows:
            if 'same directory' in r:
                stated = 'same directory'
            elif 'separated' in r:
                stated = 'separated'
            if stated:
                break
        ok = (stated == measured)
        print('   %-4s %-22s %-14s val=%-14s test=%-14s 文中=%-14s'
              % ('ok' if ok else 'FAIL', pair, measured, val, test, stated or '(未找到该行)'))
        if not ok:
            fails.append('%s: yaml says %s, text says %s' % (pair, measured, stated))
        if named not in (art + sup):
            print('        · 备注：文档用基名 `%s` 指它，归档副本名带路径前缀' % named)

    print('\n[2] MANIFEST 自称的数量（重算）')
    man = os.path.join(ARCHIVE_YAMLS, 'MANIFEST.md')
    if not os.path.exists(man):
        print('   FAIL 缺 MANIFEST.md')
        fails.append('manifest missing')
    else:
        m = re.search(r'Totals:\s*(\d+)\s*yamls,\s*(\d+)\s*with val == test', io.open(
            man, encoding='utf-8').read())
        yamls = [f for f in os.listdir(ARCHIVE_YAMLS) if f.endswith('.yaml')]
        same_n = 0
        for f in yamls:
            v, t = keys(os.path.join(ARCHIVE_YAMLS, f))
            if v is not None and v == t:
                same_n += 1
        stated_n, stated_same = (int(m.group(1)), int(m.group(2))) if m else (None, None)
        ok = (stated_n == len(yamls)) and (stated_same == same_n)
        print('   %-4s MANIFEST 称 %s 份 / %s 份 val==test；实测 %d 份 / %d 份'
              % ('ok' if ok else 'FAIL', stated_n, stated_same, len(yamls), same_n))
        if not ok:
            fails.append('manifest count: stated %s/%s, measured %d/%d'
                         % (stated_n, stated_same, len(yamls), same_n))

    print()
    print('失败 %d 项' % len(fails))
    print('ALL PASS' if not fails else 'FAILED: ' + '; '.join(fails))
    return 0 if not fails else 1


if __name__ == '__main__':
    sys.exit(main())
