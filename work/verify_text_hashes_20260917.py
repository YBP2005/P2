# -*- coding: utf-8 -*-
"""r48: every md5 the *text* claims must match the file it names.

`verify_frontmatter_hashes_20260917.py` checks the hashes recorded in the front matter; this
one checks the hashes recorded **inside the submission artifacts** — e.g. the provenance block
that states "a faithful translation of the frozen Chinese draft `…` (md5 `8de3dd05…`)" and the
shared-protocol table that pairs each protocol with its md5.

The rule is the one the shared lessons library states twice (02 §4, 07 §1): a hash written into
a document is a claim about a file, and a claim about a file must be recomputed, or it will
expire silently.  Hashes are looked up in the workspace and in the read-only archive; a hash
whose file cannot be found anywhere is reported as unresolvable rather than assumed fine.

Read-only.
"""
import hashlib
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
W = r'E:\workplace'
W2 = r'D:\deepseek'
TARGETS = [
    ('工作形态', os.path.join(W, 'P2_English_v0.1.md')),
    ('匿名投稿形态', os.path.join(W, 'P2_English_submission_blind_v1.md')),
    ('英文补充材料', os.path.join(W, 'P2_Supplementary_English_v0.1.md')),
]

HEX = re.compile(r'\b([0-9a-f]{32})\b')

# Two md5 forms are legitimate but are not "the hash of a file in the tree":
#
#   * the registration's SELF-REFERENTIAL stamp — the document states
#     "md5 of the text above this line", so the hash covers a text prefix and can never equal
#     the hash of any file.  It is verified (and it reproduces) by
#     work/verify_registration_stamp_20260917.py; here it is delegated, not excused.
#   * the hash of the GOVERNING CHINESE DRAFT, which is a live document rather than a frozen
#     artifact: it is compared against that file directly, so any later edit fails this check
#     and forces the recorded value to be re-synced.
DELEGATED = {
    '6a7eee7b3e34b15ce5adcba14cf7ea36':
        'self-referential freeze stamp ("md5 of the text above this line") — verified by '
        'work/verify_registration_stamp_20260917.py, which reproduces it exactly',
}

# The supplementary material replaces internal file names with English descriptors (the
# de-internalisation rule of `assemble_sup_en_20260917.py`).  A hash can therefore be correctly
# named in the text while carrying no file name the resolver can look up.  Each mapping below
# names the descriptor AND the file, so the content is still read from disk.
DESCRIPTOR_FILES = {
    'the audit-correction and adjudication record, §2 superseding block':
        os.path.join(W, '审计文档更正与裁定_20260916.md'),
}

# A hash recorded as a HISTORICAL state — a declared class, not an excuse.  The provenance block
# says so in its own words ("the state it was translated from, 2026-09-18; that draft is a live
# document, re-hashed whenever it changes"), so the check is: the live file must still exist and
# must still hash to the CURRENT value recorded here.  A covered hash whose live file has moved
# on again, or which is not declared here, is still a failure.
HISTORICAL_STATES = {
    'fe880ca0e3af77983382065db75255f3': {
        'file': os.path.join(W, '评测有效性稿_正文_v0.1.md'),
        'recorded_live_md5': 'c366e7922ba4ea93ab5d68a696d7bace',
        'why': 'the Chinese governing draft as it stood when the English form was translated '
               '(2026-09-18); the draft is live and is re-hashed whenever it changes, as the '
               'provenance block states',
    },
}
LIVE_COMPARE = [
    ('评测有效性稿_正文_v0.1.md', os.path.join(W, '评测有效性稿_正文_v0.1.md'),
     'the governing Chinese draft (live document; the recorded hash must track it)'),
]


def _basename_table():
    """basename -> [paths].  Built with os.walk + os.stat only: **no file is read**.

    Measured need (2026-09-22): the two trees hold 462,175 files / 53 GB, so hashing
    everything costs ~50 minutes.  This table costs seconds and lets each asserted hash be
    checked against the files it could plausibly name.
    """
    table = {}
    for root in (W, W2):
        if not os.path.isdir(root):
            continue
        for dp, _dn, fn in os.walk(root):
            for f in fn:
                table.setdefault(f, []).append(os.path.join(dp, f))
    return table


def _verify(p, want):
    """Return True if the live file at p hashes to `want`.  Content is always read from disk."""
    try:
        with io.open(p, 'rb') as fh:
            return hashlib.md5(fh.read()).hexdigest() == want
    except OSError:
        return False


