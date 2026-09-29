# -*- coding: utf-8 -*-
"""复核入口 ④：校验本次从 B 机拉回的产物的 sha256 与字节数（应当全部一致）。

用法：python -X utf8 work/verify_pulled.py [目录]
默认目录：E:\\workplace\\xeval_20260916
"""
import hashlib, io, os, sys

sys.stdout.reconfigure(encoding='utf-8')
d = sys.argv[1] if len(sys.argv) > 1 else r'E:\workplace\xeval_20260916'
sp = os.path.join(d, 'SHA256SUMS.txt')
if not os.path.exists(sp):
    sys.exit(f'!! 找不到 {sp}')

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
