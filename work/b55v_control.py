# -*- coding: utf-8 -*-
"""B55 val 半列的**阳性控制 + 网格口径量化**（在 B 机上跑，读 /tmp/b55v_s*.csv + /workspace/runs）。

做三件事：
  1. **阳性控制**：同一检查点、同一 val 切分，重评的 mAP50-95 应等于各 run `results.csv` 同 epoch 的
     `metrics/mAP50-95(B)`；逐族报 |Δ| 的均值/最大/超限计数。
  2. **网格口径量化**：`5 轮网格 argmax` vs `逐 epoch argmax`（后者从 results.csv 全曲线读），把
     「prem_val(grid) ≤ prem_val(true)」从猜测变成**实测的上偏量**。
  3. **mAP75 关键量**：每 run 的 `max_grid mAP75`、`last.pt 的 mAP75`，以及
     `prem_val(grid) = max_grid mAP75 − mAP75(e_f)` —— 这是稿内 val 侧兑现率的分子口径。

同时落一份 tidy 汇总 `/tmp/b55v_summary.csv`（逐 run 一行）供取回。
用法：python b55v_control.py [--glob '/tmp/b55v_s*.csv'] [--root /workspace/runs] [--out /tmp/b55v_summary.csv]
"""
import argparse
import csv
import glob as _g
import io
import os
import statistics as st

FAM = [('shwd2sf', 'base100', 'r10_shwd2sf_base100_3way_s%dn'),
       ('shwd2sf', 'lr005_100ep', 'r10_shwd2sf_lr005_100ep_3way_s%dn'),
       ('smoke2sf', 'base100', 'r10_smoke2sf_base100_3way_s%dn'),
       ('smoke2sf', 'lr005_100ep', 'r10_smoke2sf_lr005_100ep_3way_s%dn')]


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def curve_of(d):
    """results.csv 全曲线 → **按检查点编号**的 {epoch: mAP50-95}。

    ⚠ 实测口径（2026-09-28，B 机，800 个 grid 行判定）：`results.csv` 的 `epoch` 列是 **1-based**，
    而权重文件名 `epoch{N}.pt` 的 N 是 0-based ⇒ `epoch{N}.pt` 对应 results.csv 的第 **N+1** 行。
    判据：|重评 − 曲线[e]| 中位 0.6462 pp vs |重评 − 曲线[e+1]| 中位 **0.0161** pp（724/800 ≤0.05 pp），
    且 742/760 行 curve[e+1] 更近。故此处统一把曲线下标 **减 1**，落到检查点编号上。
    """
    p = os.path.join(d, 'results.csv')
    out = {}
    if not os.path.exists(p):
        return out
    rows = list(csv.DictReader(io.open(p, encoding='utf-8', errors='replace')))
    if not rows:
        return out
    col = next((c for c in rows[0] if c.strip() == 'metrics/mAP50-95(B)'), None)
    for r in rows:
        try:
            out[int(float(r['epoch'])) - 1] = float(r[col]) * 100
        except (TypeError, ValueError, KeyError):
            pass
    return out


def mean(xs):
    xs = [x for x in xs if x is not None]
    return st.mean(xs) if xs else float('nan')


