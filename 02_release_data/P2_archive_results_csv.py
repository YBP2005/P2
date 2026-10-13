# -*- coding: utf-8 -*-
"""把 70 个新 run 的 results.csv + args.yaml 原件存回本地（防 A 被回收/覆盖）。"""
import importlib.util as u, io, os, sys
sys.stdout.reconfigure(encoding='utf-8')
sp=u.spec_from_file_location('p2', r'E:\workplace\work\p2_pod.py'); P2=u.module_from_spec(sp); sp.loader.exec_module(P2)
CELLS_A=[('fire','base30'),('fire','lr005_30ep'),('mask20','base30'),('mask20','lr005_30ep'),
         ('mende20','base30'),('mende20','lr005_30ep')]
CELLS_B=[('p_d15toai','base100'),('p_d15toai','lr005_100ep'),
         ('p_masktomende','base100'),('p_masktomende','lr005_100ep')]
DST=r'E:\workplace\work\_p2_collect\raw_results'
os.makedirs(DST, exist_ok=True)
got=0
for tag, cells in (('A', CELLS_A), ('B', CELLS_B)):
    cl=P2.connect(tag); sf=cl.open_sftp()
    try:
        for c,a in cells:
            for s in range(45,52):
                run='r10_%s_%s_3way_s%dn'%(c,a,s)
                od=os.path.join(DST, tag, run); os.makedirs(od, exist_ok=True)
                for f in ('results.csv','args.yaml'):
                    try:
                        sf.get('/workspace/runs/%s/%s'%(run,f), os.path.join(od,f)); got+=1
                    except Exception as e:
                        print('缺', tag, run, f, repr(e)[:50])
    finally:
        sf.close(); cl.close()
    print('%s 完成' % tag, flush=True)
print('共取回', got, '个文件 →', DST)
