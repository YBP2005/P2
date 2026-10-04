# -*- coding: utf-8 -*-
"""build_provenance.py — 为 published_logs/ 的第三方训练日志写出 PROVENANCE.md。

纪律（与项目其它脚本一致）：
  * 单写者：只写 published_logs\\PROVENANCE.md，若存在则先备份为 .bak_before_<stamp>；
  * **映射靠内容哈希证明，不靠猜**：本地文件与来源包内条目的对应关系由
    sha256 相等来建立；凡不能由哈希配上的条目一律进"未溯源"清单，
    绝不按文件名相似度硬配；
  * 脚本自己打印校验摘要，但"改了没有"以退出后重读文件为准（见调用方）。

数据来源（全部为本目录既有产物，非新增下载）：
  _work\\kg\\<owner>__<repo>.zip         下载器留下的原始 zip（内含源内相对路径）
  _work\\kg_hits.csv                     下载器自己记录的 ds -> 源内路径
  _work\\kg_candidates.csv               Kaggle API 返回的 url / 许可 / 版本
  _work\\tree_kimmkless__YoloDetector.json  GitHub API tree（含 commit sha）
  SHA256SUMS.txt                          先前生成的字节清单（本脚本复核它）
"""
import csv, hashlib, io, json, os, shutil, sys, time, zipfile

sys.stdout.reconfigure(encoding='utf-8')

D = r'D:\deepseek\analysis\eval_validity\published_logs'
W = os.path.join(D, '_work')
KG = os.path.join(W, 'kg')
OUT = os.path.join(D, 'PROVENANCE.md')
RETRIEVAL = '2026-09-16'
STAMP = time.strftime('%Y%m%d-%H%M%S')

# ---------------------------------------------------------------- helpers
def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()

def local_files():
    return sorted(n for n in os.listdir(D) if n.endswith('.csv') and n != 'SHA256SUMS.txt')

