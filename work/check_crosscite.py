# -*- coding: utf-8 -*-
"""
G12：P1 ↔ P2 互引与口径一致性的机械检查（依据 `互引记录_P1_P2_20260916.md` §6）。

只读：不改任何稿件。每次任一篇改稿后跑一次。
用法：python -X utf8 work/check_crosscite.py        （退出码 0 = 全绿）

检查项（编号沿用互引记录 §6）：
  ① P1 侧 `companion paper` **首次出现**处必须点名主题；且不得裸用 `副论文`/`另一篇`
  ② P2 侧每处内部代号 `P1` 都必须依附于点名主题的说法；且不得裸用 `副论文`/`另一篇`
  ③ [本文件新增，原 §6 未列] 两个头条读数 **+1.434 / +0.507 pp** 在两篇中逐字一致
  ④ 置换下界：两篇出现的下界值必须**数值一致**（允许 0.001953 与 0.0020 两种拼写，|Δ| < 5e-5）
  ⑤ 两篇都引用同一份共享工具清单，且都不把它写成自家方法学
"""
import io, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
P1 = r'D:\deepseek\analysis\M3_draft\00_FULL_DRAFT_v0.4.md'
P1S = r'D:\deepseek\analysis\M3_draft\00_SUPPLEMENTARY_v0.4.md'
P2 = r'E:\workplace\评测有效性稿_正文_v0.1.md'
P2S = r'E:\workplace\P2_补充材料.md'   # P2 补充材料（S6 声明共享工具，⑤b 需读它）

SHARED = ['多模型盲审清单_通用_20260915.md', 'DSH+本地+云端_工作方法指南.md']  # 共享工具（互引记录 §5 末行）
# ⑤b 的形式决定（P2 侧，r30）：**声明 + md5，不附正文**——见补充材料 S6。
# 故 ⑤b 只要求**至少一篇**提到文件名（P2 已在 S6 落实）；P1 侧是否照做由 D 侧决定 → 记为 NOTE。
FLOORS = ['0.25', '0.031', '0.0156', '0.001953', '0.0020']
TOPIC_P1 = r'evaluation validity'
TOPIC_P2 = r'伴生论文|the budgeted fine-tuning study'

results = []      # (项, 结论, 说明)


def load(p):
    if not os.path.exists(p):
        print(f'!! 文件缺失：{p}')
        return None
    return io.open(p, encoding='utf-8', errors='ignore').read()


def add(item, ok, msg):
    results.append((item, ok, msg))
    tag = 'PASS' if ok else ('FAIL' if ok is False else 'NOTE')
    print(f'  [{tag}] {item}：{msg}')


