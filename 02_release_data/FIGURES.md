# 图的数据来源与解析值（审计用）

- `xeval_analysis_20260916.txt` (md5 8b74b2eb6228)

## Fig.1 分解（解析自分解表）
- shwd2sf: Δgap=+0.779 = 难度差 +0.759 + 选点乐观 +0.020（校验 +0.779）
- smoke2sf: Δgap=+0.461 = 难度差 +1.041 + 选点乐观 -0.580（校验 +0.461）

## Fig.2 兑现率（解析自兑现率表）
- aitod20/base (n=1): prem_val=0.786 pp, prem_test=-0.377 pp, 兑现率=-48%
- shwd2sf/base (n=10): prem_val=1.469 pp, prem_test=0.735 pp, 兑现率=50%
- shwd2sf/strat (n=10): prem_val=0.865 pp, prem_test=0.151 pp, 兑现率=18%
- smoke2sf/base (n=10): prem_val=0.691 pp, prem_test=0.507 pp, 兑现率=73%
- smoke2sf/strat (n=10): prem_val=0.605 pp, prem_test=-0.158 pp, 兑现率=-26%
- 合计：prem_val 均值 +0.883 pp → prem_test 均值 +0.172 pp，兑现率 19%

## Fig.3 四单位（源 `split_units_recompute_20260916.txt`，md5 dedf9e1b828d）
- release: 10/19
- protocol: 13/19
- yolo_dist: 4/19
- reported: 12/19

## Fig.4 公开日志溢价（解析自正文 §5.5 分布行，n=20）
- 值：[0.0, 0.0, 0.1, 0.14, 0.16, 0.31, 0.57, 0.7, 0.74, 0.91, 1.18, 1.33, 1.42, 1.54, 1.55, 2.07, 2.16, 2.36, 2.84, 5.65]
- 中位 1.045 pp；最大 5.65；正例 18/20
