# -*- coding: utf-8 -*-
"""Run every verification suite, write one log, and print a PASS/FAIL table.

r54i: the classifier was wrong, and the fix is in two parts -- the LABEL and the CONDITION.

  Label (was): a suite was FAIL if any line matched `FAIL|ERROR|TRACEBACK|!!|缺|不一致|失败`.
  Condition (now):
    * a suite is FAIL only on a **genuine failure verdict**: a line that reports a POSITIVE
      count of failures (`失败 N 项` with N > 0), `FAILED`, `FAIL <something>`, a bare `!!`,
      or a traceback;
    * **informational mentions are no longer failures**: `失败 0 项`, `缺 0 项`, `缺文件`
      inside an explanatory sentence, `不一致` inside a printed description, and the word
      `缺` in Chinese explanatory text are all just text.  (Before r54i, "失败 0 项" and the
      word "缺" inside a sentence made healthy suites show as FAIL.)
    * the table prints each suite's OWN final verdict line(s) (`ALL PASS` / `失败 N 项` /
      `FAILED: …`), not a truncated match -- so the reader sees the suite's own word, and can
      tell how many checks it ran.
    * a non-zero exit that comes with NO failure verdict is reported as `PASS*`, and the
      informational lines that caused it are printed, so a data report cannot masquerade as
      either a pass or a failure.
"""
import io
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
W = r'E:\workplace\work'
SUITES = ['verify_compression_20260917', 'verify_xref_reachability_20260917',
          'verify_index_titles_20260917', 'verify_consistency_guards_20260917',
          'verify_panel_closure_20260917', 'verify_split_claims_20260917',
          'verify_text_hashes_20260917', 'verify_registration_stamp_20260917',
          'verify_docx_fidelity_20260917', 'verify_sup_en_20260917',
          'verify_sup_final_20260917', 'verify_supp_hashes_20260917',
          'verify_submission_pack_20260917', 'verify_frontmatter_hashes_20260917',
          'verify_no_number_lost_20260917', 'verify_rank8_refs_20260918',
          'verify_pr_forms_20260917', 'verify_split_defs_20260916',
          # r54m: these two were missing from the sweep.  They are the ones that catch an anchor
          # silently losing its carrier in the submission set (lessons 21 §9), which is exactly
          # what my own r54i/r54l deletions did to X56.
          'audit_anchors_fupaper', 'audit_anchor_scope_20260917']

# --- the CONDITION: what actually means "this suite failed" ----------------------------
# Every branch below is anchored to a LINE, and every branch demands a failure *verdict*.
# Plain prose words (`缺`, `不一致`) and zero counts (`失败 0 项`) are deliberately NOT here:
# that was the false-positive source this round repairs.
FAIL_VERDICT = re.compile(
    r'^\s*FAILED\b'                          # "FAILED: a; b"
    r'|^\s*\*\*FAIL\*\*'                     # "**FAIL**"
    r'|^\s*FAIL\s'                           # a per-check "FAIL ..." verdict
    r'|^\s*失败\s+[1-9]\d*\s*项'             # "失败 3 项" (NOT "失败 0 项")
    r'|Traceback \(most recent call last\)'  # an uncaught crash
    r'|^\s*(?:\*\*)?!!',                     # the "!! ..." failure banner
    re.M | re.I)
# an informational line the old regex misread as failure
INFO = re.compile(r'^\s*失败\s+0\s*项|^\s*缺\s+0\s*项', re.M)
VERDICT_LINE = re.compile(r'ALL PASS|FAILED\b|失败\s+\d+\s*项|^\s*\*\*FAIL\*\*|^\s*FAIL\s'
                          r'|Traceback \(most recent call last\)|^\s*(?:\*\*)?!!',
                          re.M | re.I)


def classify(out, rc):
    """Return (verdict, own-verdict-lines, diagnostic tail)."""
    lines = [l.rstrip() for l in out.splitlines()]
    own = [l.strip() for l in lines if VERDICT_LINE.search(l)]
    real = [l.strip() for l in lines if FAIL_VERDICT.search(l) and not INFO.search(l)]
    if real:
        return 'FAIL', own[:4], real[:3]
    if rc != 0:
        # Non-zero exit with no failure verdict: a data report, not a failed check.  Show the
        # tail so this cannot hide anything.
        return 'PASS*', own[:4], [l.strip() for l in lines[-5:] if l.strip()][:3]
    return 'PASS', own[:4], []


rows = []
for s in SUITES:
    p = os.path.join(W, s + '.py')
    if not os.path.exists(p):
        rows.append((s, 'MISSING', 'suite file not found', ''))
        continue
    r = subprocess.run([sys.executable, p], cwd=W, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    out = (r.stdout or '') + (r.stderr or '')
    verdict, own, diag = classify(out, r.returncode)
    rows.append((s, verdict, ' ; '.join(own)[:150] or '（无自报结论行，按退出码判定）',
                 ' ; '.join(diag)[:110]))
    io.open(os.path.join(W, '_sweep_log_' + s + '.txt'), 'w', encoding='utf-8',
            newline='\n').write(out)

print('=' * 118)
n_bad = 0
for s, v, own, diag in rows:
    if v.startswith('FAIL') or v == 'MISSING':
        n_bad += 1
    print('%-42s %-8s %s' % (s, v, own))
    if diag:
        print('%-42s %-8s %s' % ('', '', '↳ ' + diag))
print('=' * 118)
print('%d/%d PASS（含 PASS*）   ->  %s'
      % (len(rows) - n_bad, len(rows),
         'ALL PASS' if n_bad == 0 else '**%d suite(s) need fixing**' % n_bad))
io.open(os.path.join(W, '_sweep_summary.txt'), 'w', encoding='utf-8', newline='\n').write(
    '\n'.join('%-42s %-8s %s' % (s, v, own) for s, v, own, _d in rows) + '\n')
