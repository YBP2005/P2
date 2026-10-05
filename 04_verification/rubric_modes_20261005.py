# -*- coding: utf-8 -*-
"""盲审评分尺 · **单一来源**（准则 38：三制式 + 0.1 粒度 + 标定带）。

★ 为什么要有这个文件：准则 38 §5.3 与 §7 要求「`维 → 制式` 只有一份定义」，
且**若同一张表存在作者树与交付侧两份，必须断言逐字节相同** —— 手写的两份副本**必然分叉**
（我们自己在 r226 就吃过「同一件事两套数」的亏）。

本模块被两处**机械渲染**：
  * 任务说明 §2 的「(g) 收口评分块（三制式）」；
  * 盲审包 Appendix A 的「A.7 收口评分块（三制式）」。

**满分与档位线一个字都不改**（15/15/15/10/10/15/10/10 = 100；档位线见 A.1 原表）。
"""
import io
import sys

sys.stdout.reconfigure(encoding='utf-8')

# (序号, 名称, 满分, 制式, 额外字段说明)
DIMS = [
    (1, 'Novelty and contribution', 15, 'A', '`credits[]` + `searched{}` + **`to_earn_more[]`**'),
    (2, 'Technical soundness', 15, 'B', '每处非满分四要素'),
    (3, 'Experimental sufficiency', 15, 'C', '**`required[]` 先声明** + `satisfied[]`'),
    (4, 'Evaluation fairness', 10, 'B', '每处非满分四要素'),
    (5, 'Reproducibility', 10, 'B', '每处非满分四要素'),
    (6, 'Appropriateness of metrics', 15, 'B', '每处非满分四要素'),
    (7, 'Statistical significance', 10, 'C', '**`required[]` 先声明** + `satisfied[]`'),
    (8, 'Uncertainty and error analysis', 10, 'C', '**`required[]` 先声明** + `satisfied[]`'),
]
MODE_NAME = {'A': 'A 加分制（从 0 起加）', 'B': 'B 扣分制（从满分扣）', 'C': 'C 分母制（完成度）'}


def maxima():
    return {n: m for n, _, m, _, _ in DIMS}


def mode_of():
    return {n: t for n, _, _, t, _ in DIMS}


def sums():
    out = {'A': 0, 'B': 0, 'C': 0}
    for _n, _name, m, t, _extra in DIMS:      # ★ 下标：0=号 1=名 2=满分 3=制式 4=附加字段
        out[t] += m
    return out


def assert_invariants():
    """不变量：满分不变、总和 100、三制式覆盖全部八维、档位线未动。"""
    assert sum(maxima().values()) == 100, '八维满分之和必须为 100'
    assert len(DIMS) == 8, '必须八维'
    assert set(mode_of().values()) <= {'A', 'B', 'C'}, '制式只能是 A/B/C'
    s = sums()
    assert s['A'] + s['B'] + s['C'] == 100, '三制式求和必须 100'
    # 与历史满分逐位一致（准则 §5.1：满分一律不动）
    HIST = {1: 15, 2: 15, 3: 15, 4: 10, 5: 10, 6: 15, 7: 10, 8: 10}
    assert maxima() == HIST, '满分被改动了！准则 §5.1 禁止'
    # 档位线（准则 §5.1：一律不动）
    BANDS = [(90.0, 100.0, 'Strong accept'), (80.0, 89.9, 'Accept'),
             (70.0, 79.9, 'Minor revision'), (55.0, 69.9, 'Major revision'),
             (0.0, 54.9, 'Reject')]
    assert BANDS[1][:2] == (80.0, 89.9), 'Accept 档线被改动！'
    return True


def render_table():
    L = ['| # | Dimension | Max | **制式** | 你还要额外给出的字段 |', '|---|---|---|---|---|']
    for n, name, m, t, extra in DIMS:
        L.append('| %d | %s | **%d** | **%s** | %s |' % (n, name, m, MODE_NAME[t], extra))
    s = sums()
    L.append('| | **Total** | **100** | A %d + B %d + C %d | |' % (s['A'], s['B'], s['C']))
    return '\n'.join(L)


