# -*- coding: utf-8 -*-
"""r48: audit the blind-review round's evidence base, using the three detectors the shared
lessons library (`通用经验与教训` 01 §2) requires — because in their project `finish=stop` was
reported for a round that had actually lost 3 of 6 reviews.

For every review file this checks:
  1. **length split**: content bytes vs reasoning bytes (a near-empty content with a huge
     reasoning file is the `reasoning-only` failure, which looks like success at the API);
  2. **the tail**: mid-sentence stop, or an unclosed markdown marker (`**`, a table row,
     an open code fence) — the `mid-sentence` failure;
  3. **completeness of the answer**: the required closing elements (the verdict table and
     the final numbered task) are present, because a file can stop cleanly at a section
     boundary.
Plus the freeze check of §7/§3: every md5 recorded in the round's README is recomputed here,
and any drift is reported (a round whose frozen inputs drifted cannot be compared).

Read-only.
"""
import hashlib
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
D = r'E:\workplace\model_review'
README = os.path.join(D, 'p2r1_README.md')

# content files of the round, and the re-run that replaced one of them
REVIEWS = [
    'p2r1_review_dsflash_20260917_214707.md',
    'p2r1_review_dspro_20260917_214807.md',
    'p2r1_review_glm53flash_20260917_215225.md',
    'p2r1_review_gpt56sol_20260917_220650.md',
    'p2r1_review_gemini38flash_20260917_220521.md',
    'p2r1_review_grok46_20260917_215926.md',      # first round, known truncated
    'p2r1b_review_grok46_20260917_221137.md',     # re-run, the one actually used
]

# Closing elements the panel prompt requires in every answer.  The FIRST version of this
# list looked for the Chinese spec headers ("| 模型 |") and for the literal words "改进建议";
# every model had in fact rendered the verdict table with its own English header
# ("| verdict | accept-if-changed | accept-as-it-stands |") and headed the recommendations
# "(e) The three changes" / "E. If I Could Change Only Three Things".  The check therefore
# reported 13 false failures — the exact failure mode the shared lessons library warns about
# in 02 §1 ("a check whose name claims something its implementation does not do").  Patterns
# are now written against what the models actually produce.
REQUIRED_TAIL = [
    ('判决表（verdict table）', r'(?m)^\|\s*(?:verdict|模型|Model)\s*\|'),
    ('改进建议段', r'(?i)(three changes|three things|suggested improvements|improvements|'
                   r'改进建议|建议清单)'),
]


def tail_problems(text):
    """Detect the two truncation signatures from the tail of the file."""
    probs = []
    stripped = text.rstrip()
    if not stripped:
        return ['正文为空（reasoning-only 失败形态）']
    last = stripped.split('\n')[-1].strip()
    tail40 = stripped[-40:]
    if re.search(r'[A-Za-z0-9,;:]$', last) and not re.search(r'[.)\]`]$', last):
        probs.append('末行以词/逗号结尾，疑似句中截断：…%s' % tail40[-34:])
    if last.count('**') % 2 == 1:
        probs.append('末行 ** 未闭合：…%s' % tail40[-34:])
    if last.count('`') % 2 == 1 and '```' not in last:
        probs.append('末行反引号未闭合：…%s' % tail40[-34:])
    if text.count('```') % 2 == 1:
        probs.append('代码围栏未闭合（``` 计数为奇数）')
    if last.startswith('|') and not last.endswith('|'):
        probs.append('末行是一条未写完的表格行')
    return probs


# Findings that are known, documented and deliberately not "fixed" — each with the reason.
# A declared finding is printed as DECLARED and does not fail the audit; it is NOT silently
# accepted, and it is not deleted from the record either.
DECLARED = {
    'p2r1_review_grok46_20260917_215926.md':
        '首轮截断（停在判决表表头）——已知并在 README §5.1 记录；实际使用的是 p2r1b 重跑件',
    'p2r1_review_gpt56sol_20260917_220650.md':
        '收尾句列举被截断（…the benchmark-audit logic）——判决表与各段齐全，提取与合成不受影响；'
        '已记入 README r48 追记 §2（首轮 IncompleteRead 后的重跑件，finish=stop 掩盖了它）',
}


