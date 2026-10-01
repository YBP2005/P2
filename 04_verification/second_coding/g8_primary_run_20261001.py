# -*- coding: utf-8 -*-
"""r163（D32）：把第 3 轮的 **primary 映射**读数落成随包发布件，并证明随包那份是哪一版。

缺陷 D32：补充材料第 3 轮印的 per-coder κ 区间（0.105-0.325，median 0.308）出自 **primary 映射**的跑批，
而随包的 `kappa_g8_20260929.txt` 是 `--sens` 变体（首行自名"敏感性变体"，值 0.063-0.278 / median 0.260），
README 又没标这个 caveat，第 3 轮的回执（v1）也不在包内。

本脚本做两件事（都不改稿件）：
  1. 用**同一条脚本**（`kappa_g8_20260929.py`）在**第 3 轮 v1 回执**上重跑 **primary**；
  2. 同一条脚本跑 `--sens`，与随包那份**逐行核对**（证明随包那份确实是敏感性变体）。

跑法：`kappa_g8_20260929.py` 现在支持 `G8_SUP` / `G8_RET` / `G8_OUT` 三个环境变量做路径覆盖，
所以这里**不做源码改写**，只设环境变量后调用同一条脚本 —— 复算链因此是"一条脚本 + 一组输入"。

**路径解析**（同 `work/item2_final_v2_20260925.py`，包内可跑）：`P2_ROOT` 优先，否则从本脚本位置向上找
带 `01_paper/` 的包根，再退到作者树；v1 回执与随包敏感性件优先"与本脚本同目录"（包内布局）。

用法： python -X utf8 g8_primary_run_20261001.py [--apply]
"""
import io
import os
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
W_AUTHOR = r'E:\workplace'
APPLY = '--apply' in sys.argv


def find_root():
    cands = [os.environ.get('P2_ROOT'),
             os.path.dirname(HERE), os.path.dirname(os.path.dirname(HERE)), W_AUTHOR]
    for c in cands:
        if c and os.path.isdir(os.path.join(c, '01_paper')):
            return c
    return W_AUTHOR


ROOT = find_root()


def pick(*rels):
    """包内布局优先（与本脚本同目录），否则按作者树相对路径。"""
    for rel in rels:
        p = os.path.join(HERE, rel)
        if os.path.exists(p):
            return p
    for rel in rels:
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            return p
    return None


def find_ret():
    """第 3 轮 v1 回执所在目录：作者树在 `returns_v1/`，包内则**以 `v1_` 前缀平铺在第二编码目录里**。"""
    for d in (os.path.join(HERE, 'returns_v1'),
              os.path.join(ROOT, '盲审归档', '编码_G8_20260929', 'returns_v1'),
              HERE, os.path.join(ROOT, 'work')):
        if not os.path.isdir(d):
            continue
        fs = [f for f in os.listdir(d)
              if 'G8_coding_' in f and f.endswith('_20260929.md') and '_v2_' not in f]
        if fs:
            return d
    return None


KAPPA = pick('kappa_g8_20260929.py', os.path.join('work', 'kappa_g8_20260929.py'))
RET_V1 = find_ret()
SUP = pick(os.path.join('01_paper', 'P2_Supplementary_English_v0.1.md'),
           'P2_Supplementary_English_v0.1.md')
SENS_SHIPPED = pick('kappa_g8_20260929.txt', os.path.join('work', 'kappa_g8_20260929.txt'))


def run(out_path, sens):
    env = dict(os.environ, G8_OUT=out_path)
    if SUP:
        env['G8_SUP'] = SUP
    if RET_V1:
        env['G8_RET'] = RET_V1
    cmd = [sys.executable, '-X', 'utf8', KAPPA] + (['--sens'] if sens else [])
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', env=env)
    if r.returncode != 0:
        print((r.stdout or '')[-1500:]); print((r.stderr or '')[-1500:])
        sys.exit('!! 变体跑批失败：%s' % out_path)
    return [l for l in (r.stdout or '').splitlines() if '中位' in l or 'overall κ' in l]


def main():
    if not (KAPPA and RET_V1 and SUP and SENS_SHIPPED):
        sys.exit('!! 缺件：KAPPA=%s RET=%s SUP=%s SENS=%s' % (KAPPA, RET_V1, SUP, SENS_SHIPPED))
    print('  包根 = %s' % ROOT)
    print('  判读脚本 = %s' % KAPPA)
    print('  v1 回执 = %s（%d 份）'
          % (RET_V1, len([f for f in os.listdir(RET_V1) if 'G8_coding_' in f and '_v2_' not in f])))
    print('  已印标记来源 = %s' % SUP)
    out = os.path.join(tempfile.mkdtemp(prefix='g8kappa_'), 'out.txt')
    print('  --- primary 映射 ---')
    for l in run(out, False):
        print('    ' + l)
    pri = io.open(out, encoding='utf-8').read()
    print('  --- --sens 变体 ---')
    for l in run(out, True):
        print('    ' + l)
    sen = io.open(out, encoding='utf-8').read()
    shipped = io.open(SENS_SHIPPED, encoding='utf-8').read()

    ok_primary = '0.105' in pri and '0.325' in pri and '中位 0.308' in pri
    same = sen.strip() == shipped.strip()
    print('\n  primary 含 0.105-0.325 / 中位 0.308：%s' % ok_primary)
    print('  --sens 变体与随包 %s 逐行相同：%s' % (os.path.basename(SENS_SHIPPED), same))
    if not ok_primary:
        sys.exit('!! primary 读数与稿件印的区间不符 —— 停手')
    if not same:
        sys.exit('!! --sens 与随包件不同 —— "随包那份是敏感性变体"就不成立，停手')
    if not APPLY:
        print('\n[dry-run] 未写盘（上面就是两份读数）。')
        return 0
    dest = os.path.join(HERE, 'kappa_g8_primary_20261001.txt')
    if os.path.basename(HERE) != 'work':
        print('\n包内运行：判读与核对已完成；不写回（该目录是发布件本身）。')
        return 0
    io.open(dest, 'w', encoding='utf-8', newline='\n').write(pri)
    print('\n已写 %s' % dest)
    return 0


sys.exit(main())