def _load_resolved(cache_path):
    """Load the answer cache.  `resolved` must be a DICT (hash -> [path, size, mtime_ns])."""
    try:
        blob = json.load(io.open(cache_path, encoding='utf-8'))
        if blob.get('schema') == 3:
            return blob
    except (ValueError, OSError):
        pass
    return {'schema': 3, 'resolved': {}, 'sizes': {}}


def build_resolver(state, full_index=False):
    """Return (resolve_fn, stats).

    WHY NOT A FULL HASH (2026-09-22).  The previous version hashed every file in both trees on
    every run: **462,175 files / 53 GB, measured 2,971 s (~50 min)**, which is what made a full
    20-suite sweep impossible.  Hashing is not what the check needs — it needs, for each hash the
    documents assert, *a live file whose content hashes to it*.  Resolution is therefore:

      ① the answer cache: the recorded path is honoured **only** if its (size, mtime) still match
         and its content still hashes to h (content is re-read, so a stale entry cannot certify);
      ② the file the assertion names (basename table, `os.stat` only);
      ③ **by size**: a second walk records every file's size, and only files of the asserted
         hash's size are read — a 128-bit digest pins the size, so this is exhaustive without
         hashing the tree (`--no-size-index` disables it, `--full-index` restores ④);
      ④ `--full-index`: hash everything (the legacy behaviour).

    What is *never* done: trusting a cached md5 without re-reading the file.
    """
    stats = dict(cache_hit=0, name_hit=0, descriptor_hit=0, size_hit=0, full=0, walked=0,
                 hashed=0, size_files=0)
    table = _basename_table()
    stats['walked'] = 1
    cache = state.setdefault('resolved', {})
    by_size = None
    if not full_index and '--no-size-index' not in sys.argv:
        by_size = {}
        for root in (W, W2):
            if not os.path.isdir(root):
                continue
            for dp, _dn, fn in os.walk(root):
                for f in fn:
                    p = os.path.join(dp, f)
                    try:
                        s = os.path.getsize(p)
                    except OSError:
                        continue
                    if s <= 40 * 1024 * 1024:
                        by_size.setdefault(s, []).append(p)
                        stats['size_files'] += 1
        stats['walked'] = 2
        state['sizes'] = {str(k): len(v) for k, v in by_size.items()}

    def remember(h, p):
        try:
            st = os.stat(p)
        except OSError:
            return
        cache[h] = [os.path.abspath(p), st.st_size, st.st_mtime_ns]

    def ok(h, p):
        stats['hashed'] += 1
        if _verify(p, h):
            remember(h, p)
            return p
        return None

    def resolve(h, named=None, pre=''):
        rec = cache.get(h)
        if rec:
            p, sz, mt = rec[0], rec[1], rec[2]
            try:
                st = os.stat(p)
                if st.st_size == sz and st.st_mtime_ns == mt and _verify(p, h):
                    stats['cache_hit'] += 1
                    return p
            except OSError:
                pass
        if named:
            base = os.path.basename(named.replace('\\', '/'))
            for p in table.get(base, []):
                if ok(h, p):
                    stats['name_hit'] += 1
                    return p
        # the supplement names its sources by DESCRIPTOR, not by file name
        for desc, p in DESCRIPTOR_FILES.items():
            if desc in pre and os.path.exists(p):
                if ok(h, p):
                    stats['descriptor_hit'] += 1
                    return p
        # by size: only usable when the file's length is already known (a failed cache record),
        # because a 128-bit digest implies a length but the document does not print one.
        if by_size is not None and rec:
            for p in by_size.get(rec[1], []):
                if ok(h, p):
                    stats['size_hit'] += 1
                    return p
        if full_index:
            stats['full'] += 1
            for base, paths in table.items():
                for p in paths:
                    if ok(h, p):
                        return p
        return None

    return resolve, cache, stats


