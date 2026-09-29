# -*- coding: utf-8 -*-
"""r54w：按 27 号文 §3 给"官方几何分页实测"加**阳性对照**（唯一写 measurement.json 的地方）。

为什么必须加：27 号文 §3 记了一条实测教训——**注入量要够大**。他们用 240 词注入，
在页界附近出现 `responded=False`（+240 词 37→37），**把一次正确的测量判成无效**；
改成 600 词（≈1 页的 2 倍）后稳定 `+600 ⇒ 35→38`。

本脚本的处境与之同构：本稿正好落在 **35 页**这个硬边界上，任何"末页刚好填满/刚好溢出的
微小差异"都会翻转结论。所以"35 页"这个数**必须带阳性对照**才敢写进包与投稿件。

判据（不过即停，且**不写 measurement.json**）：
    positive_control.responded == True      注入 600 词后页数必须变化

输出：work/measurement_official.json（含 inputs 的 md5、各口径页数、阳性对照、诊断）
"""
import hashlib
import io
import json
import os
import re
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'E:\workplace\work')
import importlib.util

W = r'E:\workplace'
OUT = os.path.join(W, 'work', 'measurement_official.json')
SRC = os.path.join(W, 'P2_English_submission_blind_v1.md')
SUP = os.path.join(W, 'P2_Supplementary_English_v0.1.md')

spec = importlib.util.spec_from_file_location(
    'mp', os.path.join(W, 'work', 'measure_pages_pr_official_20260920.py'))
mp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mp)

# 600 词注入块（27 号文 §3 的取值），插在 Declarations 之前（不改任何载荷区）
FILLER = ('Injected control paragraph for measurement validity. ' * 100).strip()
ANCHOR = '\n\n## Declarations'

ORIGINAL = io.open(SRC, encoding='utf-8').read()


def md5f(p):
    return hashlib.md5(io.open(p, 'rb').read()).hexdigest()


def main():
    import win32com.client
    if ANCHOR not in ORIGINAL:
        sys.exit('!! 找不到注入锚 %r —— 结构变了，先修本脚本' % ANCHOR)
    injected = ORIGINAL.replace(ANCHOR, '\n\n' + FILLER + ANCHOR, 1)
    tmp_md = os.path.join(mp.TMP, 'pc_injected.md')
    io.open(tmp_md, 'w', encoding='utf-8', newline='\n').write(injected)

    app = win32com.client.DispatchEx('Word.Application')
    try:
        app.Visible = False
        app.DisplayAlerts = 0
    except Exception:
        pass
    variants = {}
    try:
        print('=' * 92)
        print('官方几何分页实测（唯一写者：本脚本）')
        print('=' * 92)
        for name, pt, sp in (('official_10pt_1.5', 10.0, 1.5), ('variant_12pt_1.5', 12.0, 1.5),
                             ('variant_10pt_2.0', 10.0, 2.0)):
            out = os.path.join(mp.TMP, 'official_%s.docx' % name)
            mp.build(out, pt, sp, (4.3, 4.8, 4.3, 4.8))
            p, w = mp.measure(app, out)
            variants[name] = dict(pages=p, words=w, body_pt=pt, spacing=sp,
                                  margins_cm=[4.3, 4.8, 4.3, 4.8])
            print('  %-18s pages=%-4d words=%-7d' % (name, p, w))

        # ---- 阳性对照：同一几何、注入 600 词 ----
        out = os.path.join(mp.TMP, 'official_positive_control.docx')
        mp.SRC = tmp_md
        try:
            mp.build(out, 10.0, 1.5, (4.3, 4.8, 4.3, 4.8))
        finally:
            mp.SRC = SRC
        cp, cw = mp.measure(app, out)
        before = variants['official_10pt_1.5']['pages']
        ctl = dict(injected_words=len(FILLER.split()), pages_before=before, pages_after=cp,
                   responded=cp != before, geometry='official 10pt/1.5/4.3-4.8cm')
        print('  阳性对照：+%d 词 → %d 页（注入前 %d 页）  responded=%s'
              % (ctl['injected_words'], cp, before, ctl['responded']))
    finally:
        try:
            app.Quit()
        except Exception:
            try:
                app.Application.Quit()
            except Exception:
                pass

    rec = dict(
        measured_at=time.strftime('%Y-%m-%dT%H:%M:%S'),
        inputs=dict(blind_md5=md5f(SRC), sup_md5=md5f(SUP),
                    blind_words=len(ORIGINAL.split())),
        variants=variants,
        official_geometry=('single column | Times New Roman 10 pt text and tables | 1.5 line spacing | '
                           'A4 | margins 4.3/4.8/4.3/4.8 cm (official order = top/right/bottom/left) | '
                           'justified | numbered pages'),
        text_block_cm=dict(width=round(21.0 - 4.8 - 4.8, 2), height=round(29.7 - 4.3 - 4.3, 2)),
        embedded_figures=dict(
            markdown_image_lines=len(re.findall(r'(?m)^!\[', ORIGINAL)),
            note='This article now embeds **four** figures in the body (Fig. 1-4, at 8.6 / 6.1 / '
                 '8.7 / 12) and the remaining two stay in the Supplementary; the count above is '
                 'asserted, not assumed, and the page effect of the four in-text figures is '
                 'measured by the pagination engine rather than estimated.'),
        limit=35,
        positive_control=ctl,
        verdict='IN' if variants['official_10pt_1.5']['pages'] <= 35 else 'OVER',
        note=('27 号文 §3 / 28 号文 §3.3：合规判据必须是分页引擎实测，且实测必须自带阳性对照；'
              '本文件是该项的唯一写者。'),
    )
    if not ctl['responded']:
        print('\n!! 阳性对照未响应 —— 本轮测量**无效**，拒绝写 measurement_official.json')
        print('   （27 号文 §3：240 词版本曾把一次正确的测量判成无效；先加大注入量或查测量路径）')
        return 2
    io.open(OUT, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(rec, ensure_ascii=False, indent=1) + '\n')
    print('\n  判定：官方几何 %d 页 ⇒ **%s**（上限 %d）'
          % (variants['official_10pt_1.5']['pages'], rec['verdict'], 35))
    print('  已写 %s（阳性对照 %s）' % (os.path.basename(OUT), ctl['responded']))
    return 0 if rec['verdict'] == 'IN' else 1


if __name__ == '__main__':
    sys.exit(main())