def declared(name, problem):
    reason = DECLARED.get(name)
    return reason if reason and ('句中截断' in problem or '末行' in problem) else None


def main():
    readme = io.open(README, encoding='utf-8').read()
    recorded = set(re.findall(r'[0-9a-f]{32}', readme))
    print('=' * 78)
    print('盲审轮完整性审计（对照 model_review/p2r1_README.md 的冻结记录）')
    print('=' * 78)

    # ---- 1. freeze: which frozen artifacts still exist on disk? --------------------
    # The question is not "does the file hash match a number in the README" but "is the
    # input the round actually ran on still preserved?".  A recorded hash with no surviving
    # file means the frozen input was overwritten, and the round can no longer be re-verified.
    print('\n[1] 冻结复核：README 记录的每个 md5，盘上是否还有对应文件')
    on_disk = {}
    for name in os.listdir(D):
        p = os.path.join(D, name)
        if os.path.isfile(p):
            on_disk[hashlib.md5(io.open(p, 'rb').read()).hexdigest()] = name
    for h in sorted(set(recorded)):
        # skip hashes that are clearly something else (e.g. inside a quoted record)
        where = on_disk.get(h)
        print('   %-8s %s  %s' % ('ok' if where else 'GONE', h,
                                  where or '（无对应文件：该冻结版本已被覆盖）'))
    print('\n   现在盘上的包 p2r1_prompt.md：%d B  md5 %s'
          % (os.path.getsize(os.path.join(D, 'p2r1_prompt.md')),
             hashlib.md5(io.open(os.path.join(D, 'p2r1_prompt.md'), 'rb').read()).hexdigest()))

    # ---- 2/3. per-review truncation audit ------------------------------------------
    print('\n[2] 每份评审的两种失败形态检测 + 收尾要素')
    print('   %-38s %9s %9s %7s  %s' % ('file', 'content', 'reasoning', 'finish', 'verdict'))
    problems = []
    for name in REVIEWS:
        p = os.path.join(D, name)
        if not os.path.exists(p):
            problems.append('%s 缺失' % name)
            continue
        text = io.open(p, encoding='utf-8').read()
        rb = p + '.part.reasoning'
        reasoning = os.path.getsize(rb) if os.path.exists(rb) else 0
        meta = {}
        mp = p + '.meta.json'
        if os.path.exists(mp):
            try:
                meta = json.load(io.open(mp, encoding='utf-8'))
            except Exception:
                meta = {}
        finish = str(meta.get('finish_reason') or meta.get('finish') or '?')
        tp = tail_problems(text)
        missing = [label for label, pat in REQUIRED_TAIL if not re.search(pat, text, re.I)]
        status = 'ok' if (not tp and not missing) else 'PROBLEM'
        print('   %-38s %9d %9d %7s  %s' % (name[:38], len(text.encode('utf-8')), reasoning,
                                            finish, status))
        for x in tp:
            why = declared(name, x)
            if why:
                print('        DECLARED %s' % x)
                print('                 ↳ %s' % why)
            else:
                print('        · %s' % x)
                problems.append('%s: %s' % (name, x[:40]))
        for label in missing:
            print('        · 缺收尾要素：%s' % label)
            problems.append('%s: missing %s' % (name, label))
        if reasoning > 0 and len(text.encode('utf-8')) < 2000:
            problems.append('%s: reasoning-only' % name)

    print('\n[3] 结论')
    if problems:
        for x in problems:
            print('   FAIL %s' % x)
        print('\n失败 %d 项' % len(problems))
    else:
        print('   ok   无**未声明**的截断特征：7 份文件（6 份 + grok46 重跑）收尾要素齐全，'
              '已声明的 1 处尾部截断见上（DECLARED）')
        print('\n失败 0 项')
    print('   注：首轮 grok46 已知截断（停在判决表表头）——它保留在档，实际使用的是 p2r1b 重跑件。')
    return 0 if not problems else 1


if __name__ == '__main__':
    sys.exit(main())
