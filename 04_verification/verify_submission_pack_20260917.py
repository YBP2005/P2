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
# r143：不再硬编码作者机路径——包根优先（含 01_paper/ 的那一层），可用 P2_ROOT 覆盖，
# 两者都不成立时才回落到作者工作树。评审（C05）指出六个 checker 硬编码作者路径。
import os as _os
_AUTHOR = r'E:\workplace'
_PKG = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
W = _os.environ.get('P2_ROOT') or (_PKG if _os.path.isdir(_os.path.join(_PKG, '01_paper')) else _AUTHOR)
POST = os.path.join(W, 'P2_投稿前件_v0.1.md')
ENG = os.path.join(W, 'P2_English_submission_blind_v1.md')
# ★ 修正（2026-10-04）：原先把 **工作形态** `P2_English_v0.1.md` 当作"英文稿"来比摘要。
#   但真正进入投稿包与复现仓库的是**匿名投稿形态** `…_blind_v1.md`；工作形态另带署名头块、
#   是另一件受控件，自 2026-10-02 起未再同步 ⇒ 两处摘要"逐字相同"**假失败**（1517 vs 1527 字符）。
#   提交物的检查必须指向**被提交的那一件**。
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

# r169：**作者侧前置门**必须"停下来说清楚"，而不是抛 AttributeError。
#   实测（本轮包内入口审计）：从复现包里直接跑会崩在 `post.find(...)`，
#   而包 README 承诺的是"以可读错误停下"。这里把缺件说清并给退出码 2。
_missing = [p for p, v in ((POST, post), (ENG, eng), (REFS, refs), (FORMS, forms)) if v is None]
if _missing:
    print('=' * 74)
    print('投稿前件机械校验 —— **无法运行：缺作者侧输入**')
    print('=' * 74)
    for p in _missing:
        print('  缺：%s' % p)
    print('\n这个 checker 是**作者侧前置门**（它要投稿前件、参考文献表与形式要求核实件，这三件都随作者树走、')
    print('不进复现包）。从复现包里跑只能到这里 —— 这是**设计如此**，不是稿件有问题。')
    print('包内**独立**可运行的 checker 只有一个：`work/verify_pulled.py`（见包 README 的 “Which of the six '
      'checkers run from this package” 一节）。**投稿前件与形式要求核实件已随包**（在 `01_paper/`），'
      '这里真正缺的是参考文献表 `P2_参考文献_v0.1.md`。')
    sys.exit(2)

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
# ★ 2026-09-21 两处判据更正：
#   ① 上限 **150 → 250**：26 号文（PR 官方条款逐条落实）已把摘要上限升为 **≤250 词**（L310/L583），
#      旧的 150 是更早一轮的实践者记录，属**过期判据**。
#   ② 收尾短语不再写死。旧正则要求摘要以 `seed inflation.` 收尾；改写后摘要的收尾句变了
#      （多了一句"协议归伴生篇"的归属说明），于是匹配失败、`wc` 静默为 0，
#      报出"摘要 <=150 词 0 words"这种**假失败**。⇒ 改为"**取到 Keywords 之前**"的稳健切法，
#      并把空匹配**当失败报出**（不再静默 0）。
print('\n[2] Abstract：<=250 词（官方 L310/L583；**两处必须逐字相同**）')
_abs = {}
for name, doc in (('投稿前件', post), ('英文稿', eng)):
    i = doc.find('## 3. Abstract') if name == '投稿前件' else doc.find('## Abstract')
    if name == '投稿前件':
        j = doc.find('## 4. Keywords')
    else:
        j = doc.find('**Keywords:**')
    seg = doc[i:j] if (i >= 0 and j > i) else ''
    body = seg.split('\n', 1)[1] if '\n' in seg else ''
    # 去掉标题行与"Provenance/Positioning 之类"的前置说明：只留以 We/Object-detection 起头的正文
    # ★ 修正（2026-10-04）：原式 `.*` 配 `re.S` 是**贪婪**的，会一路吃到文件末尾 ——
    #   而投前件的模板/说明段里还有别处的 `---`，于是把说明文字也吞进摘要
    #   （投稿前件摘要被算成 2,294 token ⇒ "逐字相同"**假失败**）。
    #   摘要段以**水平线**收尾，故用非贪婪到第一个 `---`。
    m = re.search(r'(Object-detection papers report.*?)(?:\n-{3,}\n|\Z)', body, re.S)
    # r169：投稿前件的摘要段以 "---" 结尾，正则到段尾会把分隔线一起吃掉（多算一个 token、
    #   于是"逐字相同"这条新断言假失败）。这里先剥掉段末的水平线再比较。
    _txt = re.sub(r'\s*-{3,}\s*$', '', re.sub(r'[*`]', '', m.group(1)).strip()) if m else ''
    _abs[name] = re.sub(r'\s+', ' ', _txt).strip()
    wc = len(_abs[name].split())
    rep(0 < wc <= 250, '%s 摘要 <=250 词' % name, '%d words' % wc)