def render_skeleton():
    """★ **两处共用、必须逐字节相同**的骨架（准则 §7 的双份一致性断言就是断它）。
    含：三制式表 + 0.1 粒度总则 + 制式 A/B/C 三段定义 + 收口块形状。"""
    return '''**八个维度的满分与档位线一个字都不改**（15/15/15/10/10/15/10/10 = 100；档位线见 §A.1）。
改的只是**每一维的记分方向**，按维度性质分三种制式：

@TABLE@

**粒度总则**：**所有维度与总分一律以 `0.1` 为最小刻度**（例 `13.7`、`8.2`、`76.4`）。
**不要**把 0.1 抹掉——档位边界上 0.1 常常决定档位（`85.1` 与 `84.9`）。

#### 制式 A（第 1 维）：加分制

把该维的分数**从 0 加起**，由若干 **credit** 组成；每个 credit 给五件套：

```
credits[]:
  - what:         <创新点，一句话>
    nearest_prior: <最接近的已发表工作 + 出处（作者/年/venue 或 arXiv 号）>
    why_new:      <为什么不是它的组合 / 调参>
    evidence:     <稿内哪一处证据支撑：章节号 / 表号 / 原句>
    points:       <该项分值，0.1 网格，如 +3.5>
searched:
  queries:   <你用过的查询词>
  venues:    <检索的 venue / 库>
  window:    <时间窗>
to_earn_more[]:
  - <要达到更高一档还差什么> ⇒ <可加几分，如 +1.2>
```

* **自洽**：`Σ credits = 该维分数`；**总分那一行仍填八维之和**。
* **反自利条款**：若 `nearest_prior` 在方法上**已经覆盖**了该点 ⇒ **该 credit 不计**（写出来、给 0 分，并说明）。
* ★ **`to_earn_more[]` 是最值钱的一栏**：请把"该补什么、能加几分"写具体（可执行到"改某句/补某表"这一级）。
* **锚点 = 标定带**（**不是**"只能选 0/5/10/15"这种取值集合）：

  | 区间 | 这一带是什么 |
  |---|---|
  | **0–5** | 与已发表工作**无实质差别 → 仅增量式**（已知方法的组合 / 调参） |
  | **5–10** | **有被证据支撑的局部新洞见**（某一轴上的新发现 / 新测量），**但尚未形成新框架** |
  | **10–15** | 提出**被证据支撑的新框架 / 新机制 / 新测量**，**能改变同领域做法** |

  **两条必须同时成立**：① ★ **带内任何 `0.1` 级的值都合法**；分数 = `Σ credits`；**带只用于校准、不限制取值**。
  ② **边界规则**：**左闭右开** `[0,5)` / `[5,10)` / `[10,15]`（顶端 `15` 闭合）；
  若你的分恰好落在边界上，**在 `evidence` 或 `to_earn_more` 里说明一句它归哪一带**。

#### 制式 B（第 2、4、5、6 维）：扣分制

**从该维满分往下扣**。每处**非满分**都要给**四要素**：

1. **扣分算式**：`满分 X − 实得 Y = 扣 Z`（一位小数）；
2. **位置**：章节号 / 表号 / 公式 / 被引原句（**必须能在包内定位**）；
3. **类别**：`WRITING` / `ANALYSIS` / `NEW_RUNS` / `NEW_DATA`；
4. **改后预期**：`after = <该维修好后的分数>`。

**自洽**：`满分 − 该维分数 = Σ 该维扣分`。

#### 制式 C（第 3、7、8 维）：分母制（完成度）

**两步，顺序不能反**：

1. **先声明 `required[]`** —— **先验应做清单**，请在"看这篇做了什么"**之前**写出（**分母不许事后收缩**）；
   每项写清"**做这件事需要什么**"（`ANALYSIS` / `NEW_RUNS` / `NEW_DATA`），这样作者能判断成本。
2. **再逐项判 `satisfied[]`** —— 对 `required[]` 的每一项标 `yes` / `partial` / `no`，并给出**包内位置**。

**得分 = 满分 × (满足项数 / 应做项数)**，其中 `yes` 计 **1.0**、`partial` 计 **0.5**、`no` 计 **0**；
**取整规则写死**：**四舍五入到 `0.1`**（如 `15 × 11.5/14 = 12.3`）。

```
required[]:            # 先写，后看
  R1: <应做项>  (class: ANALYSIS|NEW_RUNS|NEW_DATA)
  R2: ...
satisfied[]:
  R1: yes|partial|no   — 位置：<章节/表/原句>
  R2: ...
score = max × (Σ权重 / |required|)，四舍五入到 0.1
```

#### 收口块的形状（**逐维一行，共 8 行 + Total**）

| Dimension | Score | Max | Deducted | Reason + location | Fix (class) | Score after fix |
|---|---|---|---|---|---|---|
| 1 Novelty and contribution | | **15** | | | | |
| 2 Technical soundness | | **15** | | | | |
| 3 Experimental sufficiency | | **15** | | | | |
| 4 Evaluation fairness | | **10** | | | | |
| 5 Reproducibility | | **10** | | | | |
| 6 Appropriateness of metrics | | **15** | | | | |
| 7 Statistical significance | | **10** | | | | |
| 8 Uncertainty and error analysis | | **10** | | | | |
| **Total** | | **100** | | | | |

**比对用 `round(x, 1)`**：`八维和 == 总分` 请按 `round(…, 1)` 比较（精确相等会因浮点假红）；
`100 − 总分 == 扣分之和` 同理。
'''.replace('@TABLE@', render_table())


def render_block():
    """任务件用：骨架 + 收尾（补字段清单 + 两条总自洽）。"""
    return render_skeleton() + '''
**在收口块之后、`decision by` 之前**，把制式 A 与制式 C 的字段按下面三行补全（**只补这三项**）：

```
credits[] + searched{} + to_earn_more[]   # 第 1 维（制式 A）
required[] + satisfied[]                   # 第 3 维（制式 C）
required[] + satisfied[]                   # 第 7、8 维（制式 C，两维各一套）
```

**仍要满足的两条总自洽**：

* **`总分 = 八个分项之和`**（按 `round(x, 1)` 比较，例如 `13.7 + … = 76.4`）；
  请**不要**另报一个与分项之和不同的总分。
* **`100 − 总分 = 八维扣分之和`**（对不上就写出残差及来源，例如"整体印象另扣 −2.5，不归属单一维度"）。
'''