def msd(xs):
    xs = [x for x in xs if x is not None]
    return (st.mean(xs), st.pstdev(xs)) if len(xs) > 1 else ((xs[0] if xs else float('nan')), float('nan'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--glob', default='/tmp/b55v_s*.csv', help='grid+last 的 CSV 通配')
    ap.add_argument('--glob2', default='/tmp/b55v_best_s*.csv', help='best 的 CSV 通配')
    ap.add_argument('--root', default='/workspace/runs')
    ap.add_argument('--out', default='/tmp/b55v_summary.csv')
    a = ap.parse_args()

    rows = []
    files = sorted(set(_g.glob(a.glob)) | set(_g.glob(a.glob2)))
    skipped = []
    for p in files:
        if p.endswith('.done') or p.endswith('.pid'):
            continue
        rd = csv.DictReader(io.open(p, encoding='utf-8', errors='replace'))
        if not rd.fieldnames or 'tag' not in rd.fieldnames or 'epoch' not in rd.fieldnames:
            skipped.append(os.path.basename(p))     # 例如本脚本自己落的 summary.csv
            continue
        for r in rd:
            if r.get('run'):
                rows.append(r)
    print('读入 %d 个 CSV（跳过 %d 个非明细文件：%s），%d 行（grid+last+best）'
          % (len(files) - len(skipped), len(skipped), ','.join(skipped) or '-', len(rows)))

    # 去重：重启时两片可能对同一 (run, epoch, tag) 各写一行 ⇒ 保留首次，并**核对重复行数值一致**
    ded, dup, bad = {}, 0, 0
    for r in rows:
        k = (r['run'], str(r['epoch']), r['tag'])
        if k in ded:
            dup += 1
            if (ded[k].get('map50_95') != r.get('map50_95')) or (ded[k].get('map75') != r.get('map75')):
                bad += 1
                print('   ✗ 重复行数值不一致：%s' % (k,))
        else:
            ded[k] = r
    rows = list(ded.values())
    print('去重后 %d 行；折叠重复 %d 行，其中数值不一致 %d 行' % (len(rows), dup, bad))

    fail = [r for r in rows if str(r.get('map50_95', '')).startswith('FAIL')]
    print('失败行 %d' % len(fail))
    for r in fail[:8]:
        print('   FAIL', r['run'], r['epoch'], r['tag'], str(r.get('map50_95'))[:40])

    grid = [r for r in rows if r['tag'] == 'grid']
    last = {r['run']: r for r in rows if r['tag'] == 'last'}
    best = {r['run']: r for r in rows if r['tag'] == 'best'}
    RUNS = sorted({r['run'] for r in rows})
    CV = {rn: curve_of(os.path.join(a.root, rn)) for rn in RUNS}

    # --- 1. 阳性控制 ---
    print('\n## 1 阳性控制：重评 mAP50-95 vs results.csv（已按 1-based 修正到检查点编号）')
    print('| cell | arm | n | 均值Δ | 中位|Δ| | 最大|Δ| | ≤0.05pp | ≤0.2pp | >1pp |')
    print('|---|---|---|---|---|---|---|---|---|')
    allD = []
    for cell, arm, tpl in FAM:
        ds = []
        for r in grid:
            if r['cell'] != cell or r['arm'] != arm:
                continue
            v = f(r['map50_95'])
            c = CV.get(r['run'], {}).get(int(r['epoch']))
            if v is not None and c is not None:
                ds.append(v - c)
        allD += ds
        if not ds:
            print('| %s | %s | 0 | - | - | - | - | - | - |' % (cell, arm)); continue
        ad = [abs(x) for x in ds]
        print('| %s | %s | %d | %+.4f | %.4f | %.4f | %d/%d | %d/%d | %d |' % (
            cell, arm, len(ds), st.mean(ds), st.median(ad), max(ad),
            sum(1 for x in ad if x <= 0.05), len(ad), sum(1 for x in ad if x <= 0.2), len(ad),
            sum(1 for x in ad if x > 1.0)))
    if allD:
        ad = [abs(x) for x in allD]
        print('\n**合计**：n=%d 均值Δ=%+.4f 中位|Δ|=%.4f 最大|Δ|=%.4f；≤0.05pp %d/%d，≤0.2pp %d/%d，>1pp %d'
              % (len(allD), st.mean(allD), st.median(ad), max(ad),
                 sum(1 for x in ad if x <= 0.05), len(ad),
                 sum(1 for x in ad if x <= 0.2), len(ad), sum(1 for x in ad if x > 1.0)))
        # 若不做 1-based 修正会得到什么（留证：曾把这里当成"控制失败"）
        # 错误配对 = 用 results.csv 原始 epoch 列直接对 epoch{N}.pt，即 CV[e-1]
        wrong = [abs(f(r['map50_95']) - CV.get(r['run'], {}).get(int(r['epoch']) - 1, float('nan')))
                 for r in grid if f(r['map50_95']) is not None]
        wrong = [x for x in wrong if x == x]
        if wrong:
            print('（若**不做** 1-based 修正、拿 results.csv 原始 epoch 列直接对 `epoch{N}.pt`：中位|Δ|=%.4f，'
                  '≤0.05pp %d/%d ⇒ 会把一次完全正常的复现误判为"控制失败"）'
                  % (st.median(wrong), sum(1 for x in wrong if x <= 0.05), len(wrong)))

    # --- 2/3. 逐 run 汇总 ---
    summ = []
    for cell, arm, tpl in FAM:
        for s in range(42, 52):
            run = tpl % s
            g = sorted([r for r in grid if r['run'] == run], key=lambda r: int(r['epoch']))
            lr = last.get(run)
            if not g:
                continue
            cv = CV.get(run, {})
            g_eps = [int(r['epoch']) for r in g]
            g95 = [f(r['map50_95']) for r in g]
            g75 = [f(r['map75']) for r in g]
            ok = [i for i, v in enumerate(g95) if v is not None]
            if not ok:
                continue
            i95 = max(ok, key=lambda i: g95[i])
            ok75 = [i for i, v in enumerate(g75) if v is not None]
            i75 = max(ok75, key=lambda i: g75[i]) if ok75 else None
            t_ep = max(cv, key=lambda e: cv[e]) if cv else None
            # best.pt 的真实 epoch：用「重评 mAP50-95 与全曲线最近邻」反查
            br = best.get(run)
            b_ep, b_res = '', ''
            if br and f(br.get('map50_95')) is not None and cv:
                b_ep = min(cv, key=lambda e: abs(cv[e] - f(br['map50_95'])))
                b_res = '%.4f' % (cv[b_ep] - f(br['map50_95']))
            summ.append(dict(
                run=run, cell=cell, arm=arm, seed=s,
                grid_max_5095='%.4f' % g95[i95], grid_argmax_ep=g_eps[i95],
                true_argmax_ep=t_ep if t_ep is not None else '',
                true_max_5095='%.4f' % cv[t_ep] if t_ep is not None else '',
                grid_minus_true='%.4f' % (g95[i95] - cv[t_ep]) if t_ep is not None else '',
                last_5095=('%.4f' % f(lr['map50_95'])) if lr and f(lr['map50_95']) is not None else '',
                map75_grid_max=('%.4f' % g75[i75]) if i75 is not None else '',
                map75_grid_argmax_ep=g_eps[i75] if i75 is not None else '',
                map75_at_true_argmax_ep=('%.4f' % g75[g_eps.index(t_ep)]) if (t_ep in g_eps and g75[g_eps.index(t_ep)] is not None) else '',
                map75_last=('%.4f' % f(lr['map75'])) if lr and f(lr['map75']) is not None else '',
                map75_best=('%.4f' % f(br['map75'])) if br and f(br['map75']) is not None else '',
                map50_95_best=('%.4f' % f(br['map50_95'])) if br and f(br['map50_95']) is not None else '',
                best_epoch_match=b_ep, best_match_resid=b_res,
                prem_val_best_last=('%.4f' % (f(br['map75']) - f(lr['map75'])))
                if (br and lr and f(br['map75']) is not None and f(lr['map75']) is not None) else '',
                prem_val_grid_75=('%.4f' % (g75[i75] - f(lr['map75']))) if (i75 is not None and lr and f(lr['map75']) is not None) else '',
                prem_true_5095=('%.4f' % (cv[t_ep] - cv[max(cv)])) if cv else '',
                n_grid=len(g_eps), n_ck=len(g_eps) + (1 if lr else 0),
            ))
    if summ:
        with io.open(a.out, 'w', encoding='utf-8', newline='\n') as fh:
            w = csv.DictWriter(fh, fieldnames=list(summ[0].keys()))
            w.writeheader()
            w.writerows(summ)
        print('\n逐 run 汇总 → %s（%d 行）' % (a.out, len(summ)))

    print('\n## 2 网格口径：grid-argmax 比 逐 epoch-argmax 低多少（mAP50-95, val）')
    print('| cell | arm | n | 均值(grid−true) | 最大 | grid argmax=真 argmax 的 run 数 |')
    print('|---|---|---|---|---|---|')
    for cell, arm, tpl in FAM:
        ss = [r for r in summ if r['cell'] == cell and r['arm'] == arm and r['grid_minus_true'] != '']
        d = [f(r['grid_minus_true']) for r in ss]
        same = sum(1 for r in ss if str(r['grid_argmax_ep']) == str(r['true_argmax_ep']))
        print('| %s | %s | %d | %+.4f | %.4f | %d |' % (cell, arm, len(d), mean(d), max(d) if d else float('nan'), same))

    print('\n## 3 mAP75（val 侧，5 轮网格）')
    print('| cell | arm | n | 均值 max_grid mAP75 | 均值 last.pt mAP75 | 均值 prem_val(grid) | prem 范围 |')
    print('|---|---|---|---|---|---|---|')
    for cell, arm, tpl in FAM:
        ss = [r for r in summ if r['cell'] == cell and r['arm'] == arm]
        gm = [f(r['map75_grid_max']) for r in ss]
        lm = [f(r['map75_last']) for r in ss]
        pm = [f(r['prem_val_grid_75']) for r in ss]
        pmv = [x for x in pm if x is not None]
        print('| %s | %s | %d | %.4f | %.4f | %+.4f | [%+.3f, %+.3f] |' % (
            cell, arm, len(ss), mean(gm), mean(lm), mean(pmv),
            min(pmv) if pmv else float('nan'), max(pmv) if pmv else float('nan')))
    print('\n（口径提醒）prem_val(grid) 由 **5 轮网格** 峰值算出 ⇒ 峰值取不满，故它 ≤ 逐 epoch argmax 的 prem_val；'
          '它若作**分母**（兑现率 = prem_test / prem_val），算出的兑现率会**偏高**。与 test 半列同口径。')

    print('\n## 4 best.pt 侧（与 test 半列**同检查点**配对用）')
    print('| cell | arm | n | 均值 best mAP75 | 均值 last mAP75 | 均值 prem_val(best−last) |')
    print('|---|---|---|---|---|---|')
    for cell, arm, tpl in FAM:
        ss = [r for r in summ if r['cell'] == cell and r['arm'] == arm]
        bm = [f(r['map75_best']) for r in ss]
        lm = [f(r['map75_last']) for r in ss]
        pb = [f(r['prem_val_best_last']) for r in ss if r['prem_val_best_last'] != '']
        print('| %s | %s | %d | %.4f | %.4f | %+.4f |' % (cell, arm, len(ss), mean(bm), mean(lm), mean(pb)))

    print('\n## 5 best.pt 的真实 epoch 反查（重评 mAP50-95 与 results.csv 全曲线最近邻）')
    res = [f(r['best_match_resid']) for r in summ if r['best_match_resid'] != '']
    hit = sum(1 for r in summ if r['best_match_resid'] != '' and abs(f(r['best_match_resid'])) <= 0.05)
    eqarg = sum(1 for r in summ if r['best_epoch_match'] != '' and str(r['best_epoch_match']) == str(r['true_argmax_ep']))
    print('| 项 | 值 |')
    print('|---|---|')
    print('| 可反查 run 数 | %d |' % len(res))
    print('| 最近邻残差 中位/最大 | %.4f / %.4f |' % (st.median([abs(x) for x in res]), max([abs(x) for x in res])))
    print('| 残差 ≤0.05 pp（即 best.pt 就是曲线上的某点） | %d/%d |' % (hit, len(res)))
    print('| best.pt 的 epoch == 曲线 argmax 的 run 数 | %d/%d |' % (eqarg, len(res)))
    epc = {}
    for r in summ:
        if r['best_epoch_match'] != '':
            epc[str(r['best_epoch_match'])] = epc.get(str(r['best_epoch_match']), 0) + 1
    print('| best epoch 分布 | %s |' % ', '.join('%s:%d' % kv for kv in sorted(epc.items(), key=lambda x: -x[1])[:8]))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
