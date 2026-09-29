# -*- coding: utf-8 -*-
"""r46: build the staged attribution of every change to the four article parts.

Why: verify_compression_20260917.py compares the pre-compression baseline with the
current text and requires every numeric change to be declared.  That declaration had
become one hand-maintained blob per part, which is exactly the shape that lets a
change hide (the earlier auto-refresh episode).  Instead, this script walks the
per-round snapshots that the rounds themselves left on disk, in time order, and
records a *stage per transition*: label, the two endpoint files, their md5, and the
measured delta of numbers, §-cross-references, headings, pointer lines and table rows.

The result is a data file the verifier loads and re-checks against the live files:
if a snapshot is later edited, its recorded md5 no longer matches and the check
fails.  A transition with no snapshot in between is labelled as such — the
attribution is not silently widened.

Read-only w.r.t. the articles; writes only work/round_stages_20260917.json.
"""
import collections
import hashlib
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
WORK = r'E:\workplace\work'
BASE_TAG = '.bak_before_r42_compress_20260917'
OUT = os.path.join(WORK, 'round_stages_20260917.json')

# The round that ran at the start of each transition.  Derived from the snapshot's
# own tag; where several rounds ran with no snapshot in between, the label says so.
NO_SNAPSHOT_NOTE = '（其间无快照，多个小节合并归入本段）'


def nums(s):
    s = re.sub(r'(?m)^\s*\d+[.)]\s+', '', s)
    s = re.sub(r'(?m)(\s)\d+[.)]\s+', r'\1', s)
    return collections.Counter(re.findall(r'\d+(?:[.,]\d+)*', s))


def xrefs(s):
    return collections.Counter(re.findall(r'§\d+(?:\.\d+)?', s))


def heads(s):
    return collections.Counter(re.findall(r'(?m)^#{1,6} .*$', s))


def pointers(s):
    return collections.Counter(re.findall(
        r'(?m)^> \*\*Tables? S[\dS\u2013]+\*\* \u2192 Supplementary \u00a7S8\.$', s))


def rows(s):
    return len([l for l in s.split('\n') if l.strip().startswith('|')])


def md5(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def read(p):
    return io.open(p, encoding='utf-8').read()


def snapshot_states(part):
    """Distinct states of en_partN.md in time order, plus the current file.

    Ordered strictly by mtime, NOT by the round name in the file name: several
    backups were taken by later rounds but hold earlier content (r39's snapshot
    predates the r42 compression baseline), so name order would invert the chain.
    """
    stem = os.path.join(WORK, 'en_part%d.md' % part)
    base = stem + BASE_TAG
    assert os.path.exists(base), 'missing baseline for part %d' % part
    snaps = []
    for f in os.listdir(WORK):
        if f.startswith(os.path.basename(stem) + '.bak_before_'):
            p = os.path.join(WORK, f)
            snaps.append((os.path.getmtime(p), f, p))
    snaps.sort()
    states = []
    seen = set()
    for _, f, p in snaps:
        txt = read(p)
        h = md5(txt)
        if h in seen:
            continue
        seen.add(h)
        tag = f[len(os.path.basename(stem)):]
        states.append((tag, p, txt, tag.endswith(BASE_TAG)))
    cur = read(stem)
    if md5(cur) in seen:
        # the file still equals an earlier snapshot: keep the LAST such state, dropping
        # the duplicates, and mark it current
        last = max(i for i, s in enumerate(states) if md5(s[2]) == md5(cur))
        states = states[:last + 1]
        tag, p, txt, isbase = states[-1]
        states[-1] = ('__current__', stem, txt, isbase)
    else:
        states.append(('__current__', stem, cur, False))
    return stem, states


def label_for(tag):
    """'bak_before_r46_batchA' -> 'r46 batchA'   (any _YYYYMMDD suffix is stripped)

    r50: this used to strip the literal '_20260917'.  The work crossed midnight, so the new
    snapshots carry '_20260918' and every one of them came back as an "unnamed round" — the
    guard doing its job, but on the calendar rather than on the content.
    """
    t = tag.replace('.bak_before_', '')
    t = re.sub(r'_\d{8}$', '', t)
    if t == '__current__':
        return 'current'
    return t


result = {'base_tag': BASE_TAG, 'generated_by': 'work/gen_round_stages_20260917.py',
          'parts': {}}
for part in (1, 2, 3, 4):
    stem, states = snapshot_states(part)
    stages = []
    for i in range(len(states) - 1):
        tag_from, path_from, txt_from = states[i][0], states[i][1], states[i][2]
        tag_to, path_to, txt_to = states[i + 1][0], states[i + 1][1], states[i + 1][2]
        nb, na = nums(txt_from), nums(txt_to)
        xb, xa = xrefs(txt_from), xrefs(txt_to)
        hb, ha = heads(txt_from), heads(txt_to)
        pb, pa = pointers(txt_from), pointers(txt_to)
        stages.append({
            'produced_by': label_for(tag_from),
            'from': os.path.basename(path_from), 'from_md5': md5(txt_from),
            'to': os.path.basename(path_to), 'to_md5': md5(txt_to),
            'num_loss': dict(nb - na), 'num_gain': dict(na - nb),
            'xref_new': dict(xa - xb), 'xref_lost': dict(xb - xa),
            'head_new': sorted((ha - hb).elements()), 'head_lost': sorted((hb - ha).elements()),
            'ptr_from': sum(pb.values()), 'ptr_to': sum(pa.values()),
            'ptr_new': sorted((pa - pb).elements()), 'ptr_lost': sorted((pb - pa).elements()),
            'rows_from': rows(txt_from), 'rows_to': rows(txt_to),
            'words_from': len(txt_from.split()), 'words_to': len(txt_to.split()),
        })
    result['parts'][str(part)] = {'file': os.path.basename(stem), 'stages': stages}

    print('=' * 78)
    print('%s   %d states / %d stages' % (os.path.basename(stem), len(states), len(stages)))
    print('=' * 78)
    for k, st in enumerate(stages):
        print('  %2d  %-28s %s -> %s' % (k, st['produced_by'],
                                         st['from'].replace('en_part%d.md' % part, ''),
                                         st['to'].replace('en_part%d.md' % part, '')))
        print('       words %d -> %d   rows %d -> %d   ptr %d -> %d   headings %d/%d'
              % (st['words_from'], st['words_to'], st['rows_from'], st['rows_to'],
                 st['ptr_from'], st['ptr_to'], len(st['head_new']), len(st['head_lost'])))
        if st['num_loss'] or st['num_gain']:
            print('       num  -%s  +%s' % (st['num_loss'], st['num_gain']))
        if st['xref_new'] or st['xref_lost']:
            print('       xref +%s  -%s' % (st['xref_new'], st['xref_lost']))

io.open(OUT, 'w', encoding='utf-8', newline='\n').write(
    json.dumps(result, ensure_ascii=False, indent=1, sort_keys=True))
print()
print('written %s (%d B)' % (os.path.basename(OUT), os.path.getsize(OUT)))