def main():
    p1, p1s, p2, p2s = load(P1), load(P1S), load(P2), load(P2S)
    if p1 is None or p2 is None:
        sys.exit('!! 关键文件缺失，无法检查')

    print('=' * 96)
    print('P1 ↔ P2 互引与口径一致性检查')
    print('=' * 96)
    print(f'  P1 主稿：{P1}  ({len(p1)} 字符)')
    print(f'  P1 补充：{P1S if p1s is None else "有"}')
    print(f'  P2 正文：{P2}  ({len(p2)} 字符)')
    print()

    # ---------- ① P1：首次出现点名主题
    print('① P1 侧 companion paper 的用法')
    hits = [m.start() for m in re.finditer(r'companion paper', p1)]
    if not hits:
        add('①-首现点名', False, 'P1 主稿没有 `companion paper`（互引记录 §1 要求 P1→P2 有 2 处）')
    else:
        first = p1[max(0, hits[0] - 60):hits[0] + 80].replace('\n', ' ')
        ok = bool(re.search(TOPIC_P1, first))
        add('①-首现点名', ok, f'首次出现处 {"含" if ok else "不含"} 主题词 ⇒ …{first.strip()[:90]}…')
        add('①-其后可裸用', None, f'共 {len(hits)} 处；互引记录允许首现之后用 `the companion paper`')
    for w in ['副论文', '另一篇']:
        n = p1.count(w)
        add(f'①-禁裸用 {w}', n == 0, f'P1 主稿含 {n} 处')

    # ---------- ② P2：代号必须依附主题
    print('\n② P2 侧内部代号 P1 的用法')
    # 注意：`互引记录_P1_P2_20260916.md` 这类**文件名**里也有 P1，须排除（前后是 `_`/`-`）
    CODE = r'(?<![A-Za-z0-9_\-])P1(?![0-9A-Za-z_\-])'
    lines = [(k, l) for k, l in enumerate(p2.split('\n'), 1) if re.search(CODE, l)]
    bad = [(k, l) for k, l in lines if not re.search(TOPIC_P2, l)]
    add('②-代号依附主题', not bad,
        f'含 P1 的行 {len(lines)} 行，未点名主题的 {len(bad)} 行' +
        ('；' + '; '.join(f'L{k}' for k, _ in bad) if bad else ''))
    for w in ['副论文', '另一篇']:
        n = p2.count(w)
        add(f'②-禁裸用 {w}', n == 0, f'P2 正文含 {n} 处')
    n13 = len(re.findall(r'(?m)^## 13\. ', p2))
    add('②-§13 已移出正文', n13 == 0, f'正文含 `## 13.` {n13} 处（G5 要求移入内部件）')

    # ---------- ③ 头条读数逐字一致
    print('\n③ 两个头条读数（+1.434 / +0.507 pp）')
    for num in ['1.434', '0.507']:
        pats = [r'\*\*\+' + num + r' pp\*\*', r'\+' + num + r' pp', r'\+' + num]
        got = {}
        for who, txt in (('P1主', p1), ('P1补', p1s or ''), ('P2', p2)):
            forms = set()
            for p in pats:
                for m in re.finditer(p, txt):
                    forms.add(m.group(0))
            got[who] = forms
        ok = bool(got['P1主']) and bool(got['P2'])
        add(f'③-{num} 两篇都有', ok, '；'.join(f'{k}={sorted(v)}' for k, v in got.items() if v))
        if ok:
            # 允许 ** 加粗差异，但数字与单位必须一致
            norm = {k: {v.replace('*', '') for v in vs} for k, vs in got.items()}
            inter = norm['P1主'] & norm['P2']
            add(f'③-{num} 写法一致', bool(inter), f'两篇共有写法：{sorted(inter)}')

    # ---------- ④ 置换下界数值一致
    print('\n④ 置换检验可达下界（按数值比较）')
    def floors(txt):
        out = {}
        for f in FLOORS:
            n = len(re.findall(re.escape(f), txt.replace(',', '')))
            if n:
                out[f] = n
        return out
    f1, f2 = floors(p1 + (p1s or '')), floors(p2)
    add('④-P1 侧下界拼写', None, str(f1) or '（无）')
    add('④-P2 侧下界拼写', None, str(f2))
    v1 = {float(k) for k in f1}
    v2 = {float(k) for k in f2}
    common = {a for a in v1 if any(abs(a - b) < 5e-5 for b in v2)}
    if not v1 or not v2:
        add('④-可比性', False, '至少一侧没有下界值 ⇒ 无法比对（互引记录 §5 的下界表可能只存在于 P2）')
    else:
        add('④-共有下界数值一致', bool(common), f'P1 {sorted(v1)} ∩ P2 {sorted(v2)} = {sorted(common)}（|Δ|<5e-5）')
        spell = ('0.001953' in f2 and '0.0020' in f2)
        add('④-同一值两种拼写', None if spell else True,
            'P2 同时使用 0.001953 与 0.0020（= 2/2¹⁰，同一个下界）⇒ **必须按数值比较**，不能按字符串比较'
            if spell else 'P2 只用一种拼写')

    # ---------- ⑤ 共享工具
    print('\n⑤ 共享工具（多模型盲审清单 / DSH 工作法）')
    # ⑤a：共享工具"概念"是否在场（不要求出现内部文件名——那是投稿形式问题）
    CONCEPT = r'(?i)(multi-model|blinded external model-review|多模型|模型核对|model-review layer)'
    for who, txt in (('P1主', p1), ('P1补', p1s or ''), ('P2', p2)):
        n = len(re.findall(CONCEPT, txt))
        add(f'⑤a-{who} 共享工具概念在场', n > 0, f'命中 {n} 处')
    # ⑤b：形式已定（P2 侧 r30）＝"声明 + md5，不附正文"。P2 在补充材料 S6 落实；
    #      P1 侧是否照做仍待 D 侧 → 该侧记 NOTE。
    for who, txt in (('P1主', p1), ('P1补', p1s or ''), ('P2(正文+补充)', p2 + '\n' + (p2s or ''))):
        got = {s: len(re.findall(re.escape(s), txt)) for s in SHARED}
        n_any = sum(got.values())
        add(f'⑤b-{who} 引用内部清单文件名', True if n_any else None,
            '；'.join(f'{s}×{n}' for s, n in got.items()) +
            ('　⇒ 已引' if n_any else '　⇒ 未引；**P1 侧待 D 侧按同一形式落实**（P2 已在补充材料 S6 给出文件名与 md5）'))
    for who, txt in (('P1主', p1), ('P2', p2)):
        claim = re.findall(r'(?i)(our (own )?(multi-model|blinded)[^.]{0,40}(method|methodolog|protocol))', txt)
        add(f'⑤-{who} 未把共享工具写成自家方法学', not claim,
            ('命中：' + str(claim[:2])) if claim else '未发现"自家方法学"式表述')

    # ---------- ⑥ G3 边界（谁拥有溢价派生主张）
    # ⑥a 查 **P2**（中文稿）：用中文表述与配对差值，不用英文短语。
    # ⑥b 查 **P1**：只禁**活引用**；`Relocated by the trim pass … verbatim` 这类搬迁/压缩记录是历史留痕，豁免。
    print('\n⑥ G3 边界：溢价派生主张的归属')
    EXEMPT_LINE = r'Relocated by|verbatim|compression record|supersede'
    def live_count(txt, pat):
        n = 0
        for line in (txt or '').split('\n'):
            if pat in line and not re.search(EXEMPT_LINE, line):
                n += 1
        return n
    P2_OWN = ['基线臂获益更多', '+0.416', '+0.526', '+0.272', '+0.589']
    for pat in P2_OWN:
        n2 = p2.count(pat)
        add(f'⑥a-归属 P2（中文稿）：{pat}', n2 > 0, f'P2 出现 {n2} 次')
    P1_FORBID = ['larger for the baseline arm than for the strategy arm in every cell measured',
                 '+0.79 vs +0.39', '+1.03 vs +0.49', 'understates the arm difference in every cell']
    for pat in P1_FORBID:
        n1 = live_count(p1, pat) + live_count(p1s, pat)
        add(f'⑥b-P1 不得活引用：{pat[:44]}', n1 == 0,
            f'P1 活引用 {n1} 处（搬迁记录里的逐字引用已豁免）')
    for keep in ['+1.76 pp', '+0.54 pp']:
        n = p1.count(keep) + (p1s or '').count(keep)
        add(f'⑥c-P1 保留旧协议对照 {keep}', n > 0, f'出现 {n} 次')
    for keep in ['+1.434', '+0.507']:
        n = p1.count(keep) + (p1s or '').count(keep)
        n2 = p2.count(keep)
        add(f'⑥c-两篇并存且都有 {keep}', n > 0 and n2 > 0, f'P1 {n} 次 / P2 {n2} 次')
    nptr = len(re.findall(r'companion paper on evaluation validity', p1 + (p1s or '')))
    add('⑥d-P1 指向伴生论文（正文+补充）', nptr >= 2, f'出现 {nptr} 处（正文与补充各应至少 1）')

    # ---------- 汇总
    fails = [r for r in results if r[1] is False]
    notes = [r for r in results if r[1] is None]
    print()
    print('=' * 96)
    print(f'检查项 {len(results)}｜PASS {len(results) - len(fails) - len(notes)}｜FAIL {len(fails)}｜NOTE {len(notes)}')
    if fails:
        print('FAIL 明细：')
        for it, _, m in fails:
            print(f'   · {it}：{m}')
    print('全部通过' if not fails else '有 FAIL（见上）')
    return 0 if not fails else 1


if __name__ == '__main__':
    sys.exit(main())