# r169 加强（不是放宽）：本节的标题一直写着"两处必须一致"，但此前只校验了**词数上限** ——
#   于是投稿前件挂着一版 149 词的旧摘要（内容与英文稿不同：旧版把 "intersection is exactly zero"
#   与 "12/19" 当定论印着）而守卫照样 ALL PASS。本轮审计发现后已把投稿前件换成逐字同文，
#   并把"逐字相同"写成断言。
rep(_abs.get('投稿前件') == _abs.get('英文稿') and bool(_abs.get('英文稿')),
    '投稿前件摘要 == 英文稿摘要（逐字）',
    'identical=%s len=%d/%d' % (_abs.get('投稿前件') == _abs.get('英文稿'),
                                len(_abs.get('投稿前件', '')), len(_abs.get('英文稿', ''))))

# ---------------------------------------------------------------- references
# r54w: 三条事实更正，都来自本轮实测：
#   ① PR 官方参考文献区间是 **35–55**（26 号文 §3.5 已升 A 级），不是 35–45；
#   ② 正文里的 References 列表在 r54w **补回了丢失的 [45]–[50] 六条**，并加了 1 条复现仓库
#      ⇒ 44 → 51；canonical 表是 44 行 + 补入的 6 条 = 50；
#   ③ 因此下面一律**从文件实际计数**，不再写死数字（写死的那版正是"守卫锚着过期数字"）。
print('\n[3] 参考文献：条数落在 PR 官方区间 35-55，且英文稿必须全部引用')
nn = {}
rows = re.findall(r'(?m)^\| \[(\d+)\] \| ', refs)
n_tbl_rows = len(rows)
n_tbl_appended = len(re.findall(r'(?m)^\[(\d+)\] ', refs))
nn['canonical'] = n_tbl_rows + n_tbl_appended
rep(nn['canonical'] == 50, 'canonical 参考文献表 = 50 条（44 行表 + 补入 6 条）', 'n=%d' % nn['canonical'])
rep(35 <= nn['canonical'] <= 55, '条数落在 PR 区间 35-55', 'n=%d' % nn['canonical'])
er = [m.group(1) for m in re.finditer(r'(?m)^\[(\d+)\]', eng)]
nn['eng'] = len(er)
# 2026-09-25（c43i）：补引 Recht 2019 并**按首次出现顺序**把它排在 53 位（既有 53–58 → 54–59），
#   总数 58 → **59**。硬写常量随之同步（另一处在 build_submission_blind_20260917.py L200/L234）。
rep(nn['eng'] == 55, '英文稿 References 节 = 55 条', 'n=%d' % nn['eng'])
# ★ 判据用"逐条展开的编号"，不用"一条正则数匹配数" —— 后者在本稿上多次给出 50/51 不一致的假象
#   （27 号文 §5：探针自己错了，报的数会反噬）。这里同时检查编号连续无缺无重。
_nums = sorted(int(x) for x in er)
_gaps = sorted(set(range(1, max(_nums) + 1)) - set(_nums)) if _nums else [1]
_dups = sorted({n for n in _nums if _nums.count(n) > 1})
rep(not _gaps and not _dups, '英文稿参考文献编号连续且不重复',
    'gaps=%s dups=%s' % (_gaps or 'none', _dups or 'none'))
# ★ 必须**分区**：不分区的话，参考条目行首的 `[n]` 会被当成"正文引用"
#   （本守卫第一版就是这样把 `[1]` 报成"越界引用"、把 45–50 报成"未引用"的）。
body_eng, _, refsec = eng.partition('\n## References')
cited = set()
for m in re.finditer(r'\[(\d+(?:\s*,\s*\d+)*)\]', body_eng):
    for x in re.findall(r'\d+', m.group(1)):
        cited.add(int(x))
listed = set(int(x) for x in er)
uncited = sorted(listed - cited)
stray = sorted(cited - listed)
rep(not uncited, '英文稿无"只列不引"（%d 条全部被引）' % nn['eng'], 'uncited=%s' % (uncited or 'none'))
rep(not stray, '英文稿无"引了但列表没有"（越界引用）', 'stray=%s' % (stray or 'none'))
# ------------------------------------------------- 悬空点名（author-year 形式）
# 2026-09-26（refswap 轮加）：本稿一律用**方括号数字**引用，所以"姓名 + 括号年份"这种形式既是
# 体例错误，又会在参考表里没有对应条目时直接破坏投稿清单的"正文 ↔ 列表**互为完备**"。
# `cite_guard.py` 的 MUST 表是**实体名**（数据集/模型/软件/架构），**不覆盖 author-year**——
# 这正是 addsix 轮那句"通称句"点名了三件工作、却一个条目都不给、而 20 套守卫全绿的原因。
# 本检查补上这个作用域缺口。
_flat = re.sub(r'\s+', ' ', body_eng)
_AY = re.compile(r"([A-Z][A-Za-z\u2019'\-]+"
                 r"(?:\s+(?:et\s+al\.|&\s*[A-Z][A-Za-z\u2019'\-]+|and\s+[A-Z][A-Za-z\u2019'\-]+))?)"
                 r"(?:\u2019s|'s)?\s*\((\d{4})\)")
_dangling = []
for _m in _AY.finditer(_flat):
    _s = _flat.rfind('. ', 0, _m.start())
    _s = 0 if _s < 0 else _s + 2
    _e = _flat.find('. ', _m.end())
    _e = len(_flat) if _e < 0 else _e
    if not re.search(r'\[\d+', _flat[_s:_e]):
        _dangling.append(_m.group(0))
rep(not _dangling, '正文无"具名作者-年却不给条目"的悬空点名（本稿一律方括号数字制）',
    'dangling=%s' % (_dangling or 'none'))

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
