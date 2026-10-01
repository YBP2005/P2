# -*- coding: utf-8 -*-
"""复核入口 ④：校验本次从 B 机拉回的产物的 sha256 与字节数（应当全部一致）。

用法：python -X utf8 work/verify_pulled.py [目录]
默认目录：E:\\workplace\\xeval_20260916
"""
import hashlib, io, os, sys

sys.stdout.reconfigure(encoding='utf-8')
# r154：不再把作者机路径当默认。根解析：P2_ROOT -> 包根（含 01_paper/ 的那一层）-> 作者树；
# 默认再指向包内随件 02_release_data/xeval_20260916（论文 §S7 入口① 用的那份）。
_PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_AUTHOR = r'E:\workplace'
_ROOT = os.environ.get('P2_ROOT') or (_PKG if os.path.isdir(os.path.join(_PKG, '01_paper')) else _AUTHOR)
_DEF = os.path.join(_ROOT, '02_release_data', 'xeval_20260916')
d = sys.argv[1] if len(sys.argv) > 1 else (_DEF if os.path.isdir(_DEF) else os.path.join(_AUTHOR, 'xeval_20260916'))
sp = os.path.join(d, 'SHA256SUMS.txt')
if not os.path.exists(sp):
    print('!! 找不到 %s' % sp)
    print('   本入口校验**从远端拉回的产物目录**里的 SHA256SUMS.txt；')
    print('   论文 §S7 入口① 用的 xeval_20260916/ 随包发布在 02_release_data/xeval_20260916/，')
    print('   入口④ 的 _xframe/ 属**未放行的作者侧输入**（远端机中间目录），从本包单跑时不会存在。')
    print('   用法：python work/verify_pulled.py <拉回的目录>')
    sys.exit(2)

n = bad = 0
miss = []
for line in io.open(sp, encoding='utf-8'):
    if not line.strip():
        continue
    # 两种清单格式都支持：
    #   A) "<sha256>  <bytes>  <rel>"                （xeval_20260916）
    #   B) "<sha256>  <bytes>  <rel>\t<url>"          （_xframe，带来源 URL）
    head = line.strip().split('\t')[0]
    f = head.split()
    if len(f) != 3:
        continue
    h, size, rel = f[0], int(f[1]), f[2]
    p = os.path.join(d, rel.replace('/', os.sep))
    n += 1
    if not os.path.exists(p):
        miss.append(rel); bad += 1; continue
    raw = io.open(p, 'rb').read()
    if hashlib.sha256(raw).hexdigest() != h or len(raw) != size:
        print('  BAD       %s' % rel); bad += 1

print('目录：%s' % d)
print('记录 %d 条；不一致 %d 条%s' % (n, bad, ('；缺失：' + ', '.join(miss[:5])) if miss else ''))
print('全部一致 ok' if bad == 0 else 'FAIL：有 %d 条不一致' % bad)
sys.exit(0 if bad == 0 else 1)