def read_manifest():
    """SHA256SUMS.txt -> {name: (sha, bytes)}"""
    out = {}
    with io.open(os.path.join(D, 'SHA256SUMS.txt'), 'r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) >= 3:
                out[parts[2]] = (parts[0].lower(), int(parts[1]))
    return out

def zip_index():
    """{sha256: (zipname, entrypath, bytes)}  —— 把每个 kg zip 的每个条目都哈希一遍"""
    idx = {}
    zips = sorted(n for n in os.listdir(KG) if n.endswith('.zip'))
    for z in zips:
        try:
            with zipfile.ZipFile(os.path.join(KG, z)) as zf:
                for name in zf.namelist():
                    if name.endswith('/'):
                        continue
                    b = zf.read(name)
                    idx.setdefault(sha256_bytes(b), []).append((z, name, len(b)))
        except zipfile.BadZipFile:
            print('  !! 不是有效 zip: %s' % z)
    return idx, zips

def kg_candidates():
    """ref -> dict(url, licence, version, title)"""
    out = {}
    p = os.path.join(W, 'kg_candidates.csv')
    with io.open(p, 'r', encoding='utf-8-sig', newline='') as fh:
        for row in csv.DictReader(fh):
            ref = (row.get('ref') or '').strip()
            if not ref:
                continue
            out.setdefault(ref, {
                'url': (row.get('url') or '').strip(),
                'licence': (row.get('licenseName') or '').strip() or '未标注',
                'version': (row.get('currentVersionNumber') or '').strip(),
                'title': (row.get('title') or '').strip(),
                'lastUpdated': (row.get('lastUpdated') or '').strip(),
            })
    return out

def kg_hits():
    """本地 zip 名（owner__repo）-> {源内路径小写后 basename: 源内路径}"""
    out = {}
    p = os.path.join(W, 'kg_hits.csv')
    with io.open(p, 'r', encoding='utf-8-sig', newline='') as fh:
        for row in csv.DictReader(fh):
            ds = (row.get('ds') or '').strip()
            f = (row.get('file') or '').strip().replace('\\', '/')
            if not ds or not f:
                continue
            out.setdefault(ds.replace('/', '__'), []).append(f)
    return out

# ---------------------------------------------------------------- build
mismatch = []
local = local_files()
man = read_manifest()
zidx, zips = zip_index()
cands = kg_candidates()

# 本地字节与清单复核
rows = []
for n in local:
    b = io.open(os.path.join(D, n), 'rb').read()
    h = sha256_bytes(b)
    m = man.get(n)
    ok = bool(m) and m[0] == h and m[1] == len(b)
    if not ok:
        mismatch.append(n)
    rows.append({'name': n, 'sha': h, 'bytes': len(b), 'in_manifest': ok})

# 哈希匹配 zip 条目
for r in rows:
    hits = zidx.get(r['sha'], [])
    r['zip_hits'] = hits
    if len(hits) == 1:
        z, entry, sz = hits[0]
        ref_owner = os.path.splitext(z)[0]          # owner__repo
        r['src_kind'] = 'Kaggle dataset'
        r['src_key'] = ref_owner
        r['src_path'] = entry
        r['src_url'] = 'https://www.kaggle.com/datasets/' + ref_owner.replace('__', '/')
        r['match'] = 'sha256 与包内条目相同'
        c = cands.get(ref_owner.replace('__', '/'))
        r['licence'] = c['licence'] if c else '未查到'
        r['src_version'] = c['version'] if c else '未查到'
    elif len(hits) > 1:
        # 多命中：只有当全部命中都是**字节相同**的副本、且其中恰有一个 `__test__*` 探针包时才可裁定
        # （探针包是下载器的试拉，规范来源取非探针的那一个）。否则不猜。
        real = [h for h in hits if not os.path.basename(h[0]).startswith('__test__')]
        if len(real) == 1:
            z, entry, sz = real[0]
            ref_owner = os.path.splitext(z)[0]
            r['src_kind'] = 'Kaggle dataset'
            r['src_key'] = ref_owner
            r['src_path'] = entry
            r['src_url'] = 'https://www.kaggle.com/datasets/' + ref_owner.replace('__', '/')
            r['licence'] = (cands.get(ref_owner.replace('__', '/')) or {}).get('licence', '未查到')
            r['src_version'] = (cands.get(ref_owner.replace('__', '/')) or {}).get('version', '未查到')
            others = ', '.join('%s:%s' % (zz, ee) for zz, ee, _ in hits if zz != z)
            r['match'] = ('sha256 命中 %d 处，全部字节相同；其中 %s 是下载器的探针包，'
                          '规范来源取 `%s`' % (len(hits), others, os.path.basename(z)))
        else:
            r['src_kind'] = '?'
            r['match'] = 'sha256 命中 %d 个包内条目（需人工裁定）' % len(hits)
            r['src_key'] = '; '.join('%s:%s' % (z, e) for z, e, _ in hits)
            r['src_path'] = ''
            r['src_url'] = ''
            r['licence'] = ''
            r['src_version'] = ''
    else:
        r['src_kind'] = '未溯源'
        r['match'] = '本地 sha256 在 kg 的 zip 里找不到'
        r['src_key'] = ''
        r['src_path'] = ''
        r['src_url'] = ''
        r['licence'] = ''
        r['src_version'] = ''

# GitHub：kimmkless/YoloDetector（本地无 zip，按字节数 + 树 sha 证明）
gh_p = os.path.join(W, 'tree_kimmkless__YoloDetector.json')
gh_sha, gh_entries = None, []
if os.path.exists(gh_p):
    j = json.load(io.open(gh_p, 'r', encoding='utf-8'))
    gh_sha = j.get('sha')
    gh_entries = [(e['path'], e.get('size')) for e in j.get('tree', []) if 'results.csv' in e.get('path', '')]

for r in rows:
    if r['src_kind'] != '未溯源':
        continue
    cand = [(p, s) for p, s in gh_entries if s == r['bytes']]
    if len(cand) == 1 and gh_sha:
        p, s = cand[0]
        r['src_kind'] = 'GitHub repo'
        r['src_key'] = 'kimmkless/YoloDetector'
        r['src_path'] = p
        r['src_url'] = 'https://raw.githubusercontent.com/kimmkless/YoloDetector/%s/%s' % (gh_sha, p)
        r['src_repo_url'] = 'https://github.com/kimmkless/YoloDetector/tree/%s' % gh_sha
        r['licence'] = '仓库含 `LICENSE`（本目录未留存其内容，故未判定许可类型）'
        r['src_version'] = 'commit %s' % gh_sha[:12]
        r['match'] = '字节数与 GitHub tree 中该路径相同（%d B）' % s
    elif len(cand) > 1:
        r['match'] = '字节数命中多个 GitHub 路径，需人工裁定'
    else:
        r['match'] = '字节数在 GitHub tree 里无唯一匹配'

# ---------------------------------------------------------------- write
untraced = [r for r in rows if r['src_kind'] == '未溯源']
by_src = {}
for r in rows:
    by_src.setdefault(r['src_key'] or '(未溯源)', []).append(r)

# 许可未标注的 Kaggle dataset 数（不要硬编码，随数据算）
n_unknown = len({k for k in by_src
                 if by_src[k][0].get('licence') in ('Unknown', '未查到', '', None)})
n_undet = len({k for k in by_src if 'LICENSE' in (by_src[k][0].get('licence') or '')})

L = []
A = L.append
A('# 公开第三方日志的来源（PROVENANCE）')
A('')
A('> **这份文件补上的是"来源"，不是"字节"**。字节早已由同目录 `SHA256SUMS.txt` 钉住；')
A('> 本文件补的是**每个文件从哪里来、在来源里叫什么、按什么许可取回**，')
A('> 从而让 `selection_premium_public_20260916.md` 从"可核字节、不可溯源"变成**可核字节 + 可溯源**。')
A('')
A('| 项 | 值 |')
A('|---|---|')
A('| 取回日期 | 全部文件均为 **%s** 当日取回 |' % RETRIEVAL)
A('| 文件数 | **%d** 个 CSV（另 1 个 `SHA256SUMS.txt`） |' % len(rows))
A('| 来源数 | **%d** 个（%d Kaggle dataset + %d GitHub repo） |' % (
    len([k for k in by_src if k != '(未溯源)']),
    len([k for k in by_src if k != '(未溯源)' and 'kimmkless' not in k]),
    len([k for k in by_src if 'kimmkless' in k])))
A('| 与 `SHA256SUMS.txt` 的复核 | **%d/%d 一致（sha256 与字节数双查）** |' % (len(rows) - len(mismatch), len(rows)))
A('| 未溯源条目 | **%d** |' % len(untraced))
A('| 生成方式 | `analysis\\work\\build_provenance.py`（可复跑；映射由**内容哈希**建立，非按文件名相似度猜配） |')
A('')
A('## 0. 映射是怎么证明的（这一节决定这张表能不能信）')
A('')
A('下载器留下了每个 Kaggle dataset 的**原始 zip**（`_work\\kg\\<owner>__<repo>.zip`，内含源内相对路径）。')
A('本脚本把**每个 zip 的每个条目**都哈希一遍，再把本地 24 个 CSV 的 sha256 与这些条目对撞：')
A('')
A('- 对撞**唯一命中** → 该条目的"包内路径"就是该文件的真实来源路径，`src_key` 即该 dataset；')
A('- 对撞**零命中** → 进 §3 未溯源清单，**不猜**；')
A('- 对撞**多命中** → 标注"需人工裁定"，同样不猜。')
A('')
A('kimmkless/YoloDetector 没有 zip（它是 GitHub 仓库），改用**GitHub tree API 的路径字节数**做唯一性匹配，')
A('并在 commit sha `%s` 上固定。' % (gh_sha[:12] if gh_sha else '未知'))
A('')
A('## 1. 逐文件来源表')
A('')
A('| 本地文件 | 字节 | sha256[:16] | 来源类型 | 来源 | 源内路径 | 许可 | 匹配依据 |')
A('|---|---|---|---|---|---|---|---|')
for r in rows:
    A('| `%s` | %d | `%s` | %s | %s | `%s` | %s | %s |' % (
        r['name'], r['bytes'], r['sha'][:16], r['src_kind'],
        r['src_key'] or '—', r['src_path'] or '—', r['licence'] or '—', r['match']))
A('')
A('## 2. 按来源汇总')
A('')
A('| 来源 | 类型 | 源内文件数 | 规范 URL | 许可 | 版本/固定点 |')
A('|---|---|---|---|---|---|')
for k in sorted(by_src):
    rs = by_src[k]
    first = rs[0]
    url = first.get('src_repo_url') or first['src_url'] or '—'
    A('| `%s` | %s | %d | %s | %s | %s |' % (
        k, first['src_kind'] if k != '(未溯源)' else '—', len(rs),
        url, first['licence'] or '—', first['src_version'] or '—'))
A('')
A('## 3. 未溯源 / 需人工裁定')
A('')
if untraced:
    for r in untraced:
        A('- `%s`（%d B，sha256 `%s`）—— %s' % (r['name'], r['bytes'], r['sha'][:16], r['match']))
else:
    A('**无。** 全部 %d 个文件都由内容哈希或唯一字节数匹配到了具体来源路径。' % len(rows))
A('')
A('## 4. 这份溯源**没有**覆盖的东西（写进正文时必须照实说）')
A('')
A('1. **Kaggle 侧的确切下载版本**：`kg_candidates.csv` 记的是**探查当时**的 `currentVersionNumber`，')
A('   不等于下载当时的版本。可证的是"我们分析的字节 = 这些哈希"，而不是"这些字节 = 当时 Kaggle 的那一版"。')
A('   其中 `ikram0703/train-results-yolov8-and-yolov8ema` 的记录版本是 **2**，其余为 1。')
A('2. **逐文件的下载时刻**：本目录只知统一取回日期（%s）。' % RETRIEVAL)
A('   注意：Kaggle 下载会保留源侧 mtime，所以部分本地文件的 mtime 是**源侧日期**（例如 `ayyappakorla` 为 2025-06-18），**不可当取回日期用**。')
A('3. **数据集与协议**：公开日志不带 yaml，**无法**由本文件推出这些基准的 `val` 与 `test` 是否同一目录。')
A('   "溢价存在"与"基准别名"是两条独立证据，不能用本文件互相代替。')
A('4. **许可的可再分发边界**：%d 个来源的许可**未标注**（Kaggle 侧 `Unknown`，见 §2），另有 %d 个来源'
  '（GitHub）仓库内有 `LICENSE` 但本目录未留存其内容。' % (n_unknown, n_undet))
A('   本项目**不再分发**这些 CSV，只分发哈希与来源指针；引用其派生统计量时应说明来源未标注许可。')
A('5. **本目录里还有一个不是有效 zip 的下载**：`_work\\kg\\craneid__wearingmaskc19.zip`（`BadZipFile`）。')
A('   它**不属于**本文分析的 24 个文件，记录在此以免被误认为"分析过的来源"。')
A('')
A('## 5. 复核方法（任何人可复跑）')
A('')
A('```')
A('python analysis\\work\\build_provenance.py    # 重建本文件并打印校验摘要')
A('```')
A('')
A('脚本会：① 重算 24 个 CSV 的 sha256 与字节数并与 `SHA256SUMS.txt` 对照；')
A('② 重算每个 `_work\\kg\\*.zip` 内每个条目的 sha256 并重建映射；③ 打印不一致清单（应为空）。')
A('')
A('---')
A('')
A('生成时间 %s（脚本 `build_provenance.py`，备份后缀 `.bak_before_%s`）' % (STAMP, STAMP))

text = '\n'.join(L) + '\n'

if os.path.exists(OUT):
    bak = OUT + '.bak_before_' + STAMP
    shutil.copy2(OUT, bak)
    print('backup -> %s' % os.path.basename(bak))
with io.open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
    fh.write(text)

print('wrote %s (%d chars)' % (os.path.basename(OUT), len(text)))
print('files=%d  traced=%d  untraced=%d  manifest_mismatch=%d' % (
    len(rows), len(rows) - len(untraced), len(untraced), len(mismatch)))
print('sources=%d' % len([k for k in by_src if k != '(未溯源)']))
for k in sorted(by_src):
    print('   %-52s %d' % (k, len(by_src[k])))
if mismatch:
    print('MANIFEST MISMATCH: %s' % ', '.join(mismatch))
for r in rows:
    if r['src_kind'] in ('未溯源', '?'):
        print('UNTRACED: %s' % r['name'])
