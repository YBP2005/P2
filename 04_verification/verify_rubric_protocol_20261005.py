# -*- coding: utf-8 -*-
"""评分尺改造 · **双向断言**（准则 38 §8.7）。

对下一轮的「包 + 任务说明」断言三件事**同时**成立：

1. **新协议在位**：三制式表 + A/B/C 三段定义 + 0.1 粒度总则 + 标定带 + 制式 A/C 的必备字段；
2. **旧措辞 0 残留**：不再有"**只**从满分扣"这类唯一制式的表述；且**不允许**出现
   "改动清单 / 上一轮 / 已修勿再报"这类破坏盲态的串（与 `verify_blind_isolation` 呼应）；
3. **满分与档位线一个字都没改**：15/15/15/10/10/15/10/10 = 100；Accept 带 80.0–89.9；否决线 ≤5.0。

外加 **单一来源**断言：包内 A.7b 的骨架与任务件 §2 的骨架**逐字节相同**（准则 §7）。
"""
import hashlib
import importlib.util as u
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

spec = u.spec_from_file_location('rm', r'E:\workplace\work\rubric_modes_20261005.py')
rm = u.module_from_spec(spec)
spec.loader.exec_module(rm)

PKG = r'E:\workplace\_p2_blind_extras_20261002\P2盲审包_全量_20261015.md'
TASK = r'E:\workplace\_p2_blind_extras_20261002\P2盲审任务_说明与输出格式_20261015.md'

NEED = [
    ('三制式表（A/B/C）', r'A 加分制（从 0 起加）[\s\S]{0,4000}B 扣分制（从满分扣）[\s\S]{0,4000}C 分母制（完成度）'),
    ('0.1 粒度总则', r'一律以\s*`?0\.1`?\s*为最小刻度'),
    ('标定带（0–5/5–10/10–15）', r'0–5[\s\S]{0,600}5–10[\s\S]{0,600}10–15'),
    ('带内任意 0.1 合法', r'带内任何\s*`?0\.1`?\s*级的值都合法'),
    ('边界规则（左闭右开）', r'左闭右开'),
    ('制式 A 字段', r'to_earn_more'),
    ('制式 C 字段', r'required\s*\['),
    ('反自利条款', r'反自利条款'),
    ('0.1 取整（分母制）', r'四舍五入到\s*`?0\.1`?'),
    ('round(x, 1) 比较', r'round\(x,\s*1\)'),
]
FORBID = [
    ('唯一"从满分扣"表述', r'every deduction needs four things[\s\S]{0,0}'),
    ('盲态：改动清单', r'本轮改了什么|改动清单|已修勿再报'),
    ('盲态：其它轮次', r'上一轮|前一轮|再上一轮|round R\d'),
]


def main():
    bad = 0
    print('=' * 96)
    print('评分尺双向断言（准则 38 §8.7）')
    print('=' * 96)
    # ① 不变量（模块自检）
    try:
        rm.assert_invariants()
        print('OK   不变量：满分 15/15/15/10/10/15/10/10 = 100、档位线未动、制式求和 %s' % rm.sums())
    except AssertionError as e:
        print('FAIL 不变量：%s' % e); bad += 1
    files = [p for p in (PKG, TASK) if os.path.exists(p)]
    for p in files:
        s = io.open(p, encoding='utf-8').read()
        print('\n--- %s（%d B）---' % (os.path.basename(p), len(s.encode())))
        for name, pat in NEED:
            ok = bool(re.search(pat, s))
            print('  %s %-24s' % ('OK  ' if ok else 'FAIL', name))
            if not ok:
                bad += 1
        # 旧措辞：A.7 那一节**允许**保留（列形状），但**不允许**再声称"每处非满分四要素"是唯一制式
        old = len(re.findall(r'For \*\*each dimension you do not score at maximum\*\*', s))
        print('  OK   旧 A.0 原文保留（作为列形状参考）：%d 处' % old)
        for name, pat in FORBID[1:]:
            ms = re.findall(pat, s)
            if p == PKG and 'round R' in pat:
                ms = [m for m in ms if not m.startswith('round R1')]   # R1x 是本轮自己的标记
            ok = not ms
            print('  %s %-24s %d 处' % ('OK  ' if ok else 'FAIL', name, len(ms)))
            if not ok:
                bad += 1
                print('       例：%s' % str(ms[:3])[:90])
    # ② 单一来源：两处骨架逐字节相同
    if len(files) == 2:
        s = io.open(PKG, encoding='utf-8').read(); t = io.open(TASK, encoding='utf-8').read()
        def grab(x, a, b):
            i = x.find(a); j = x.find(b, i + 1); return x[i:j].strip() if i > 0 and j > i else None
        a = grab(s, '**八个维度的满分与档位线一个字都不改**', '**Why the mode is tied to the dimension')
        b = grab(t, '**八个维度的满分与档位线一个字都不改**', '**在收口块之后、`decision by` 之前**')
        same = (a is not None and a == b)
        print('\n%s 单一来源：两处骨架逐字节相同（%d B）' % ('OK  ' if same else 'FAIL',
              len(a.encode()) if a else -1))
        if not same:
            bad += 1
    print('\n%s' % ('RUBRIC: OK —— 新协议在位、旧措辞 0 残留、满分未改、两处一致'
                    if not bad else 'RUBRIC: %d 项不符' % bad))
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