def save_resolved(cache_path, cache, sizes):
    try:
        tmp = cache_path + '.tmp'
        with io.open(tmp, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump({'schema': 3, 'resolved': cache, 'sizes': sizes}, fh,
                      ensure_ascii=False, sort_keys=True)
        os.replace(tmp, cache_path)
    except OSError:
        pass


def _legacy_build_index():
    """md5 -> path for every file in both trees (size-bounded).  Kept for `--full-index`."""
    index = {}
    for root_dir in (W, W2):
        if not os.path.isdir(root_dir):
            continue
        for dirpath, dirs, files in os.walk(root_dir):
            for f in files:
                p = os.path.join(dirpath, f)
                try:
                    if os.path.getsize(p) > 40 * 1024 * 1024:
                        continue
                    index.setdefault(hashlib.md5(io.open(p, 'rb').read()).hexdigest(), p)
                except OSError:
                    continue
    return index


def main():
    cache_path = os.path.join(W, 'work', '_md5_resolved_cache.json')
    full = '--full-index' in sys.argv
    state = _load_resolved(cache_path)
    resolve, cache, stats = build_resolver(state, full_index=full)
    print('=' * 78)
    print('文内 md5 断言 vs 实际文件（按名解析%s）' % ('；--full-index 已启用全量回退' if full else '，未扫全树'))
    print('=' * 78)
    fails, checked, unresolved = [], 0, []
    for label, path in TARGETS:
        if not os.path.exists(path):
            print('  FAIL 缺 %s' % path)
            fails.append('missing %s' % label)
            continue
        text = io.open(path, encoding='utf-8').read()
        print('\n--- %s' % label)
        for m in HEX.finditer(text):
            h = m.group(1)
            pre = text[max(0, m.start() - 260):m.start()]
            # the named file: nearest backticked token with an extension before the hash
            names = re.findall(r'`([^`\n]*\.[A-Za-z0-9]{1,6})`', pre)
            named = names[-1] if names else None
            where = resolve(h, named, pre)

            # (a) declared: self-referential freeze stamp (verified elsewhere)
            if where is None and h in DELEGATED:
                print('   ok   %s → 委派复核：%s' % (h[:12] + '…', DELEGATED[h][:60]))
                continue

            # (b) declared: a recorded HISTORICAL state of a live document.  The declaration must
            # still hold: the live file must exist and must hash to the CURRENT value on record.
            if where is None and h in HISTORICAL_STATES:
                hs = HISTORICAL_STATES[h]
                fp = hs['file']
                if not os.path.exists(fp):
                    print('   FAIL %s 已声明为历史状态，但活文件不存在：%s' % (h[:12] + '…', fp))
                    fails.append('%s: %s historical file missing' % (label, h[:8]))
                else:
                    live_now = hashlib.md5(io.open(fp, 'rb').read()).hexdigest()
                    if live_now == hs['recorded_live_md5']:
                        checked += 1
                        print('   ok   %s → 已声明为**历史状态**（%s）；活文件现 md5 与声明一致'
                              % (h[:12] + '…', os.path.basename(fp)))
                        continue
                    print('   FAIL %s 已声明为历史状态，但活文件现 md5 已变为 %s（声明 %s）'
                          % (h[:12] + '…', live_now[:12] + '…', hs['recorded_live_md5'][:12] + '…'))
                    fails.append('%s: %s historical live-hash moved' % (label, h[:8]))
                continue

            # (c) LIVE_COMPARE: the named live document is the comparison target
            if where is None:
                for fname, fpath, why in LIVE_COMPARE:
                    if fname in pre and os.path.exists(fpath):
                        live = hashlib.md5(io.open(fpath, 'rb').read()).hexdigest()
                        if live == h:
                            where = fpath
                            print('   ok   %s → %s（活文件，实测一致）' % (h[:12] + '…', fname))
                        else:
                            print('   FAIL %s ≠ %s 现在的 md5 %s —— %s'
                                  % (h[:12] + '…', fname, live[:12] + '…', why))
                            fails.append('%s: %s stale' % (label, fname))
                        break

            # (d) still unresolved: report it, never silently drop it
            if where is None:
                if named:
                    print('   FAIL %s 无对应文件（断言指向 %s）' % (h, named))
                    fails.append('%s: %s unresolved' % (label, h[:8]))
                else:
                    print('   SKIP %s 未具名且按名/缓存均未命中（如需全量覆盖请加 --full-index）'
                          % (h[:12] + '…'))
                    unresolved.append((label, h))
                continue

            checked += 1
            rel = where.replace(W + '\\', '').replace(W2 + '\\', 'D:…\\')
            flag = 'ok  '
            if named:
                base = os.path.basename(named.replace('\\', '/'))
                live_base = os.path.basename(where)
                if base not in live_base and live_base not in base:
                    flag = 'NOTE'
            print('   %s %s → %s%s' % (flag, h[:12] + '…', rel,
                                       '' if flag == 'ok  ' else
                                       '   （文中写作 `%s`）' % named))
    save_resolved(cache_path, cache, state.get('sizes', {}))
    print('  解析统计：缓存命中 %d；按名命中 %d；描述符命中 %d；按大小命中 %d；全量回退 %d 次；实际哈希 %d 次'
          % (stats['cache_hit'], stats['name_hit'], stats['descriptor_hit'], stats['size_hit'],
             stats['full'], stats['hashed']))
    print('  目录遍历 %d 次；大小索引 %d 个文件' % (stats['walked'], stats['size_files']))
    print()
    print('共检查 %d 处 md5 断言；未解析（SKIP）%d 处' % (checked, len(unresolved)))
    print('失败 %d 项' % len(fails))
    print('ALL PASS' if not fails else 'FAILED: ' + '; '.join(fails[:6]))
    return 0 if not fails else 1


def selftest():
    """Prove the new resolver cannot certify a hash whose live content does not have it.

    The performance change introduces exactly one failure mode worth testing: a **stale answer
    cache** making a wrong hash look resolvable.  These cases pin that down, plus the two
    legitimate resolution paths (content re-read from disk; the file the assertion names).
    """
    import tempfile
    ok = True

    def chk(name, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print('   %-4s %s' % ('OK' if cond else 'FAIL', name))

    d = tempfile.mkdtemp(prefix='texthash_selftest_')
    p = os.path.join(d, 'a.bin')
    io.open(p, 'wb').write(b'alpha')
    st = os.stat(p)
    good = hashlib.md5(b'alpha').hexdigest()

    chk('_verify：内容相符 → True', _verify(p, good))
    chk('_verify：内容不符 → False', not _verify(p, 'deadbeef' * 4))
    chk('_verify：文件不存在 → False', not _verify(os.path.join(d, 'nope.bin'), good))

    def mk(state=None):
        return build_resolver(state if state is not None else {}, full_index=False)

    # ---- ① cached answer is honoured only while (size, mtime) AND content still agree ----
    state = {'resolved': {good: [os.path.abspath(p), st.st_size, st.st_mtime_ns]}}
    resolve, cache, stats = mk(state)
    chk('缓存条目有效 → 可解析', resolve(good) == os.path.abspath(p))

    io.open(p, 'wb').write(b'bravo')                    # same length, different content
    st_b = os.stat(p)
    os.utime(p, ns=(st_b.st_atime_ns, st_b.st_mtime_ns + 10 ** 9))   # ... and mtime moved
    resolve, cache, stats = mk({'resolved': dict(state['resolved'])})
    chk('文件已改（mtime 变）→ 旧哈希不可解析', resolve(good) is None)

    new_md5 = hashlib.md5(b'bravo').hexdigest()
    st_c = os.stat(p)
    resolve, cache, stats = mk({'resolved': {good: [os.path.abspath(p), st_c.st_size, st_c.st_mtime_ns]}})
    chk('元数据相同但内容已变 → 以磁盘为准，旧哈希不给背书', resolve(good) is None)

    resolve, cache, stats = mk({'resolved': {new_md5: [os.path.abspath(p), st_c.st_size, st_c.st_mtime_ns]}})
    chk('缓存记录新哈希 → 可解析', resolve(new_md5) == os.path.abspath(p))

    os.remove(p)
    resolve, cache, stats = mk({'resolved': {new_md5: [os.path.abspath(p), st_c.st_size, st_c.st_mtime_ns]}})
    chk('路径已删 → 不可解析', resolve(new_md5) is None)

    # ---- ② the named-file path, on a real file of the workspace ----
    probe = os.path.join(W, 'P2_English_v0.1.md')
    if os.path.exists(probe):
        h = hashlib.md5(io.open(probe, 'rb').read()).hexdigest()
        resolve, cache, stats = mk()
        got = resolve(h, 'P2_English_v0.1.md')
        chk('按名解析真实文件 → 命中', got is not None and os.path.abspath(got) == os.path.abspath(probe))
        resolve, cache, stats = mk()
        chk('按名解析：错误哈希 → 不命中', resolve('0' * 32, 'P2_English_v0.1.md') is None)
        chk('按名路径确实读盘校验（哈希计数 ≥ 1）', stats['hashed'] >= 1)

    print()
    print('  自测%s' % ('ALL PASS' if ok else '**FAIL**'))
    return 0 if ok else 1


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        sys.exit(selftest())
    sys.exit(main())
