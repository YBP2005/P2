# 独立编码任务（v4.6 · 终版）：19 个目标检测基准的「切分计数单元」判定

**你要做的事**：对 **19 个基准 × 4 个计数单元 = 76 格**，各判一个取值（**七选一**），
并为**每一格**给出逐字锚点作为理由。

**四个计数单元**：`release` · `protocol` · `yolo_dist` · `reported`

**取值分两套**：
* **`release` 列（九值，与作者同名）**：`n_a` · `no_yaml` · `no_split` · `no_val` · `no_test` · `alias` · `independent_test` · `test_gated` · `contradictory`
* **`protocol` 列（七值）**：`no_split` · `no_val` · `no_test` · `alias` · `independent_test` · `test_gated` · `contradictory`
* **`yolo_dist` / `reported` 列（七值）**：`independent` · `alias` · `absent` · `gated` · `unknown` · `not_recorded` · **`blocked`（受阻）**

**铁律三条**
1. **只看本文件里的证据卡。** 卡片就是全部依据；卡片里没有的，**不许**用你的记忆、常识或联网补。
2. **每一格都要 reason**，且必须含 **判定树命中的步号** + **卡片里的逐字锚点（带行号/字符偏移）**。四格不许复用同一句。
3. **`not_recorded` 与 `blocked` 都有门槛**（见第一部分 §3 与 §6·F5）：
   * `not_recorded` = **主证据件没有**（且无可推导替代证据、判定树每一步都无法评估）——三条全真才可用；
   * `blocked` = **有主证据件、但判定树卡在某一步**（该步证据不足，既不能判真也不能判假）。
   二者**不可混用**；用错会被复核打回。


---

# 第一部分 · 判定程序（先读这一部分，再动卡片）

# v4.3 判定程序（19 目标检测基准 × 4 计数单元 × **7 取值**）

> **本文件是 v4 的"规则部分"**，与 `v4 · 任务书` 配套。目的：让 **19×4 = 76 格每一格都有唯一判定**，
> 或者有一个**明写的、可复核的理由**说明为何只能判 `not_recorded`。
>
> **v3 的失败教训**：上一轮十家编码者在 190 个 `reported` 格里判出 **189 格 `not_recorded`**。
> 原因不是编码者不用心，而是 Rules 只给了**含义**、没给**判定程序**：`reported` 的"证据面"没有界定，
> 且 `not_recorded` 没有触发门槛 ⇒ 变成万能兜底。**v4 用下面的规则把这两点钉死。**

---

### 0 三条总则（先读）

1. **只看发到你的证据卡。** 每行的证据卡就是该行的**全部依据**；卡片里没有的，一律不许从记忆或外部知识补。
2. **每格独立判定。** 同一行四格允许不一致，也允许"四格各自不同"，这是设计的一部分。
3. **不确定时按"最低可判"走**，而不是一律 `not_recorded`：
   **先试 §2 的判定树；只有当判定树的全部条件都无法评估时，才可判 `not_recorded`**（见 §3 门槛）。

---

### 1 七个取值（六值 + `blocked`；**判定式定义**，不是"含义"）

> **注**：§1.2 的映射表只覆盖**六值**。第七值 `blocked` 的定义与用法见 **§6 · F5**（口径 A）。

每一格的判定分两步：**先算三个布尔量**，再由 §1.2 的**映射表**落值。

### 1.1 三个布尔量

| 量名 | 它问什么 | 判"真"的最低证据 |
|---|---|---|
| **`HAS`** | 该单元下**存在一个 test 层**（目录/键/文件/官方声明的测试集） | 卡片里能指到 test 件／`test:` 键／协议声明的测试集 |
| **`SEP`** | 该 test 层**可分离**：它与**检查点选择所用的那一半**（通常 `val`）**不是同一批数据** | 两条路径/两个文件/两组集合名**不同**；或官方明说二者不相交 |
| **`LOCAL`** | 该 test 的评测**可在本地完成**（GT 可见 + 有评测脚本），**无需**提交服务器/申请/标注被扣留 | 卡片给出评测命令且 GT 可取；反面：要求 `submit`/leaderboard/标注不公开 |

> **`HAS=false` 有两种子情形，必须分清**（v3 的最大混淆源）：
> * **`HAS_false_explicit`**：卡片**主动显示"这一层没有"**（如"该 yaml 只有 `train`/`val` 两键"、"there is no test split"）。
> * **`HAS_false_absent`**：卡片**压根没提**这一层（没有清单、没有键、没有声明）。
> 前者 ⇒ `absent`；后者 ⇒ `not_recorded`。

### 1.2 取值映射表（**唯一**落值方式）

| `HAS` | `SEP` | `LOCAL` | ⇒ 取值 |
|---|---|---|---|
| false（**explicit**） | — | — | `absent` |
| false（**absent** = 卡片未提） | — | — | `not_recorded` |
| true | **false** | — | `alias` |
| true | true | **false**（需提交/申请/扣留） | `gated` |
| true | true | **true** | `independent` |
| 任意 | 任意 | 卡片内**两条陈述互相矛盾** | `unknown` |

**由此得到的三条硬边界（v3 最常混）**
* `absent` 只在 **`HAS=false` 且卡片主动显示"没有"** 时成立；卡片未提 ⇒ `not_recorded`。
* `alias` **不需要**问 `LOCAL`（同批数据时"能不能本地评"无意义）。
* `unknown` **不是**"我不确定"，而是"卡片里有**两条**可逐字指出的**矛盾**陈述"。

---

### 2 判定树（逐单元；**按顺序**执行，第一个命中的即答案）

### 2.1 `release` —— 基准**自己发布**的切分件

> 证据面：**该基准的发布物**（官方压缩包目录布局、官方 API/文件清单、发布说明）。
> **不看**任何第三方镜像 yaml（那是 `yolo_dist` 的证据面）。

1. 卡片给出发布物的**目录/文件清单**：是否存在一个**独立命名的 test 件**（如 `test2017/`、`Test/`、`test.txt`）？
   * **否** ⇒ `absent`（卡片必须显示清单里只有 train/val 之类）→ 停。
   * **是** ⇒ 继续 2。
2. 该 test 件与**选择用的那一半**是否同一批数据（同路径/同集合）？
   * **是** ⇒ `alias` → 停。
   * **否** ⇒ 继续 3。
3. 发布物是否**同时**提供了"如何本地评测"（评测脚本 + GT 可见）？或明确要求**提交服务器/标注扣留**？
   * 本地可评 ⇒ `independent` → 停。
   * 需提交/扣留 ⇒ `gated` → 停。
   * 卡片都没提 ⇒ 回到 1/2 的结论若已定就落值；否则 **`not_recorded`**。
4. 若卡片**自相矛盾**（如 README 一处说发布 test、另一处说不发布）⇒ `unknown` → 停。

### 2.2 `protocol` —— **官方协议**声明的那个测试，能否本地自评

> 证据面：**论文/官方 repo 里规定的评测协议**（提交方式、leaderboard、标注是否公开）。

1. 官方协议是否声明了一个**测试集**？
   * **否**（协议只用 val，或没有官方 test）⇒ `absent` → 停。
   * **是** ⇒ 继续 2。
2. 协议中的测试集是否**就是**选择所用那一半（同集合）？⇒ `alias` → 停；否则继续 3。
3. 协议是否要求**提交到服务器**（leaderboard / codalab / 官方评测服务），或**标注被扣留**、或"需申请"？⇒ `gated` → 停。
4. 协议是否给出**可本地运行的评测**（公开 GT + 脚本）⇒ `independent` → 停。
5. 协议文本在卡片里**互相矛盾** ⇒ `unknown`；**未提及** ⇒ `not_recorded`。

### 2.3 `yolo_dist` —— 拿**通用 YOLO 发行包**起来就用的实践者

> 证据面：**该发行包（Ultralytics/YOLOv5 等）的 `*.yaml` 配置 + 该 yaml 的官方文档页**。
> **这是唯一用 yaml 的单元**（与 `release` 的证据面**不重合**）。看 yaml 里 `train:` / `val:` / `test:` 三个键。

1. yaml 里**有没有 `test:` 键**？
   * **无，且卡片给出了该 yaml 的键清单（能看出只有 `train`/`val`）** ⇒ `HAS=false(explicit)` ⇒ **`absent`** → 停。
     （注：本单元下"没有 `test:` 键"就是**这一层不存在**，不是 `unknown`。）
   * **无，且卡片压根没给该 yaml** ⇒ `HAS=false(absent)` ⇒ **`not_recorded`** → 停。
   * **有** ⇒ `HAS=true`，继续 2。
2. `test:` 与 `val:` 是否**指到同一路径/同一文件**（或官方文档说二者同源）？
   * **是** ⇒ `SEP=false` ⇒ **`alias`** → 停。
   * **否** ⇒ `SEP=true`，继续 3。
3. 该 yaml 的官方文档页是否说明 `test:` 需**下载额外数据后本地评**？⇒ `LOCAL=true` ⇒ **`independent`** → 停。
   是否说明需**提交评测**（如 COCO `test-dev` 要提交）或数据**不可得**？⇒ `LOCAL=false` ⇒ **`gated`** → 停。
4. 卡片里同一 yaml 的 `test:` 键**前后不一致**（两处指向不同文件）⇒ `unknown`。

### 2.4 `reported` —— **实际出现的那个数**是在哪一半上产生的

> **v4 把证据面钉死**：只看卡片里**指定的那一个署名工件**（该基准的官方论文/官方 repo 的 README 或评测脚本），
> **不再接受**"社区引用""大家通常"这类开放面。卡片必须写明是**哪个文件的哪几行**。

1. 卡片是否给出了**产生该基准报告数字的那条命令/那一节**（例如 `val.py --data X.yaml --split test`、或论文 §Experiments 里"we report on the test set"）？
   * **无** ⇒ `not_recorded`（**这是唯一允许 not_recorded 的情形**）→ 停。
   * **有** ⇒ 继续 2。
2. 那条命令/那一节**作用在哪一半**？
   * 作用在**与选择相同的一半**（通常是 `val`；或明确"we select the best checkpoint on the same split we report"）⇒ `alias` → 停。
   * 作用在**独立的 test**，且该 test **可本地评** ⇒ `independent` → 停。
   * 作用在**独立的 test**，但需**提交**（如 `test-dev`）⇒ `gated` → 停。
3. 卡片里对"报告在哪一半"有**两条互相矛盾**的陈述 ⇒ `unknown`。
4. `absent` 在 `reported` 下**仅在一种情形**成立：卡片明确显示**该基准没有任何报告数字**（例如它不是一个被报告的基准）。否则不要用 `absent`。

---

### 3 `not_recorded` 的**触发门槛**（v4 新增；必须逐字满足）

> 只有当下面**三条全部为真**时，才可以在该格写 `not_recorded`，并在 `reason` 里**逐条**注明"我检查了哪些位置、都没有"：

1. 卡片**没有**给出该单元证据面上的**主证据件**（`release`→发布物清单；`protocol`→协议文本；
   `yolo_dist`→yaml 键；`reported`→产生报告数字的那条命令/那一节）；
2. 且卡片**没有**给出任何**可推导**该格的替代证据（如目录布局、评测命令、官方声明）；
3. 且按 §2 的判定树，**每一步的条件都无法评估**。

**凡不满足这三条而写 `not_recorded`，该格视为无效**（会被复核打回）。反之，若三条件满足，`not_recorded`
是**正确且必须**的答案 —— 不许为了"填满"而猜 `alias` 或 `independent`。

---

### 4 reason 字段的**最低内容**（每一格都要）

```
ROW <n> | <benchmark> | release=<v> | protocol=<v> | yolo_dist=<v> | reported=<v> |
  release_reason: <判定树命中第几步 + 卡片里的逐字锚点（含行号）>
  protocol_reason: <同上>
  yolo_dist_reason: <同上>
  reported_reason: <同上；若 not_recorded，按 §3 逐条注明检查了哪些位置>
```

* 锚点必须**逐字**（引号内原文），并给**行号或 sha256 前缀**；不许"大意如此"。
* 四格各自写 reason，**不许复用同一句**（若确实是同一步，也要分别写出各自命中的证据）。

---

### 5 与上一版的关系

| 项 | v3 | **v4** |
|---|---|---|
| 六值 | 只给**含义** | 给**判定式**（`T`/`S` 两个布尔量） |
| 单元证据面 | 重叠、未界定 | **每个单元钉死一个证据面**（`yolo_dist` 独占 yaml） |
| `reported` | "论文／代码库／社区引用" | **只看卡片指定的署名工件的具体行** |
| `not_recorded` | 无门槛（结果 189/190） | **三条门槛**，不满足即无效 |
| reason | 一句话 | **逐格、逐字锚点 + 判定树步号** |
| 出题端 | 无自检 | **必须先用本判定程序自跑一遍 19×4**（见 `v4 · 就绪自检`） |


---

### 6 五个分叉的**裁定**（作者已拍板，2026-10-08；本节优先于前文任何含糊处）

> 这五条是出题端自检（`03_v4_就绪自检.md`）抓出来的"仍会各判各的"之处。**以下为最终口径，编码者必须照此执行。**

**F1 · yaml 的 `test:` 键"存在但值为空/空注释行" ⇒ `absent`。**
* 依据：**空值等于没有定义该层**。判定树 §2.3 第 1 步据此执行：键在但值为空 ⇒ `HAS=false(explicit)`。
* 受影响行：Objects365、Open Images v7（两行 yaml 的 `test:` 均为空注释行）。

**F2 · "该基准在发行包里根本没有这份 yaml" ⇒ `absent`；"卡片里没给这份 yaml" ⇒ `not_recorded`。**
* 判定依据是**卡片里有没有'该发行包不提供此配置'这一事实**：
  卡片写明"无 `DOTAv2.yaml`（404）"、"官方仓只有 README/utils.py，无 yaml" ⇒ `absent`；
  卡片只是**没贴**这份 yaml、也没说它在不在 ⇒ `not_recorded`。
* 受影响行：DOTA v2、NWPU、MAFA、WIDER FACE、Mendeley、D-Fire（均属前者 ⇒ `absent`）。

**F3 · 官方只发 val、test 隐藏（需提交） ⇒ `gated`。**（**定义选择**，非事实判断，特此注明）
* 理由：`gated` 的字面就是"有留出测试但**不能本地自评**"；xView 的 test 是**存在**的（官方挑战赛用它），
  只是标注不公开、要提交 ⇒ 落在 `gated` 更贴合该取值的设计意图。
* 反之，若某基准**连 test 都不存在**（官方只声明 val、没有测试集）⇒ 那是 `absent`（见 F4）。
* 受影响行：xView（`release` 格）。

**F4 · 官方协议**从不提 test**（既没说有、也没说没有） ⇒ `not_recorded`；
协议**明说"只有 val"/"不发布 test"** ⇒ `absent`。**
* 分界与 F2 同构：**"没有这一层的陈述"**才是 `absent`。
* 受影响行：NWPU VHR-10、SHWD（协议侧均无任何 test 陈述 ⇒ `not_recorded`）。

**F5 · 只判七值（六值 + `受阻`），不必细分。**

* 你要判的是**七个**字面量之一：`independent` · `alias` · `absent` · `gated` · `unknown` · `not_recorded` · **`blocked`**。
* **不要**去区分"是哪种没有"（例如"没有该键"与"没有该层"）—— 那是**出题端在分析阶段**的事。
* 只需保证：**判定树命中了哪一步 + 卡片里哪句逐字原文**支持它。

### ★ `blocked`（受阻）的定义 —— 口径 A（作者已拍板，2026-10-08）

**含义**：判定树**走到了中途**，某一步的条件**既不能判真、也不能判假**（即"有主证据件，但该步所需的证据不足"）。

**为什么需要它**：六值与 §3 门槛之间有缝 ——
* 若**有**主证据件但**不完整**，则 §3 第 1 条不成立 ⇒ **不许**写 `not_recorded`；
* 但判定树又无法落值 ⇒ 六值内**无解**。
这个缝不能靠放宽门槛来填（那会退回"万能兜底"），所以正式设 `blocked` 一档把缝**显式暴露**出来。

**用法与纪律**
1. **能落六值就落六值**；只有在判定树**卡在某一步**时才写 `blocked`。
2. 写 `blocked` 时，`reason` 必须**逐字**给出：
   * **卡在哪一步**（§2.1/§2.2/§2.3/§2.4 的第几步）；
   * **需要有但卡片里没有的那条证据**是什么（一句话点名，例如"缺官方发布物的 test 档清单"）；
   * 你**已经检查过**的 E1/E2/E3/E4 位置。
3. **统计口径（如实告知）**：`blocked` 会**单列为"规则未覆盖格"**，**不计入**编码者之间的一致率；
   它本身是**对任务书的反馈**（指出该补哪一格证据），不会被当成"你判错了"。
4. **不许**用 `blocked` 代替思考：如果某格其实能由判定树落值，写 `blocked` 会被复核打回。


---

### 7 ★ v4.4 **同构版**：`release` 与 `protocol` 的取值与判定树（**本节覆盖 §1.2 与 §2.1/§2.2**）

> **为什么改**：作者的 19×4 标记表里，`release` 列有一条**表里没写**的规则 —— 标 `n_a` 的行
> **既不进"非独立"分子、也不进"不可判"列，只留在 19 行分母里**（补充材料逐字）；且作者把"没有"分成
> `no_test`/`no_val`/`no_split`/`no_yaml`/`n_a` 多种。前几版的六值把这些**压平**，导致作者的
> `release` **10/19**、`protocol` **13/19** 两套计数**无法复现**。本节把这两列改成**与作者同名同构**。

### 7.1 `release` 列：**九个取值**（与作者标记同名）

判定树**按顺序**执行，第一个命中的即答案：

1. **这层给不给"可用的独立 test 制品"？**
   * 该层的切分制品/脚本**根本不提供**独立 test 制品（例如只发 train/val 制品）；
   * **或**虽有 test 制品但**不附带标注**（不构成可用测试）——
   ⇒ **`n_a`**（= *not applicable*，**不是** unknown）→ 停。
2. 该层**连切分配置/清单都不存在**（第一方根本没有这类文件）⇒ **`no_yaml`** → 停。
3. 该层**没有 train/val/test 概念**（其 "split" 指别的东西，如 positive/negative）⇒ **`no_split`** → 停。
4. 该层**没有 val**（无可分离的"选择用那一半"）⇒ **`no_val`** → 停。
5. 该层**明确没有 test**（有 val，但没有 test 制品）⇒ **`no_test`** → 停。
6. 该层的 test 与选择用那一半**是同一批数据** ⇒ **`alias`** → 停。
7. 该层提供独立 test，且**能本地评**（标注可见 + 有评测脚本）⇒ **`independent_test`** → 停。
8. 该层提供独立 test，但**须提交服务器 / 标注扣留**、不能本地评 ⇒ **`test_gated`** → 停。
9. 该层**官方陈述互相矛盾** ⇒ **`contradictory`** → 停。

### 7.2 `protocol` 列：**七个取值**（与作者同名；**不设 `n_a`**）

1. 协议**没有 train/test 概念** ⇒ **`no_split`** → 停。
2. 协议**没有 val**（无可分离的选择半）⇒ **`no_val`** → 停。
3. 协议**明确不设 test** ⇒ **`no_test`** → 停。
4. 协议声明的 test **就是**选择用的那一半 ⇒ **`alias`** → 停。
5. 协议声明独立 test，且**能本地自评** ⇒ **`independent_test`** → 停。
6. 协议声明 test，但**须提交服务器 / 标注扣留** ⇒ **`test_gated`** → 停。
7. 协议文本**互相矛盾** ⇒ **`contradictory`** → 停。
8. 协议文本**既没说有、也没说没有** test ⇒ **`not_recorded`**（§3 门槛仍适用）。

### 7.3 未改动的两列

`yolo_dist` 与 `reported` **沿用前文六值 + `blocked`** 不变（它们本就与作者标记同构）。

### 7.4 `blocked` 仍然可用（七值之外的第七标记）

任一列若**判定树卡在某一步**（有主证据件但该步证据不足）⇒ 写 **`blocked`**，并给"卡在第几步 + 缺哪条证据 + 已检查位置"。

### 7.5 计数（收件端按此复现作者口径）

* `release` 的"非独立"= 该列中 `alias` + `test_gated` + `no_test` + `no_val` + `no_split` + `no_yaml` + `contradictory`（**`n_a` 与 `independent_test` 不计**）；
* `protocol` 的"非独立" = 同上（该列无 `n_a`）；`independent_test` 不计。

---

### 8 ★ 计数口径声明（**本版采用；须全文一致，不得混用**）

`release` 与 `protocol` 两列的判定**依赖一个必须先声明、再全程一致使用的口径**。本版采用 **reported-test 口径**：

> **`release` / `protocol` 问的是：该层是否为"文献实际报告所依据的那个 test 划分"提供公开标注。**

由此有两条必须遵守的推论：

1. **仅有公开且带标注的 `val` 划分，不足以判 `independent_test`。**
   若该层**没有 test 制品** ⇒ 判 **`no_val`**；若**有 test 制品但其标注被扣留或须提交服务器** ⇒ 判 **`test_gated`**。
2. **替代口径（any-held-out 口径）**：若把判据改成"**是否存在任何公开且带标注的留出划分（`val` 计入）**"，
   则部分行会**整列改变取值**，作者表里 `release` 与 `protocol` 两个小计**也会随之改变**。
   **两套口径各自自洽，但混用会同时制造假翻转与假一致。**

**作答要求**：每一行的 `release` reason 里，**用一句话写清你是按哪条口径落的**（例如
"本层有 test 制品但标注扣留 ⇒ reported-test 口径下判 `test_gated`"）。**不得在不同行之间换口径。**

---

### 9 ★ 三种易错情形的**通用裁定规则**（v4.6 新增；与 §7、§8 连用）

以下三条适用于**任何**基准，**不是针对某一行**。凡命中，请在 reason 里**点名你用的是哪一条**。

### 9.1 多层/多变体：**判定"被报告的那一个"，并写明是哪一个**
若该层**同时定义了两个或更多的 test 变体**（例如一个 "dev" 变体与一个 "challenge" 变体，
或一个"已发布"的测试集与一个"托管在评测平台"的挑战集）：
* 按 **§8 的 reported-test 口径**，判**该基准自己的文档指示作者去报告的那一个变体**；
* **不得**把两个变体的性质**混在一格**里（例如"其一有标注、其二无标注"⇒ 不要因此判 `contradictory`，见 §9.3）；
* reason 必须写出 **"本格判的是 <变体名>"**。

### 9.2 `test_gated` 与"根本没有可用 test 制品"的**界线**
* **`test_gated`** 要求：该层**确实存在一个 test 制品**（test 的**图像可下载**），
  只是其**标注被扣留**、或**须提交到评测服务器**才能得分。
* 若该层**连 test 图像都不可下载**（"neither images nor labels … available"），
  则该层**没有可用的 test 制品** ⇒ **不得判 `test_gated`**；
  此时若该层**也没提供一个带标注的留出划分**（例如只发了 val 的图像、没发 val 的标注），判 **`no_val`**；
  若该层**明确不设 test**，判 **`no_test`**。
* **自检句**（写进 reason）：**"test 的图像能不能下载？"** —— 能 ⇒ 才可考虑 `test_gated`；不能 ⇒ 走上一段的三种落值。

### 9.3 `contradictory` 的**触发门槛**（必须逐字满足，否则**不得**判 `contradictory`）
判 `contradictory` **要求**：**同一份官方来源（或同一发布层）把同一个对象描述成两种互不相容的样子**。
典型的**合格**情形：
* 同一个发布层**同时给出两套互斥的切分配置**（例如两个不同的切分目录，其 train/val 名单**互不相同**）；
* 同一个仓里**两处官方文本对"测试标注是否公开"给出相反陈述**；
* 同一个发布物里**某一切分档的标注件为空**，而另一档声称包含该切分。
**不合格**（**不得**据此判 `contradictory`）：
* **两个不同的对象**被不同来源分别描述（例如"dev 变体有标注"与"challenge 变体无标注"——那是 **§9.1** 的情形）；
* 一个来源**没写**、另一个来源写了（那是**证据缺失**，走 `not_recorded` / `blocked`）；
* 一个**第三方**镜像与官方不一致（第三方不算官方来源）。
* **自检句**：**"这两句说的是不是同一个对象？"** —— 不是 ⇒ **不得**判 `contradictory`。

### 9.4 与 `blocked` 的关系
若你觉得 §9.1–§9.3 都不足以决定某一格，**不要**猜一个值 —— 按 §3 判 **`blocked`**，
并在 reason 里写明"**卡在第几步 + 缺哪条证据 + 已检查位置**"。
---

# 第二部分 · 19 张证据卡（每行的全部依据）

> 每张卡按四类证据件组织：**E1** 切分件正文（yaml 的 train/val/test 三行）· **E2** 官方文档段 ·
> **E3** 报告口径出处（"我们在哪个 split 上报告"的命令或论文节）· **E4** 发布物/评测清单。
> **卡里只有证据，没有任何标记。** 标记由你按判定树自己得出。

# v4.3 · 证据卡（19 行）—— **只含逐字证据，不含任何标记**

> **给编码者的使用说明**：每张卡按四类证据件组织。**卡片就是该行的全部依据**，卡里没有的不许补。
> **判定请严格按 `00_v4_判定程序.md` 的判定树**（先算 `HAS`/`SEP`/`LOCAL`，再按 §1.2 映射表落值）。
> 每格的 reason 必须含**判定树步号 + 卡片里的逐字锚点 + 行号**。
>
> **证据件代号**：**E1** 切分件正文 · **E2** 官方文档段 · **E3** 报告口径出处 · **E4** 发布物/评测清单。
> **采集纪律**：全部经 `curl` 直取原文 + `git ls-remote` 取 commit（**未用 GitHub API**）；行号为**原文件自身行号**；
> 采不到的**逐项写 `NOT FOUND`** 并列出查过的位置。**本文件不含任何 mark、不含任何结论。**

---

### 卡 1 · COCO

* **E1 切分件**（`ultralytics/cfg/datasets/coco.yaml` @ `ultralytics/ultralytics@8df35349a376abfcde230dd3868280f5f2ef28c2`）：
  `train: train2017.txt` · `val: val2017.txt` · **`test: test-dev2017.txt`**（三键齐、互不相同）。
* **E2 官方文档**：`cocodataset.org/#detection-eval` 与 guidelines 页给出 `Val ~5K（scores immediate, no leaderboard）` /
  `Test-Dev ~20K（5 submissions per day, leaderboard）`；逐字：**"annotations for train and validation data will be released, but not for test"**。
* **E3 报告口径**（**同页两处互相矛盾，均逐字**）：
  * `dataset/guidelines.htm:26`（2017 段）：**"Results in papers should generally be reported on test-dev…"**
  * `dataset/guidelines.htm:50`（2015 段）：**"in a publication it is not acceptable to report results on test-dev only"**（`:45` 另指向 test-standard）。
* **E4 发布物/评测**：`cocodataset/cocoapi@8c9bcc3cf640524c4c20a9c40e89cb6a2f2fa0e9`；官方另提供 `test-dev` 提交服务。
* **NOT FOUND**：无。

#### R0d 补采证据（AutoDL 公共区 COCO2017 **实物清单**，2026-10-09；只读列举）

* **来源**：`/root/autodl-pub/COCO2017/`（归档 `_p2_missing_evidence_20261008/_from_autodl/p2_probe/pub_inventory2.txt`）。
* **目录逐字**：`annotations_trainval2017.zip`（252,907,541 B）· `test2017.zip`（6,646,970,404 B）·
  `train2017.zip`（19,336,861,798 B）· `val2017.zip`（815,585,330 B）。
* **★ `annotations_trainval2017.zip` 的完整文件清单（逐字，共 6 项）**：
  `annotations/instances_train2017.json` · `annotations/instances_val2017.json` · `annotations/captions_train2017.json` ·
  `annotations/captions_val2017.json` · `annotations/person_keypoints_train2017.json` · `annotations/person_keypoints_val2017.json`。
  **该包含 "test" 的条目数 = 0**（实测 `unzip -l … | grep -ci test` = 0）。
* **★ `test2017.zip` 内只有 `test2017/*.jpg`**（首条 `test2017/000000259564.jpg`）；
  **含 `.json` 或 `annotation` 的条目数 = 0**。
* **⇒ 事实**：官方发布物**给出 test 图像、但不给出 test 标注**（标注包名即 `annotations_trainval`，且包内无 test 项）
  —— 与 "只要提交才能评测 test-dev" 的口径一致；**test 层存在、但本地无法自评**。
* **对照**：`train2017.zip` 与 `val2017.zip` 为图像包，其标注在 `annotations_trainval2017.zip` 内（train/val 均有）。
### 卡 2 · PASCAL VOC

* **E1**（`ultralytics/cfg/datasets/VOC.yaml` @ 同一 commit）：`train`/`val` 均指 `images/train2007`；**`val` 与 `test` 同指 `images/test2007`**
  （论文 §6.1 记录：该 yaml 由一个转换脚本从**单一 `images_dir`** 写出两键）。
* **E2**：官方开发包（`host.robots.ox.ac.uk`）提供 `train/val` 与 `test` 两套，测试标注公开（VOC2007 test 标注随包发布）。
* **E3 报告口径**：官方 leaderboard 页说明"结果提交到 test server"；各方法论文通常报 test。**逐字出处**见 `_e3_e1/e3_rows01_05.md`。
* **E4**：PASCAL VOC 官方**无 git 仓库**；devkit tar 的 sha256 = `6101e33483e1f252821085f4b85634d334c1d44a0a5bc3921cd64320a40bd2cf`。
* **NOT FOUND**：无。

#### R0 补采证据（2026-10-08，逐字）

**[D]** ### 目标格：release

- **采到**（官方发布物清单、2007 test 标注随包发布、test server 之有无、2007 与 2012 的区别，均为逐字/逐包核验）

**A. 官方发布物清单（E4：本轮逐个下载官方包并列出内容）**

1. **VOC2007 官方「开发套件代码+文档」包 = 仅代码/文档，不含任何切分件**
   - 逐字（页面上的下载条目）:「Download the development kit code and documentation (250KB tar file)」| 出处: `http://host.robots.ox.ac.uk/pascal/VOC/voc2007/index.html` | 段: `index.html:327`
   - 逐字（页面上的下载条目）:「Download the training/validation data (450MB tar file)」| 出处: 同页 | 段: `index.html:326`
   - 包本体: `http://host.robots.ox.ac.uk/pascal/VOC/voc2007/VOCdevkit_08-Jun-2007.tar` | 大小 `256,000` bytes | sha256 `f4027a9768d6eef4a7eb958740ac9eda26f52dda2bbd1a8da9ae63083b7f89f8`
   - 该包内容（`tar -tf`，共 41 项）:`VOCdevkit/VOCcode/`（`VOCinit.m`、`VOCevaldet.m`、`VOCevalcls.m`…）、`VOCdevkit/devkit_doc.pdf`、`VOCdevkit/example_*.m`、`VOCdevkit/local/VOC2006/dummy`、`VOCdevkit/local/VOC2007/dummy`、`VOCdevkit/results/VOC2006/Main/dummy`、`VOCdevkit/results/VOC2007/{Main,Layout,Segmentation}/dummy`。**无** `ImageSets/`、`Annotations/`、`JPEGImages/`。
   - 文件/段: 包内清单；重现命令 `tar -tf VOCdevkit_08-Jun-2007.tar`

2. **VOC2007 官方「trainval」包 = 只发布 train / val / trainval 三档，包内无任何 test 项**
   - 包本体: `http://host.robots.ox.ac.uk/pascal/VOC/voc2007/VOCtrainval_06-Nov-2007.tar` | 大小 `460,032,000` bytes（HTTP 头 `Content-Range: bytes 0-0/460032000`）| sha256 `7d8cd951101b0957ddfd7a530bdc8a94f06121cfc1e511bb5937e973020c7508`
   - 该包内容（`tar -tf`，共 10,945 项）:
     - `VOCdevkit/VOC2007/Annotations/*.xml` = **5,011** 个
     - `VOCdevkit/VOC2007/JPEGImages/*.jpg` = **5,011** 个
     - `VOCdevkit/VOC2007/ImageSets/Main/train.txt`（**2,501** 行）、`ImageSets/Main/val.txt`（**2,510** 行）、`ImageSets/Main/trainval.txt`（**5,011** 行）
     - `VOCdevkit/VOC2007/ImageSets/Main/<class>_{train,val,trainval}.txt`（20 类）
     - `VOCdevkit/VOC2007/ImageSets/Segmentation/{train.txt,val.txt,trainval.txt}`
     - `VOCdevkit/VOC2007/SegmentationClass/`、`VOCdevkit/VOC2007/SegmentationObject/*.png` = **422** 个
   - 核验（仅事实）: 对该包 `tar -tf` 输出执行 `grep -i "test"` → **NO ENTRY CONTAINING 'test'**（即该包内不存在 `test.txt`、也不存在任何 test 标注）。
   - 文件/段: 包内清单；重现命令 `tar -tf VOCtrainval_06-Nov-2007.tar | grep -i test`

3. **VOC2007 官方「test」包 = test 标注公开单独发布（两个变体）**
   - 逐字（页面条目）:「Download the annotated test data (430MB tar file)」| 出处: `http://host.robots.ox.ac.uk/pascal/VOC/voc2007/index.html` | 段: `index.html:357`
   - 逐字（页面条目）:「Download the annotation only (12MB tar file, no images)」| 出处: 同页 | 段: `index.html:358`
   - 包本体（annotation-only 变体）: `http://host.robots.ox.ac.uk/pascal/VOC/voc2007/VOCtestnoimgs_06-Nov-2007.tar` | 大小 `12,492,800` bytes | sha256 `ee71b6ec2a2c8a449af661a85207afafd4bf3574521e91208bd757bc69365941`
   - 该包内容（`tar -tf`，共 5,404 项）:
     - `VOCdevkit/VOC2007/Annotations/*.xml` = **4,952** 个（例: `VOCdevkit/VOC2007/Annotations/000001.xml`）
     - `VOCdevkit/VOC2007/ImageSets/Main/test.txt` = **4,952** 行（首行 `000001`，末行 `009963`）
     - `VOCdevkit/VOC2007/ImageSets/Main/<class>_test.txt`（20 类）、`ImageSets/Main/train_test.txt`
     - `VOCdevkit/VOC2007/ImageSets/Layout/test.txt`、`ImageSets/Segmentation/test.txt`
     - `VOCdevkit/VOC2007/SegmentationClass/*.png` = **210** 个
     - 无 `JPEGImages/`（该变体即「no images」）
   - 逐字（该包中一份 test 标注的内容体，证明是完整 bbox 标注而非仅 id 列表）:
     `<annotation>` / `<folder>VOC2007</folder>` / `<filename>000001.jpg</filename>` / `<source>` … `<database>The VOC2007 Database</database>` … `<object>` / `<name>dog</name>` … `<bndbox>` / `<xmin>48</xmin>` / `<ymin>240</ymin>` / `<xmax>195</xmax>` / `<ymax>371</ymax>` / `</bndbox>`
     | 文件: `VOCdevkit/VOC2007/Annotations/000001.xml` | 重现命令 `tar -xOf VOCtestnoimgs_06-Nov-2007.tar VOCdevkit/VOC2007/Annotations/000001.xml`
   - 包本体（含图变体，仅取大小，未下载全量）: `http://host.robots.ox.ac.uk/pascal/VOC/voc2007/VOCtest_06-Nov-2007.tar` | `Content-Range: bytes 0-0/451020800`（=`430.2` MiB，与页面 `430MB` 一致）

4. **官方两阶段发布 + 「test 真值在挑战结束后才发布」的逐字原始声明（E2）**
   - 逐字:「The data will be made available in two stages; in the first stage, a development kit will be released consisting of training and validation data, plus evaluation software (written in MATLAB). One purpose of the validation set is to demonstrate how the evaluation software works ahead of the competition submission.」| 出处: `http://host.robots.ox.ac.uk/pascal/VOC/voc2007/index.html` | 段: `index.html:263-267`（Data 节）
   - 逐字:「In the second stage, the test set will be made available for the actual competition. As in the VOC2006 challenge, no ground truth for the test data will be released until after the challenge is complete.」| 出处: 同页 | 段: `index.html:270-273`
   - 逐字（规模）:「The data has been split into 50% for training/validation and 50% for testing. … In total there are 9,963 images, containing 24,640 annotated objects.」| 出处: 同页 | 段: `index.html:276-280`

5. **官方公告「2007 test 标注已可下载」的逐字（E3，发布会话）**
   - 逐字:「06-Nov-07: The annotated test data is now available to download. If you use the VOC2007 data in a publication, please include the appropriate citation .」| 出处: `http://host.robots.ox.ac.uk/pascal/VOC/voc2007/index.html` | 段: `index.html:70-71`（News 节）
   - 逐字:「11-Jun-07: Test data is now available.」| 出处: 同页 | 段: `index.html:82`
   - 逐字（Test Data 节启动句 + 内容说明）:「The annotated test data for the VOC challenge 2007 is now available:」/「This is a direct replacement for that provided for the challenge but additionally includes full annotation of each test image, and segmentation ground truth for the segmentation taster images.」| 出处: 同页 | 段: `index.html:354`、`index.html:361-362`
   - 逐字（时间表）:「11 June 2007: Test set made available.」| 出处: 同页 | 段: `index.html:424`

6. **官方 devkit 文档中的切分档定义与文件清单（E2/E4，官方 PDF）**
   - 包: `http://host.robots.ox.ac.uk/pascal/VOC/voc2007/devkit_doc_07-Jun-2007.pdf` | 大小 `178,965` bytes | sha256 `0cd0ba27d88dd66643417eac04b21bbe434cf2ed50ece6594438175e83354574` | 23 页；转换命令 `pdftotext -layout devkit_doc_07-Jun-2007.pdf devkit2007.txt`
   - 逐字:「For the main tasks – classification and detection, there are four sets of images provided:」/「train: Training data」/「val: Validation data (suggested). The validation data may be used as additional training data (see below).」/「trainval: The union of train and val.」/「test: Test data. The test set is not provided in the development kit. It will be released in good time before the deadline for submission of results.」| 文件: `devkit2007.txt:171-182`（PDF 第 3 页，§2.1）
   - 逐字:「The VOC2007/ImageSets/Main/ directory contains text files specifying lists of images for the main classification/detection tasks.」/「The files train.txt, val.txt, trainval.txt and test.txt list the image identifiers for the corresponding image sets (training, validation, training+validation and testing).」| 文件: `devkit2007.txt:869-877`（PDF 第 16 页，§8.1.1）
   - 逐字:「The VOC2007/ImageSets/Segmentation/ directory contains text files specifying lists of images for the segmentation taster task.」/「The files train.txt, val.txt, trainval.txt and test.txt list the image identifiers for the corresponding image sets…」| 文件: `devkit2007.txt:939-944`（§8.1.3）
   - 逐字（安装后目录结构）:「VOCdevkit/VOC2007/ImageSets         % image sets」/「VOCdevkit/VOC2007/Annotations       % annotation files」/「VOCdevkit/VOC2007/JPEGImages        % images」/「VOCdevkit/VOC2007/SegmentationObject % segmentations by object」/「VOCdevkit/VOC2007/SegmentationClass % segmentations by class」| 文件: `devkit2007.txt:765-773`（§7.1）
   - 逐字（trainval 与 devkit 是两个包）:「training/validation sets for the challenge are provided in a separate archive which can be obtained via the VOC web pages [1].」| 文件: `devkit2007.txt:745-746`（§7）

7. **VOC2007 的评测/提交方式（本轮 E3：无 test server，走邮件+归档 URL）**
   - 逐字:「The results files should be collected in a single archive file (tar/zip) and placed on an FTP/HTTP server accessible from outside your institution. Email the URL and any details needed to access the file to Mark Everingham, me@comp.leeds.ac.uk .」| 出处: `http://host.robots.ox.ac.uk/pascal/VOC/voc2007/index.html` | 段: `index.html:447-450`（Submission of Results 节）
   - 逐字:「Details of the required file formats for submitted results can be found in the development kit documentation.」| 出处: 同页 | 段: `index.html:443-444`
   - 核验（仅事实）: VOC2007 页全文（`index.html`，共 539 行）中**不出现** `evaluation server` 这一提法；`index.html` 的 `href` 全量清单中**无**任何 evaluation server 链接（该页外链仅有 `iccv2007.rutgers.edu`、`pascal-network.org`、`flickr.com`、`results/index.shtml`、`htmldoc/index.html` 等）。

**B. VOC2012 与 VOC2007 的区别（编码者点名的「同族版本混淆」）**

8. **官方「自 VOC2007 起 就不再发布 test 标注，改由 evaluation server 提交」的逐字分界句**
   - 逐字:「In VOC2007 we made all annotations available (i.e. for training, validation and test data) but since then we have not made the test annotations available. Instead, results on the test data are submitted to an evaluation server.」| 出处: `http://host.robots.ox.ac.uk/pascal/VOC/voc2012/index.html` | 段: `index.html:706-708`（Best Practice 节）

9. **VOC2012「test 标注未发布、评测由官方 server 提供」的逐字**
   - 逐字:「The test data will be made available according to the challenge timetable . Note that the only annotation in the data is for the action task and layout taster. As in 2008-2011, there are no current plans to release full annotation - evaluation of results will be provided by the organizers.」| 出处: `http://host.robots.ox.ac.uk/pascal/VOC/voc2012/index.html` | 段: `index.html:514-517`（Test Data 节）
   - 逐字:「The test data can be downloaded from the evaluation server .」/「You can also use the evaluation server to evaluate your method on the test data.」| 出处: 同页 | 段: `index.html:520-521`
   - 逐字:「Results must be submitted using the automated evaluation server:」| 出处: 同页 | 段: `index.html:592`（Submission of Results 节；下一行 `:595` 为 `PASCAL VOC Evaluation Server` 链接）
   - 逐字:「03-Sep-12: The PASCAL VOC Evaluation Server is now open for submissions. Note that results on the validation set can be checked, but test set results will be withheld until after the challenge closing date.」| 出处: 同页 | 段: `index.html:110`（News 节）
   - 逐字:「25-Jun-12: The test data is now available for download from the evaluation server.」| 出处: 同页 | 段: `index.html:113`
   - 逐字:「Since algorithms should only be run once on the test data we strongly discourage multiple submissions to the server (and indeed the number of submissions for the same algorithm is strictly controlled), as the evaluation server should not be used for parameter tuning.」| 出处: 同页 | 段: `index.html:711-714`

10. **VOC2012 官方 devkit 文档里的「两阶段发布 / test 无标注」逐字（E2/E4）**
    - 包: `http://host.robots.ox.ac.uk/pascal/VOC/voc2012/devkit_doc.pdf` | 大小 `425,744` bytes | sha256 `58f3b0957a6ad0439995d1e2eb32c05f3a4c4b350a2063077dc1031c33c39aa6`；转换命令 `pdftotext -layout devkit_doc.pdf devkit2012.txt`
    - 逐字:「The VOC2012 data is released in two phases: (i) training and validation data with annotation is released with this development kit; (ii) test data without annotation is released at a later date.」| 文件: `devkit2012.txt:215-217`（PDF 第 4 页，§2 Data）
    - 逐字:「For the classification and detection tasks there are four sets of images provided:」/「train: Training data」/「val: Validation data (suggested)…」/「trainval: The union of train and val.」/「test: Test data. The test set is not provided in the development kit. It will be released in good time before the deadline for submission of results.」| 文件: `devkit2012.txt:222-232`（§2.1）
    - 逐字:「The dataset includes images from the 2008–2011 datasets, for which no test set annotation has been released.」| 文件: `devkit2012.txt:242-243`（§2.1）
    - 逐字（图像集文件名）:「The files train.txt, val.txt, trainval.txt and test.txt list the image identifiers for the corresponding image sets (training, validation, training+validation and testing).」| 文件: `devkit2012.txt:1167-1170`（§10.1.1）

11. **VOC2012 官方页面的发布物清单（E4：本轮核验页面 link 全量清单）**
    - 包本体: `http://host.robots.ox.ac.uk/pascal/VOC/voc2012/VOCtrainval_11-May-2012.tar` | `Content-Range: bytes 0-0/1999639040`（与页面 `(2GB tar file)` 一致）
    - 包本体: `http://host.robots.ox.ac.uk/pascal/VOC/voc2012/VOCdevkit_18-May-2011.tar` | 大小 `511,488` bytes（与页面 `(500KB tar file)` 一致）| sha256 `6101e33483e1f252821085f4b85634d334c1d44a0a5bc3921cd64320a40bd2cf`（与上一轮记录一致）
    - 逐字（页面条目）:「Download the training/validation data (2GB tar file)」/「Download the development kit code and documentation (500KB tar file)」/「Download the PDF documentation (500KB PDF)」| 出处: `http://host.robots.ox.ac.uk/pascal/VOC/voc2012/index.html` | 段: `index.html:492-499`
    - 核验（仅事实）: VOC2012 页 `href` 全量清单中，VOC2012 自身的下载件**只有** `VOCtrainval_11-May-2012.tar` 与 `VOCdevkit_18-May-2011.tar` 两个；**无**任何 test 包链接（test 只在 `evaluation server` 处提供，见第 9 条）。`VOCdevkit_18-May-2011.tar` 内容（`tar -tf`，共 44 项）亦**不含** `ImageSets/`，`grep -i test` → 无 `test` 项。

**本轮下载件 sha256（复核用）**

| 文件 | URL | bytes | sha256 |
|---|---|---|---|
| `VOCdevkit_08-Jun-2007.tar` | `http://host.robots.ox.ac.uk/pascal/VOC/voc2007/VOCdevkit_08-Jun-2007.tar` | 256,000 | `f4027a9768d6eef4a7eb958740ac9eda26f52dda2bbd1a8da9ae63083b7f89f8` |
| `VOCtrainval_06-Nov-2007.tar` | `http://host.robots.ox.ac.uk/pascal/VOC/voc2007/VOCtrainval_06-Nov-2007.tar` | 460,032,000 | `7d8cd951101b0957ddfd7a530bdc8a94f06121cfc1e511bb5937e973020c7508` |
| `VOCtestnoimgs_06-Nov-2007.tar` | `http://host.robots.ox.ac.uk/pascal/VOC/voc2007/VOCtestnoimgs_06-Nov-2007.tar` | 12,492,800 | `ee71b6ec2a2c8a449af661a85207afafd4bf3574521e91208bd757bc69365941` |
| `devkit_doc_07-Jun-2007.pdf` | `http://host.robots.ox.ac.uk/pascal/VOC/voc2007/devkit_doc_07-Jun-2007.pdf` | 178,965 | `0cd0ba27d88dd66643417eac04b21bbe434cf2ed50ece6594438175e83354574` |
| `VOCdevkit_18-May-2011.tar` | `http://host.robots.ox.ac.uk/pascal/VOC/voc2012/VOCdevkit_18-May-2011.tar` | 511,488 | `6101e33483e1f252821085f4b85634d334c1d44a0a5bc3921cd64320a40bd2cf` |
| `devkit_doc.pdf` (2012) | `http://host.robots.ox.ac.uk/pascal/VOC/voc2012/devkit_doc.pdf` | 425,744 | `58f3b0957a6ad0439995d1e2eb32c05f3a4c4b350a2063077dc1031c33c39aa6` |

- 未下载（仅取 HTTP 头大小）:`VOCtest_06-Nov-2007.tar` = 451,020,800 bytes；`VOCtrainval_11-May-2012.tar` = 1,999,639,040 bytes。
- 文本化重现命令（本节所有 `index.html:<line>` / `devkit200*.txt:<line>`）:
  `curl -sSL -A "Mozilla/5.0" -o voc2007_index.html "http://host.robots.ox.ac.uk/pascal/VOC/voc2007/index.html"` → `sed -e 's/<[^>]*>/ /g' -e 's/&nbsp;/ /g' -e 's/&amp;/\&/g' voc2007_index.html | sed -e 's/[ \t]\+/ /g' -e 's/^ //' | cat -n > voc2007.txt`
  （`voc2012/index.html` 同法 → `voc2012.txt`；PDF 用 `pdftotext -layout`）

- VOC 官方**无 git 仓库**（发布物为 tar 包，无 commit 可钉）；上述 sha256 即版本钉。本轮 `git ls-remote` 未用于 VOC。

---
### 卡 3 · Objects365

* **E1**（`Objects365.yaml` @ 同一 commit）：**有 `test:` 键但值为空注释行**；`train: images/train`（约 80000 图）。
* **E2**：`docs.ultralytics.com/datasets/detect/objects365`（含 test 说明）。
* **E3 报告口径**（论文）：ICCV 2019 §4.2 逐字 **"the results are reported on the Objects365 validation set as described in Table 2"**。
* **E4**：**NOT FOUND** —— 官方站点导航无 code/eval 页；4 个候选仓库 raw 全 404 或 `github.com:443` 连接失败（已重试 2 次，失败原文已录）。
* **附带不一致（只报观测）**：Objects365 的 val 图数跨来源不同（论文 Table 2 = 38k；Ultralytics yaml = 80000 images）。

#### 补采证据（2026-10-08，逐字）

- 目标: 官方**评测代码**在哪（上一轮 4 个候选仓 raw 404 / 连接失败）；另采论文 ICCV2019 中**评测协议**那一节（比 §4.2 更早/更晚的段落）。
- 结果: **官方评测代码 = NOT FOUND**（试过的入口见下）；**论文评测协议节 = 采到**（§4.1 Experiment Setup，位于 §4.2 之前）；**官方挑战赛/提交平台侧的评测口径 = 采到**（workshop 页 + Biendata Evaluation 页）。
- 逐字证据:

  1. **论文评测协议节（§4.1 "Experiment Setup"，早于 §4.2）**：
     「The COCO style mmAP is adopted to evaluate the performance of our Objects365 benchmark. More specifically, we average the IoU=.50:.05:.95 for all the object categories.」
     | 出处: https://openaccess.thecvf.com/content_ICCV_2019/papers/Shao_Objects365_A_Large-Scale_High-Quality_Dataset_for_Object_Detection_ICCV_2019_paper.pdf | 文件: `o365paper.pdf`（同 URL，794,578 bytes，sha 未钉）经 `pdftotext -layout` 输出的 `o365.txt:317-319`（`4.1. Experiment Setup` 标题在 `:315`；`4.2. Results on Object365` 标题在 `:255`，§4.2 的 split 句在 `:258-260`）

  2. **同一论文 §4.1 内的实现/评测设置（紧接上句）**：
     「For the implementation details, we follow the setting defined in Detectron [14, 15] for COCO. We train our detector on 8 1080-Ti GPUs, with a batch-size of 16. The input image size is 800×1333, which is also the same in the training process and testing process.」
     | 出处: 同上 PDF | 文件: `o365.txt:321-325`（§4.1）

  3. **官方挑战赛页（Full Track 评测协议，含 split 与 COCO 判据）**：
     「The goal of Full Track is to explore the upper-bound performance of object detection systems, given all the 365 classes and 600K+ training images. 30K images are used for validation and another 100K images are used for testing. To evaluate the performance of object detection, the evaluation criteria for COCO (IOU from 0.5 to 0.95) benchmark will be adopted.」
     | 出处: http://www.objects365.org/workshop2019.html | 文件: `workshop2019.html:208`

  4. **官方挑战赛页（提交平台）**：
     「The competitions platform is provided by <a href="https://www.biendata.com/">Biendata</a>. The entrances of registration and submission are about to open. Wait a moment.」
     | 出处: http://www.objects365.org/workshop2019.html | 文件: `workshop2019.html:198`

  5. **官方提交平台（Biendata）Evaluation 页（提交文件格式＝COCO）**：
     「The submission file shall have an identical format with COCO competition, i.e. in JSON. The file shall be a list, and each element of the list is a dictionary data structure as following:」
     同页另有小节标题逐字 `Evaluation Metric`、`Submit`、`Test Submission`、`Full Track Test Submissions`。
     | 出处: https://www.biendata.xyz/competition/objects365/Evaluation/ | 文件: `bd_eval.html:431`（`Evaluation Metric` 标题在 `:447`；`Test Submission` 文本同在 `:431` 前后的导航节）

  6. **官方站点本体＝GitHub Pages（承载仓库可钉，但仓库内无评测代码）**：
     `curl -I http://www.objects365.org/overview.html` 逐字响应头含 `Server: GitHub.com`、`ETag: "648ab190-e1a"`；站点 CNAME 仓库为 `sshao0516/Objects365`（`CNAME` 文件存在），`git ls-remote https://github.com/sshao0516/Objects365 HEAD` → `e042eb0ed41238d9cc1c7d0c08bfe650154fee08	HEAD`。
     该仓库全量文件清单（jsDelivr flat listing，共 77 项）**无任何评测代码/脚本**：`.DS_Store`、`_config.yml`、`CNAME`、`crowd_human_track.html`、`css/modern-business.css`、`data_samples.txt`、`DIW_Leader_Board.pdf`、`download.html`、`explore.html`、`footer.js`、`full_track.html`、`gulpfile.js`、`images/*`、`index.html`、`js/explore.js`、`js/jqBootstrapValidation.js`、`LICENSE`、`navigation.js`、`overview.html`、`people.html`、`README.md`、`slides/*.pptx|pdf`、`tiny_track.html`、`vendor/**`、`workshop2019.html`。
     | 出处: https://data.jsdelivr.com/v1/packages/gh/sshao0516/Objects365@master?structure=flat | 文件: `/tmp` 采集件 `o365site_files.json`（77 项 `files[].name`）；repo@commit: `sshao0516/Objects365@e042eb0ed41238d9cc1c7d0c08bfe650154fee08`

  7. **GitHub 上不存在 `Objects365` 账号（故一切 `Objects365/*` 路径必然 404）**：
     `curl https://api.github.com/users/Objects365` → HTTP 404，逐字正文 `{"message": "Not Found", "documentation_url": "https://docs.github.com/rest", "status": "404"}`（`objects365` 小写同 404）。
     | 出处: https://api.github.com/users/Objects365 | 文件: 响应正文（本项为账号存在性事实，非 sha）

- 若 NOT FOUND: 官方评测代码 —— 试过的入口 =
  - 候选仓（`raw.githubusercontent.com/<repo>/HEAD/README.md` 与/或 `git ls-remote` 均 404；`GitHub 账号 Objects365 不存在` 见上第 7 条）：
    `https://github.com/Objects365/Objects365`、
    `https://github.com/Objects365/objects365`、
    `https://github.com/Objects365/Objects365-Devkit`、
    `https://github.com/Objects365/Objects365_devkit`、
    `https://github.com/Objects365/Objects365_Devkit`、
    `https://github.com/Objects365/Objects365-dataset`、
    `https://github.com/Objects365/dataset`、
    `https://github.com/Objects365/Objects365Dataset`、
    `https://github.com/Objects365/objects365.github.io`、
    `https://github.com/Objects365/Objects365.github.io`
  - Megvii 系：`https://github.com/megvii/Objects365`、`https://github.com/megvii-model/Objects365`、`https://github.com/megvii-model/Objects365-Devkit`、`https://github.com/megvii-model/Objects365-Dataset`、`https://github.com/megvii-research/Objects365`、`https://github.com/Megvii-BaseDetection/Objects365`；
    `https://api.github.com/orgs/megvii-model/repos` → 404（该 org 不存在）；`https://api.github.com/orgs/megvii/repos` → `"public_repos": 0`；`https://api.github.com/orgs/megvii-research/repos?per_page=100` → 无任何 objects365/365/dataset/devkit 仓；`https://api.github.com/search/repositories?q=objects365+org:Megvii-BaseDetection` → 0 命中
  - SenseTime 系：`https://github.com/SenseTime/Objects365`、`https://github.com/sensetime/Objects365`、`https://github.com/OpenSenseTime/Objects365`、`https://github.com/Sense-X/Objects365`、`https://github.com/SenseTime/objects365.github.io`（均 404）；`https://api.github.com/orgs/SenseTime/repos` → 仅 `SenseTime/.github`（`"public_repos": 1`）；`https://api.github.com/orgs/Sense-X` → 404；`https://api.github.com/orgs/OpenSenseTime` → 404
  - 论文作者侧：`https://github.com/shao-shuai/objects365`、`https://github.com/shaoshuai/objects365`、`https://github.com/ShuaiShao/objects365`、`https://github.com/zhangtianyuan/Objects365`、`https://github.com/zhiqwang/objects365`、`https://github.com/vision-jeff/Objects365`（均 404）；
    `https://api.github.com/users/sshao0516/repos?per_page=100` 全量 11 个仓中无评测代码仓（`al-folio`,`bj_gas`,`CrowdHuman`,`dotfiles`,`hexo-theme-next`,`home-assistant-vaillant-plus`,`moltbot`,`Objects365`,`sshao0516`,`sshao0516.github.io`,`vaillant-plus-cn-api`）；
    作者主页 `https://www.sshao.com/`（仅列 Objects365 论文 PDF 与 `https://www.objects365.org/`、`https://www.objects365.org/workshop2019.html`）、`https://www.zemingli.com/`（仅 YOLOX 等，无 Objects365 代码）
  - 官方站点：`http://www.objects365.org/evaluation.html`、`/code.html`、`/devkit.html`（均 404）；`/devkit.zip`、`/code.zip`、`/Objects365_Devkit.zip`、`/Objects365_devkit.zip`、`/evaluation.zip`、`/full_track.zip`、`/annotation.zip`、`/scripts/`、`/devkit/`、`/evaluation/`（均 404）；已通读 `overview.html`、`download.html`、`workshop2019.html`、`full_track.html`、`tiny_track.html`、`navigation.js`、`footer.js`（`download.html` 全文只有 CC-BY 许可与软件许可，下载入口指向 `https://data.baai.ac.cn/details/Objects365_2020`；`navigation.js` 导航只有 Home/Explore/Dataset·Download/Challenges·Detection In the Wild Challenge Workshop/Leaderboard·Full|Tiny|CrowdHuman Track/About·People，**无 code/evaluation 页**）
  - 提交平台：`https://data.baai.ac.cn/details/Objects365_2020`（HTTP 200，764 bytes，前端渲染）、`https://www.biendata.xyz/competition/objects365/`、`https://www.biendata.xyz/competition/objects365/Evaluation/`（Evaluation 页正文只有提交格式与 `Evaluation Metric` 标题，**无评测代码**）
  - GitHub 发现性搜索（未取 sha）：`https://api.github.com/search/repositories?q=objects365+in:name&per_page=40` → `total_count: 17`，全部为第三方（`sshao0516/Objects365`、`google-research-datasets/DaTaSeg-Objects365-Instance-Segmentation`、`KainingYing/SAM_Objects365`、`rendicahya/objects365-downloader`、`megan-bond/Objects365`、`YashBhamare123/Objects365`、`leezhao415/Objects365_to_VOC_Convertor`、`voidrank/Objects365toolkits`、`chuxiuhong/download_objects365`、`itmorn/download_Objects365`、`JureHudoklin/objects365_utils`、`patienceFromZhou/objects365.github.io`、`ITLAN-dev/objects365-download-tools`、`Le1kk/Objects365-Tiny-Track`、`segfaultDelirium/reindex_labels_objects365`、`tucker666/open-image-objects365-labels-mapping`、`segfaultDelirium/remove_files_not_containing_class_from_Objects365`）；`q=Objects365&sort=stars&per_page=30` 亦无官方仓
  - Wayback：`https://web.archive.org/cdx/search/cdx?url=objects365.org&matchType=domain&...` → 连接失败（`Failed to connect to web.archive.org port 443`，重试 2 次）
  - 备注（仅事实）：Objects365 官方**无 GitHub 账号**（`Objects365`/`objects365` 均 404），论文正文对外只给出 `www.objects365.org`（`o365.txt:31` 逐字 `models have been released at www.objects365.org.`；脚注 2 逐字 `2https://www.objects365.org`，`o365.txt:180`）。

---

### 卡 4 · Open Images v7

* **E1**（`open-images-v7.yaml` @ 同一 commit）：**有 `test:` 键但值为空注释行**。
* **E2**：官方 facts 页 + Ultralytics 文档页。
* **E3 报告口径**（**同一官方域名下两处冲突，均逐字**）：
  * `challenge.html:222`：**"The test set (100k images) and the evaluation servers are hosted by Kaggle."**
  * `download_v7.html:1166-1167` 与 `:517`：**公开提供 125,436 张的 test 标注**。
  * 官方自己在 `challenge2019.html:243` 以 **WARNING 1** 逐字标出该冲突。
* **E4**：`openimages/dataset@077282972acd0ad8628f1526760ad239a38a8a97`；官方评测实现在 `tensorflow/models@34a21326906b9574fa11c4d6d0a5c534ff039267`。
* **NOT FOUND**：无。

#### R0 补采证据（2026-10-08，逐字）

**[A]** ### 目标格：release
- **采到**
- 官方发布物清单 = 官方 Download 页（`download_v7.html`）「Annotations and metadata」节，逐条列出 train / validation / **test** 三档：

  **清单结构（节标题原文）**：
- 逐字证据: 「Annotations and metadata」 | 出处: https://storage.googleapis.com/openimages/web/download_v7.html | 文件/段: download_v7.html:453
- 逐字证据: 「Image IDs」 | 出处: https://storage.googleapis.com/openimages/web/download_v7.html | 文件/段: download_v7.html:455
- 逐字证据: 「Image labels」 | 出处: https://storage.googleapis.com/openimages/web/download_v7.html | 文件/段: download_v7.html:478
- 逐字证据: 「Boxes」 | 出处: https://storage.googleapis.com/openimages/web/download_v7.html | 文件/段: download_v7.html:501
- 逐字证据: 「Segmentations」 | 出处: https://storage.googleapis.com/openimages/web/download_v7.html | 文件/段: download_v7.html:524

  **① 图像 ID（含独立命名的 test 件）**：
- 逐字证据: 「<a download href="https://storage.googleapis.com/openimages/2018_04/test/test-images-with-rotation.csv" ><button class="button">Test</button></a」 | 出处: https://storage.googleapis.com/openimages/web/download_v7.html | 文件/段: download_v7.html:470-472（href=`https://storage.googleapis.com/openimages/2018_04/test/test-images-with-rotation.csv`）
- 逐字证据: 「href="https://storage.googleapis.com/openimages/2018_04/train/train-images-boxable-with-rotation.csv" ><button class="button">Train</button></a >」 | 出处: https://storage.googleapis.com/openimages/web/download_v7.html | 文件/段: download_v7.html:459-461（Train）
- 逐字证据: 「href="https://storage.googleapis.com/openimages/2018_04/validation/validation-images-with-rotation.csv" ><button class="button">Validation</button></a >」 | 出处: https://storage.googleapis.com/openimages/web/download_v7.html | 文件/段: download_v7.html:465-467（Validation）

  **② 图像级标签（test 件公开）**：
- 逐字证据: 「<a download href="https://storage.googleapis.com/openimages/v5/test-annotations-human-imagelabels-boxable.csv" ><button class="button">Test</button></a」 | 出处: https://storage.googleapis.com/openimages/web/download_v7.html | 文件/段: download_v7.html:493-495（href=`https://storage.googleapis.com/openimages/v5/test-annotations-human-imagelabels-boxable.csv`）

  **③ 检测框标注（test 件公开 → 直接决定 test 标注是否公开）**：
- 逐字证据: 「<a download href="https://storage.googleapis.com/openimages/v5/test-annotations-bbox.csv" ><button class="button">Test</button></a」 | 出处: https://storage.googleapis.com/openimages/web/download_v7.html | 文件/段: download_v7.html:516-518（href=`https://storage.googleapis.com/openimages/v5/test-annotations-bbox.csv`）
- 逐字证据: 「<a download href="https://storage.googleapis.com/openimages/v5/validation-annotations-bbox.csv" ><button class="button">Validation</button></a」 | 出处: https://storage.googleapis.com/openimages/web/download_v7.html | 文件/段: download_v7.html:510-512（Validation）
- 逐字证据: 「<a download href="https://storage.googleapis.com/openimages/v6/oidv6-train-annotations-bbox.csv" ><button class="button">Train</button></a」 | 出处: https://storage.googleapis.com/openimages/web/download_v7.html | 文件/段: download_v7.html:504-506（Train）

  **④ 分割掩码（test 件公开）**：
- 逐字证据（原始 HTML；test 档按钮 `id="seg_test_button"`，train/validation 同构）: 「<button class="button" id="seg_test_button" onclick="toggle_download_view('seg_', 'test')" > Test </button>」 | 出处: https://storage.googleapis.com/openimages/web/download_v7.html | 文件/段: download_v7.html:545-551

  **⑤ 官方"三档划分"的发布说明（逐字）**：
- 逐字证据: 「If you're interested in downloading the full set of training, test, or validation images (1.7M, 125k, and 42k, respectively; annotated with bounding boxes, etc.), you can download them packaged in various」 | 出处: https://storage.googleapis.com/openimages/web/download_v7.html | 文件/段: download_v7.html:398-400
- 逐字证据: 「Each line should follow the format $SPLIT/$IMAGE_ID, where $SPLIT is either "train", "test", "validation", or "challenge2018"; and $IMAGE_ID is the image ID that」 | 出处: https://storage.googleapis.com/openimages/web/download_v7.html | 文件/段: download_v7.html:433-435
- 逐字证据（原始 HTML 的示例文件块）: 「<pre> train/f9e0434389a1d4dd train/1a007563ebc18664 test/ea8bfd4e765304db</pre >」 | 出处: https://storage.googleapis.com/openimages/web/download_v7.html | 文件/段: download_v7.html:437-441
- 逐字证据: 「The dataset is split into a training set (9,011,219 images), a validation set (41,620 images), and a test set (125,436 images). The images are annotated with image-level labels, object bounding boxes, object segmentation masks, visual relationships, and localized narratives as described below.」 | 出处: https://storage.googleapis.com/openimages/web/factsfigures_v7.html | 文件/段: factsfigures_v7.html:251
- 逐字证据: 「For the validation and test sets, we provide exhaustive box annotation for all object instances, for all available positive image-level labels (again, except for "groups-of"). All boxes were manually drawn. We deliberately tried to annotate boxes at the most specific level in our semantic hierarchy as possible. On average, there are 7.4 boxes per image in the validation and test sets. For Open Images V5, we improved the annotation density, which now comes close to the density in the training set. This ensures more precise evaluation of object detection models. In contrast to the training set, on the validation and test sets we annotated human body parts on all images for which we have a positive label.」 | 出处: https://storage.googleapis.com/openimages/web/factsfigures_v7.html | 文件/段: factsfigures_v7.html:327

  **⑥ 发布物实体可达性核验（2026-10-19，`curl -sI` → HTTP 状态码）**：
| 官方发布文件 URL | HTTP |
|---|---|
| https://storage.googleapis.com/openimages/v5/test-annotations-bbox.csv | 200 |
| https://storage.googleapis.com/openimages/v5/validation-annotations-bbox.csv | 200 |
| https://storage.googleapis.com/openimages/v6/oidv6-train-annotations-bbox.csv | 200 |
| https://storage.googleapis.com/openimages/2018_04/test/test-images-with-rotation.csv | 200 |

  **⑦ "评测是否需提交 / 能否本地评"（官方两处口径，均逐字）**：
- 逐字证据（**数据集自带 test 档可本地评**）: 「To obtain the evaluation results with the Tensorflow Object Detection API, use oid_od_challenge_evaluation.py util. Please see this Tutorial on how to run the metric.」 | 出处: https://storage.googleapis.com/openimages/web/evaluation.html | 文件/段: evaluation.html:83
- 逐字证据（**Challenge 隐藏集须提交 Kaggle**）: 「To create a submission, click on 'Late Submissions' / 'Submit Predictions', accept terms and conditions and upload a solution file.」 | 出处: https://storage.googleapis.com/openimages/web/challenge_overview.html | 文件/段: challenge_overview.html:81
- 逐字证据（同上）: 「Note that when you are submitting to RVC servers your score will be visible on the public leaderboard and you will only be able to see the private score after the challenge ends.」 | 出处: https://storage.googleapis.com/openimages/web/challenge_overview.html | 文件/段: challenge_overview.html:82

#### 目标格：protocol
- **采到**
- 官方域名下"test set"两处不同含义，**官方自己逐字标出冲突**（编码者要的那两处含义，原文如下）：
- 逐字证据（**含义 A：100k 隐藏 Challenge 集，须提交**）: 「The test set (100k images) and the evaluation servers are hosted by Kaggle.」 | 出处: https://storage.googleapis.com/openimages/web/challenge.html | 文件/段: challenge.html:222（节标题 `:221` = 「Results submission」）
- 逐字证据（**官方 WARNING 1，明确二者不是一个东西**）: 「WARNING 1: Open Images V5 has a test set (with public annotations). This is NOT the same as the Challenge set (which has hidden annotations).」 | 出处: https://storage.googleapis.com/openimages/web/challenge2019.html | 文件/段: challenge2019.html:243
- 逐字证据（含义 A 的完整协议段）: 「The annotated data available for the participants is part of the Open Images V5 train and validation sets (reduced to the subset of classes covered in the Challenge, see below). The participants are recommended to use the training set provided on this page for traning models, and the validation set for validation. The Challenge set (100k images) with hidden annotations, on which participants are evaluated, is hosted by Kaggle. All tracks have the same Challenge set.」 | 出处: https://storage.googleapis.com/openimages/web/challenge2019.html | 文件/段: challenge2019.html:241
- 逐字证据（leaderboard 口径）: 「Note: the public leaderboard on the Kaggle website is the most reliable indicator of your performance, as it is based on images and annotations distributed identically to the hidden test set on which participants will be ranked for final evaluation. The validation set is also indicative of performance on the Challenge set, but is not exactly identically distributed. The best reference is the public leaderboard.」 | 出处: https://storage.googleapis.com/openimages/web/challenge2019.html | 文件/段: challenge2019.html:242
- 逐字证据（Challenge 集发布与评测服务器开启）: 「June 3d 2019: Challenge set released by Kaggle (100k images). Evaluation server for the object detection and visual relationship detection tracks opens.」 | 出处: https://storage.googleapis.com/openimages/web/challenge2019.html | 文件/段: challenge2019.html:65
- 逐字证据（2019 服务器仍在、可评隐藏集）: 「The evaluation servers of the 2019 challenge are still accessible. This enables evaluating new methods on the hidden challenge dataset and to compare properly to previous results. Please check the Train data and Evaluation section.」 | 出处: https://storage.googleapis.com/openimages/web/challenge_overview.html | 文件/段: challenge_overview.html:61
- 逐字证据（协议总述）: 「The challenge set used to report results can be downloaded from Kaggle. Training and validation sets can be downloaded from Challenge Download section. The evaluation protocols for each track are described in the Evaluation section. The python implementation of all three evaluation protocols is released as a part of the Tensorflow Object Detection API.」 | 出处: https://storage.googleapis.com/openimages/web/challenge_overview.html | 文件/段: challenge_overview.html:74
- 逐字证据（**含义 B：V5/V7 公开 test 档，标注公开**）: 「For the validation and test sets, we provide exhaustive box annotation for all object instances, for all available positive image-level labels (again, except for "groups-of"). All boxes were manually drawn. We deliberately tried to annotate boxes at the most specific level in our semantic hierarchy as possible. On average, there are 7.4 boxes per image in the validation and test sets. For Open Images V5, we improved the annotation density, which now comes close to the density in the training set. This ensures more precise evaluation of object detection models. In contrast to the training set, on the validation and test sets we annotated human body parts on all images for which we have a positive label.」 | 出处: https://storage.googleapis.com/openimages/web/factsfigures_v7.html | 文件/段: factsfigures_v7.html:327
- 逐字证据（官方评测指标与本地实现）: 「The challenge uses a variant of the standard PASCAL VOC 2010 mean Average Precision (mAP) at IoU > 0.5. There are three key features of Open Images annotations, which are addressed by the new metric:」 | 出处: https://storage.googleapis.com/openimages/web/evaluation.html | 文件/段: evaluation.html:47
- 逐字证据（官方 GT 生成步骤）: 「The ground-truth files contain only leaf-most image-level labels and boxes. To produce ground-truth suitable for evaluating this metric correctly using the Tensorflow Object Detection API, please run the script on both image-level labels csv file and boxes csv file. Using FiftyOne (see below), the expansion is done automatically when computing the metric.」 | 出处: https://storage.googleapis.com/openimages/web/evaluation.html | 文件/段: evaluation.html:61
- 逐字证据（官方 metric 归属）: 「The implementation of this mAP variant is publicly available through the open-source tool FiftyOne as well as through the Tensorflow Object Detection API under the name 'OID Challenge Object Detection Metric'.」 | 出处: https://storage.googleapis.com/openimages/web/evaluation.html | 文件/段: evaluation.html:69-70

- **E4 / commit**：
- 官方数据仓 `openimages/dataset@077282972acd0ad8628f1526760ad239a38a8a97`（`git ls-remote … HEAD`，2026-10-19）；该仓 `README.md` 全文仅 3 行、无发布物清单：
- 逐字证据: 「As of V4, [the Open Images Dataset moved to a new site](https://storage.googleapis.com/openimages/web/index.html).」 | 出处: https://raw.githubusercontent.com/openimages/dataset/master/README.md | 文件/段: README.md:3
- 官方评测实现 `tensorflow/models@34a21326906b9574fa11c4d6d0a5c534ff039267`（同上方法取得）。
- 卡内已指名的官方评测脚本（出处: https://storage.googleapis.com/openimages/web/evaluation.html:83）: `oid_od_challenge_evaluation.py`。

---
### 卡 5 · DOTA v1.0

* **E1**（`ultralytics/cfg/datasets/DOTAv1.yaml:13-15` @ 同一 commit）：`train=images/train`（1411）· `val=images/val`（458）· **`test=images/test`（937）**（三键齐、互不相同）。
* **E2**：官方下载页 `captain-whu.github.io/DOTA` 说明 v1.0 的四档划分。
* **E3 报告口径**：官方 devkit `DOTA_devkit@99388551054be9a6dabb01c8bb2a7eb562d57b4f`：
  **同文件内并列两种 `imagesetfile` 示例** —— `:277` 注释给 `testset.txt`（生效），`:283` 给 `valset.txt`。
* **E4**：`captain-whu/DOTA@59cb20cf…`；`DOTA_devkit` 同上。
* **NOT FOUND**：无。

#### R0 补采证据（2026-10-08，逐字）

**[B]** **本节涉及的仓库与 sha（`git ls-remote … HEAD` 取得）**

| 仓库 | HEAD sha | 用途 |
|---|---|---|
| `CAPTAIN-WHU/DOTA` | `59cb20cfe8a42ff750c0985776b01f4d7e550e18` | 官方站（GitHub Pages）承载仓库，镜像取正文 |
| `CAPTAIN-WHU/DOTA_devkit` | `99388551054be9a6dabb01c8bb2a7eb562d57b4f` | 官方 devkit |
| `CAPTAIN-WHU/ODAI` | `4d672abd6d3af323384250af9d884e2e02e0c6a4` | ODAI-18（ICPR'2018）官方竞赛站，基于 DOTA-v1.0 |
| `ultralytics/ultralytics` | `803c8b96c1a6fc0533434fc5be0e3e0a3d122482` | `DOTAv1.yaml` |

#### 目标格：release

**采到**（DOTA-v1.0 官方发布物逐字名称 = 三档；test 的 GT/评测条件逐字采到）。
**NOT FOUND**：`test-challenge` / `test-dev` 作为 **DOTA-v1.0** 发布物档位的逐字名称（该四档名称在官方与 Ultralytics 文档中**只出现在 DOTA-v2.0 段**，逐字来源与入口见下 5、6）。

逐字证据：

1. **官方数据页 DOTA-v1.0 段的全部下载条目（只有 3 项，无 test 标注项）**
   - 「Baidu Drive: Training set , Validation set , Testing images」
     | 出处: https://captain-whu.github.io/DOTA/dataset.html （镜像件 `jsd_dataset.html`） | 文件/段: `dataset.html:235-238`（三行逐字：`:236` `<a href="https://pan.baidu.com/s/1kWyRGaz">Training set</a>,`；`:237` `<a href="https://pan.baidu.com/s/1qZCoF72">Validation set</a>,`；`:238` `<a href="https://pan.baidu.com/s/1i6ly9Id">Testing images</a>`）
   - 「Google Drive: Training set , Validation set , Testing images」
     | 出处: 同上 | 文件/段: `dataset.html:241-244`（`:242` Training set；`:243` Validation set；`:244` Testing images，链接 `https://drive.google.com/drive/folders/1mYOf5USMGNcJRPcvRVJVV1uHEalG5RPl?usp=sharing`）
   - 同一页 DOTA-v1.0 段（`:232` `<h3>DOTA-v1.0</h3>` 起、`:248` `</ul>` 止）内**无第 4 个条目**。

2. **官方站首页的 v1.0 发布新闻（逐字，含原拼写）**
   - 「2018-01-26 DOTA-v1.0 released with all images and oriented bounding box annotations for training and vallidation!」
     | 出处: https://captain-whu.github.io/DOTA/index.html （镜像件 `jsd_index.html`） | 文件/段: `index.html:159`

3. **论文 §3.4「Dataset splits」（test 的 GT 是否公开 + 评测条件）**
   - 「In order to ensure that the training data and test data distributions approximately match, we randomly select half of the original images as the training set, 1/6 as validation set, and 1/3 as the testing set. We will publicly provide all the original images with ground truth for training set and validation set, but not for the testing set. For testing, we are currently building an evaluation server.」
     | 出处: https://ar5iv.labs.arxiv.org/html/1711.10398 （arXiv:1711.10398） | 文件/段: `dota_ar5iv.html:447`（`<p id="S3.SS4.p1.1">`；小标题 `3.4 Dataset splits` 在 `:444`）

4. **官方站首页 DOTA-v1.0 描述句（逐字）**
   - 「DOTA-v1.0 contains 15 common categories, 2,806 images and 188, 282 instances. The proportions of the training set, validation set, and testing set in DOTA-v1.0 are 1/2, 1/6, and 1/3, respectively.」
     | 出处: 同 2 | 文件/段: `index.html:176-177`

5. **「test-dev / test-challenge」四档名称的逐字出现位置（供档位名称核对；逐字采录，不作版本判断）**
   - 「The 11,268 images of DOTA are split into training, validation, test-dev, and test-challenge sets.」 | `index.html:189`
   - 「we have two test sets, namely test-dev and test-challenge.」 | `index.html:191`
   - 「Test-dev contains 2,792 images and 353,346 instances. We released the images but not the ground truths. Test-challenge contains 6,053 images and 1,090,637 instances. The images and ground truths of test-challenge will be available only during the challenging.」 | `index.html:193-195`
   - 出处: https://captain-whu.github.io/DOTA/index.html | 文件: `jsd_index.html`
   - 上述三句在页面上的**上一级标题**逐字为 `<strong>DOTA-v2.0</strong>`（`index.html:187`），其 `<li>` 块为 `:186-196`。

6. **同四档名称在 Ultralytics 官方文档页重复出现（位于 "DOTA-v2.0" 小节下）**
   - 小节标题逐字 `DOTA-v2.0` | `docs_400f112c.html:35`
   - 「Image splits:」 `:41`；「Training: 1,830 images with 268,627 instances.」 `:43`；「Validation: 593 images with 81,048 instances.」 `:44`；「Test-dev: 2,792 images with 353,346 instances.」 `:45`；「Test-challenge: 6,053 images with 1,090,637 instances.」 `:46`
   - 出处: https://docs.ultralytics.com/datasets/obb/dota-v2/ | 文件/段: `docs_400f112c.html:41-46`（纯文本抽件同句在 `dota_docs.txt:80-84`）
   - 该页 `DOTA-v1.0` 小节（`:21-25`）逐字只有三项：`Contains 15 common categories.` / `Comprises 2,806 images with 188,282 instances.` / `Split ratios: 1/2 for training (1,411 images), 1/6 for validation (458 images), and 1/3 for testing (937 images).`

7. **负向核查（逐字 grep 结果，非结论）**
   - `grep -i "test-dev\|test-challenge"` 在 `dataset.html`、`tasks.html`、`evaluation.html`、`results.html`、`code.html` 与 `index.html` 的 DOTA-v1.0 `<li>` 块（`index.html:175-178`）内**零命中**。
   - `grep -i "challenge"` 在 `index.html` 仅命中 `:182`（DOTA-v1.5 的 `DOAI Challenge 2019`）、`:189`、`:191`、`:193`（均属 DOTA-v2.0 段）。
   - 官方 `dataset.html`、`tasks.html`、`evaluation.html`、`results.html` 四页均无 `test-challenge` 字样。

8. **评测是否需提交 / 需注册（官方评测链路口径）**
   - 「For evaluation, you must registrate and submit on the Evaluation Server」
     | 出处: https://captain-whu.github.io/DOTA/tasks.html | 文件/段: `tasks.html:107-108`（链接 `http://www.icdar2017chinese.site:5080/evaluation1/`）
   - 「You need to submit a zip file containing results for all test images for evaluation. The results are stored in n (n is the numer of categories) files, "Task1_plane.txt, Task1_storage-tank.txt, ..." , each file contains all the detections for a specific category.」
     | 出处: 同上 | 文件/段: `tasks.html:115-116`
   - 「Task1 Evaluation Server」/「Task2 Evaluation Server」 → `http://bed4rs.net:8001/evaluation1`、`http://bed4rs.net:8001/evaluation2`
     | 出处: https://captain-whu.github.io/DOTA/evaluation.html | 文件/段: `evaluation.html:139`、`:142`
   - 官方评测服务器**实测在线页逐字**：「DOTA performance evaluation server」(`bed4rs.html:48`)、「Log in to DOTA」(`:71`)、「Note: You are allowed to evaluate your results only when you are registered.」(`:72`)
     | 出处: http://bed4rs.net:8001/evaluation1 （`curl` → HTTP 200，2565 bytes；本地件 `bed4rs.html`）

9. **ODAI-18（ICPR'2018）官方竞赛站——同一 CAPTAIN-WHU 团队、基于 DOTA-v1.0**（逐字采录，供 v1.0 发布物/test 条件核对）
   - 「The DOAI-18 CONTEST's train, validation sets are the same as the DOTA-v1, test images are from DOTA-v1 test sets and other extra images.」
     | 出处: https://captain-whu.github.io/ODAI/dataset.html （镜像 `https://cdn.jsdelivr.net/gh/CAPTAIN-WHU/ODAI@master/dataset.html`） | 文件/段: `odai_dataset.html:184-187`（小标题 `Dataset Split For DOAI-18` 在 `:181`）
   - 「DOTA-v1.0 on Baidu Drive: Training set , Validation set , Testing images」 | `odai_dataset.html:217`
   - 「DOTA-v1.0 on Google Drive: Training set , Validation set , Testing images」 | `odai_dataset.html:220`
   - 被 HTML 注释掉（`<!-- … -->`）的条目，逐字供对照：「Dota Training Annotations [Google Drive] [Baidu Drive]」`odai_dataset.html:210-212`；「Dota Validation Annotations [Google Drive] [Baidu Drive]」`:213-215`；「Testing images [Google Drive] [Baidu Drive]」`:206-208`
   - 「For download the extra test images and submit your results, registrate on the contest page.」
     | 出处: https://captain-whu.github.io/ODAI/index.html | 文件/段: `odai_index.html:87`
   - 「The registration is open now. Please registrate to download the extra test images and submit your results.」 | `odai_index.html:73`
   - 「Extra test images for ODAI-18 available」March 16, 2018 /「Submission open」March 16, 2018 /「Submission deadline」April 25, 2018 | `odai_index.html:149-157`
   - 被 HTML 注释掉：「Whole Train, validation sets and part of test images are avaliable」February 1, 2018 | `odai_index.html:143-145`
   - 「Specificly, the Train and Validation sets are the same as DOTA-v1. However, the images of Test set are partly from DOTA-v1, other test images are not available currently.」 | `odai_index.html:196-197`
   - repo@commit: `CAPTAIN-WHU/ODAI@4d672abd6d3af323384250af9d884e2e02e0c6a4`

10. **官方 devkit README 的数据目录结构（逐字，含代码块）**
    - 「The subdirectory of "basepath"(which is used in "DOTA.py", "ImgSplit.py") is in the structure of」 + 代码块逐行 `.` / `├── images` / `└── labelTxt`
      | 出处: https://github.com/CAPTAIN-WHU/DOTA_devkit/blob/master/readme.md | 文件/段: `readme.md:62-67` | repo@commit: `CAPTAIN-WHU/DOTA_devkit@99388551054be9a6dabb01c8bb2a7eb562d57b4f`

**NOT FOUND 子项与入口**：DOTA-v1.0 的**四档**（train / val / test / test-challenge）逐字名称 →
试过的入口 = `https://captain-whu.github.io/DOTA/`（直连 000）、`https://captain-whu.github.io/DOTA/dataset.html`（000）、`.../tasks.html`（000）、`.../evaluation.html`（000）、`https://cdn.jsdelivr.net/gh/CAPTAIN-WHU/DOTA@master/{index,dataset,tasks,evaluation,results,code,index-old}.html`（`index-old.html` 经 jsDelivr → 301 → `raw.githubusercontent.com`（000），取不到）、`https://captain-whu.github.io/ODAI/{index,dataset}.html`（000）与镜像 `.../gh/CAPTAIN-WHU/ODAI@master/{index,dataset}.html`（200，已采）、`https://ar5iv.labs.arxiv.org/html/1711.10398`（200，已采）、`https://github.com/CAPTAIN-WHU/DOTA_devkit/blob/master/readme.md`（已采）。

#### 目标格：protocol

**采到**（官方协议文本：任务定义 / 用哪个测试集 / 判据 / 提交方式 / test 标注条件）。

逐字证据：

1. **官方 Tasks 页 · Task1 评测协议（逐字，标题 `Evaluation Protocol` 在 `tasks.html:131`）**
   - 「The evaluation protocol for oriented bounding box is a little different from the protocol in the original PASCAL VOC. We use the intersection over the union area of two polygons(ground truth and prediction) to calculate the IoU. The rest follows the PASCAL VOC.」
     | 出处: https://captain-whu.github.io/DOTA/tasks.html | 文件/段: `tasks.html:135-136`

2. **官方 Tasks 页 · Task2 评测协议（逐字，标题 `Evaluation Protocol` 在 `tasks.html:177`）**
   - 「The evaluation protocol for horizontal bounding boxes follows the PASCAL VOC benchmark, which uses mean Average Precision( mAP ) as metric.」
     | 出处: 同上 | 文件/段: `tasks.html:180-181`

3. **官方 Tasks 页 · 任务定义与 ground truth（逐字）**
   - 「We introduce two detection tasks. Task1 uses the initial oriented bounding boxes (OBB) as ground truth.」 | `tasks.html:93`
   - 「Task2 uses the generated HBB as ground truth.」 | `tasks.html:94`
   - 「Task1 has more practical value and we recommond you to test your algorithms in Task1.」 | `tasks.html:95`
   - 「The aim of this task is to locate the ground object instances with an OBB.」 | `tasks.html:100`
   - 「In the task, the ground truths for training and testing are generated by calculating the horizontal bounding boxes over original annotated bounding boxes.」 | `tasks.html:145-146`

4. **官方 Tasks 页 · 提交方式（= 用哪个测试集）**
   - 「You need to submit a zip file containing results for all test images for evaluation.」 | `tasks.html:115`（Task1）、`tasks.html:164`（Task2）
   - 「For evaluation, you must registrate and submit on the Evaluation Server」 | `tasks.html:107-108`、`tasks.html:156-157`

5. **论文 §3.4（split 定义 + test 标注不公开 + 评测服务器）**
   - 同 release 节第 3 条（`dota_ar5iv.html:447`）

6. **论文 §5.1 / §5.2（任务与指标）**
   - 「To comprehensively evaluate the state of the art deep learning based detection methods on DOTA, we propose two tasks, namely detection on horizontal bounding boxes ( HBB for short) and detection on oriented bounding boxes ( OBB for short).」
     | 出处: https://ar5iv.labs.arxiv.org/html/1711.10398 | 文件/段: `dota_ar5iv.html:580`（纯文本抽件 `dota_paper.txt:249`）
   - 「For evaluation metrics, we adopt the same mAP calculation as for PASCAL VOC.」 | `dota_ar5iv.html:840`（`dota_paper.txt:442`）
   - 「Images in DOTA are so large that they cannot be directly sent to CNN-based detectors. Therefore, we crop a series of 1024 × 1024 patches from the original images with a stride set to 512.」 … 「In the testing phase, first we send the cropped image patches to obtain temporary results and then we combine the results together to restore the detecting results on the original image. Finally, we use non-maximum suppression (NMS) on these results based on the predicted classes.」 | `dota_paper.txt:438`、`:441`

7. **官方站首页 · v1.0 split 比例句** | `index.html:176-177`（同 release 节第 4 条）

8. **官方评测页 · 提交格式与常见错误（逐字）**
   - 「Please be careful about the format , otherwise the results cannot be correctly tested.」 | `evaluation.html:102`
   - 「As the evaluation server is still improving, if you have problems using them, you can choose to send the results with correct format to Email: dotawebsite3@gmail.com . Please attach your Team name, Institute and team members to the email, otherwise the results will not be evaluated. The evaluation process executed by human takes about 2 days, please take it easy.」 | `evaluation.html:110-114`
   - 「Empty files are a frequent source of evaluation errors. Please make sure that no file corresponding to any class is left empty. In other words, ensure that every class has at least one prediction.」 | `evaluation.html:122-126`
   - 出处: https://captain-whu.github.io/DOTA/evaluation.html

9. **官方评测服务器页 · 需注册才能评测** | `bed4rs.html:72`（同 release 节第 8 条）

10. **ODAI-18 页 · 协议与提交指回 DOTA Tasks 页（逐字）**
    - 「For more details and submission format, refer to the Tasks Page on DOTA.」 | `odai_index.html:188-190`
    - 「Task1 uses the initial annotation as ground truth, while Task2 uses the generated axis-aligned bounding boxes as ground truth.」 | `odai_index.html:170`
    - 「NOTE: Except the train/val set of DOTA-v1, extra data is also allowed to train your detector, but you must give a description in your submission.」 | `odai_index.html:202`

11. **官方 devkit · 评测脚本 docstring 与生效配置（逐字）**
    - 「To use the code, users should to config detpath, annopath and imagesetfile」 / 「detpath is the path for 15 result files, for the format, you can refer to "http://captain.whu.edu.cn/DOTAweb/tasks.html"" / 「search for PATH_TO_BE_CONFIGURED to config the paths」 / 「Note, the evaluation is on the large scale images」
      | 文件/段: `dota_evaluation_task1.py:8-11`（docstring） | repo@commit: `CAPTAIN-WHU/DOTA_devkit@99388551054be9a6dabb01c8bb2a7eb562d57b4f`
    - `detpath = r'PATH_TO_BE_CONFIGURED/Task1_{:s}.txt'`（`:281`）
      `annopath = r'PATH_TO_BE_CONFIGURED/{:s}.txt' # change the directory to the path of val/labelTxt, if you want to do evaluation on the valset`（`:282`）
      `imagesetfile = r'PATH_TO_BE_CONFIGURED/valset.txt'`（`:283`）
    - 紧邻的注释示例行（`:275-277`）：`# imagesetfile = r'/home/dingjian/code/DOTA/DOTA/media/testset.txt'`

**NOT FOUND 子项**：无（本格要求的「用哪个测试集 / 怎么评测 / 标注是否扣留」原句均已采到）。
补充说明（逐字核查结果）：官方站 `index.html` 与 `dataset.html` 内**无评测协议句**（`grep -i "protocol|mAP|PASCAL|IoU"` 在 `index.html`、`dataset.html` 零命中）；协议句集中在 `tasks.html` 与 `evaluation.html`。

#### 目标格：yolo_dist

**采到**。

逐字证据：

1. **`DOTAv1.yaml` 的 train / val / test 三行（逐字，含行内注释）**
   - `train: images/train # train images (relative to 'path') 1411 images` | 文件/段: `ultralytics/cfg/datasets/DOTAv1.yaml:13`
   - `val: images/val # val images (relative to 'path') 458 images` | `:14`
   - `test: images/test # test images (optional) 937 images` | `:15`
   - 紧邻上下文（逐字）：`:11` `# Train/val/test sets as 1) dir: path/to/imgs, 2) file: path/to/imgs.txt, or 3) list: [path/to/imgs1, path/to/imgs2, ..]`；`:12` `path: DOTAv1 # dataset root dir`
   - 出处: https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/datasets/DOTAv1.yaml （raw: `https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/cfg/datasets/DOTAv1.yaml`）
   - repo@commit: `ultralytics/ultralytics@803c8b96c1a6fc0533434fc5be0e3e0a3d122482`（`git ls-remote … HEAD`，连试 3 次同值）
   - **sha 一致性**：main 分支件（2026-10-19 16:57 取，1182 bytes）与按 commit 钉取件（`https://cdn.jsdelivr.net/gh/ultralytics/ultralytics@803c8b96c1a6fc0533434fc5be0e3e0a3d122482/ultralytics/cfg/datasets/DOTAv1.yaml`，17:07 取，1182 bytes）`diff` 为空 → `IDENTICAL`；钉取件同三行仍在 `:13`/`:14`/`:15`。

2. **该 yaml 自己声明的「官方文档页」URL（逐字）**
   - `# Documentation: https://docs.ultralytics.com/datasets/obb/dota-v2` | 文件/段: `DOTAv1.yaml:4`（同一行在文档页 HTML 内逐字重复于 `docs_400f112c.html:67`）

3. **该官方文档页里与「test 数据是否可下载 / 是否需提交」相关的全部逐字句**
   - 「Use the YAML that matches the release you downloaded, or author a custom YAML if you are working with DOTA-v2 or another derivative. Both releases download automatically (2 GB) from Ultralytics GitHub assets the first time you train.」
     | 出处: https://docs.ultralytics.com/datasets/obb/dota-v2/ | 文件/段: `docs_400f112c.html:64`（抽件 `dota_docs.txt:95`）
   - 「A dataset YAML file specifies image/label roots, class names, and other important metadata. Ultralytics maintains official YAML files for the two most commonly used releases:」 | `docs_400f112c.html:59`
   - `DOTAv1.yaml`（链接到 `https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/datasets/DOTAv1.yaml`） | `docs_400f112c.html:61`
   - 页内嵌 yaml 全文三键（逐字，与 1 同）：`train: images/train # train images (relative to 'path') 1411 images`（`:76`）/ `val: images/val # val images (relative to 'path') 458 images`（`:77`）/ `test: images/test # test images (optional) 937 images`（`:78`）
   - `download: https://github.com/ultralytics/assets/releases/download/v0.0.0/DOTAv1.zip` | `docs_400f112c.html:99`（抽件 `dota_docs.txt:128`）
   - 代码块注释逐字 `# Split train and val set, with labels.`（`:102`）/ `# Split test set, without labels.`（`:109`），函数 `split_trainval(`（`:103`）与 `split_test(`（`:110`）
   - 「The raw imagery routinely exceeds 10,000 pixels on a side, so tiling is recommended before feeding the data to YOLO.」 | `docs_400f112c.html:100`
   - 「To train a model on the DOTA v1 dataset, you can utilize the following code snippets. Always refer to your model's documentation for a thorough list of available arguments.」 | `docs_400f112c.html:116`
   - `results = model.train(data="DOTAv1.yaml", epochs=100, imgsz=1024)` | `docs_400f112c.html:122`（Python tab）、`:146`（FAQ 段重复）
   - `yolo obb train data=DOTAv1.yaml model=yolo26n-obb.pt epochs=100 imgsz=1024` | `docs_400f112c.html:166`（该页 tab 面板的 CLI 变体，逐字含前置注释 `# Train a pretrained YOLO26n-OBB model on the DOTAv1 dataset`）
   - 「Please note that all images and associated annotations in the DOTAv1 dataset can be used for academic purposes, but commercial use is prohibited.」 | `docs_400f112c.html:153`（抽件 `dota_docs.txt:153`）

**NOT FOUND 子项**：「该文档页里关于 **test 数据是否需提交（submit）到评测服务器**」的说明句 → 试过的入口 = 上述文档页全文（`grep -i "submit|submission|server|leaderboard"` 在 `docs_400f112c.html` 与抽件 `dota_docs.txt` 内零命中）；同页仅有 `split_test(` + `# Split test set, without labels.`（`:109-110`）与 `test: images/test # test images (optional) 937 images`（`:78`）两句涉及 test。
（另：`https://docs.ultralytics.com/datasets/detect/dotav1/` → HTTP **404**，无该路径页。）

#### 目标格：reported

**采到**（官方报告数字的产出位置与产出命令；官方来源中「we report on ⟨val|test|test-dev⟩」这一**句型**的逐字句 = NOT FOUND）。

逐字证据：

1. **官方 Results 页 · DOTA-v1.0 排行榜（报告数字的官方落点）**
   - 「DOTA-v1.0 Leaderboard」 | 出处: https://captain-whu.github.io/DOTA/results.html | 文件/段: `results.html:112`（`<h1 align="center">`）
   - 「Task1 - Oriented Object Detection」 | `results.html:113`
   - 「Task2 - Horizontal Object Detection」 | `results.html:152`
   - 表数据源（逐字）: `"ajax": "leaderboards/learderboard1.txt"` | `results.html:248`；`"ajax": "leaderboards/learderboard2.txt"` | `results.html:301`

2. **排行榜落盘文件（报告数字本体）**
   - 文件 `leaderboards/learderboard1.txt` 为 JSON，顶层键逐字 `data`，`data` 长度 324；单条字段名逐字含 `mAP`、`TeamNames`、`TeamMembers`、`Institute`、`description`、`date`、`created_date` 与 15 个类名键（`BD`、`BC`、`HC`、`LV`、`Harbor`、`Plane`、`RA`、`SBF`、`SP`、`ST`、`SV`、`Ship`、`TC`、`Bridge`、`GTF`）
     | 出处: https://cdn.jsdelivr.net/gh/CAPTAIN-WHU/DOTA@master/leaderboards/learderboard1.txt （HTTP 200，263,838 bytes）
   - 首条逐字片段：`{"BD": 0.874, "mAP": 0.824, "BC": 0.893, "HC": 0.798, "TeamNames": "DH_RSIA", ...}`

3. **报告数字所依据的测试集（官方 Tasks 页）**
   - 「You need to submit a zip file containing results for all test images for evaluation.」 | `tasks.html:115`（Task1）、`:164`（Task2）
   - 「For evaluation, you must registrate and submit on the Evaluation Server」 | `tasks.html:107-108`

4. **产生报告数字的官方命令（devkit 侧）**
   - `dota_evaluation_task1.py` 生效配置块（逐字）：`detpath = r'PATH_TO_BE_CONFIGURED/Task1_{:s}.txt'`（`:281`）/ `annopath = r'PATH_TO_BE_CONFIGURED/{:s}.txt' # change the directory to the path of val/labelTxt, if you want to do evaluation on the valset`（`:282`）/ `imagesetfile = r'PATH_TO_BE_CONFIGURED/valset.txt'`（`:283`）
     | 文件/段: `dota_evaluation_task1.py:281-283` | repo@commit: `CAPTAIN-WHU/DOTA_devkit@99388551054be9a6dabb01c8bb2a7eb562d57b4f`
   - 同文件 docstring 逐字：「Note, the evaluation is on the large scale images」 | `dota_evaluation_task1.py:11`
   - README 指引逐字：「Evaluating the result, you can refer to the "dota_evaluation_task1.py" and "dota_evaluation_task2.py" (or "dota-v1.5_evaluation_task1.py" and "dota-v1.5_evaluation_task2.py" for DOTA-v1.5)」 | `readme.md:57`

5. **Ultralytics 文档页产生数字的命令（val 走 `val: images/val` 458 张）**
   - `yolo obb train data=DOTAv1.yaml model=yolo26n-obb.pt epochs=100 imgsz=1024` | `docs_400f112c.html:166`
   - `results = model.train(data="DOTAv1.yaml", epochs=100, imgsz=1024)` | `docs_400f112c.html:122`
   - 同页 `val: images/val # val images (relative to 'path') 458 images` | `docs_400f112c.html:77`
   - 该页**无** `model.val(...)` 调用、**无** `split='test'`：`grep -n "model\.val\|split='test'\|split=&quot;test"` → 零命中。

6. **论文侧的报告口径句（逐字）**
   - 「We evaluate the state of the art object detection methods on DOTA.」 | 出处: https://ar5iv.labs.arxiv.org/html/1711.10398 | 文件/段: `dota_paper.txt:240`（§5 Evaluations 标题 `:239`）
   - 「To build a baseline for object detection in Earth Vision, we evaluate state-of-the-art object detection algorithms on DOTA.」 | `dota_paper.txt:29`（摘要）
   - 表题逐字：`Table 4: Numerical results (AP) of baseline models evaluated with HBB ground truths.` | `dota_paper.txt:334`；`Table 5: Numerical results (AP) of baseline models evaluated with OBB ground truths.` | `dota_paper.txt:436`
   - 跨数据集表头逐字出现 `Testing set` | `dota_paper.txt:469`（属 §6 cross-dataset 的 Table 6）

**NOT FOUND 子项**：官方来源中「we report on ⟨val|test|test-dev⟩」这一句型的逐字句。
试过的入口 = `https://ar5iv.labs.arxiv.org/html/1711.10398` 全文（`grep -i "we report\|report the result\|results on the test"` 零命中；`report` 仅命中页尾 UI 文本 `dota_paper.txt:688-689`）、`https://captain-whu.github.io/DOTA/results.html`、`.../tasks.html`、`.../evaluation.html`、`.../index.html`、`.../dataset.html`、`.../code.html`、`https://docs.ultralytics.com/datasets/obb/dota-v2/`、`https://arxiv.org/pdf/2102.12219`（DOTA-v2.0/TPAMI 论文；两次下载分别 `HTTP:000` 与 `HTTP:200` 但 PDF 截断，`pdftotext` → `Syntax Error: Couldn't read xref table`，未采用；且该文为 v2.0 论文，按任务边界未纳入）。

#### 镜像一致性交叉校验（DOTA 站，用于支撑 jsDelivr 取件可信）

- 前一轮（同目录 `e3_rows01_05.md`）从**直连** `https://captain-whu.github.io/DOTA/...` 取得的行号与本次 jsDelivr 镜像件**逐字同位置一致**：`dataset.html:238`、`:244`（`Testing images`）、`index.html:176-177`（v1.0 比例句）、`evaluation.html:139`、`:142`（Task1/Task2 Evaluation Server）、`evaluation.html:102`、`:107`（格式句 / 提交句，句跨 `:107-108`）。
- 镜像取件 URL 形如 `https://cdn.jsdelivr.net/gh/CAPTAIN-WHU/DOTA@master/<file>`；仓库 `CAPTAIN-WHU/DOTA` 存在性由 jsDelivr 包元数据 `https://data.jsdelivr.com/v1/packages/gh/CAPTAIN-WHU/DOTA@master`（HTTP 200，`"name": "CAPTAIN-WHU/DOTA", "version": "master"`）与 `git ls-remote https://github.com/CAPTAIN-WHU/DOTA HEAD` = `59cb20cfe8a42ff750c0985776b01f4d7e550e18` 双重确认。

---

#### R0c 补采证据（AutoDL 公共数据集区**实物清单**，2026-10-09；只读列举）

* **来源**：`/root/autodl-pub/DOTA/`。
* **目录结构（逐字）**：`train/{images, labelTxt-v1.0, labelTxt-v1.5}` · `val/{images, labelTxt-v1.0, labelTxt-v1.5}` ·
  **`test/` 下只有 `images/`（内含 `DOTA_test_part1.zip` 3,051,312,165 B · `DOTA_test_part2.zip` 3,614,455,386 B · `DOTA_test_test_info.json` 4,229,815 B）**。
* **★ 决定性事实**：**`test/` 没有任何 `labelTxt*` 目录**；而 `train/` 与 `val/` **各有** `labelTxt-v1.0`（内含 `labelTxt.zip` 与 `Train_Task2_gt.zip` / `Val_Task2_gt.zip`）与 `labelTxt-v1.5`。
  ⇒ **发布物按档位给出了 train 与 val 的 GT，test 只给图像**；`DOTA_test_test_info.json` 仅为测试信息清单（**非 GT**）。
* **用途**：`DOTA v1.0 · release`（与论文 §3.4「publicly provide … ground truth for training set and validation set, **but not for the testing set**」**互证**）。
### 卡 6 · DOTA v2.0

* **E1**：**`ultralytics` 无 `DOTAv2.yaml`（404）**；`DOTAv1.yaml:4` 的文档链接指向 `docs/dota-v2`，而 `:3` 自称 "DOTA 1.0"（**v1/v2 混写**）。
* **E2**：官方 `index.html` 逐字 **"11,268 images of DOTA are split into training, validation, test-dev, and test-challenge sets."** +
  **"Test-dev contains 2,792 images … not the ground truths."**
* **E3 报告口径**（论文 arXiv:2102.12219）：§IV-G3 逐字 **"All the DOTA-v2.0 experiments in this paper are evaluated on test-dev."**；
  TABLE VI 题注 **"…we use the DOTA-v2.0 test-dev set."**；`tasks.html` **"…results for all test images for evaluation."**
* **E4**：`dingjiansw101/AerialDetection@fbb7726b…`（`GETTING_STARTED.md:56` 与 `:72-74` 的 `tools/test.py` 命令；
  split 由 `configs/DOTA/faster_rcnn_RoITrans_r50_fpn_1x_dota.py:172-175` 的 `DOTA_test1024.json` 钉死）。
* **NOT FOUND**：无。

### 卡 7 · VisDrone-DET

* **E1**（`VisDrone.yaml:13-15` @ 同一 commit）：`train`(6471) · `val`(548) · **`test=images/test  # test-dev images(1610)`**。
* **E2**：官方仓 `README.md:21` 逐字 **"Note that the bounding box annotations of test-dev are avalialbe. Researchers can use test-dev to publish papers. testset-challenge … annotations is unavailable."**
* **E3 报告口径**（论文 arXiv:2001.06303）：§IV **"the test-dev subset is used as the default test set for public evaluation"** + §IV-D **"Results on the test-dev set."**
* **E4**：`VisDrone-Dataset@4364e826…`；`VisDrone2018-DET-toolkit@00544578…`（**纯 Matlab，无 CLI**）。
  **官方 CLI 命令 `NOT FOUND`**；镜像命令见 `SFFNet val.py:9-17`（`split='val'`）、`tph-yolov5 README:27/31`、`esod README:130/150`（test-dev）。
* **附带不一致（只报观测）**：`toolkit README:38` 只承认 training/validation/test-challenge 三套，**未含 test-dev**。

#### R0 补采证据（2026-10-08，逐字）

**[A]** ### 目标格：release
- **采到**
- 官方发布物清单 = 官方仓 `VisDrone/VisDrone-Dataset` 的 `## Download` 节，**逐条列出四个 DET 件**（trainset / valset / testset-dev / testset-challenge）：
- 逐字证据（**test-dev / test-challenge 的标注公开性，一句话给全**）: 「Note that the bounding box annotations of test-dev are avalialbe. Researchers can use test-dev to publish papers. testset-challenge is used for VisDrone2020 Challenge and the annotations is unavailable. 」 | 出处: https://raw.githubusercontent.com/VisDrone/VisDrone-Dataset/4364e8265275dfa44fd8f767b5180af58580194d/README.md | 文件/段: README.md:21
- 逐字证据（trainset 件）: 「* trainset (1.44 GB): [BaiduYun](https://pan.baidu.com/s/1K-JtLnlHw98UuBDrYJvw3A) | [GoogleDrive](https://drive.google.com/file/d/1a2oHjcEcwXP8oUF95qiwrqzACb2YlUhn/view?usp=sharing)」 | 出处: https://raw.githubusercontent.com/VisDrone/VisDrone-Dataset/4364e8265275dfa44fd8f767b5180af58580194d/README.md | 文件/段: README.md:27
- 逐字证据（valset 件）: 「* valset (0.07 GB):  [BaiduYun](https://pan.baidu.com/s/1jdK_dAxRJeF2Xi50IoML1g) | [GoogleDrive](https://drive.google.com/file/d/1bxK5zgLn0_L8x276eKkuYA_FzwCIjb59/view?usp=sharing)」 | 出处: https://raw.githubusercontent.com/VisDrone/VisDrone-Dataset/4364e8265275dfa44fd8f767b5180af58580194d/README.md | 文件/段: README.md:29
- 逐字证据（testset-dev 件，末尾 `(GT avalialbe)` 为原文拼写）: 「* testset-dev (0.28 GB): [BaiduYun](https://pan.baidu.com/s/1RdRfSWV-1IFK7aWljLU_LQ) | [GoogleDrive](https://drive.google.com/open?id=1PFdW_VFSCfZ_sTSZAGjQdifF_Xd5mf0V) (GT avalialbe)」 | 出处: https://raw.githubusercontent.com/VisDrone/VisDrone-Dataset/4364e8265275dfa44fd8f767b5180af58580194d/README.md | 文件/段: README.md:31
- 逐字证据（testset-challenge 件，**无 GT 标注说明**）: 「* testset-challenge (0.28 GB): [BaiduYun](https://pan.baidu.com/s/1lvEkCgy1WWK4B7TLki4yBQ) | [GoogleDrive](https://drive.google.com/file/d/1KN8R3oioOvSXH492GEVk-Hx74nWHAcXT/view?usp=sharing)」 | 出处: https://raw.githubusercontent.com/VisDrone/VisDrone-Dataset/4364e8265275dfa44fd8f767b5180af58580194d/README.md | 文件/段: README.md:33
- 逐字证据（官方 toolkit 入口，仅 Matlab）: 「* [Matlab beta](https://github.com/VisDrone/VisDrone2018-DET-toolkit)」 | 出处: https://raw.githubusercontent.com/VisDrone/VisDrone-Dataset/4364e8265275dfa44fd8f767b5180af58580194d/README.md | 文件/段: README.md:37

- 官方 toolkit 侧的发布物/标注公开性表述（与上条**并列**，口径不同，见下）：
- 逐字证据（**"三套数据"清单，未含 test-dev**）: 「For DET competition, there are three sets of data and labels: training data, validation data, and test-challenge data. There is no overlap between the three sets.」 | 出处: https://raw.githubusercontent.com/VisDrone/VisDrone2018-DET-toolkit/005445782213e20cb91bc50a597db3dd949e749a/README.md | 文件/段: README.md:38
- 逐字证据（三档图像数表）: 「      Dataset                            Training              Validation            Test-Challenge     ---------------------------------------------------------------------------------------------------       Object detection in images       6,471 images            548 images             1,580 images」 | 出处: https://raw.githubusercontent.com/VisDrone/VisDrone2018-DET-toolkit/005445782213e20cb91bc50a597db3dd949e749a/README.md | 文件/段: README.md:42-44
- 逐字证据（**标注公开范围**）: 「The challenge requires a participating algorithm to locate the target bounding boxes in each image. The objects to be detected are of various types including pedestrians, cars, buses, and trucks. We manually annotate the bounding boxes of different objects and ignored regiones in each image. Annotations on the training and validation sets are publicly available.」 | 出处: https://raw.githubusercontent.com/VisDrone/VisDrone2018-DET-toolkit/005445782213e20cb91bc50a597db3dd949e749a/README.md | 文件/段: README.md:46
- 逐字证据（下载入口需注册）: 「The link for downloading the data can be obtained by registering for the challenge at  http://www.aiskyeye.com/」 | 出处: https://raw.githubusercontent.com/VisDrone/VisDrone2018-DET-toolkit/005445782213e20cb91bc50a597db3dd949e749a/README.md | 文件/段: README.md:48-50

#### 目标格：protocol
- **采到**
- 官方论文（TPAMI，arXiv:2001.06303）§4 逐字给出协议：
- 逐字证据（**"用哪个测试集、标注是否扣留"一网打尽**）: 「for accessing the VisDrone dataset and perform evaluation of those four tasks. Notably, for each task, the images/videos in the training, validation, and testing subsets are captured at different locations, but share similar scenarios and attributes. The training subset is used to train the algorithms, the validation subset is used to validate the performance of algorithms, the test-challenge subset is used for workshop competition, and the test-dev subset is used as the default test set for public evaluation. We manually annotate the bounding boxes of different categories of objects in each image or frame. After that, crosschecking is conducted to ensure annotation quality. The annotated ground-truths for training and validation subsets are made available to participants, but the groundtruths of the testing subset are reserved in order to avoid (over)fitting of algorithms.」 | 出处: https://arxiv.org/pdf/2001.06303 | 文件/段: vd_paper.pdf → pdftotext:167（§4 数据集描述段）
- 逐字证据（DET 四档图像数）: 「The DET dataset consists of 10, 209 images in unconstrained challenging scenes, including 6, 471 images in the training subset, 548 in the validation subset, 1, 580 in the test-challenge subset, and 1, 610 in the test-dev subset. We plot the number of objects in different object categories with different occlusion degrees in Fig. 2. Notably, the class imbalance issue significantly affect the detection performance. For example, the number of the awning-tricycle instances is more than 40� less than the car instances.」 | 出处: https://arxiv.org/pdf/2001.06303 | 文件/段: vd_paper.pdf → pdftotext:176（§4.1）
- 逐字证据（ar5iv HTML 同句，供交叉核）: 「for accessing the VisDrone dataset and perform evaluation of those four tasks. Notably, for each task, the images/videos in the training, validation, and testing subsets are captured at different locations, but share similar scenarios and attributes. The training subset is used to train the algorithms, the validation subset is used to validate the performance of algorithms, the test-challenge subset is used for workshop competition, and the test-dev subset is used as the default test set for public evaluation. We manually annotate the bounding boxes of different categories of objects in each image or frame. After that, cross-checking is conducted to ensure annotation quality. The annotated ground-truths for training and validation subsets are made available to participants, but the ground-truths of the testing subset are reserved in order to avoid (over)fitting of algorithms.」 | 出处: https://ar5iv.labs.arxiv.org/html/2001.06303 | 文件/段: 2001.06303:621

- 官方 toolkit README 的协议/评测例程（**官方仅 Matlab，无 CLI**）：
- 逐字证据（三套、互不相交）: 「For DET competition, there are three sets of data and labels: training data, validation data, and test-challenge data. There is no overlap between the three sets.」 | 出处: https://raw.githubusercontent.com/VisDrone/VisDrone2018-DET-toolkit/005445782213e20cb91bc50a597db3dd949e749a/README.md | 文件/段: README.md:38
- 逐字证据（**官方评测例程 = `evalDET.m`，本地跑，需自备 GT 路径**）: 「Evaluation Routines  The notes for the folders:  evalDET.m is the main function used to evaluate your detector -please modify the dataset path and result path -use "isImgDisplay" to display the groundtruth and detections」 | 出处: https://raw.githubusercontent.com/VisDrone/VisDrone2018-DET-toolkit/005445782213e20cb91bc50a597db3dd949e749a/README.md | 文件/段: README.md:51-55
- 逐字证据（官方提交格式为 TXT）: 「DET Submission Format  Submission of the results will consist of TXT files with one line per predicted object.It looks as follows:       <bbox_left>,<bbox_top>,<bbox_width>,<bbox_height>,<score>,<object_category>,<truncation>,<occlusion>」 | 出处: https://raw.githubusercontent.com/VisDrone/VisDrone2018-DET-toolkit/005445782213e20cb91bc50a597db3dd949e749a/README.md | 文件/段: README.md:57-61
- 说明：论文 `:167` 与 toolkit `:38/:46` 在"标注公开范围"上一致（GT 只公开 train/val），但**集合命名不一致**（论文有 test-dev、toolkit 无）——仅记录观测。

- **附带不一致（只报观测，不下判断）**：`toolkit README:38` 只承认 training/validation/test-challenge 三套，**未含 test-dev**；而 `VisDrone-Dataset README:21` 与论文 `:167` 均以 test-dev 为公开测试集。
- **官方 CLI 评测命令：NOT FOUND**（官方 toolkit 全文仅 Matlab 例程；试过的入口见本节末）。

#### 目标格：yolo_dist
- **采到**（该格 yaml 的 `train:`/`val:`/`test:` 三行逐字 + 行号）
- 逐字证据（三键齐、互不相同）:
  - `train: images/train # train images (relative to 'path') 6471 images`
  - `val: images/val # val images (relative to 'path') 548 images`
  - `test: images/test # test-dev images (optional) 1610 images`
  | 出处: https://raw.githubusercontent.com/ultralytics/ultralytics/803c8b96c1a6fc0533434fc5be0e3e0a3d122482/ultralytics/cfg/datasets/VisDrone.yaml | 文件/段: ultralytics/cfg/datasets/VisDrone.yaml:13-15 @ `ultralytics/ultralytics@803c8b96c1a6fc0533434fc5be0e3e0a3d122482`
- 逐字证据（下载脚本；**明确忽略 test-challenge 档**）: 「  # Download (ignores test-challenge split)」 | 出处: https://raw.githubusercontent.com/ultralytics/ultralytics/803c8b96c1a6fc0533434fc5be0e3e0a3d122482/ultralytics/cfg/datasets/VisDrone.yaml | 文件/段: VisDrone.yaml:73
- 逐字证据（下载 URL 列表：train/val/test-dev 三个 zip，test-challenge 被注释掉）: 「  urls = [       f"{ASSETS_URL}/VisDrone2019-DET-train.zip",       f"{ASSETS_URL}/VisDrone2019-DET-val.zip",       f"{ASSETS_URL}/VisDrone2019-DET-test-dev.zip",       # f"{ASSETS_URL}/VisDrone2019-DET-test-challenge.zip",   ]」 | 出处: https://raw.githubusercontent.com/ultralytics/ultralytics/803c8b96c1a6fc0533434fc5be0e3e0a3d122482/ultralytics/cfg/datasets/VisDrone.yaml | 文件/段: VisDrone.yaml:75-80
- 逐字证据（test-dev 目录 → yaml 的 `test` 档）: 「  splits = {"VisDrone2019-DET-train": "train", "VisDrone2019-DET-val": "val", "VisDrone2019-DET-test-dev": "test"}」 | 出处: https://raw.githubusercontent.com/ultralytics/ultralytics/803c8b96c1a6fc0533434fc5be0e3e0a3d122482/ultralytics/cfg/datasets/VisDrone.yaml | 文件/段: VisDrone.yaml:84
- 逐字证据（同 yaml 第 4 行指向的官方文档页）: 「# Documentation: https://docs.ultralytics.com/datasets/detect/visdrone」 | 出处: https://raw.githubusercontent.com/ultralytics/ultralytics/803c8b96c1a6fc0533434fc5be0e3e0a3d122482/ultralytics/cfg/datasets/VisDrone.yaml | 文件/段: VisDrone.yaml:4

- 该 yaml 的官方文档页（E2），逐字：
- 逐字证据（**test 档性质：held-out / 用于最终评估**）: 「Split Images Description Train 6,471 Labeled aerial images used to train the detector Validation 548 Images used for evaluation during development Test-dev 1,610 Held-out images for final evaluation of the trained model」 | 出处: https://docs.ultralytics.com/datasets/detect/visdrone/ | 文件/段: docs_visdrone.html:46
- 逐字证据（**第四档 test-challenge 被扣留、不下载**）: 「A fourth split, test-challenge (1,580 images), is withheld for the VisDrone competition and is not downloaded, which is why the full DET set totals 10,209 images.」 | 出处: https://docs.ultralytics.com/datasets/detect/visdrone/ | 文件/段: docs_visdrone.html:47
- 逐字证据（文档页内嵌 yaml 三行原文）: 「train: images/train # train images (relative to 'path') 6471 images val: images/val # val images (relative to 'path') 548 images test: images/test # test-dev images (optional) 1610 images」 | 出处: https://docs.ultralytics.com/datasets/detect/visdrone/ | 文件/段: docs_visdrone.html:70-72
- 逐字证据（文档页下载说明与代码）: 「# Download (ignores test-challenge split) dir = Path(yaml["path"]) # dataset root dir urls = [ f"{ASSETS_URL}/VisDrone2019-DET-train.zip", f"{ASSETS_URL}/VisDrone2019-DET-val.zip", f"{ASSETS_URL}/VisDrone2019-DET-test-dev.zip", # f"{ASSETS_URL}/VisDrone2019-DET-test-challenge.zip",」 | 出处: https://docs.ultralytics.com/datasets/detect/visdrone/ | 文件/段: docs_visdrone.html:128-134
- 逐字证据（文档页训练命令示例）: 「results = model.train(data="VisDrone.yaml", epochs=100, imgsz=640) To label additional aerial images and manage VisDrone training runs in your browser, use Ultralytics Platform.」 | 出处: https://docs.ultralytics.com/datasets/detect/visdrone/ | 文件/段: docs_visdrone.html:148

- 交叉核验：以 commit 钉住的同一文件经 `cdn.jsdelivr.net/gh/ultralytics/ultralytics@803c8b96…/ultralytics/cfg/datasets/VisDrone.yaml` 取回，第 13-15 行逐字与上完全一致（HTTP 200）。

#### 目标格：reported
- **采到**（官方论文逐字给出"报在 test-dev（并另报 test-challenge）"）
- 逐字证据（DET 结果节标题）: 「4.4 Results and Analysis」 | 出处: https://arxiv.org/pdf/2001.06303 | 文件/段: vd_paper.pdf → pdftotext:208（**§4.4 Results and Analysis**）
- 逐字证据（**报在 test-challenge 的那一节**；双栏致 pdftotext 拆行，此处合引）: 「Results on the test-challenge set. Top 10 object detec-」 … 「tors in the VisDrone-DET2018 [7], VisDrone-DET2019 [10] and VisDrone-DET2020 [14] challenges are presented in Table 2. In contrast to existing object detection datasets, e.g., MS COCO [19] and UA-DETRAC [23], one of the most challenging issues in the VisDrone-DET dataset is the extremely small scale of objects.」 | 出处: https://arxiv.org/pdf/2001.06303 | 文件/段: vd_paper.pdf → pdftotext:209 与 :356
- 逐字证据（**报在 test-dev 的那一节 + 该节产生的数字**）: 「In the VisDrone-DET2020 challenge [14], the use of the Cascade R-CNN [58] framework has become wide-spread due to its high performance and easy extensibility. Compared with the baseline Cascade R-CNN [58] with the mAP score of 16.09%, the submitted varaints largely improve the performance by combining several effective modules. DroneEye2020 is mainly based on Cascade R-CNN [58] with recursive feature pyramid and switchable strous convolution [79], achieving the best performance with 34.57 mAP. TAUN uses mean teacher [96] to train the cascade DetectoRS model [58], [79], which performs similarly as DroneEye2020. CDNet and CascadeAdapt combine Cascade R-CNN [58] with deformable convolutions, and then improve the detection accuracy using several data augmentation strategies such as sub-image splitting and mosaic [68]. These results indicate that the detection accuracy of small objects can be improved by enhancing IoU thresholds to train multiple localization branches. Results on the test-dev set. For the test-dev set, CornerNet [93] achieves the top AP score of 23.43%, which uses the Hourglass-104 backbone for feature extraction. In contrast to FPN [61] and RetinaNet [64] with extra stages against the image classification task to handle objects with various scales, DetNet [78] re-designs the backbone network for object detection, which maintains the spatial resolution and enlarges the receptive field, achieving 20.07% AP score. Meanwhile, RefineDet [64] with the VGG-16 backbone performs better than RetinaNet [63] with the ResNet-101 backbone, i.e., 19.89% vs. 18.94% in terms of AP score. This is because RefineDet [64] uses the object detection module to regress the locations and sizes of objects based on the coarsely adjusted anchors from the anchor refinement module.」 | 出处: https://arxiv.org/pdf/2001.06303 | 文件/段: vd_paper.pdf → pdftotext:363
- 逐字证据（ar5iv HTML 小节标题，供交叉核）: 「Results on the test-challenge set.」 | 出处: https://ar5iv.labs.arxiv.org/html/2001.06303 | 文件/段: 2001.06303:1152
- 逐字证据（ar5iv HTML 同上）: 「Results on the test-dev set.」 | 出处: https://ar5iv.labs.arxiv.org/html/2001.06303 | 文件/段: 2001.06303:1170
- 逐字证据（ar5iv HTML 小节编号）: 「IV-D Results and Analysis」 | 出处: https://ar5iv.labs.arxiv.org/html/2001.06303 | 文件/段: 2001.06303:1149

- **产生报告数字的命令：NOT FOUND**（官方无论文附带 CLI；镜像命令见卡 7 已录 `SFFNet val.py:9-17` / `tph-yolov5 README:27,31` / `esod README:130,150`——本次未采，因不属该基准的署名工件）。

---
### 卡 8 · AI-TOD

* **E1（本行的判定依据就是"矛盾"，两处均逐字）**：
  * `Chasel-Tsui/mmdet-aitod README.md:2`：**"We have now released the full sets (trainval, test) of AI-TOD-v2!"**
  * `Chasel-Tsui/mmdet-aitod README.md:21`：**"In this stage, we only release the train, val annotations of the AI-TOD-v2, the test annotations will be used to hold further competitions."**
  * 跨仓第三处：`jwwangchn/AI-TOD README.md:80`：**"Training, Validation and Testing sets are both publicly available now."**
* **E2**：同上（README 即官方文档）。
* **E3 报告口径**（**镜像内也自相矛盾**）：`mmdet-nwdrka/README.md:33` **"Table 1. Training Set: AI-TOD-v2 trainval set, Validation Set: AI-TOD-v2 test set"**（即报 test）；
  但 `:43-44` 又称报 val。
* **E4**：`jwwangchn/AI-TOD@7f56cb6b…`（master）；`Chasel-Tsui/mmdet-aitod@e3e56711…`（main）；
  官方镜像 config 三套口径：`aitodv2_detection.py:33-47`（train=trainval / **val=test** / test=test）·
  `aitodv2train_detection.py:36-50`（train=train / val=val / test=val）· `aitod_detection.py:33-47`（train=trainval / val=test / test=test）。

### 卡 9 · UAVDT

* **E1**：**无官方 Ultralytics yaml**。三个镜像：
  * `SFFNet ultralytics/cfg/datasets/UAVDT.yaml:1-4`：三键**全空**；
  * `alibaba/esod data/uavdt.yaml:2-4`：`train=train_ds.txt` / **`val=test_ds.txt`** / `test=test.txt`（**键名与文件名冲突**）；
  * `forever208/yolov5_train_on_UAVDT data/UAVDT.yaml:11-14`：`test` 键**为空**。
* **E2**：官方 ECCV 2018 论文（arXiv:1804.00518）§2.1 逐字 **"…divided into training and testing sets, with 30 and 70 sequences, respectively…"**。
* **E3 报告口径**：同上论文 §3 逐字 **"All the algorithms are trained on the training set and evaluated on the testing set."**
* **E4**：官方 **NOT FOUND**（无官方 GitHub 仓；官方项目页 `sites.google.com` 连接失败；`esod README:159` 逐字 **"UAVDT : coming soon."**）。
  镜像：`dronefreak/DetectionBench` `.github/README.md:171` + `configs/dataset/uavdt.yaml:35` **`eval_split: test`** + `configs/uavdt_yolo.yaml:70`。
  commit：`CQNU-ZhangLab/SFFNet@1e6a3c9c…` · `alibaba/esod@bde3571b…` · `forever208/yolov5_train_on_UAVDT@a14a4629…` · `dronefreak/DetectionBench@68a01c3f…`。

#### R0 补采证据（2026-10-08，逐字）

**[A]** ### 目标格：release
- **NOT FOUND**（官方发布物清单未采到：官方项目页整域不可达，无官方仓）
- 唯一采到的**官方"发布物在哪"陈述**（仍不构成发布物清单，故本格记 NOT FOUND）：
- 逐字证据: 「       comprehensively. The dataset and all the experimental results are avail-        able in https://sites.google.com/site/daviddo0323/.」 | 出处: https://openaccess.thecvf.com/content_ECCV_2018/papers/Dawei_Du_The_Unmanned_Aerial_ECCV_2018_paper.pdf | 文件/段: uavdt_eccv.pdf → pdftotext:50-51（§1 Introduction 末）
- 逐字证据（官方公布的量级，非文件清单）: 「The UAVDTbenchmark consists of 100 video sequences, which are selected from over 10 hours of videos taken with an UAV platform at a number of locations in urban areas, representing various common scenes including squares, arterial streets, toll stations, highways, crossings and T-junctions. The average, min, max length of a sequence are 778.69, 83 and 2, 970 respectively. The videos are recorded at 30 frames per seconds (fps), with the resolution of 1080 � 540 pixels.」 | 出处: https://openaccess.thecvf.com/content_ECCV_2018/papers/Dawei_Du_The_Unmanned_Aerial_ECCV_2018_paper.pdf | 文件/段: uavdt_eccv.pdf → pdftotext:115-120（§2 UAVDT Benchmark）
- 逐字证据（标注规模）: 「For annotation, we ask over 10 domain experts to label our dataset using the vatic tool7 for two months. With several rounds of double-check, the annotation errors are reduced as much as possible. Specifically, about 80, 000 frames in the UAVDTbenchmark dataset are annotated over 2, 700 vehicles with 0.84 million bounding boxes. According to PASCAL VOC [16], the regions that cover too」 | 出处: https://openaccess.thecvf.com/content_ECCV_2018/papers/Dawei_Du_The_Unmanned_Aerial_ECCV_2018_paper.pdf | 文件/段: uavdt_eccv.pdf → pdftotext:169-173（§2.1 Data Annotation）
- 逐字证据（结论段重申）: 「In this paper, we construct a new and challenging UAV benchmark for 3 foun- dational visual tasks including DET, MOT and SOT. The dataset consists of 100 videos (80k frames) captured with UAV platform from complex scenarios. All frames are annotated with manually labelled bounding boxes and 3 circum- stances attributes, i.e., weather condition, flying altitude, and camera view. SOT dataset has additional 8 attributes, e.g., background clutter, camera rotation and」 | 出处: https://openaccess.thecvf.com/content_ECCV_2018/papers/Dawei_Du_The_Unmanned_Aerial_ECCV_2018_paper.pdf | 文件/段: uavdt_eccv.pdf → pdftotext:680-685（§5 Conclusion）

- **试过的入口（全部）**：
  - https://sites.google.com/view/uavdt — 官方项目页（新 Sites），`curl -sI` = 000（整域不可达）
  - https://sites.google.com/site/daviddo0323/ — ECCV 论文逐字给出的官方地址，000
  - https://sites.google.com/site/daviddo0323/projects/uavdt — 项目子页，000
  - https://sites.google.com/ — 整域探测，000
  - http://archive.org/wayback/available?url=sites.google.com/view/uavdt — 超时（无输出）
  - http://archive.org/wayback/available?url=sites.google.com/site/daviddo0323/projects/uavdt — 超时
  - https://web.archive.org — 000（Wayback 整域不可达）
  - https://raw.githubusercontent.com/DaweiDu/UAVDT/refs/heads/main/README.md — 000（超时）
  - https://raw.githubusercontent.com/DaweiDu/UAVDT/refs/heads/master/README.md — 404
  - https://raw.githubusercontent.com/VisDrone/UAVDT/{main,master}/README.md — 000（超时）
  - https://raw.githubusercontent.com/VisDrone/UAVDT-Dataset/main/README.md — 000（超时）
  - https://raw.githubusercontent.com/uavdt/UAVDT/main/README.md — 404
  - git ls-remote https://ghproxy.net/https://github.com/DaweiDu/UAVDT HEAD — 空（无该仓）
  - git ls-remote https://ghproxy.net/https://github.com/VisDrone/UAVDT HEAD — 超时
  - https://ghproxy.net/https://github.com/ultralytics/ultralytics/commits/main.atom — 403（代理拒绝 HTML/atom，git 协议可用）
  - https://r.jina.ai/https://sites.google.com/view/uavdt — 000（代理不可达）
  - https://api.allorigins.win/raw?url=…sites.google.com/view/uavdt — 408
  - https://api.codetabs.com/v1/proxy?quest=…sites.google.com/… — 522
  - https://api.cors.lol/?url=… — 429
  - https://corsproxy.io/?url=… — 401（需 key）
  - https://thingproxy.freeboard.io/fetch/… — 000
  - https://urlreq.appspot.com/req?method=GET&url=… — 000
  - http://www.aiskyeye.com/ → https://aiskyeye.com/ — 200（VisDrone 官方站；全文无 UAVDT 条目，只有 VISDRONE）
  - https://openaccess.thecvf.com/content_ECCV_2018/papers/Dawei_Du_The_Unmanned_Aerial_ECCV_2018_paper.pdf — 200（官方论文；只给项目页地址，无发布物清单）
  - https://arxiv.org/abs/1804.00518 — 200（同上，无发布物清单）
  - https://ar5iv.labs.arxiv.org/html/1804.00518 — 200（同上）
  - 第三方（**非官方，不构成 release 证据面，仅记录**）：https://openxlab.org.cn/datasets/OpenDataLab/UAVDT · https://opendatalab.com/OpenDataLab/UAVDT · https://raw.githubusercontent.com/dataset-ninja/uavdt/refs/heads/main/DOWNLOAD.md（本次 000/301，未取回）

#### 目标格：protocol
- **采到**（官方协议文本关于"用哪个测试集、怎么评测"的原句）
- 逐字证据（**划分与测试集构成**）: 「    Notably, our benchmark is divided into training and testing sets, with 30 and 70 sequences, respectively. The testing set consists of 20 sequences for both DET and MOT tasks, and 50 for SOT task. Besides, training videos are taken at dif- ferent locations from the testing videos, but share similar scenes and attributes. This setting reduces the overfitting probability to particular scenario.」 | 出处: https://openaccess.thecvf.com/content_ECCV_2018/papers/Dawei_Du_The_Unmanned_Aerial_ECCV_2018_paper.pdf | 文件/段: uavdt_eccv.pdf → pdftotext:250-254（§2）
- 逐字证据（**"在训练集上训练、在测试集上评测"**）: 「We run a representative set of state-of-the-art algorithms for each task. Codes for these methods are either available online or from the authors. All the algorithms are trained on the training set and evaluated on the testing set. Interestingly,」 | 出处: https://openaccess.thecvf.com/content_ECCV_2018/papers/Dawei_Du_The_Unmanned_Aerial_ECCV_2018_paper.pdf | 文件/段: uavdt_eccv.pdf → pdftotext:291-293（§3 Evaluation and Analysis）
- 逐字证据（**评测指标**）: 「Metrics. We follow the strategy in the PASCAL VOC challenge [16] to compute the Average Precision (AP) score in the Precision-Recall plot to rank the perfor- mance of DET methods. As performed in KITTI-D [19], the hit/miss threshold of the overlap between a pair of detected and groundtruth bounding boxes is set to 0.7.」 | 出处: https://openaccess.thecvf.com/content_ECCV_2018/papers/Dawei_Du_The_Unmanned_Aerial_ECCV_2018_paper.pdf | 文件/段: uavdt_eccv.pdf → pdftotext:311-315（§3.1 Metrics）
- 逐字证据（训练集/测试集不同地点）: 「and MOT tasks, and 50 for SOT task. Besides, training videos are taken at dif- ferent locations from the testing videos, but share similar scenes and attributes. This setting reduces the overfitting probability to particular scenario.」 | 出处: https://openaccess.thecvf.com/content_ECCV_2018/papers/Dawei_Du_The_Unmanned_Aerial_ECCV_2018_paper.pdf | 文件/段: uavdt_eccv.pdf → pdftotext:252-254
- 逐字证据（ar5iv HTML 同句，供交叉核）: 「Notably, our benchmark is divided into training and testing sets, with 30 30 and 70 70 sequences, respectively. The testing set consists of 20 20 sequences for both DET and MOT tasks, and 50 50 for SOT task. Besides, training videos are taken at different locations from the testing videos, but share similar scenes and attributes. This setting reduces the overfitting probability to particular scenario.」 | 出处: https://ar5iv.labs.arxiv.org/html/1804.00518 | 文件/段: 1804.00518:559
- 逐字证据（ar5iv HTML 同句，供交叉核）: 「We run a representative set of state-of-the-art algorithms for each task. Codes for these methods are either available online or from the authors. All the algorithms are trained on the training set and evaluated on the testing set. Interestingly, we find that some high ranking algorithms in other datasets may fail in complex scenarios.」 | 出处: https://ar5iv.labs.arxiv.org/html/1804.00518 | 文件/段: 1804.00518:591

- **检索观测（只报事实，不下判断）**：对官方 ECCV 全文（852 行 pdftotext 文本）检索 `submit` / `leaderboard` / `withhold` / `reserved`，**均无命中**；`not available` 仅 1 处（`:540`，指表格单元格数据缺失，非标注扣留）：
- 逐字证据: 「the data is not available.」 | 出处: https://openaccess.thecvf.com/content_ECCV_2018/papers/Dawei_Du_The_Unmanned_Aerial_ECCV_2018_paper.pdf | 文件/段: uavdt_eccv.pdf → pdftotext:540
- **官方发布/评测服务入口：NOT FOUND**（同 release 格的入口列表）。

#### 目标格：reported
- **采到**（官方论文里"报告在 testing set"的那一节与那句）
- 逐字证据（报告节标题）: 「3 Evaluation and Analysis」 | 出处: https://openaccess.thecvf.com/content_ECCV_2018/papers/Dawei_Du_The_Unmanned_Aerial_ECCV_2018_paper.pdf | 文件/段: uavdt_eccv.pdf → pdftotext:289（§3 Evaluation and Analysis）
- 逐字证据（DET 子节标题）: 「3.1 Object Detection」 | 出处: https://openaccess.thecvf.com/content_ECCV_2018/papers/Dawei_Du_The_Unmanned_Aerial_ECCV_2018_paper.pdf | 文件/段: uavdt_eccv.pdf → pdftotext:296（§3.1 Object Detection）
- 逐字证据（**"报告在 testing set"**）: 「are trained on the training set and evaluated on the testing set. Interestingly,」 | 出处: https://openaccess.thecvf.com/content_ECCV_2018/papers/Dawei_Du_The_Unmanned_Aerial_ECCV_2018_paper.pdf | 文件/段: uavdt_eccv.pdf → pdftotext:293
- 逐字证据（**产生 DET 报告数字的图：在 testing set 上**）: 「Fig. 3. Precision-Recall plot on the testing set of the UAVDT-DET dataset. The legend presents the AP score and the GPU/CPU speed of each DET method respectively.」 | 出处: https://openaccess.thecvf.com/content_ECCV_2018/papers/Dawei_Du_The_Unmanned_Aerial_ECCV_2018_paper.pdf | 文件/段: uavdt_eccv.pdf → pdftotext:306-307（Fig. 3 题注）
- 逐字证据（**该图/节产生的数字**）: 「Overall Evaluation Figure 3 shows the quantitative comparisons of DET methods, which shows no promising accuracy. For example, R-FCN obtains 70.06% AP score even in the hard set of KITTI-D9, but only 34.35% in our dataset. This maybe our dataset contains a large number of small objects due」 | 出处: https://openaccess.thecvf.com/content_ECCV_2018/papers/Dawei_Du_The_Unmanned_Aerial_ECCV_2018_paper.pdf | 文件/段: uavdt_eccv.pdf → pdftotext:327-330（Overall Evaluation）
- 逐字证据（**产生报告数字的实现细节口径**）: 「Implementation Details. We train all DET methods on a machine with CPU i9 7900x and 64G memory, as well as a Nvidia GTX 1080 Ti GPU. Faster-RCNN and R-FCN are fine-tuned on the VGG-16 network and Resnet-50, respectively. We use 0.001 as the learning rate for the first 60k iterations and 0.0001 for the next 20k iterations. For region-free methods, the batch size is 5 for 512 � 512 model according to the GPU capacity. For SSD, we use 0.005 as the learning rate for 120k iterations. For RON, we use the 0.001 as the learning rate for the first 90k iterations, then we decay it to 0.0001 and continue training for the next 30k iterations. For all the algorithms, we use a momentum of 0.9 and a weight decay of 0.0005.」 | 出处: https://openaccess.thecvf.com/content_ECCV_2018/papers/Dawei_Du_The_Unmanned_Aerial_ECCV_2018_paper.pdf | 文件/段: uavdt_eccv.pdf → pdftotext:316-325（Implementation Details）
- 逐字证据（ar5iv HTML 同句，供交叉核）: 「Figure 3: Precision-Recall plot on the testing set of the UAVDT-DET dataset. The legend presents the AP score and the GPU/CPU speed of each DET method respectively.」 | 出处: https://ar5iv.labs.arxiv.org/html/1804.00518 | 文件/段: 1804.00518:594

- **产生报告数字的命令：NOT FOUND**（官方无论文附带脚本、无官方仓；四个 baseline 为 Faster-RCNN / R-FCN / SSD / RON，论文未给可执行命令）。

---
### 卡 10 · xView

* **E1**（`ultralytics/cfg/datasets/xView.yaml:13-15`）：**无 `test` 键**；仅 `train=images/autosplit_train.txt` / `val=images/autosplit_val.txt`
  （即 847 张有标注 train 的 90/10），**不使用官方 282 张 `val_images`** ⇒ 与官方"val"**不是同一批图**。
* **E2**：官方 challenge 站（Vue SPA，逐字文本在 `/static/js/app.ddc604566a3ed108624c.js`）逐字：
  **"The private test set will be used to evaluate final submissions after the Challenge deadline."** ·
  **"Validation set : val_images.zip. Solvers should run inference code against these inputs …"** ·
  **"val_images.zip contains 282 images of a validation set … Labels are not available for the validation set."**
* **E3 报告口径**：`DIUx-xView/xView1_baseline scoring/score.bash:7` **`export groundtruth=$(ls /pfs/validate_labels -1)`** +
  `:17` **`python score.py /pfs/$input_repo/ $groundtruth --output /pfs/out/$timestamp`**（评测口径 = validation）。
* **E4**：`DIUx-xView/xView1_baseline@8efe3407…`（注：`DIUx-xView/xView-baseline` 不存在，404）。

#### 补采证据（2026-10-08，逐字）

- 目标: 官方是否声明"报告/评测在 validation 还是 test"；官方 challenge 站或 `DIUx-xView` 组织下 README/FAQ 里关于 **test 集如何评测、是否需提交** 的逐字句。
- 结果: **采到**（官方 challenge 站 FAQ/Tutorial/规则正文 + 官方 `DIUx-xView` 仓 README/评分脚本）。
- 逐字证据:

  1. 「For each submission, your containerized code is used to perform inference over the images in the validation dataset, producing a set of bounding box predictions for each input image. Then a mean average precision (mAP) score is computed across all the bounding box predictions. Submissions are ranked by mAP.」
     | 出处: https://challenge.xviewdataset.org/ （Tutorial/FAQ 正文，SPA 客户端渲染） | 文件: `app.js:1`（= `https://challenge.xviewdataset.org/static/js/app.ddc604566a3ed108624c.js`，HTTP 200，157,513 bytes；单行压缩文件，共 2 行；按字符偏移定位：offset 24152）

  2. 「When your solution is submitted to the xView platform and evaluated on the validation set, it is parallelized and run many times to perform inference over the whole set of validation images. Each time your code is run, it sees a single input image, and should produce a single output file containing your predictions for the given input.」
     | 出处: 同上 | 文件: `app.js:1`（offset 108740）

  3. 「When you submit a containerized solution through the app, your container is evaluated on the validation set. This dataset is quite large, so it may take some time for scores to be evaluated.」
     | 出处: 同上 | 文件: `app.js:1`（offset 109580）

  4. 「Holdout test set : after the Challenge deadline, a private leaderboard will be computed using this holdout set. Neither images nor labels from the holdout set are available for download.」
     | 出处: 同上（Tutorial Step 1「Download data」正文） | 文件: `app.js:1`（offset 105012）

  5. 「12. Leaderboard results. Results from the public leaderboard, as displayed on Challenge website pages, are provided for informational purposes only. The public leaderboard does not determine winners or eligibility for monetary incentives or awards. Final proposed solutions will be scored on a separate private test dataset, evaluated by the Challenge Sponsor to determine winners and eligibility for monetary incentives.」
     | 出处: 同上（Rules 正文） | 文件: `app.js:1`（offset 88605）

  6. 「Prizes will be awarded according based on a Solvers’ final proposed solution. While Solvers may submit and receive a score on the leaderboard for multiple proposed solutions throughout the course of the Challenge, final proposed solutions will be evaluated at the conclusion of the Challenge using the xView test data.」
     | 出处: 同上（Rules 正文） | 文件: `app.js:1`（offset 60156）

  7. 「Q: How do I submit my solution? … The challenge deadline has passed, so submission evaluation functionality is no longer available. You can still login to view your submissions, view other information about the challenge, download data, etc.」
     | 出处: 同上（FAQ 正文） | 文件: `app.js:1`（offset 139033）

  8. 「The private test set will be used to evaluate final submissions after the Challenge deadline.」（同页 Dataset 描述，与上一轮 (a) 同源）
     | 出处: 同上 | 文件: `app.js:1`（offset 77753）

  9. 「Labels are not available for the validation set. Because the validation images are available for download, you can also evaluate your predictions locally on your own.」
     | 出处: 同上（Tutorial 正文） | 文件: `app.js:1`（offset 101030）

  10. 「which is the proper format for submitting to the xView challenge portal.」
      | 出处: https://raw.githubusercontent.com/DIUx-xView/xView1_baseline/master/README.md | 文件: `README.md:14`

  11. 「The 'scoring/' folder contains code for evaluating a set of predictions (exported from 'create_detections.py' or 'create_detections.sh') given a ground truth label geojson.」
      | 出处: 同上 | 文件: `README.md:16`

  12. 官方评分脚本的 ground-truth 目录与入口（逐字两行）：
      `export groundtruth=$(ls /pfs/validate_labels -1)` / `python score.py /pfs/$input_repo/ $groundtruth --output /pfs/out/$timestamp`
      | 出处: https://raw.githubusercontent.com/DIUx-xView/xView1_baseline/master/scoring/score.bash | 文件: `scoring/score.bash:7`（ground truth）、`:17`（入口命令）；同仓 `README.md:16` 亦逐字见上

  13. `DIUx-xView` 组织下全部 17 个仓（发现性清单，未取 sha）：`xView1_baseline`、`data_utilities`、`xView2_baseline`、`xView2_scoring`、`xView2_first_place`、`xView2_second_place`、`xView2_third_place`、`xView2_fourth_place`、`xView2_fifth_place`、`xView2-deploy`、`xview3-reference`、`xView3_first_place`、`xView3_second_place`、`xView3_third_place`、`xView3_fourth_place`、`xView3_fifth_place`、`SARFish`。
      其中 `xView2_scoring/README.md` 全文逐字仅 3 行：「# xview2-metrics」/「Reference code showing how scores/metrics are computed for the xView2 Challenge」/「See https://xview2.org for more information.」
      | 出处: https://api.github.com/orgs/DIUx-xView/repos?per_page=100 ；https://raw.githubusercontent.com/DIUx-xView/xView2_scoring/master/README.md | 文件: 响应清单 / `README.md:1-3`

- 备注（仅事实定位，不作判断）:
  - challenge 站为 Vue SPA，静态 HTML 仅 `<div id=app></div>`，上述正文均位于 `app.js` 的字符串字面量中；`app.js` 为**单行压缩**（`wc -l` = 2），故以 `:1` + 字符偏移给出定位。
  - 官方站内同时存在两类表述：**提交后即时评测＝validation set**（证据 1/2/3），**赛后最终评奖＝private test/holdout set**（证据 4/5/6）；官方 2018 规则原文另要求提交容器镜像（证据 7 的 FAQ、`app.js` 内 `Transmitting submission...`、`My Submissions`、`Error 201/202/203` 等错误码段落）。

---


### 卡 11 · DIOR

* **E1**（镜像 `Hamedlk80/DIOR-R-Rotated-Object-Detection-YOLOv8@6be5a006533e7b6a985f38d0004eaf58afcb8881`
  `diorr_obb_analysis/data.yaml:1-4`）：只有 `train:` / `val:`，**无 `test:`**。
* **E2**：官方页 `gcheng-nwpu.github.io` 的 DIOR / DIOR-R 段落（只给下载链接）。
* **E3 报告口径**（论文 arXiv:1909.00133）：§5.1 p.12 + **Table 3 表题 p.14 逐字 "…on the proposed DIOR test set."**
* **E4**：官方**无代码仓**；镜像 notebook `Colab_DIORR_YOLO.ipynb:1219-1224 / 1231-1232` 逐字 **`model.val(..., split='val')`**。
* **采集层提醒**：任务书早先写的 `Hamedlk80/DIOR-R-Object-Detection` **不存在**（404 / "Repository not found"，重试 2 次）；
  实际仓为 `…-YOLOv8` 那个。

#### R0 补采证据（2026-10-08，逐字）

**[B]** ### 目标格：release

**部分采到**：官方站/论文侧的**发布物口径句**与**下载入口**已采到；**发布物清单本体**（具体有哪些切分件/压缩包/目录、test 件是否含标注、是否需提交）= **NOT FOUND**（官方只给 Google Drive / BaiduNetDisk 链接，两个链接页本次均取不到文件清单）。

逐字证据：

1. **官方站 DIOR 段全文（逐字，共 3 句 + 1 条下载句；无文件清单、无 test 标注句、无提交/服务器句）**
   - 「"DIOR" is a large-scale benchmark dataset for object detection in optical remote sensing images, which consists of 23,463 images and 192,518 object instances annotated with horizontal bounding boxes.」
     | 出处: https://gcheng-nwpu.github.io/ （直连 HTTP:000；镜像件 `nwpu_9b9a09.html` = `https://cdn.jsdelivr.net/gh/gcheng-nwpu/gcheng-nwpu.github.io@master/index.html`，HTTP 200，43,686 bytes） | 文件/段: `nwpu_9b9a09.html:513-514`
   - 「"DIOR-R" is an extended version of DIOR annotated with oriented bounding boxes, which shares the same images with DIOR. Both of the two datasets are freely available under the [CC BY-NC 4.0] license agreement.」 | `nwpu_9b9a09.html:515`
   - 「The dataset can be downloaded from Google Drive or BaiduNetDisk .」 + 两个链接
     | `nwpu_9b9a09.html:519`
     - Google Drive = `https://drive.google.com/open?id=1UdlgHk49iu6WpcJ5467iT-UqNPpx__CC`
     - BaiduNetDisk = `https://pan.baidu.com/s/1iLKT0JQoKXEJTGNxt5lSMg`
   - 段标题逐字 `DIOR and DIOR-R datasets` | `nwpu_9b9a09.html:512`
   - 该段所在引用条目逐字（2020 ISPRS）：`[paper] [DIOR dataset]`（**无 `[code]`**）| `nwpu_9b9a09.html:419`；对照 DIOR-R 条目为 `[paper] [code] [DIOR-R dataset]` | `:389`
   - 全页 `grep -i "test|valid|train|split"` 在 `nwpu_page.txt`（273 行抽件）内仅命中无关行（NWPU-Captions / MAR20 等条目）。

2. **论文侧公开性句 + 官方旧入口脚注（逐字）**
   - 「This motivates us to create a large‐scale dataset named DIOR. It is publicly available2 and can be used freely for object detection in optical remote sensing images.」
     | 出处: https://arxiv.org/pdf/1909.00133 （DIOR 官方论文；亦 arXiv:1909.00133） | 文件/段: PDF 第 10 页；`dior_u8.txt:485-486`
   - 脚注逐字：「2 http://www.escience.cn/people/gongcheng/DIOR.html」 | PDF 第 10 页 | `dior_u8.txt:518`

3. **论文 Table 2：切分件逐字名称 + 各子集图数（发布物侧唯一的名称清单）**
   - 表题逐字：「Table 2」/「Number of images per object class and per subset.」；表头逐字：「Train  val   Trainval  Test」；末行逐字：`Wind mill … 11725`、`Total`
     | 出处: 同上 PDF | 文件/段: PDF 第 13 页；`dior_u8.txt:590-591`、`:611-613`
   - 总量句逐字（摘要）：「The dataset contains 23463 images and 192472 instances, covering 20 object classes.」 | PDF 第 1 页 | `dior_u8.txt:21`
     （同页官方站口径为 `23,463 images and 192,518 object instances`，见上 1；两处逐字并列采录，不作判断。）

4. **论文 §5.1：trainval / test 切分计数（逐字）**
   - 「we randomly selected 11725 remote sensing images (i.e., 50% of the dataset) as trainval set, and the remaining 11738 images are used as test set. The trainval data consists of two parts, the training (train) set and validation (val) set.」
     | PDF 第 12 页 | `dior_u8.txt:580-582`

**NOT FOUND 子项**：官方发布物**清单本体**（有哪些切分件/压缩包/目录；test 件是否含标注/是否扣留；评测是否需提交）。
试过的入口（全部）：

```
https://gcheng-nwpu.github.io/                                                   -> HTTP 000
https://cdn.jsdelivr.net/gh/gcheng-nwpu/gcheng-nwpu.github.io@master/index.html  -> HTTP 200（已采；仅 3 句 + 下载链接）
https://drive.google.com/open?id=1UdlgHk49iu6WpcJ5467iT-UqNPpx__CC               -> HTTP 000
https://drive.google.com/drive/folders/1UdlgHk49iu6WpcJ5467iT-UqNPpx__CC         -> HTTP 000
https://drive.google.com/embeddedfolderview?id=1UdlgHk49iu6WpcJ5467iT-UqNPpx__CC#list -> HTTP 000
https://pan.baidu.com/s/1iLKT0JQoKXEJTGNxt5lSMg                                  -> HTTP 200，但页内逐字为「部分文件违规，已被过滤」「已失效」，未列出任何文件名（本地件 baidu_dior.html）
http://www.escience.cn/people/gongcheng/DIOR.html                                -> HTTP 000（论文脚注 2 的官方旧入口）
https://web.archive.org/web/2019/http://www.escience.cn/people/gongcheng/DIOR.html -> HTTP 000
http://archive.org/wayback/available?url=escience.cn/people/gongcheng/DIOR.html  -> HTTP 000
http://archive.org/wayback/available?url=www.escience.cn/people/gongcheng/DIOR.html -> HTTP 000
http://timetravel.mementoweb.org/api/json/2019/http://www.escience.cn/people/gongcheng/DIOR.html -> HTTP 000
https://www.sciencedirect.com/science/article/pii/S0924271619302825              -> HTTP 403（出版版）
https://arxiv.org/pdf/1909.00133                                                  -> HTTP 200（已采；全文 1065 行，grep "download|submit|evaluation server|not available|withhold" 零命中）
```

#### 目标格：protocol

**采到**（官方论文 §5.1/§5.2 的协议原句：用哪个测试集、怎么评测）。
**NOT FOUND**：官方**官网**侧的任何协议句（官方页 DIOR 段全文仅 3 句，见 release 节第 1 条）；以及「标注是否扣留」的原句（论文/官网全文均无此句）。

逐字证据：

1. **论文 §5.1「Experimental Setup」· split 定义（用哪个测试集）**
   - 「In order to guarantee the distributions of training‐validation (trainval) data and test data are similar, we randomly selected 11725 remote sensing images (i.e., 50% of the dataset) as trainval set, and the remaining 11738 images are used as test set. The trainval data consists of two parts, the training (train) set and validation (val) set.」
     | 出处: https://arxiv.org/pdf/1909.00133 | 文件/段: PDF 第 12 页（`5.1 Experimental Setup` 标题同页）；`dior_u8.txt:580-582`

2. **论文 §5.1 · 判正判据（怎么评测：IoU>50%）**
   - 「A detection is regarded as correct if its bounding box has more than 50% overlap with the ground truth; otherwise, the detection is seen as a false positive.」
     | 同页 | `dior_u8.txt:585-586`

3. **论文 §5.1 · 指标（AP / mAP）**
   - 「We used average precision (AP) and mean AP as measures for evaluating the object detection performance. One can refer to (Cheng and Han, 2016) for more details about these two metrics.」
     | 同页 | `dior_u8.txt:634-636`

4. **论文 §5 · 评测范围（逐字）**
   - 「This section focuses on benchmarking some representative deep learning based object detection methods on our proposed DIOR dataset in order to provide an overview of the state‐of‐the‐art performance for future research work.」
     | 同页（§5 标题 `5. Benchmarking Representative Methods` 在 `dior_u8.txt:573`） | `dior_u8.txt:575-576`

5. **论文 §5.1 · 实验规模句（逐字）**
   - 「We conducted all experiments on a computer with a single Intel core i7 CPU, 64 GB of memory, and an NVIDIA Titan X GPU for acceleration.」 | `dior_u8.txt:586-587`

6. **论文 §5 · 基线方法公平性句（逐字）**
   - 「To make fair comparisons, we kept all the experiment settings the same as that depicted in corresponding papers.」 | `dior_u8.txt:622-623`

7. **论文 Table 2 表题/表头（子集名称逐字 `Train` / `val` / `Trainval` / `Test`）** | PDF 第 13 页 | `dior_u8.txt:590-591`

8. **论文 Table 3 表题（报告口径落在 test set）**
   - 「Detection average precision (%) of 12 representative methods on the proposed DIOR test set.」
     | 出处: 同上 PDF | 文件/段: PDF 第 14 页 | `dior_u8.txt:668-670`

**NOT FOUND 子项与入口**：
(a) 官网协议句 → `https://gcheng-nwpu.github.io/`（000）与镜像件 `nwpu_9b9a09.html`（200，已逐行 grep，DIOR 段 `:512-519` 内无 `split/test/val/train/protocol` 句）。
(b) 「test 标注是否扣留」原句 → arXiv:1909.00133 全文（`dior.pdf` 19 页 / `dior_u8.txt` 1065 行，`grep -i "withhold|held|blind|not available|evaluation server|submit|submission"` 零命中）＋ 官网镜像页全文零命中。
(c) 出版版 → `https://www.sciencedirect.com/science/article/pii/S0924271619302825`（HTTP 403）。

#### 目标格：reported

**部分采到**：报告口径**句**（论文 Table 3 表题明确写 `on the proposed DIOR test set`）已采到；产生报告数字的**命令** = **NOT FOUND**（官方无代码仓：官方页 DIOR 条目只有 `[paper] [DIOR dataset]`、无 `[code]`；论文全文无命令行）。

逐字证据：

1. **报告口径句（唯一明确写出落点的一句话，Table 3 表题）**
   - 「Detection average precision (%) of 12 representative methods on the proposed DIOR test set. The entries with the best APs for each object category are bold‐faced.」
     | 出处: https://arxiv.org/pdf/1909.00133 | 文件/段: PDF 第 14 页；`dior_u8.txt:668-670`

2. **结果陈述句（逐字）**
   - 「The results of 12 representative methods are shown in Table 3. We have the following observations from Table 3.」 | PDF 第 13 页 | `dior_u8.txt:640`
   - Table 3 表体内最末列列名逐字为 `mAP`（表头行 `dior_u8.txt:680`：`Backbone c1 c2 … c20 mAP`）；最高值句逐字：「The detection results of RetinaNet (Lin et al., 2017c) with ResNet‐101 and PANet (Liu et al., 2018b) with ResNet‐101 both achieve the highest mAP of 66.1%.」 | `dior_u8.txt:645-646`

3. **摘要侧的基线报告口径（逐字）**
   - 「Finally, we evaluate several state‐of‐the‐art approaches on our DIOR dataset to establish a baseline for future research.」 | PDF 第 1 页 | `dior_u8.txt:26-27`

4. **官方无代码仓的直接逐字证据**
   - 官方页 DIOR 引用条目（2020 ISPRS）：`[paper] [DIOR dataset]` —— 无 `[code]` | `nwpu_9b9a09.html:419`
   - 官方页 DIOR 段内唯一「运行/获取」句为下载句：「The dataset can be downloaded from Google Drive or BaiduNetDisk .」 | `nwpu_9b9a09.html:519`
   - 官方页 DIOR-R 条目（2022 TGRS）逐字含 `[code]` → `https://github.com/jbwang1997/AOPG` | `nwpu_9b9a09.html:389`

**NOT FOUND 子项与入口**：产生报告数字的**命令**（命令行 / 脚本 / 评测入口）
试过的入口 = `https://gcheng-nwpu.github.io/`（000）与镜像 `https://cdn.jsdelivr.net/gh/gcheng-nwpu/gcheng-nwpu.github.io@master/index.html`（200，全页无命令/脚本/repo 入口，DIOR 段 `:512-519`）、`https://arxiv.org/pdf/1909.00133` 全文（`dior_u8.txt` 1065 行，`grep -i "python |command|script|github|code is available|evaluation server"` 零命中）、`https://pan.baidu.com/s/1iLKT0JQoKXEJTGNxt5lSMg`（页内无文件/脚本清单）、`https://www.sciencedirect.com/science/article/pii/S0924271619302825`（403）。
（对照：任务书提到的镜像仓 `Hamedlk80/DIOR-R-Rotated-Object-Detection-YOLOv8` 属第三方镜像，前一轮已采，本格不计入官方来源。）

---

### 补采结果汇总（本轮 · 只列采集状态）

| 行 | 基准 | release | protocol | yolo_dist | reported |
|---|---|---|---|---|---|
| 5 | DOTA v1.0 | 采到（v1.0 = 三档逐字；`test-challenge` 属 v1.0 档位名称 = NOT FOUND，四档逐字来源已定位到 v2.0 段） | 采到 | 采到（三行 + 钉 commit；文档页「需提交」说明 = NOT FOUND） | 采到（排行榜 + 提交要求 + devkit 命令）；「we report on ⟨val\|test⟩」句型 = NOT FOUND |
| 11 | DIOR | 部分采到（口径句 + 下载入口）；清单本体 = NOT FOUND | 采到（论文 §5.1/§5.2）；官网协议句 = NOT FOUND | 本行无此格 | 部分采到（Table 3 表题）；命令 = NOT FOUND（官方无代码仓） |

*本文件不含任何判定、评分或 mark；所有未采到项均附全部试过的入口。*

#### R0b 补采证据（无卡机 + 本机直取，2026-10-08；逐字）

* **来源**：`gcheng-nwpu.github.io`（43,686 B；文本 21,162 字符）· arXiv:1909.00133 官方论文 PDF（2,282,047 B）
  · 归档 `_p2_missing_evidence_20261008/_from_nocard/p2_ev/DIOR/`。
* **官方页的 DIOR 条目逐字**：`"DIOR" is a large-scale benchmark dataset …`，并给两个入口标签
  **`[DIOR dataset]`** 与 **`[DIOR-R dataset]`**（均指向本页 `#Datasets` 锚），**数据集本体只有外链**。
* **官方给出的下载入口（逐字 URL）**：
  * `[Google Drive] https://drive.google.com/open?id=1UdlgHk49iu6WpcJ5467iT-UqNPpx__CC`（**实测 307，可跳转**）；
  * `[BaiduNetDisk] https://pan.baidu.com/s/1mifR6tU`（另有 `s/1iLKT0JQoKXEJTGNxt5lSMg`、`s/1hqwzXeG`、`s/1VpQGGoSVTdFCtROVnH4s3A?pwd=wye2`）。
  * ⇒ **官方页只给下载入口，不给"包含哪些文件/切分件"的清单**（这正是本格原先缺的证据）。
* **仍未采到**：**发布物清单本体**（需登录 Google Drive / Baidu 才能列目录；两台机器对 `drive.google.com` 可跳转但取不到匿名目录列表）。
* **旁证（**非官方，仅登记**）**：HuggingFace `danielz01/DIOR-RSVG` **受权限限制**；
  arXiv:1909.00133 的 ar5iv 版只回跳转壳（5,408 字符），**不是** TGRS 正式版，故未作协议证据使用。
### 卡 12 · NWPU VHR-10

* **E1**：**无 yaml**（TorchGeo 侧；split 由 Python 定义）。
* **E2**：TorchGeo `torchgeo/datasets/vhr10.py:46-49` 逐字：positive **650** / negative **150**（该 split 的含义是 positive/negative，不是 train/test）。
* **E3 报告口径**：**NOT FOUND**（两篇官方论文 Semantic Scholar 均 `CLOSED`；官方页 `gcheng-nwpu.github.io` 无任何 train/val/test 句）。
* **E4**：`microsoft/torchgeo@ceb558ee1616d545431d6a59c41a2276b18025bd`；
  第一方 datamodule **自己现切**：`torchgeo/datamodules/vhr10.py:31-32` `val_split_pct=0.2`/`test_split_pct=0.2` ·
  `:77` `manual_seed(0)` · `:78-86` `random_split(...)`（val/test 都从 positive 集 650 图里切）；
  第一方命令 `tests/tasks/test_detection.py:41,59,61` `main(['fit'|'test', --config tests/conf/vhr10_obj_det.yaml])`。

#### 补采证据（2026-10-08，逐字）

- 目标: 官方论文（Cheng et al.）里"在 test set 上报告"的逐字句（Semantic Scholar 曾 CLOSED；改试 arXiv / IEEE PDF 直链 / 作者主页 PDF / paperswithcode）。
- 结果: **NOT FOUND**（两篇官方论文的"在 test set 上报告"逐字句均未取到；两篇均非 OA，PDF 直链/作者侧均不可得）。
- 逐字证据（本次可采到的、同作者组的官方描述；**均不含 split/在 test set 上报告** 的句子）:

  1. 同作者组官方综述对 NWPU VHR-10 的定义性描述（**无 train/test 切分句、无"在 test set 上报告"句**）：
     「NWPU VHR-10 dataset (Cheng et al., 2014a)1. This is a challenging 10-class geospatial object detection dataset, which can be used for both single class and multi-class objects detection. These ten classes of objects are airplane, ship, storage tank, baseball diamond, tennis court, basketball court, ground track field, harbor, bridge, and vehicle. This dataset contains totally 800 VHR optical RSIs, from which 757 airplanes, 302 ships, 655 storage tanks, 390 baseball diamonds, 524 tennis courts, 159 basketball courts, 163 ground track fields, 224 harbors, 124 bridges, and 477 vehicles were manually annotated with axis-aligned bounding boxes used for ground truth.」
     | 出处: https://arxiv.org/pdf/1603.06201 （Gong Cheng, Junwei Han, "A Survey on Object Detection in Optical Remote Sensing Images"） | 文件: `nwpu_survey.pdf` 经 `pdftotext -layout` 输出的 `nwpu_survey.txt:1136-1145`（§7.1 Datasets）
     核验：该综述全文 `grep -i -E "test set|training set|testing set|split|50%|half of"` 的唯一命中均为通用机器学习段落（`nwpu_survey.txt:125,808,866,872,876,912,1070,1322`），**无 NWPU VHR-10 的 train/test 切分或报告口径句**。

  2. 官方站点（作者维护）数据集段全文**不含** `train`/`test`/`split` 字样（上一轮已录；本轮复核同结论）：`https://gcheng-nwpu.github.io/` 的 "NWPU VHR-10 dataset" 段只有 800 图、10 类、CC BY-NC 4.0 与 OneDrive/BaiduNetDisk 下载句。

  3. 作者主页对这两篇论文只给出 IEEE 摘要页与百度网盘分享（**无 PDF 直链**，逐字 href）：
     `https://ieeexplore.ieee.org/abstract/document/7560644`（TGRS 2016）、`https://pan.baidu.com/s/158JPjYQvXwnkrAqKF72Jgg#list/path=%2F`；2014 ISPRS 篇对应 `https://www.sciencedirect.com/science/article/abs/pii/S0924271614002524`。
     | 出处: https://gcheng-nwpu.github.io/ （Publications 段） | 文件: `gcheng.html` 的 Publications 段（标题 `Learning Rotation-Invariant Convolutional Neural Networks for Object Detection in VHR Optical Remote Sensing Images` / `Multi-class geospatial object detection and geographic image classification based on collection of part detectors`）

- 若 NOT FOUND: 试过的入口 =
  - `https://api.semanticscholar.org/graph/v1/paper/DOI:10.1109/TGRS.2016.2601622?fields=title,openAccessPdf,externalIds,isOpenAccess` → `"isOpenAccess": false`，`"openAccessPdf": {"url": "", "status": "CLOSED", "license": null}`
  - `https://api.semanticscholar.org/graph/v1/paper/DOI:10.1016/j.isprsjprs.2014.10.002?...` → `"status": "CLOSED"`
  - `https://api.unpaywall.org/v2/10.1109/TGRS.2016.2601622?email=…` → `is_oa False`，`best_oa_location = None`
  - `https://api.unpaywall.org/v2/10.1016/j.isprsjprs.2014.10.002?email=…` → `is_oa False`
  - `https://ieeexplore.ieee.org/document/7560644`（TGRS 2016 官方直链） → HTTP **202**，0 bytes（无正文）
  - `https://www.infona.pl/resource/bwmeta1.element.ieee-art-000007560644` → HTTP 404
  - `https://daneshyari.com/search?q=collection+of+part+detectors` → HTTP 504
  - `https://core.ac.uk/search?q=Learning+Rotation-Invariant+Convolutional+Neural+Networks`（另一次同站检索 `q=automatic fire detection system deep convolutional low-power resource-constrained`）→ HTTP 403（`<title>Just a moment...</title>`，Cloudflare）
  - `https://ir.nwpu.edu.cn/simple-search?query=NWPU+VHR-10` → HTTP 412
  - `https://gcheng-nwpu.github.io/` → 仅摘要页链接 + `https://pan.baidu.com/s/158JPjYQvXwnkrAqKF72Jgg#list/path=%2F`（需登录，未取到文件）
  - `https://arxiv.org/pdf/1603.06201` → 取到（同作者组综述，**无该句**，逐字见上）
  - `http://export.arxiv.org/api/query?search_query=all:%22NWPU%20VHR-10%22&max_results=30` → HTTP **301**（未返回条目）
  - `https://paperswithcode.com/dataset/nwpu-vhr-10` → HTTP **302**（无正文）
  - `https://www.researchgate.net/publication/305703275` → HTTP **403**
  - 两篇论文的 DOI 原文页（付费墙）：`https://ieeexplore.ieee.org/abstract/document/7560644`、`https://www.sciencedirect.com/science/article/abs/pii/S0924271614002524`

---

### 卡 13 · SHWD

* **E1**：第一方**无 yaml**；镜像 `gengyanlei/fire-smoke-detect-yolov4@98b1fec0f82e09d67ef5fc657a80eaf0b1450360`
  `yolov5/data/Reflective_vests.yaml:3-4`：`train` 与 `val` **同指一个文件**，**无 `test:`**。
* **E2**：官方 README（`njvisionpower/Safety-Helmet-Wearing-Dataset@c952631dfc352e0defdd54b4785a9be6576451ad`）**全文无协议句、无 gated 句**；
  benchmark 表只给 `map | 88.5 | 86.3 | 75.0`，**无 split 标注**。
* **E3 报告口径**：**NOT FOUND**（官方无论文；README 无"报告在哪个 split"的句子）。
* **E4**：镜像命令 `python test_yolo.py`（单图 demo）+ `README.md:59-60` / `train_yolo.py:106-107` 的
  **`splits=[(2028,'trainval')]` vs `[(2028,'test')]`** 两处并列。

#### 补采证据（2026-10-08，逐字）

- 目标: 官方 README 或相关论文里关于 **train/val/test 划分** 的逐字句（官方 README 全文无 split 句；再查数据集随附 `README`/`说明` 文件、以及引用该数据集的论文里的划分描述）。
- 结果: **采到**（引用该数据集的论文里有逐字划分描述；并核验官方仓内**不存在**第二份 README/说明文件）。
- 逐字证据:

  1. **引用论文中的划分描述（逐字，完整句）**：
     「The dataset follows a 7:2:1 random split ratio. Specifically, it is divided into three major subsets: the training set contains 5306 images for model learning; the validation set has 1516 images for evaluating the model’s performance during training; and the test set consists of 759 images for the final test of the model’s generalisation ability.」
     同段前置句逐字：「The helmet detection dataset used for the experiments in this study is SHWD. The dataset, consisting of 7581 images, contains a wide range of examples of helmet and head detection in diverse scenes, lighting conditions, size scales, and different degrees of target occlusion,」/「The images included 9,044 labelled helmet targets and 111,515 labelled normal head targets.」
     | 出处: https://www.nature.com/articles/s41598-025-08828-z （"A YOLOv8 algorithm for safety helmet wearing detection in complex environment", Scientific Reports） | 文件: `s41598-025-08828-z.html:1034`（该句在 HTML 中位于第 1034 行；论文正文 "The helmet detection dataset used for the experiments in this study is SHWD" 同段）
     该文引用 SHWD 的仓库 URL 逐字为 `https://github.com/njvisionpower/Safety-Helmet-Wearing-Dataset`（同页 4 处）。
     | 出处: 同上 | 文件: `s41598-025-08828-z.html`（参考文献段）

  2. **数据集随附 `README`/`说明` 文件核验 = 不存在**：官方仓 `njvisionpower/Safety-Helmet-Wearing-Dataset` 在默认分支 `master` 的**全量文件清单**（jsDelivr flat listing，共 28 项）逐字为：
     `/demo1.jpg`、`/image/1.jpg`、`/image/1_result.jpg`、…、`/image/10.jpg`、`/image/10_result.jpg`、`/LICENSE`、`/README.md`、`/test_symbol.py`、`/test_yolo.py`、`/train_yolo.py`
     —— 除 `README.md` 外**没有**任何第二份 README/说明文件，也没有 `*.txt`/`*.md`/`说明*` 之类随附说明。
     | 出处: https://data.jsdelivr.com/v1/packages/gh/njvisionpower/Safety-Helmet-Wearing-Dataset@master?structure=flat | 文件: 采集件 `shwd_files.json` 的 `files[].name`（28 项）

  3. **第三方 Kaggle 镜像亦未暴露随附说明文件**（各镜像 API 的 `files` 字段逐字均为空数组）：
     `https://www.kaggle.com/api/v1/datasets/view/zxy000/shwd-dataset`（title `SHWD_dataset`）→ `"files": []`；
     `https://www.kaggle.com/api/v1/datasets/view/dngtrnphmtunse183674/helmet-shwd`（title `Helmet_shwd`）→ `"files": []`；
     `https://www.kaggle.com/api/v1/datasets/view/tundng111/shwd-tnghp`（title `SHWD_Tổnghợp`）→ `"files": []`；三者 `description` 字段均为空串。
     | 出处: 上述三条 Kaggle API URL | 文件: 各响应 payload 的 `files` / `description` 字段

- 备注（仅事实）：官方 README 侧上一轮已逐字采到的"报告口径"段仍为无 split 的基准表（`README.md:18-21`）；本轮新增的是**引用论文侧**的 7:2:1 划分句与**随附说明文件不存在**的清单核验。

---

#### R0 补采证据（2026-10-08，逐字）

**[C]** **第一方识别**：`njvisionpower/Safety-Helmet-Wearing-Dataset`，默认分支 `master`，HEAD = `c952631dfc352e0defdd54b4785a9be6576451ad`。
commit 定点核验（两路互证，内容一致）：
- `curl -L https://codeload.github.com/njvisionpower/Safety-Helmet-Wearing-Dataset/tar.gz/refs/heads/master` → HTTP 200，3,609,709 B；tar 内文件 mtime 全为 `2019-12-17 20:39`。
- `https://data.jsdelivr.com/v1/packages/gh/njvisionpower/Safety-Helmet-Wearing-Dataset@c952631dfc352e0defdd54b4785a9be6576451ad?structure=flat` → HTTP 200，`"version": "c952631dfc352e0defdd54b4785a9be6576451ad"`，文件数 26。
- README 三路 md5 相同 = `ed446eeb9ca2a2263b176313f184aa1e`（tar 解出件 / jsDelivr 定点件 / `raw.githubusercontent.com` master 件）。
- `git ls-remote https://github.com/njvisionpower/Safety-Helmet-Wearing-Dataset` → **失败**（`Failed to connect to github.com port 443`）。sha 采用前轮 `git ls-remote … HEAD` 的结果，并用上述内容互证锁定。

#### 目标格：reported

- **采到（"官方未声明报告 split"这一事实）**：第一方**通篇没有**任何"报告数字取自哪个 split"的语句。
- **逐字证据（官方 Benchmark 表，无 split 标注）**:
  - 「### Benchmark」 | 出处: https://cdn.jsdelivr.net/gh/njvisionpower/Safety-Helmet-Wearing-Dataset@c952631dfc352e0defdd54b4785a9be6576451ad/README.md（同 https://raw.githubusercontent.com/njvisionpower/Safety-Helmet-Wearing-Dataset/master/README.md） | 文件/段: `README.md:18`
  - 「model | darknet | mobile1.0 |  mobile0.25」 | 同上 | `README.md:19`
  - 「--------- | ------------- | ------------- | ------------- 」 | 同上 | `README.md:20`
  - 「map   |  88.5 |  86.3 |  75.0」 | 同上 | `README.md:21`
  - （该表三列逐字为 `darknet` / `mobile1.0` / `mobile0.25`，表头列名为模型名，**未出现任何 split 名**）
- **逐字证据（官方唯一涉及 split 名的两处，均为"训练配置示例"而非"报告口径"）**:
  - 「You can see function "get_dataset" in the file "train_yolo.py" to set dataset path. An example, download dataset and unzip to the path such as "D:\VOCdevkit\VOC2028", train/val dataset can set as:」 | 出处: 同上 README | 文件/段: `README.md:57`
  - 「train_dataset = VOCLike(root='D:\VOCdevkit', splits=[(2028, 'trainval')])」 | 同上 | `README.md:59`
  - 「val_dataset = VOCLike(root='D:\VOCdevkit', splits=[(2028, 'test')])」 | 同上 | `README.md:60`
  - 「def get_dataset(dataset, args):」 | 出处: https://raw.githubusercontent.com/njvisionpower/Safety-Helmet-Wearing-Dataset/master/train_yolo.py | 文件/段: `train_yolo.py:104`
  - 「    if dataset.lower() == 'voc':」 | 同上 | `train_yolo.py:105`
  - 「        train_dataset = VOCLike(root='D:\VOCdevkit', splits=[(2028, 'trainval')])」 | 同上 | `train_yolo.py:106`
  - 「        val_dataset = VOCLike(root='D:\VOCdevkit', splits=[(2028, 'test')])」 | 同上 | `train_yolo.py:107`
  - 「        val_metric = VOC07MApMetric(iou_thresh=0.5, class_names=val_dataset.classes)」 | 同上 | `train_yolo.py:108`
  - 「def save_params(net, best_map, current_map, epoch, save_interval, prefix):」 | 同上 | `train_yolo.py:144`
  - 「    if current_map > best_map[0]:」 | 同上 | `train_yolo.py:146`
  - 「        net.save_parameters('{:s}_best.params'.format(prefix, epoch, current_map))」 | 同上 | `train_yolo.py:148`
- **逐字证据（官方数据规模，未按 split 拆分）**:
  - 「SHWD provide the dataset used for both safety helmet wearing and human head detection. It includes 7581 images with 9044 human safety helmet wearing objects(positive) and 111514 normal head objects(not wearing or negative). The positive objects got from goolge or baidu, and we manually labeld with LabelImg. Some of negative objects got from [SCUT-HEAD](https://github.com/HCIILAB/SCUT-HEAD-Dataset-Release). We fixed some bugs for original SCUT-HEAD and make the data can be directly loaded as normal Pascal VOC format. Also we provide some pretrained models with MXNet GluonCV.    」 | 出处: 同上 README | 文件/段: `README.md:5`
- **逐字证据（官方发布目录结构，`ImageSets` 内文件未列名）**:
  - 「We annotate the data as Pascal VOC format:  」 | 同上 | `README.md:24`
  - 「---VOC2028    」 | 同上 | `README.md:26`
  - 「    ---Annotations    」 | 同上 | `README.md:27`
  - 「    ---ImageSets    」 | 同上 | `README.md:28`
  - 「    ---JPEGImages   」 | 同上 | `README.md:29`
  - 「Two object class names for the task, "hat" for positive object and "person" for negative object.」 | 同上 | `README.md:31`

- **检查清单（官方第一方，全量核对，报 split 语句命中数 = 0）**:
  1. `README.md`（100 行，全文逐行读）：无 "we report … on the ⟨val|test|testing⟩ set"、无任何 split 比例数字、无 "test 标注扣留"/"需提交"/"leaderboard"/"evaluation server" 句。唯一带 `Benchmark` 的节为 `README.md:18-21`（三列 mAP 表）。
  2. `train_yolo.py`（345 行）、`test_yolo.py`（67 行）、`test_symbol.py`（30 行）、`LICENSE`（21 行）：grep `split|trainval|train\.txt|val\.txt|test\.txt|7:2:1|ratio|testing set|validation set|submit|benchmark` 全仓命中仅 4 处切分相关行（`README.md:59,60`、`train_yolo.py:106,107`），其余命中均为 `str.split()` / `gluon.utils.split_and_load` / `VOCLike.split` 参数名 / `image.split('.')` 等与数据集切分无关的代码。
  3. 官方仓**全量文件清单**（`data.jsdelivr.com … @c952631…?structure=flat`，26 项；与 `codeload` tar.gz 清单逐项一致，README md5 相同）逐字为：
     `demo1.jpg` · `image/1.jpg` · `image/1_result.jpg` · `image/2.jpg` · `image/2_result.jpg` · `image/3.jpg` · `image/3_result.jpg` · `image/4.jpg` · `image/4_result.jpg` · `image/5.jpg` · `image/5_result.jpg` · `image/6.jpg` · `image/6_result.jpg` · `image/7.jpg` · `image/7_result.jpg` · `image/8.jpg` · `image/8_result.jpg` · `image/9.jpg` · `image/9_result.jpg` · `image/10.jpg` · `image/10_result.jpg` · `LICENSE` · `README.md` · `test_symbol.py` · `test_yolo.py` · `train_yolo.py`
     → **无任何切分件（无 `ImageSets/*.txt`、无 `train/val/test` 列表）、无标注件、无 `*.yaml`/`*.data`/`*.names`、无说明文档**。
     | 出处: https://data.jsdelivr.com/v1/packages/gh/njvisionpower/Safety-Helmet-Wearing-Dataset@c952631dfc352e0defdd54b4785a9be6576451ad?structure=flat | 文件/段: 响应 `files[].name`（26 项）；交叉件 `codeload…/tar.gz/refs/heads/master`
  4. 官方仓无 `git tag` / Release 页可查（`github.com:443` 不可达；`git ls-remote` 失败）。
  5. 官方数据本体**不可核验**：`README.md:13` BaiduDrive `https://pan.baidu.com/s/1UbFkGm4EppdAU660Vu7SdQ` → HTTP 200（需登录，无法列目录）；`README.md:14` GoogleDrive `https://drive.google.com/open?id=1qWm7rrwvjAWs1slymbrLaCf7Q-wnGLEX` → HTTP 000（本环境不可达）。故 `ImageSets/` 内实际有哪些 txt、`test` 标注是否公开，**无法从第一方核验**。
  6. `web_search`（`SHWD official paper` / `Safety-Helmet-Wearing-Dataset paper`）未命中 SHWD 官方论文（与前轮一致）。
- **第三方（**非官方**，仅登记不得作为官方口径）**:
  - 逐字证据: 「The helmet detection dataset used for the experiments in this study is SHWD. The dataset, consisting of 7581 images, contains a wide range of examples of helmet and head detection in diverse scenes, lighting conditions, size scales, and different degrees of target occlusion, providing a rich sample resource for the study. The dataset was labelled using the LabelImg annotation software to label the objects in the images. The images included 9,044 labelled helmet targets and 111,515 labelled normal head targets. The dataset follows a 7:2:1 random split ratio. Specifically, it is divided into three major subsets: the training set contains 5306 images for model learning; the validation set has 1516 images for evaluating the model's performance during training; and the test set consists of 759 images for the final test of the model's generalisation ability.」 | 出处: https://www.nature.com/articles/s41598-025-08828-z （"A YOLOv8 algorithm for safety helmet wearing detection in complex environment", Scientific Reports；第三方论文，**不是** SHWD 官方） | 文件/段: `s41598-025-08828-z.html:1034`（HTML 第 1034 行；正文 `Experimentation → Description of the data set` 段）
  - 该段头目标数逐字为 `111,515`，与官方 `README.md:5` 的 `111514` **不一致**（逐字差异，登记备查）。
  - 该文引用 SHWD 的仓库 URL 逐字为 `https://github.com/njvisionpower/Safety-Helmet-Wearing-Dataset`。
  - 第三方仓（镜像，非官方）`gengyanlei/fire-smoke-detect-yolov4`：前轮已采其 `yolov5/data/Reflective_vests.yaml` 与 `hp.yaml`（两键 train/val，无 `test:`），本次未重复采。

- **NOT FOUND 汇总（reported 格的官方口径）**：`NOT FOUND` —— 官方 `README.md`（100 行，全文）/ `train_yolo.py`（345 行）/ `test_yolo.py`（67 行）/ `test_symbol.py`（30 行）/ 官方仓全量 26 项文件清单中，**均无**"报告数字取自哪个 split"的语句。
  - 试过的全部入口：`raw.githubusercontent.com/njvisionpower/Safety-Helmet-Wearing-Dataset/master/{README.md,train_yolo.py,test_yolo.py,test_symbol.py}`；`cdn.jsdelivr.net/gh/njvisionpower/Safety-Helmet-Wearing-Dataset@c952631dfc352e0defdd54b4785a9be6576451ad/README.md`；`data.jsdelivr.com/v1/packages/gh/njvisionpower/Safety-Helmet-Wearing-Dataset@c952631…?structure=flat`；`codeload.github.com/njvisionpower/Safety-Helmet-Wearing-Dataset/tar.gz/refs/heads/master`；`git ls-remote https://github.com/njvisionpower/Safety-Helmet-Wearing-Dataset`（失败）；`git ls-remote git://…`（失败）；`git ls-remote https://raw.githubusercontent.com/…`（失败）；`https://pan.baidu.com/s/1UbFkGm4EppdAU660Vu7SdQ`（200，需登录）；`https://drive.google.com/open?id=1qWm7rrwvjAWs1slymbrLaCf7Q-wnGLEX`（000）；`web_search` × 2。

---
### 卡 14 · SFCHD

* **E1**：第一方 `lijfrank/SFCHD-SCALE@7bfabb4533613e6917461dc3758dcff5f304bd03`
  `dataset_SFCHD/new_split_yolo/` 三档 txt（**实测**）：`train.txt` 9897 非空行 · `val.txt` 2475 · **`test.txt` 6**；
  **`test ⊆ val` = True**（`|test ∩ val|` = 6，`val.txt[:6] == test.txt` 逐行相同），`test ∩ train` = 0。
* **E2**：第一方论文摘要 p.1 + §3.2 p.4（**只声明两档**；`validation` 全文出现 **0** 次；论文给 9,898 train + 2,475 test，4:1）。
* **E3 报告口径**：同上（论文报的是它的 test 档，而该档 **= val 的前 6 行**）。
* **E4**：第一方仓**无 train/val/test/eval 脚本**（`SCALE.py` 纯 `nn.Module`；README 无命令行）。
* **采集层提醒**：论文自述的 `lijfrank-open/SFCHD-SCALE` 解析到**同一 HEAD**。

#### R0 补采证据（2026-10-08，逐字）

**[C]** **第一方识别**：`lijfrank/SFCHD-SCALE`（论文自述发布地址为 `https://github.com/lijfrank-open/SFCHD-SCALE`）。
commit 定点核验：`7bfabb4533613e6917461dc3758dcff5f304bd03`；`codeload.github.com/lijfrank/SFCHD-SCALE/tar.gz/7bfabb4533613e6917461dc3758dcff5f304bd03` → HTTP 200（32,079,745 B），tar 内 mtime 全为 `2025-05-18 00:32`。
`refs/heads/main` 的 tar.gz（32,076,666 B）与上述定点 commit **README md5 相同**（`544886cb9349dae86bc6888253d40243`）、**全树逐项相同** → 定点件即当时 HEAD。
`data.jsdelivr.com/v1/packages/gh/lijfrank/SFCHD-SCALE@7bfabb4…?structure=flat` → **HTTP 403**（jsDelivr 拒，仓过大）；改以 `codeload` tar.gz 为清单来源。

#### 目标格：release

- **采到（第一方仓 `dataset_SFCHD/` 文件清单 + 实测切分档）**:

  第一方 git 仓在 `7bfabb4…` 的**全树仅 3 个顶层条目**：`README.md`、`SCALE.py`、`dataset_SFCHD/`；另有 `results_ExDark/`、`results_SFCHD/`、`sfchd-scale.pdf`、`sfchd-scale-suppl.pdf`（tar 清单共 111 条）。

  `dataset_SFCHD/` 下切分件实测（`codeload` tar.gz 解出后 `ls -la` / `wc -l` / `unzip -l`）：

  | 路径 | 实测 | 档数 |
  |---|---|---|
  | `dataset_SFCHD/annotations/all_data.json` | 20,359,104 B；`images` 12,373 / `annotations` 50,559 / `categories` 7 | 1（全集） |
  | `dataset_SFCHD/annotations/train.json` | 16,207,810 B；`images` **9,898** / `annotations` 40,223 | 1 |
  | `dataset_SFCHD/annotations/val.json` | 4,152,148 B；`images` **2,475** / `annotations` 10,336 | 1 |
  | `dataset_SFCHD/annotations/test.json` | **0 B（空文件）** | 1 |
  | `dataset_SFCHD/new_split_yolo/train.txt` | 9,897 条路径（唯一 9,897） | 1 |
  | `dataset_SFCHD/new_split_yolo/val.txt` | 2,475 条路径（唯一 2,475） | 1 |
  | `dataset_SFCHD/new_split_yolo/test.txt` | **6 条路径**（5 个换行，末行无换行；唯一 6） | 1 |
  | `dataset_SFCHD/new_split_yolo/train.cache` | 2,905,537 B | — |
  | `dataset_SFCHD/new_split_yolo/val.cache` | 727,955 B | — |
  | `dataset_SFCHD/classes.txt` | 77 B，7 行（CRLF）：`person` / `helmet` / `self_clothes` / `safety_clothes` / `head` / `blur_head` / `blur_clothes` | — |
  | `dataset_SFCHD/labels.zip` | 3,569,708 B；含 `labels/` + `labels/*.txt` **12,372** 个（共 12,373 条目） | 无切分（单一扁平档） |
  | `dataset_SFCHD/yolo.zip` | 5,122,756 B；含 `yolo/`、`yolo/train.txt`、`yolo/val.txt`、`yolo/train/`（**9,899** 个 txt）、`yolo/val/`（**2,476** 个 txt）、`yolo/train.cache`、`yolo/val.cache` | **两档（train/val），无 test** |
  | `dataset_SFCHD/directory.md` | 1,164,092 B / **24,794 行**（纯机械树状清单，第 24,794 行为 `12 directories, 24779 files`） | — |
  | `dataset_SFCHD/images/images_files.txt`、`dataset_SFCHD/sd_train/metadata.jsonl` | 存在 | — |

  - 逐字证据（`yolo.zip` 为两档、**无 test**）: 「`yolo/`」「`yolo/val.txt`」「`yolo/val.cache`」「`yolo/train/`」「`yolo/train.txt`」「`yolo/val/`」「`yolo/train.cache`」 | 出处: `codeload.github.com/lijfrank/SFCHD-SCALE/tar.gz/7bfabb4533613e6917461dc3758dcff5f304bd03` → `dataset_SFCHD/yolo.zip` | 文件/段: `unzip -l yolo.zip` 的**全部 7 个非标注条目**（其余 12,375 条目为 `yolo/train/*.txt` 9,899 + `yolo/val/*.txt` 2,476）
  - 逐字证据（`new_split_yolo/test.txt` 全文 6 条，均为 **image 路径**、非标注）:
    「/home/yfs/data/QY_final_dataset/images/192.168.11.13_neg_7c_2832.jpg」「/home/yfs/data/QY_final_dataset/images/192.168.2.35_neg_12c_362.jpg」「/home/yfs/data/QY_final_dataset/images/192.168.2.28_caiji_1_24.jpg」「/home/yfs/data/QY_final_dataset/images/192.168.2.221_400.jpg」「/home/yfs/data/QY_final_dataset/images/192.168.2.34_neg_12c_275.jpg」「/home/yfs/data/QY_final_dataset/images/192.168.2.220_480.jpg」 | 出处: 同上 tar.gz | 文件/段: `dataset_SFCHD/new_split_yolo/test.txt:1-6`

- **逐字证据（README 里关于这些档的说明）**: 出处 https://raw.githubusercontent.com/lijfrank/SFCHD-SCALE/7bfabb4533613e6917461dc3758dcff5f304bd03/README.md （同 `https://cdn.jsdelivr.net/gh/lijfrank/SFCHD-SCALE@7bfabb4…/README.md`；md5 `544886cb9349dae86bc6888253d40243`，与 tar 解出件一致）：
  - 「## Dataset Acquisition」 | 文件/段: `README.md:107`
  - 「.  」 | `README.md:108`
  - 「├── annotations  」 | `README.md:109`
  - 「├── classes.txt  」 | `README.md:110`
  - 「├── directory.md  」 | `README.md:111`
  - 「├── images  」 | `README.md:112`
  - 「├── labels  」 | `README.md:113`
  - 「├── labels.cache  」 | `README.md:114`
  - 「├── new_split_yolo  」 | `README.md:115`
  - 「├── sd_train  」 | `README.md:116`
  - 「├── train  」 | `README.md:117`
  - 「├── Vision  」 | `README.md:118`
  - 「└── yolo  」 | `README.md:119`
  - 「8 directories, 3 files」 | `README.md:120`
  - 「Download the dataset from [链接：https://pan.baidu.com/s/1k2pWg8r-G3KSI2Q3Tdt6kg 」 | `README.md:122`
  - 「提取码：v4ao], unzip and copy the files from images into dataset_SFCHD/images. Also, unzip labels.zip and yolo.zip.」 | `README.md:123`
  - 「Google Drive: https://drive.google.com/file/d/1-2z7r3J4sZdLvVt5mllvSEwAFO49Y-zj/view?usp=sharing」 | `README.md:125`
  - **说明**：README 的 `Dataset Acquisition` 节**只**给了目录树（L109-L120）与下载指引（L122-L125）；下载指引**只提** `labels.zip` 与 `yolo.zip`，**未提** `new_split_yolo`；README 中 `new_split` 出现次数 = **1**（即 L115 的目录名本身），无任何解释句。
  - 下载入口可达性：`https://pan.baidu.com/s/1k2pWg8r-G3KSI2Q3Tdt6kg` → HTTP 200（需登录，无法列目录）；`https://drive.google.com/file/d/1-2z7r3J4sZdLvVt5mllvSEwAFO49Y-zj/view` → HTTP 000（本环境不可达）。
  - `directory.md` 逐字（`dataset_SFCHD/directory.md`）：
    - 「├── annotations  」 | `directory.md:2`；「│   ├── all_data.json  」 | `directory.md:3`；「│   ├── test.json  」 | `directory.md:4`；「│   ├── train.json  」 | `directory.md:5`；「│   └── val.json  」 | `directory.md:6`
    - 「├── new_split_yolo  」 | `directory.md:24756`；「│   ├── coco_file  」 | `directory.md:24757`；「│   ├── test.txt  」 | `directory.md:24758`；「│   ├── train.cache  」 | `directory.md:24759`；「│   ├── train.txt  」 | `directory.md:24760`；「│   ├── val.cache  」 | `directory.md:24761`；「│   └── val.txt  」 | `directory.md:24762`
    - 「└── yolo  」 | `directory.md:24786`；「    ├── train  」 | `directory.md:24787`；「    ├── train.cache  」 | `directory.md:24788`；「    ├── train.txt  」 | `directory.md:24789`；「    ├── val  」 | `directory.md:24790`；「    ├── val.cache  」 | `directory.md:24791`；「    └── val.txt  」 | `directory.md:24792`
    - 「12 directories, 24779 files」 | `directory.md:24794`
    - **注意（实测不一致）**：`directory.md:24757` 列出 `new_split_yolo/coco_file`（子目录），但 `7bfabb4…` git 仓内 `dataset_SFCHD/new_split_yolo/` 实测**只有** `test.txt` / `train.cache` / `train.txt` / `val.cache` / `val.txt`，**无 `coco_file`**。

- **`test` 档标注是否公开（实测）**:
  - `dataset_SFCHD/annotations/test.json` = **0 字节**（`ls -la` 实测 size 0；README/directory.md 均把它列为存在档）。
  - `dataset_SFCHD/new_split_yolo/test.txt` 仅 6 条 **image 路径**，不含任何标注内容。
  - 无独立 test 标注件（`labels.zip` 为**不切分**的扁平 `labels/*.txt` 全集；`yolo.zip` 只有 `train/`、`val/` 两个标注目录）。

- **评测是否需提交（实测）**: 第一方仓 `7bfabb4…` 全树**无** `val.py` / `test.py` / `train.py` / `evaluate.py` / 任何评测命令行；`README.md` 全篇**无命令行**；全仓 grep `submission|submit|leaderboard|eval server|benchmark server` = **0 命中**（检查对象：`README.md`、`SCALE.py`、`sfchd-scale.pdf` 抽文、`sfchd-scale-suppl.pdf` 抽文）。

- **README/论文是否声明 test 档与 val 档的关系 → 「无声明」（关键缺证据事实，0 命中清单）**:
  - 检查对象一：`README.md`（125 行，全文逐行）——`new_split` 命中 **1**（L115 目录名）；无一句解释 `new_split_yolo/test.txt` 与 `val.txt` 的关系；无 `test`/`val` 作为协议名的说明句。
  - 检查对象二：`sfchd-scale.pdf`（7 页，pypdf 抽文）——`new_split` 命中 **0**；`test` 词形仅 4 处：`and testing`×2、`testing`×1、`the testing`×1；只有 training/testing **两档**，**无第三档**。
  - 检查对象三：`sfchd-scale-suppl.pdf`（10 页，pypdf 抽文）——`new_split` 命中 **0**；`test` 词形仅 6 处：`and testing`×3、`for testing`×1、`testing`×2；亦只有 training/testing **两档**。
  - 检查对象四：`SCALE.py`（7,072 B）——`new_split` 命中 **0**；无任何数据切分逻辑。
  - 检查对象五：`dataset_SFCHD/directory.md`（24,794 行）——`new_split` 命中 **1**（L24756 目录名）；该文件为**纯机械树状清单**，非树状行仅 3 行（2 个空行 + L24794 汇总行 `12 directories, 24779 files`），**无散文说明**。
  - 结论式采集登记：**README / 论文 / 补充材料 / `directory.md` / `SCALE.py` 均未声明 `new_split_yolo/test.txt` 与 `val.txt` 的关系**。
  - 实测可核的关系（登记事实，不作判断）：
    - `test.txt` 6 条**全部**落于 `new_split_yolo/val.txt` 内（`comm -23 <(sort -u test.txt) <(sort -u val.txt)` 差集 = **0**；程序计数 test∩val = **6/6**）；`test.txt` 与 `train.txt` 交集 = **0**。
    - `new_split_yolo/train.txt`（9,897）∪ `val.txt`（2,475）= **12,372** 条唯一路径；`annotations/all_data.json` 有 **12,373** 张 → 差集 **1** 张 = `192.168.2.20_1c_29.jpg`（该图在 `annotations/train.json` 内，**不在** `new_split_yolo/{train,val,test}.txt` 任一档内）。
    - `new_split_yolo/{train,val}.txt` 与 `annotations/{train,val}.json` 的 image 集合**不一致**：`train.txt ∩ train.json` = 7,942；`train.txt \ train.json` = 1,955；`train.json \ train.txt` = 1,956；`val.txt ∩ val.json` = **520**；`val.txt \ val.json` = 1,955；`val.json \ val.txt` = 1,955。
    - `new_split_yolo/test.txt` 的 6 张中，**5 张**在 `annotations/train.json`、**1 张**在 `annotations/val.json`。
    - `annotations/train.json`（9,898 图 / 40,223 标注）与 `annotations/val.json`（2,475 图 / 10,336 标注）相加 = `all_data.json`（12,373 图 / 50,559 标注），集合互斥且完备。
    - `README.md:29` / `README.md:30` 的 `Training` / `Testing` 实例数逐字为 `40,223` / `10,336`，与 `annotations/train.json` / `annotations/val.json` 的 `annotations` 计数**一致**；README 中 `val` 一词**仅**出现在文件名 `val.txt` / `val.cache` 中，未作为协议名出现。
    - CLI 实测：`wc -l` 对 `test.txt` 报 5（末行无换行），路径计数为 6。

#### 目标格：protocol

- **采到（第一方论文关于 evaluation protocol 的节）**:

  - §3.2 「Data Partitioning」（PDF **第 4 页**）逐字: 「Data Partitioning: Our dataset is divided into training set and testing set, and the ratio is 4:1. We have 12,373 images in SFCHD dataset, including 9,898 images in the training set, 2,475 images in the testing set.」 | 出处: https://raw.githubusercontent.com/lijfrank/SFCHD-SCALE/7bfabb4533613e6917461dc3758dcff5f304bd03/sfchd-scale.pdf （同仓 `sfchd-scale.pdf`） | 文件/段: `sfchd-scale.pdf` PDF 第 4 页 §3.2（pypdf 抽文；该段紧接 `Table 2` 引用前）
  - §3.2 续句逐字: 「The statistics of category distribution of training and testing set under different lighting conditions are shown in Table 2.」 | 同上 | 同上（第 4 页 §3.2）
  - 摘要（PDF **第 1 页**）逐字: 「We partition the SFCHD dataset into training and testing sets with a ratio of 4:1 and validate its utility by applying several classic object detection algorithms.」 | 同上 | `sfchd-scale.pdf` 第 1 页 ABSTRACT
  - 摘要（PDF 第 1 页）发布地址逐字: 「The dataset and code are publicly available at https://github.com/lijfrank-open/SFCHD-SCALE.」 | 同上 | `sfchd-scale.pdf` 第 1 页 ABSTRACT
  - 摘要（PDF 第 1 页）规模逐字: 「SFCHD is derived from two authentic chemical plants, comprising 12,373 images, 7 categories, and 50,552 annotations.」 | 同上 | `sfchd-scale.pdf` 第 1 页 ABSTRACT

  - supplementary §D.1 「Details」段（**§D.1 标题在 PDF 第 6 页；该段在 PDF 第 7 页**）逐字: 「Details: All experiments are conducted using MMDetection [26], with dataset partitions following the default configuration. The experiments are optimized using the SGD optimizer. The momentum and weight decay are set to 0.9 and 0.0001, respectively. During the training and testing process, the image size was adjusted to 1333 * 800. The batch size is set to 2 for a single GPU, and distributed training is conducted using 4 GPUs. All models are trained on NVIDIA GeForce RTX 3090 GPUs, each with 24GB of graphics memory. We evaluate the mean average precision (mAP) of the object detection to measure the performance of all models fairly. The mAP(0.50:0.95) metric measures the mAP across different Intersection over Union (IoU) thresholds, ranging from 0.50 to 0.95 with an interval of 0.05. Similarly, mAP(0.50) is the mAP at a single IoU threshold of 0.50.」 | 出处: https://raw.githubusercontent.com/lijfrank/SFCHD-SCALE/7bfabb4533613e6917461dc3758dcff5f304bd03/sfchd-scale-suppl.pdf | 文件/段: `sfchd-scale-suppl.pdf` PDF 第 7 页 §D.1「Details」（`D.1` 标题在 PDF 第 6 页；`D.2 Validity of SCALE Module` 标题在 PDF 第 7 页）
  - supplementary `§3.1`/§「Dataset」陈述（§D.2 内，PDF 第 7 页）逐字（**ExDark**，非 SFCHD，登记备查）: 「The dataset is partitioned into a training set with 5,896 images and a testing set with 1,467 images.」 | 同上 | `sfchd-scale-suppl.pdf` 第 7 页 §D.2

- **逐字证据（README 的实验/协议侧口径）**: 出处 https://raw.githubusercontent.com/lijfrank/SFCHD-SCALE/7bfabb4533613e6917461dc3758dcff5f304bd03/README.md ：
  - 「Statistics of instance distribution per category in the SFCHD dataset」 | `README.md:26`
  - 「| Training       | 13,528  | 11,378        | 11,781          | 626            | 961   | 1,053           | 896         | 40,223  |」 | `README.md:29`
  - 「| Testing        | 3,482   | 2,920         | 3,032           | 154            | 239   | 271             | 238         | 10,336  |」 | `README.md:30`
  - 「## Experimental Results」 | `README.md:41`
  - 「Comparisons of different methods on the Pictor-v3, SHWD, and SFCHD datasets [mAP(0.50)/mAP(0.50:0.95)]」 | `README.md:42`
  - 「| Method     | Backbone  | Pictor-v3 | SHWD    | SFCHD (ours) |」 | `README.md:43`

- **协议原文中"用哪个测试集 / 怎么评测 / 标注是否扣留"的原句（逐字，如上）**：
  - "用哪个测试集"：`sfchd-scale.pdf` 第 4 页 §3.2 「Our dataset is divided into training set and testing set, and the ratio is 4:1. We have 12,373 images in SFCHD dataset, including 9,898 images in the training set, 2,475 images in the testing set.」（**两档**；未提 `val`，未提第三档）
  - "怎么评测"：`sfchd-scale-suppl.pdf` 第 7 页 §D.1 「All experiments are conducted using MMDetection [26], with dataset partitions following the default configuration.」＋「We evaluate the mean average precision (mAP) of the object detection to measure the performance of all models fairly. The mAP(0.50:0.95) metric measures the mAP across different Intersection over Union (IoU) thresholds, ranging from 0.50 to 0.95 with an interval of 0.05.」
  - "标注是否扣留"：**NOT FOUND** —— `sfchd-scale.pdf` 抽文 / `sfchd-scale-suppl.pdf` 抽文 / `README.md` / `SCALE.py` / `directory.md` 中 `withhold|withheld|not publicly|hidden|blind|submission|submit|leaderboard|eval server|benchmark server` **全部 0 命中**。
  - 试过的全部入口：`raw.githubusercontent.com/lijfrank/SFCHD-SCALE/7bfabb4533613e6917461dc3758dcff5f304bd03/{README.md,sfchd-scale.pdf,sfchd-scale-suppl.pdf,SCALE.py}`；`codeload.github.com/lijfrank/SFCHD-SCALE/tar.gz/7bfabb4533613e6917461dc3758dcff5f304bd03`（200）；`codeload.github.com/lijfrank/SFCHD-SCALE/tar.gz/main`（200）；`codeload.github.com/lijfrank/SFCHD-SCALE/tar.gz/master`（**404**）；`data.jsdelivr.com/v1/packages/gh/lijfrank/SFCHD-SCALE@7bfabb4…?structure=flat`（**403**）；`raw.githubusercontent.com/lijfrank/SFCHD-SCALE/7bfabb4…/README.md`（首次 `Recv failure`，重试 200）；`https://pan.baidu.com/s/1k2pWg8r-G3KSI2Q3Tdt6kg`（200，需登录）；`https://drive.google.com/file/d/1-2z7r3J4sZdLvVt5mllvSEwAFO49Y-zj/view`（000）；`git ls-remote https://github.com/lijfrank/SFCHD-SCALE`（失败，github.com 不可达）。

---

#### R0b 补采证据（本地直取第一方仓，2026-10-08；逐字 + 实测）

* **来源**：`lijfrank/SFCHD-SCALE@main` 的 `README.md`（本地件 sha256 `ed7bf9dee35712ed…`，9,464 B）与 `dataset_SFCHD/new_split_yolo/{train,val,test}.txt`。
* **★ 实测行数（本轮本地复核，UTF-8）**：`train.txt` **9,897** 行 · `val.txt` **2,475** 行 · `test.txt` **5** 行（393 B）。
* **官方 README 的目录树（`Dataset Acquisition` 节）** 逐字列出：`annotations` · `classes.txt` · `directory.md` · `images` · `labels` · `labels.cache` · **`new_split_yolo`** · `sd_train` · `train` · `Vision` · `yolo`（"8 directories, 3 files"）。
  ⇒ **官方确实提供 `new_split_yolo` 目录**，但**只说"unzip labels.zip and yolo.zip"**，**未说明 `new_split_yolo` 与 `yolo/` 两套切分的关系**，亦**未声明 test 与 val 的关系**。
* **README 的 Testing 行（L30）**：「| Testing | 3,482 | 2,920 | 3,032 | 154 | 239 | 271 | 238 | **10,336** |」——与本仓 `test.txt` 的 **5** 行**数量级不一致**（该行是"实例数"口径，非文件行数，但它进一步说明**官方从未把 test 档与 val 档的关系写清**）。
### 卡 15 · MAFA

* **E1**：**无 yaml**（官方无论文代码仓）。
* **E2**：官方 CVPR 2017 论文（pypdf 抽文）：§5.1 / §5.2 p.7 逐字 **"we only report the performances … on the testing set"** + Table 1 表题。
* **E3 报告口径**：同上（报 testing set）。
* **E4**：**NOT FOUND**（官方无 git 仓；论文抽文全文 **0 条 URL**）。

#### R0 补采证据（2026-10-08，逐字）

**[C]** **第一方识别**：官方**无论文之外的发布仓**（`github.com` 不可达，无法搜仓；task brief 亦述"官方无 git 仓"）。
第一方文档 = 官方 CVPR 2017 论文：Shiming Ge, Jia Li, Qiting Ye, Zhao Luo, "Detecting Masked Faces in the Wild With LLE-CNNs", CVPR 2017。
出处: https://openaccess.thecvf.com/content_cvpr_2017/papers/Ge_Detecting_Masked_Faces_CVPR_2017_paper.pdf （HTTP 200，1,202,862 B；`Last-Modified: Wed, 31 May 2017 00:40:51 GMT`；本机缓存件 `mafa.pdf`，pypdf 抽文 9 页，抽文件 `mafa.txt`）。
印刷页码映射（pypdf 抽文页脚）：PDF 第 n 页 → 印刷页 `4320 + n - 1`。

#### 目标格：release

- **采到（论文里"数据是否可下载 / test 标注是否公开"的逐字句）**:
  - 唯一涉及"发布"的句，§1（PDF **第 2 页**，印刷页 4321）逐字: 「The dataset will be released soon on the Internet, which we believe can facilitate the development of new face detectors in the future.」 | 出处: https://openaccess.thecvf.com/content_cvpr_2017/papers/Ge_Detecting_Masked_Faces_CVPR_2017_paper.pdf | 文件/段: `mafa.pdf` PDF 第 2 页 §1 Introduction（本机抽文 `mafa.txt:91`）
  - 同段前置逐字: 「Toward this end, this paper presents a dataset for masked face detection, which is denoted as MAFA. The dataset consists of 30, 811 Internet images, in which 35, 806 masked human faces are manually annotated. In the annotation process, we ensure that each image contains at least one face occluded by various types of masks, while the six main attributes of each masked face, including locations of faces, eyes and masks, face orientation, occlusion degree and mask type, are manually annotated and cross-checked by nine subjects.」 | 同上 | `mafa.pdf` PDF 第 2 页 §1（`mafa.txt:84-91`）
  - §3.2（PDF 第 4 页，印刷页 4323）逐字: 「After the annotation, we obtain 35, 806 masked faces with a minimum size of 32 × 32.」 | 同上 | `mafa.pdf` 第 4 页 §3.2 Dataset Statistics（`mafa.txt:312`）
- **采到（"论文通篇没有任何数据集下载 URL"这一事实）**:
  - 全篇 URL 式字符扫描：`grep -nE "http|www\.|\.cn|\.com|\.org"` 在 41,296 B 抽文中命中 **1 行**，逐字为「* Corresponding author: Jia Li (email: jiali@buaa.edu.cn).」 | 出处: 同上 | 文件/段: `mafa.pdf` 第 1 页脚注（`mafa.txt:43`）
  - CVPR Open Access HTML 版亦无数据集/官网外链：`curl -L https://openaccess.thecvf.com/content_cvpr_2017/html/Ge_Detecting_Masked_Faces_CVPR_2017_paper.html` → HTTP 200；对其 `href` 做 `mafa|escience|dataset|geshiming` 与 `suppl` 两次抽取，命中 **0**。
  - 该论文**无** supplementary 链接（CVPR OA HTML 页 `href` 中 `suppl` = 0 命中）。
- **NOT FOUND（官方站（第一方发布页）逐字句）**:
  - 领域内通称的官方页 `http://www.escience.cn/people/geshiming/mafa.html` 在本环境**不可达**，因此**未能采到**"数据是否可下载 / test 标注是否公开"的**官方站逐字句**。
  - **试过的全部入口**（逐条，含实测结果）：
    1. `http://www.escience.cn/people/geshiming/mafa.html` → HTTP 000（`Failed to connect to www.escience.cn port 80`，21,075 ms）
    2. `https://www.escience.cn/people/geshiming/mafa.html` → HTTP 000（`port 443`，21,028 ms）
    3. `http://www.escience.cn/people/geshiming/index.html` → 超时（>60 s）
    4. `http://escience.cn/people/geshiming/mafa.html`（无 www）→ HTTP 000
    5. `http://www.escience.cn`（裸域）→ HTTP 000
    6. `https://web.archive.org/web/2020/http://www.escience.cn/people/geshiming/mafa.html` → HTTP 000（`Failed to connect to archive.org port 443`）
    7. `http://web.archive.org/web/2020/http://www.escience.cn/…` → HTTP 000
    8. `https://archive.org/wayback/available?url=…`（两条：`mafa.html`、`index.html`）→ HTTP 000
    9. `https://web.archive.org/web/2020/…`（`web_fetch` 工具重试）→ `TypeError: fetch failed`
    10. `http://www.escience.cn/people/geshiming/mafa.html`（`web_fetch` 工具）→ `TypeError: fetch failed`
    11. `http://timetravel.mementoweb.org/timemap/link/http://www.escience.cn/people/geshiming/mafa.html` → HTTP 000
    12. `http://archive.ph/newest/http://www.escience.cn/people/geshiming/mafa.html` → HTTP 000
    13. `https://r.jina.ai/http://www.escience.cn/people/geshiming/mafa.html`（文本抽取代理）→ HTTP 000，0 B
    14. `https://sites.google.com/site/geshiming/mafa` → HTTP 000
    15. `https://sites.google.com/site/mafadataset/` → HTTP 000
    16. `https://drive.google.com/...`（本环境全域）→ HTTP 000
    17. `https://service.tib.eu/ldmservice/dataset/mafa` → HTTP 200（**第三方目录站**，非第一方；未从其中提取到官方逐字句）
    18. `https://paperswithcode.com/dataset/mafa` → HTTP 302（**第三方**）
    19. `web_search` × 5 组查询（`MAFA masked faces dataset official download page Shiming Ge` / `MAFA "Masked Faces in the Wild" download escience.cn geshiming` / `MAFA benchmark masked face detection dataset official website CVPR 2017` / `"MAFA" dataset "escience.cn/people/geshiming/mafa.html"` / `MAFA masked face dataset "will be released" OR "not publicly available" test set annotations` / `MAFA masked face dataset 官网 下载 test set 标注 不公开`）→ 返回均为第三方综述/目录页，**未给出可达的第一方发布页**
  - 逐字证据（论文内**不存在**"测试集标注不公开 / 不可下载 / 需提交"的句子）：`grep -niE "submit|submission|publicly available|not publicly"` 在 `mafa.txt`（41,296 B 全篇）命中 **0**；`grep -niE "available|release|download|http|public|request"` 全篇命中中，与数据发布相关的**仅** `mafa.txt:91` 那一句「The dataset will be released soon on the Internet」（其余为 `obtain`/`database` 等无关词）。

#### 目标格：protocol

- **采到（论文里评测协议与提交要求的那一段）**:
  - §5.1 「Experimental Settings」（PDF **第 7 页**，印刷页 4326）逐字: 「In the benchmarking process, we split the MAFA into two subsets, including a training set and a testing set. The training set consists of 25, 876 images with 29, 452 masked faces that are randomly selected from MAFA, while the testing set contains the rest 4, 935 images with 6, 354 masked faces.」 | 出处: https://openaccess.thecvf.com/content_cvpr_2017/papers/Ge_Detecting_Masked_Faces_CVPR_2017_paper.pdf | 文件/段: `mafa.pdf` 第 7 页 §5.1（本机抽文 `mafa.txt:573-577`；抽文里数字带空格即原文排版）
  - §5.1 续（同页）逐字: 「In this study, we only report the performances of our approach and the six face detectors on the testing set, while such results can be directly used to facilitate their comparisons with new models trained on the same training set of MAFA in the future.」 | 同上 | `mafa.pdf` 第 7 页 §5.1（`mafa.txt:578-582`；抽文中连字符换行为 `perfor-`/`mances`、`facili-`/`tate`，此处按行内还原）
  - §5.1 首段（同页）逐字: 「As stated in Sect. 2, existing face detection models can be roughly grouped into three major categories (i.e., boosting-based, DPM-based and CNN-based). From these three categories, we select six state-of-the-art face detectors for benchmarking, including two from the boosting-based category (SURF [18] and NPD [20]), three from the DPM-based category (ZR [37], HH [22] and HPM [7]), and one CNN-based detector (MT [35]).」 | 同上 | `mafa.pdf` 第 7 页 §5.1（`mafa.txt:560-570`）
  - §3.1 标注规则（PDF **第 3 页**，印刷页 4322）逐字: 「On these images, we ask nine subjects to manually annotate all faces, and each image is annotated by two subjects and cross-validated by the third subject.」 | 同上 | `mafa.pdf` 第 3 页 §3.1（`mafa.txt:260-262`）
  - §3.1 「Ignore」评测规则（同页）逐字: 「Similar to [30], a face will be labeled as "Ignore" if it is very difficult to be detected due to blurring, severe deformation and unrecognizable eyes, or the side length of its bounding box is less than 32 pixels. Note that faces with the label "Ignore" will not be counted as true positives or false alarms once being detected.」 | 同上 | `mafa.pdf` 第 3 页 §3.1（`mafa.txt:267-273`；抽文写作 "Ignore" 用弯引号）
  - §3.1 数据来源（同页）逐字: 「We first collect a set of facial images from the Internet. In this process, keywords such as 'face, mask, occlusion and cover' are used to retrieve more than 300K images with faces from social networks like Flickr and the image search engines like Google and Bing. Note that we only keep the images with a minimal side length of 80 pixels. After that, images that contain only faces without occlusion are manually removed. Finally, we obtain 30, 811 images in total, and each image contains at least one masked face.」 | 同上 | `mafa.pdf` 第 3 页 §3.1（`mafa.txt:251-258`）
- **"标注是否扣留 / 是否需提交"的官方原句**: **NOT FOUND**
  - `mafa.pdf` 全篇抽文（41,296 B）中 `submit|submission|publicly available|not publicly` = **0 命中**；`withhold|withheld|blind|hidden|leaderboard|server` = **0 命中**。
  - 论文**无**任何"提交到评测服务器 / 排行榜 / 标注扣留"的句子。
  - 官方站逐字句 **NOT FOUND**（官方站不可达，入口清单见上「release」节的 19 条）。
- 论文内**无 `validation` 三档**（登记事实）：`grep -ci "validat"` = **2**，两处均非 split 名，逐字为 `and cross-validated by the third subject.`（`mafa.txt:262`）与 `These results validates how effective our approach`（`mafa.txt:593`）。论文切分自述为随机二分（「that are randomly selected from MAFA」）且 `testing` 出现 **8** 次、`val` 作为单词 **0** 次。

#### 目标格：reported

- **采到（官方"报告在哪个 split"的逐字语句）**:
  - §5.1 「Experimental Settings」（PDF 第 7 页）逐字: 「In this study, we only report the performances of our approach and the six face detectors on the testing set, while such results can be directly used to facilitate their comparisons with new models trained on the same training set of MAFA in the future.」 | 出处: https://openaccess.thecvf.com/content_cvpr_2017/papers/Ge_Detecting_Masked_Faces_CVPR_2017_paper.pdf | 文件/段: `mafa.pdf` 第 7 页 §5.1（`mafa.txt:578-582`）
  - §5.1 前置句（同页）逐字: 「In the benchmarking process, we split the MAFA into two subsets, including a training set and a testing set. The training set consists of 25, 876 images with 29, 452 masked faces that are randomly selected from MAFA, while the testing set contains the rest 4, 935 images with 6, 354 masked faces.」 | 同上 | `mafa.pdf` 第 7 页 §5.1（`mafa.txt:573-577`）
  - §5.2 「Comparisons with State-of-the-Art Models」（PDF 第 7 页）逐字: 「While our AP reaches up to 76.4% over the testing set of MAFA, the second best model, MT, only reaches an AP of 60.8%.」 | 同上 | `mafa.pdf` 第 7 页 §5.2（`mafa.txt:588-590`）
  - Table 1 表题逐字: 「Table 1. Average Precision (%) on the Testing Set of MAFA」 | 同上 | `mafa.pdf` 第 7 页 Table 1（`mafa.txt:604`）
  - §5.2 末尾（同页）逐字: 「In particular, it further proves the necessity of constructing such a dataset with diversified masked faces, which can be not only used for model benchmarking but also used as an additional training source in developing new face detectors.」 | 同上 | `mafa.pdf` 第 7 页 §5.2（`mafa.txt:595-600`）
- **官方站（第一方发布页）逐字句**: **NOT FOUND**（官方站不可达；入口清单见上「release」节的 19 条）。
- 论文内**无 `validation` 档**（登记事实，同上「protocol」节）：`validat` 命中 2 处，均非 split 名。
- 逐字证据（该基准名称与任务书别名的差异，登记备查）: 「this paper presents a dataset for masked face detection, which is denoted as MAFA. The dataset consists of 30, 811 Internet images, in which 35, 806 masked human faces are manually annotated.」 | 出处: 同上 | 文件/段: `mafa.pdf` 第 2 页 §1（`mafa.txt:84-88`）；论文全篇**无** "mosaic/马赛克" 字样。
- 试过的全部入口：同「protocol」节的 19 条入口清单（论文 PDF / CVPR OA HTML / 官方站及其 8 个存档代理 / 2 个第三方目录站 / 6 组 `web_search`）。

---

### 采集汇总（仅登记采/未采，不含判定）

| 行 | 基准 | 目标格 | 结果 |
|---|---|---|---|
| 13 | SHWD | `reported` | **采到**（官方"未声明报告 split"事实 + 全量检查清单 + 官方 Benchmark 表与 train/val 配置逐字）；官方口径本身 `NOT FOUND`；第三方 SciRep 7:2:1 句已采并标注**非官方** |
| 14 | SFCHD | `release` | **采到**（第一方仓 `dataset_SFCHD/` 全部切分档清单 + README 逐字 + `test.json`=0 B / `test.txt`=6 条且 test⊆val 实测 + "README/论文/补充/`directory.md`/`SCALE.py` 对 test 与 val 关系**无声明**"的 0 命中清单） |
| 14 | SFCHD | `protocol` | **采到**（论文 §3.2 + 摘要 + supplementary §D.1 Details 协议段逐字）；"标注扣留/需提交"句 `NOT FOUND` |
| 15 | MAFA | `release` | **采到**（论文 §1「will be released soon on the Internet」逐字 + 论文全篇无任何数据集 URL + CVPR OA HTML 无外链）；官方站逐字句 `NOT FOUND`（19 条入口已列） |
| 15 | MAFA | `protocol` | **采到**（§5.1 全段 + §3.1 标注与 Ignore 规则逐字）；"标注扣留/需提交"与官方站原句 `NOT FOUND` |
| 15 | MAFA | `reported` | **采到**（§5.1「we only report the performances … on the testing set」+ §5.2 + Table 1 表题逐字）；官方站原句 `NOT FOUND` |

#### R0b 补采证据（本地直取官方 PDF，2026-10-08；逐字）

* **来源**：`_p2_missing_evidence_20261008/MAFA/MAFA_CVPR2017.pdf`（**12,028 B? 实为 1,202,862 B**；sha256 `2ab904ec252fbc24…`；CVPR 2017 官方 OA 版，9 页）
* **发布句（PDF p.2，§1 Introduction 末）**：「**The dataset will be released soon on the Internet**, which we believe can facilitate the development of new face detectors in the future.」
  **注**：**全文无任何数据集 URL**（唯一 URL 是通讯作者邮箱），亦无"test 标注公开/扣留"的声明。
* **协议与划分（PDF p.7，§5.1）**：「In the benchmarking process, we split the MAFA into **two subsets, including a training set and a testing set**. The training set consists of **25, 876 images with 29, 452 masked faces** that are randomly selected from MAFA, while the **testing set contains the rest 4, 935 images with 6, 354 masked faces**.」
  ⇒ **只有 train / test 两档，没有 validation**（全文 `validat` 仅出现于 `cross-validated` 与 `validates`）。
* **报告口径（PDF p.7，§5.1）**：「In this study, **we only report the performances of our approach and the six face detectors on the testing set**…」
* **结果表（PDF p.7，Table 1 表题）**：「**Average Precision (%) on the Testing Set of MAFA**」；正文「our AP reaches up to **76.4%** over the testing set of MAFA, the second best model, MT, only reaches an AP of **60.8%**」。
* **仍未采到**：**官方站的发布物清单**（`escience.cn` 整域不可达；见 `_无卡机拉取清单.md` 第②项）。
### 卡 16 · Mendeley face-mask

* **E1**：**无公开 yaml**。作者方镜像配置名为 `mende20_3way.yaml`（训练机上 `/root/datasets_mask/mendeley_yolo/mende20_3way.yaml`），
  由**一个生成器脚本**产出（论文 §6.1 记录：它 "wrote two keys from one `images_dir`"，故 `train == val`）。
* **E2 官方出处**（论文参考文献 [22] 逐字）：**"Mendeley Data records, 'Face Mask Detection' (data records, no venue).
  Widely used 853-image PASCAL-VOC variant: `https://www.kaggle.com/datasets/andrewmvd/face-mask-detection`"**。
* **E3 报告口径**：**NOT FOUND**。已查：① Kaggle `andrewmvd/face-mask-detection` 页面全文（**无任何评测命令**）；
  ② DataCite（前缀 `10.17632`）检索 `"face mask"` 得 4 条候选 record（`v3kry8gb59`/`xz5hbd6zds`/`8pn3hg99t4`/`7bt2d592b9`，
  DOI 与版本日期已录），**均与 [22] 所指的 853 图变体不是同一条**；③ 精确标题 `titles.title:"Face Mask Detection"`
  **只命中 `v3kry8gb59`**，**不存在标题恰为 "Face Mask Detection" 的 Mendeley record**。
* **E4**：Mendeley Data record（DOI 前缀 `10.17632`）+ Kaggle `andrewmvd/face-mask-detection` 变体页。
* **关键观测（逐词计数）**：Kaggle 该页全文 + API `description` 字段中，`train`/`val`/`test`/`split`/`validation`
  出现次数**均为 0** ⇒ **官方页面未声明任何官方划分**。
* **旁证（归属未确认，已标注）**：公开的 VOC→YOLO 生成器 `Prikshit7766/Face-Mask-Detection@ecd8be957c3a14e57d4f00cd9e62024d192479fd`
  的 `convert_voc_to_yolo.py:17-20` 逐字用**同一个** `images_dir` 同时写 `train:` 与 `val:`、**不写 `test:`** ——
  形态与 §6.1 所述一致，**但不是 `mende20_3way.yaml` 本体**。
* **另**：Kaggle 页给出的上游来源 `https://makeml.app/datasets/mask` 现为**停放域名**。

#### 补采证据（2026-10-08，逐字）

- 目标: 补 **Mendeley Data 上 DOI 前缀 `10.17632` 下所有口罩类 record 的"文件清单"**（看有没有 train/val/test 子目录），以及 **Kaggle 页 API JSON 的 `files` 列表（逐字）**。
- 结果: **采到**。
- 逐字证据:

  1. **Kaggle API JSON 的 `files` 字段（逐字）**：
     `"files":[]`
     同一 payload 中与文件相关的其余字段逐字：`"totalBytes":417887308`、`"totalBytesNullable":417887308`、`"currentVersionNumber":1`、`"lastUpdated":"2020-05-22T07:18:42.22Z"`（顶层字段；`versions[0].creationDate` 同值）、`"versions":[{"creatorNameNullable":"Larxel","creatorRefNullable":"face-mask-detection","versionNotesNullable":"Initial release","statusNullable":"Ready","versionNumber":1,"creationDate":"2020-05-22T07:18:42.22Z",…}]`（`versions[0]` 内**亦无** files 列表）。
     | 出处: https://www.kaggle.com/api/v1/datasets/view/andrewmvd/face-mask-detection | 文件: 响应 JSON 顶层 `files` 字段（值＝空数组 `[]`）

  2. **Mendeley Data（DOI 前缀 `10.17632`）口罩类 record 的文件清单**——检索口径：DataCite
     `https://api.datacite.org/dois?query=%22face%20mask%22&page%5Bsize%5D=100&prefix=10.17632` → `"total": 44`（含版本条目），去版本号后得 **21 个 base record**；逐条经
     `https://data.mendeley.com/public-api/datasets/<id>` 的 `files[].filename` 取得**顶层文件清单**（逐字）：
     （下列 `n=` 为该 record 的 `files` 数组长度；`/` 计数均为 0，即**文件名中不含任何子目录路径**）

     | # | DOI（`10.17632/…`） | record 标题 | `files` 顶层文件名（逐字） | 含 train/val/test/split 的文件名 |
     |---|---|---|---|---|
     | 1 | `v3kry8gb59` | Face Mask Detection Video Dataset | `Annotations.zip`、`Image frames.zip`（n=2） | 无 |
     | 2 | `xz5hbd6zds` | Indian Facemasks Detection Dataset | 3795 个扁平文件，样例逐字：`433333.jpg`、`433333.xml`、`as (1).jpg`、`as (1).txt`、`as (1).xml`、`with_mask_1.jpg`、`with_mask_1.txt`、`with_mask_1.xml`、`without_mask_1.jpg`、`New folder1.jpg`、`ol (1).jpg`（n=3795） | 无 |
     | 3 | `7bt2d592b9` | Face Mask Dataset 2022 | `Face_Mask_Dataset.zip`（n=1） | 无 |
     | 4 | `8pn3hg99t4` | Face Mask Wearing Image Dataset: Correct vs. Incorrect Usage | `NewFace Mask Dataset.zip`（n=1） | 无 |
     | 5 | `pk44mkx9vm` | halfFace: A face covering mask dataset of South Asian people | `halfFace_A face covering mask dataset of South Asian people.zip`、`README_FILE.txt`（n=2） | 无 |
     | 6 | `vmwfj9hshf` | Covid Face-Mask Monitoring Dataset | `classes.txt`、`Full_Dataset.rar`、`Training.rar`、`Validation.rar`（n=4） | **`Training.rar`、`Validation.rar`**（无 test） |
     | 7 | `t4rxhrgrt8` | 3D-printed mask | `Base_part_L.stl`、`Base_part.stl`、`Cup_part.stl`、`End_part.stl`、`Filter_holder.stl`、`Side_part.stl`（n=6） | 无 |
     | 8 | `vyxc5dw4yk` | REUSABLE FACE MASK CAD FILES | `FACE MASK CATIA V5.CATPart`、`FRONT CAP.CATPart`（n=2） | 无 |
     | 9 | `mcmzzct9m9` | Primary data for "Face mask-wear did not affect large-scale patterns in escape and alertness of urban and rural birds …" | `data.txt`、`READ_ME.txt`（n=2） | 无 |
     | 10 | `74p6w8xx5r` | Data for: Intelligibility of face-masked speech depends on speaking style… | `mask_spin_keyword_accuracy.csv`（n=1） | 无 |
     | 11 | `8mvrgbsyt6` | Face mask use in the community and cutaneous reactions to them during the COVID-19 pandemic | `Survey_mask_mand.zip`（n=1） | 无 |
     | 12 | `b2yzdfv9rt` | Surveillance for face mask compliance, Chennai, Tamil Nadu, India, October-December, 2020 | `Surveillance for face mask compliance, Chennai, Tamil Nadu, India, October-December, 2020.csv`（n=1） | 无 |
     | 13 | `vkv4cwhh7n` | Face mask use in the city of Chennai, India: Results from three serial cross-sectional surveys, 2021 | `All Rounds - Indoor.csv`、`All Rounds - Outdoor.csv`、`Mall Data.csv`（n=3） | 无 |
     | 14 | `cth7frh3pd` | Dr. Olusolape Ilusanya | `Data on perception of the effectiveness of face mask use in combating the spread of COVID-19 in Nigeria REVISED.xlsx`、`Data on perception on the effectiveness of face mask use in combating the spread of COVID-19.xlsx`（n=2） | 无 |
     | 15 | `h62z6vjxxc` | Association between the Use of Face Mask and Contact Dermatitis … -Supplemental Material | `Supplemental Material 1 Questionnaire.pdf`（n=1） | 无 |
     | 16 | `pg64b8wysh` | HIFNI_COVID | `HIFNI_COVID Masterchart.xlsx`（n=1） | 无 |
     | 17 | `zfd3s5hpzn` | Face Mask Reduces Gaze-Cueing Effect | `Experiment 1 Data.xlsx`、`Experiment 2 Data.xlsx`（n=2） | 无 |
     | 18 | `9s6fm7vdbc` | The collection of narratives on face mask wearing … | `The collection of narratives on face mask wearing written by members of scholarly association Navigating Knowledge Landscapes Network in May 2020.pdf`（n=1） | 无 |
     | 19 | `5n5f4xv6z6` | Emergency Dosimtery using Thermoluminescence of CaCO3 containing polymer fibers | 192 个扁平文件，样例逐字：`150lmm_bluefilterpack_2019-10-10.asc`、`20210301_Mask_1kbtest.binx`、`20210302_First_test_Omya_01_01_03_TL.calib`（n=192） | 无（仅文件名内含 `test` 字样的测量文件，非 split 目录） |
     | 20 | `zbz8p82n6k` | Two-Handed Mask Seal Technique Improves Ventilation … | `Root et al CPR Study Data.xlsx`（n=1） | 无 |
     | 21 | `zvmfd839d6` | Ho, Lukafor, and Yan-SER2024-Health System Performance | `data generation.do`、`datacovid19forreg.dta`、`disaster response--11 Dec 2023-v2.do`（n=3） | 无 |

     | 出处: `https://data.mendeley.com/public-api/datasets/<id>`（`<id>` 见上表；字段 `files[].filename`、`files[].content_details.size`、`doi.id`、`version`）；检索清单来自 `https://api.datacite.org/dois?query=%22face%20mask%22&page%5Bsize%5D=100&prefix=10.17632`（total 44） | 文件: 采集件 `mall_<id>.json`（21 份）之 `files` 数组；`dc_fm.json` 之 `data[].id/titles`

  3. **逐条事实陈述（仅核验，不作判定）**：上述 21 条 record 中，**无任何一条**的 `files[].filename` 含路径分隔符（全部为顶层文件），因此**均不存在 train/val/test 子目录**；唯一在文件名层面出现划分词的是 `10.17632/vmwfj9hshf` 的 `Training.rar` / `Validation.rar`（无 test 项）。
     另：上一轮已核 Kaggle `andrewmvd/face-mask-detection` 页面/description 中 `train`/`val`/`test`/`split`/`validation` 出现次数均为 0；本轮补到的 API `files` 亦逐字为 `[]`。
     | 出处: 同第 2 条 | 文件: `mall_*.json` 汇总

- 备注（仅事实）: DataCite 宽口径 `query=mask&prefix=10.17632` 的 `"total": 683`（与口罩无关的作物/洪水/涡旋等 record 混入），故本行采用 `query="face mask"` 口径（44 条 / 21 base record），并逐条列出其文件清单；`README_FILE.txt`（`pk44mkx9vm`）与 `READ_ME.txt`（`mcmzzct9m9`）为上述 21 条中仅有的两份"随附说明文件"，其**文件名**可逐字引用，**内容未下载**（属压缩包/说明文件本体，非本次要求的 split 句来源）。

---

### 卡 17 · WIDER FACE

* **E1**：**无 yaml**。官方分发物为 `.mat` / `.txt`；`wider_face_split.zip` 的文件清单（逐字）见 `_e3_e1/e3_rows16_19.md`。
* **E2 官方文档（关键）**：官方站点 Description 节原文逐字：
  **"Similar to MALF and Caltech datasets, we do not release bounding box ground truth for the test images.
  Users are required to submit final prediction files, which we shall proceed to evaluate."**（论文 arXiv:1511.06523 §3.1 同句）
* **E3 报告口径**：论文 §3.1 Overview 末段逐字 **"For each event class, we randomly select 40%/10%/50% data as training, validation and testing sets."**；
  评测场景逐字 **"Scenario-Ext: A face detector is trained using any external data, and tested on the WIDER FACE test partition."** /
  **"Scenario-Int: … tested on WIDER FACE test partition."**；官方 Results 页**并列** "validation set" 与 "test set" 两组曲线。
* **E4**：站点 `http://shuoyang1213.me/WIDERFACE/` + 三个 zip（train/val/test 图像、`wider_face_split.zip`、`eval_tools.zip`）。
  **旁证（逐字）**：标注包内**无** `wider_face_test_bbx_gt.txt`；`eval_tools/ground_truth/` 只有 `*_val.mat`；
  `wider_eval.m:2` 逐字 **"% Conduct the evaluation on the WIDER FACE validation set."**
  **commit `NOT FOUND`**：官方无 GitHub 仓（`git ls-remote` 两次失败，原因已录）。

### 卡 18 · CrowdHuman

* **E1**：镜像 yaml `Mackenzie-TCC-IA/tracking-system@5ed77e77…` 的 `data-crowd-humans.yaml:1-5`：**只有 `train`/`val`，无 `test` 键**。
* **E2**：官方下载页逐字**只提供** `annotation_train.odgt` / `annotation_val.odgt`。
* **E3 报告口径**（论文 §4.2 逐字）：**"The annotations of testing subset will not be made publicly available."**；
  同段另逐字 **"trained based on CrowdHuman train subset and the results are evaluated in the validation subset"**。
* **E4**：官方仓库 `sshao0516/CrowdHuman` **只是官网静态页**（README 是 Start Bootstrap 模板），**不含评测代码** ⇒
  官方评测命令 **NOT FOUND**。

#### R0c 补采证据（AutoDL 公共数据集区**实物清单**，2026-10-09；只读列举）

* **来源**：AutoDL 实例 `/root/autodl-pub/CrowdHuman/`（归档 `_p2_missing_evidence_20261008/_from_autodl/p2_probe/pub_inventory.txt`）。
* **目录逐字**：`CrowdHuman_test.zip`（3,259,241,265 B）· `CrowdHuman_train01.zip` · `CrowdHuman_train02.zip` · `CrowdHuman_train03.zip` · `CrowdHuman_val.zip`（2,488,658,160 B）
  · **`annotation_train.odgt`**（80,017,502 B）· **`annotation_val.odgt`**（23,323,139 B）。
* **★ 决定性核对**：`CrowdHuman_test.zip` 内含 `images_test/*.jpg`，**其中"标注类文件"（`.odgt`/`.json`/`.txt`/含 `annotation` 名）命中数 = 0**。
  ⇒ **发布物里 test 图像存在、test 标注不存在**；且目录里**只有 train 与 val 两个 .odgt**。
* **用途**：`CrowdHuman · release` 与 `protocol` 两格（与卡片 E2/E3 的论文原句「annotations of testing subset will not be made publicly available」**互证**）。
### 卡 19 · D-Fire (FireSmoke)

* **E1**：**无 yaml**（官方仓库只有 `README.md` / `utils/utils.py` / `LICENSE` / `figures`）。
* **E2**：官方仓库 `gaiasd/DFireDataset@4bf9c31b18fadcd44d5f0b6d66f82bc56fa5e328`（旧路径 `gaia-solutions-on-demand/DFireDataset` 重定向至此）；
  `README` L51 逐字 **"… pre-split training, validation, and test sets …"**，L54 另有说明；**"more than 21,000 images"**。
* **E3 报告口径**：**NOT FOUND** —— 官方论文（Springer `10.1007/s00521-022-07467-z`）**有登录墙**（cross-origin redirect 到 `idp.springer.com`），
  协议句未取得；已用官方 `README` L51/L54 逐字替代。
* **E4**：官方仓库**无** `val.py` / `test.py` ⇒ 官方评测命令 **NOT FOUND**。
* **附带不一致（只报观测）**：某镜像 YOLO11 仓库 README 自相矛盾 —— 指标表标题 `### Final Validation Results`（含 mAP@50 0.770）
  而示例图小节写 `Here are examples from the test set:`；其划分表图像总数 10,463 与官方 README `more than 21,000 images` 不一致。

---

#### R1 补采证据（**一手核验**，2026-10-09；只含证据事实与出处，**不含任何取值建议**）

> 本节为各行的**新增一手证据**。取件方式：官方发布物清单 / 官方仓 pin sha 的原文 / 官方论文原句；
> 一律经可出网中转机取件，抓取日期 **2026-10-09**。**GitHub 证据均已 pin sha**（下文给出）。
> **本节不含判定结论** —— 请照 §1–§7 的判定树自行落值。

**卡 1 · COCO**
* 官方标注包 `annotations_trainval2017.zip`（252,907,541 B）的中央目录**完整清单 = 6 个文件**：
  `annotations/instances_train2017.json` · `annotations/instances_val2017.json` · `annotations/captions_train2017.json` ·
  `annotations/captions_val2017.json` · `annotations/person_keypoints_train2017.json` · `annotations/person_keypoints_val2017.json`。
  含 "test" 的条目数 **= 0**。
* 官方另发 `image_info_test2017.zip`，内含 **`image_info_test-dev2017.json` 与 `image_info_test2017.json`**（**仅为图像信息，非标注**）。
* `test2017.zip`（6,646,970,404 B）内为 **40,671 条 `.jpg`**。
* 官方数据集指南原句（`dataset/guidelines.htm` @ `5e1c4da…`）：**"test-dev cannot be used for training (annotations are private)"**；
  同页 Test-Dev 行给出 **`submit limit = 5 per day`**。
* 发行包 `coco.yaml`：`:15` 的 `test:` 指向 `test-dev2017.txt` 并在注释中写 "submit via …"；`:113` 写 **"ground truth is withheld"**。

**卡 2 · PASCAL VOC**
* `VOCtest_06-Nov-2007.tar`（**451,020,800 B**）的 tar 头链**直接列出 `VOCdevkit/VOC2007/Annotations/*.xml`**。
* 官方 VOC2012 页原句：**"In VOC2007 we made all annotations available (i.e. for training, validation and test data)
  but since then we have not made the test annotations available. Instead, results on the test data are submitted to an evaluation server."**
  同页逐年写：**"This was the final year that annotation was released for the testing data"**；"2008 … **Test data annotation no longer made public**."
* 发行包 `VOC.yaml` `:18-21`：`val` 与 `test` **同指** `images/test2007`（4,952 张）。

**卡 3 · Objects365**
* 官方下载页 `objects365.org/download.html` 的**唯一外链是 BAAI 的单页应用**（764 B），**无服务端文件清单**；
  官方仓 `sshao0516/Objects365@e042eb0e` 的 `README.md` **仅 53 B**。
* 发行包 `Objects365.yaml` `:15`：**`test:` 键存在、值为空**；发行包文档原句 **"the `test:` key in the configuration is left empty"**、
  **"…1,822,289 in total, with no test split"**。

**卡 4 · Open Images v7**
* 官方 facts 页（`factsfigures_v7`）原句：**"The dataset is split into a training set (9,011,219 images),
  a validation set (41,620 images), and a test set (125,436 images)."** 与
  **"For the validation and test sets, we provide exhaustive box annotation for all object instances"**。
* `HEAD https://storage.googleapis.com/openimages/v5/test-annotations-bbox.csv` → **HTTP 200 / 77,484,237 B**（匿名可取）。
* 官方文档原句：**"The python implementation of both evaluation protocols is released as a part of Tensorflow Object Detection API."**
* Kaggle 通道是**另一个划分**：2019 页原句 **"The Challenge set (100k images) with hidden annotations … hosted by Kaggle"**，该服务器原句 **"officially closed"**。
* 发行包 `open-images-v7.yaml` 的 **`test:` 逐字为空**；其脚本只 `for split in "train", "validation"`；
  官方文档原句 **"The `test:` key in the configuration is left empty."**

**卡 5/6 · DOTA v1.0 / v2.0**
* v1.0 三个 Drive 档位的**一手清单**：`train` 与 `val` 各有 `labelTxt-v1.0/` 与 `labelTxt-v1.5/`；
  **`test` 档只有 `['images/', 'part1.zip', 'part2.zip']`，无任何 `labelTxt`**。
* 官方 news 原句：**"DOTA-v1.0 released with all images and oriented bounding box annotations for training and vallidation!"**
* v1.0 官方评测入口原句（Task 1 与 Task 2 各一条）：**"For evaluation, you must registrate and submit on the Evaluation Server"**；
  该 URL（`icdar2017chinese.site:5080`）现返回 **000**。
* v2.0 官方原句：**"Training contains 1,830 … Validation contains 593 … We released the images and ground truths for
  training and validation sets. Test-dev contains 2,792 … We released the images but not the ground truths.
  Test-challenge contains 6,053 … will be available only during the challenging."**
* 官方 devkit（pin `99388551…`）**只有 v1.0/v1.5 的评测脚本，无 v2.0**；发行包 52 个 yaml **只有 `DOTAv1.yaml`/`DOTAv1.5.yaml`**。

**卡 7 · VisDrone-DET**
* 官方仓（pin `4364e8265275dfa44fd8f767b5180af58580194d`）README 原句：
  **"Note that the bounding box annotations of test-dev are avalialbe. Researchers can use test-dev to publish papers.
  testset-challenge is used for VisDrone2020 Challenge and the annotations is unavailable."**
* 官方论文（arXiv:2001.06303）原句：**"6,471 … training subset, 548 … validation subset, 1,580 … test-challenge subset,
  and 1,610 … test-dev subset"**（合 10,209）。
* 发行包 `VisDrone.yaml` 逐字给出 `6471 / 548 / test-dev 1610 images`，并**逐字注释** `# Download (ignores test-challenge split)`。
* 官方在线评测服务器 **NOT FOUND**（`aiskyeye.com/challenge/object-detection/` 超时，有效码 000）。

**卡 8 · AI-TOD**
* 官方 Drive 清单**一手枚举**到 `complete_annotations/{aitod_train,aitod_val,aitod_trainval_v1_1.0,aitod_test_v1_1.0}.json`。
* **实测计数**（含 sha256）：train **11,214** 图 / 282,580 注 · val **2,804** / 70,424 · test **14,018** / 347,617 ·
  trainval 14,018 / 353,004；三划分图数和 **= 28,036** = README 总数；注总和 **= 700,621**。
* 官方 README 原句：**"Training, Validation and Testing sets are both publicly available now."**
* 官方论文（README 链接的 PDF）原句：**"In the case of test set, we will publicly only provide images without annotations."**
* 六类通用包检索面（ultralytics 全树 + PyPI wheel 8.4.174 解包 + docs 路由 + yolov5/yolov7/YOLOv6/darknet）对 `aitod` **全部 0 命中**。

**卡 9 · UAVDT**
* 官方划分原句：**"The official split is 30 training sequences (24,143 frames) and 70 test sequences (53,676 frames),
  with no official validation split."**
* 官方包名与出处：**`UAVDT-Benchmark-M (frames + annotations)`**，入口
  `https://drive.google.com/file/d/1m8KA6oPIRK_Iwt9TYFquC87vBc_8wRVc/view`。
* 来源说明：以上两句取自 HuggingFace `dronefreak/UAVDT` 的 `README.md`（5,975 B）；该 README **自称不托管数据**
  （"is **not** an official release of UAVDT and does not host any UAVDT images, annotations, or derived files"），
  故其对官方的陈述为**转述**；但它同时给出**官方包入口**，可交叉核验。

**卡 10 · xView**
* 官方发布清单**逐字只有 3 件**：`train_images` · `train_labels` · `val_images`。
* 官网教程原句：**"Labels are not available for the validation set."**
* 官网关于留出集原句：**"Neither images nor labels from the holdout set are available for download."**
* 评测方式：**提交容器由主办方算 mAP**；其 `api-main…/download` 端点匿名访问返回 **401**。
* 发行包 `xView.yaml` 的 `val` 是 **`autosplit` 出的 train 10%**：逐字 `val: images/autosplit_val.txt # … 10% of 847 train images`
  与 `autosplit(dir/"images"/"train")` ⇒ **不是**官方 282 图 val。
* 附带：发行包写 **847**，官方写 **846**；论文称 test 属 "public release"，与挑战站上句**冲突**。

**卡 11 · DIOR**
* 官方 Drive 目录（无需登录可列）**恰 4 个文件**：`Annotations.zip` · `ImageSets.zip` · `JPEGImages-test.zip` · `JPEGImages-trainval.zip`。
  文件 ID：`1KoQzqR20qvIXDf1qsXCHGxD003IPmXMw` · `1vOmzwxpBtwbK5o8xSa9u0IdB4H95MBHw` ·
  `11SXPqcESez9qTn4Z5Q3v35K9hRwO_epr` · `1ZHbHDM6hYAEGDC_K5eiW0yF_lzVgpuir`。
* `ImageSets.zip` **恰 6 条**：`Layout/` · `Main/` · `Main/test.txt` · `Main/train.txt` · `Main/val.txt` · `Segmentation/`
  ⇒ **有 test.txt 与 val.txt，无 trainval.txt**。行数：train **5,862** · val **5,863** · test **11,738**；train∪val = 11,725，两两交集 **0**。
* `Annotations.zip`（**32,064,775 B，已下载解包**）= **46,929 条**：`Horizontal Bounding Boxes/` **23,463** 个 XML +
  `Oriented Bounding Boxes/` **23,463** 个 XML；**test 区间（≥11726）实测 11,738 张全部有标注**。
  标注自证归属逐字：`11726.xml` 的 `<folder>` = `…/JPEGImages-test.zip/JPEGImages-test/JPEGImages-test` + `<filename>11726.jpg</filename>`。
* 官方论文（arXiv:1909.00133v2）原句：**"we randomly selected 11725 remote sensing images (i.e., 50% of the dataset) as trainval set,
  and the remaining 11738 images are used as test set."** + Table 2 合计 **5862 / 5863 / 11725 / 11738**。
* 官方 DIOR **代码仓不存在**（GitHub repo search 全为第三方个人仓）。
* 发行包层面：通用包对 `dior` 命中 **0**（全树 + wheel 8.4.174 的 51 个 yaml）。

**卡 12 · NWPU VHR-10**
* 官方域 `escience.cn` 四个变体全部 **000**（DNS 正常解析到 159.226.11.72，TCP 不通）；官方论文 **403 / `oa_status=closed`**。
* TorchGeo **HEAD = `379be63764354f078e626df239f4c1c7532959da`**（仓名已迁 **`torchgeo/torchgeo`**，`microsoft/` 为旧路径）：
  `datasets/vhr10.py`（sha256 `32efdc6e…`）的 **`split: Literal['positive','negative']` 指目标有无**；
  真正的 train/val/test 在 `datamodules/vhr10.py`（sha256 `c8190ca0…`）由 **`random_split(seed 0, 80/10/10)` 现造**。
* TorchGeo 全树 `recursive=1`（1.59 MB）对 `nwpu`/`vhr` **0 命中**（注：数据集模块名为 `vhr10`）。
* 镜像转录的官方说明只有 **positive(650) / negative(150)**。
* 通用包对 `nwpu`/`vhr` **0 命中**（yolov5 144 blob / ultralytics 1043 blob；detect 文档 24 项无 NWPU）。

**卡 13 · SHWD**
* 官方仓真身 **`njvisionpower/Safety-Helmet-Wearing-Dataset@c952631dfc352e0defdd54b4785a9be6576451ad`**
  （默认分支 **`master`**；`main` → 404）。**注：`nv0000/SHWD` 在 GitHub 不存在**（repo 与 user 均 404，HF/Gitee 亦空）。
* **26 文件穷举**：只有 `LICENSE` · `README.md` · `demo1.jpg` · 20 张 image · 3 个 `.py` ⇒ **无标注、无划分、无 yaml**。
* 数据本体**外链**（百度盘 + Google Drive id `1qWm7rrwvjAWs1slymbrLaCf7Q-wnGLEX`），跟随 Drive 确认页取得唯一文件名
  **`VOC2028.zip`**（**VOC 格式，非 YOLO**）；其**内部清单 NOT OBTAINED**（需 JS/confirm，且超 200 MB 未下载）。
* 划分声明**只在代码**：README 行 59/60 与 `train_yolo.py` 行 106/107 逐字 **`splits=[(2028,'trainval')]`** / **`splits=[(2028,'test')]`**
  ⇒ 只有 **trainval / test**、**无独立 val**，且代码把 test 直接当 `val_dataset`。
* README **未给划分样本数**，也**未说明** Benchmark 的 map **88.5 / 86.3 / 75.0** 出自哪个划分。
* 通用包对 `shwd` **0 命中**（Ultralytics 51 个 + yolov5 14 个 yaml 全量下载后 grep）。

**卡 14 · SFCHD**
* 官方仓 `lijfrank/SFCHD-SCALE@7bfabb4533613e6917461dc3758dcff5f304bd03`（`suppl`，2025-05-17），README sha256 `ed7bf9de…`。
  README 目录树确有 **`new_split_yolo`**，但下载指引只有一句 **"unzip and copy … Also, unzip `labels.zip` and `yolo.zip`"**（+ 百度盘 + Google Drive），
  **未说明两个 zip 的内容、未说明哪个是评估划分**。
* `labels.zip`（3,569,708 B）= **12,373 entry**，唯一目录 `labels/` → 12,372 个 `<图像名>.txt`；**无 classes.txt / 无 images / 无 yaml / 无任何切分信息**。
* `yolo.zip`（5,122,756 B）= **12,382 entry**：`yolo/{train,val}.txt`（**9,898 / 2,475**）+ `train.cache`/`val.cache` +
  `yolo/train/`（9,898 标签 + classes.txt）+ `yolo/val/`（2,475 + classes.txt）；**无 test.txt / 无 test/ / 无 data.yaml / 无 images**。
* `annotations/`：`all_data.json` 12,373 图 / 50,559 注 · `train.json` 9,898 / 40,223 · `val.json` 2,475 / 10,336 · **`test.json` = 0 字节**。
* **三套切分**：A `new_split_yolo` **9,897 / 2,475 / 6**（`test.txt` 393 B，**6 条路径、无末尾换行故 `wc -l`=5**；`test ⊆ val` = True）·
  B `yolo.zip` 9,898 / 2,475 **无 test** · C `annotations` 9,898 / 2,475 **0 B test**。
* A vs B/C：**train 交集仅 7,942**（仅 A 1,955 / 仅 B 1,956）；**val 交集仅 520**（各 1,955）。
* 四份 `.cache` 均内嵌**开发者绝对路径**，且**两份引用不同根**（`new_split_yolo` → `/home/yfs/data/QY_final_dataset/images/…`；
  `yolo.zip` → `/data/yfs/QY/QY_final_dataset/images/…`）；**四份 cache 中 `.yaml`/`.yml` 出现次数均为 0**。
* 官方 `directory.md`（1,164,092 B，24,794 行，末行 `12 directories, 24779 files`）确认：`new_split_yolo/` 还含仓库里没有的 `coco_file` 子目录；`yolo/` 只有 train/val。
* 报告的数值出自何处（**逐字可核**）：官方 `results_SFCHD/result_*.log` 写
  `ann_file='…/annotations/train.json'` 与 `'…/annotations/val.json'`（**`test.json` 从未出现**）；
  README "Testing" 表 7/7 类目 + 总数（3,482/2,920/3,032/154/239/271/238 = **10,336**）与 `val.json` 数量**精确相等**；
  Training **40,223** 与 `train.json` **精确相等**；YOLOv8 行对应 `result_YOLOv8*.csv` 末行 mAP50 **0.77911 / 0.78556** → README **77.9 / 78.6**。
* 通用包对 `sfchd` **0 命中**；唯一 helmet 类 yaml 是 `construction-ppe.yaml`（11 类 gloves/vest/boots/goggles…，
  规模 1132/143/141，下载源 Ultralytics assets）——**类别、规模、下载源均与本数据集不符**。

**卡 15 · MAFA**
* 官方站 **`https://imsg.ac.cn/research/maskedface.html`**（title `Masked Face Analysis`）**仍在线**；
  其 **TLS 证书已过期**：不加 `-k` 返回 **HTTP 000 `certificate has expired`**，加 `-k` 返回 **HTTP 200 / 27,915 B**。
  （`escience.cn` 确认已死：HTTP 000 / 25 s；DNS 返回含 RFC1918 私网 A 记录 = 域名被停放。`imsg.ac.cn/research/mafa` → 404。）
* 该页逐字给出 **5 件官方发布物**：
  `MAFA Datasets`(Google Drive) → `drive.google.com/open?id=1nbtM1n0--iZ3VVbNGhocxbnBGhMau_OG`（**实测 ALIVE**，目录名 `MAFA`，
  **仅 2 条**：`MAFA-Label-Test.zip` **181,569 B**（2017-12-01）· `MAFA-Label-Train.zip` **946,665 B**（2018-09-17）
  ⇒ **官方 Drive 只放标签、不放图像**）；
  `MAFA Train Datasets`(Baidu Pan) → 页面 title 逐字 `train-images.zip_免费高速下载`，标记 **`已失效`** + `部分文件违规，已被过滤`；
  `MAFA Test Datasets`(Baidu Pan) → title 逐字 **`百度网盘-链接不存在`**；
  `Face annotations(Training/Test)` 两条 → title 为 `MAFA-Label-Train.zip` / `MAFA-Label-Test.zip`，均 **`已失效`**。
* 官方原始 readme（从官方标签包内取出；**签名邮箱 `geshiming@iie.ac.cn` = 作者本人**）逐字：
  `"MAFA testing set / 1) images folder puts the 4935 image files; / 2) the label is stored in LabelTestAll.mat …"`；
  `"MAFA training set / 1) images folder puts the 25876 image files; / 2) the label is stored in LabelTrainAll.mat …"`；
  同包含作者脚本 `extract_face_from_MAFA.py`。
* 官方论文（CVF PDF **无文本层**，`Tj=TJ=Tf=BT=0`，1,202,862 B；经 300 dpi 渲染 + OCR）：
  p.2 **"…30,811 Internet images, in which 35,806 masked human faces … The dataset will be released soon on the Internet"**；
  **p.7 §5.1 "we split the MAFA into two subsets, including a training set and a testing set. The training set consists of
  25,876 images with 29,452 masked faces … while the testing set contains the rest 4,935 images with 6,354 masked faces.
  In this study, we only report the performances … on the testing set"**；
  Table 1 表题 **"Average Precision (%) on the Testing Set of MAFA"**；§5.2 "Comparisons with State-of-the-Art Models"。
* **论文全文无任何数据集 URL**（OCR 全文 grep `http`/`www`/`escience` 只命中第 1 页水印行）。
* 官方 **arXiv 版 NOT FOUND**（arXiv `ti:"Detecting Masked Faces"` 0 entry；S2 `externalIds` 无 ArXiv；`1703.03130` 是别的论文）。
* 三个 Kaggle 完整镜像（**非官方再分发**）实测：`rahulmangalampalli/mafa-data`（2,492,426,330 B）**30,816 条** =
  `test-images/images/test_…jpg`（**4,935**）+ `train-images/images/train_…jpg`（**25,876**）+ 两个 `Label*All.mat` + 两个 readme + 脚本。
* 三方独立复现：FMLD `MAFA_training.txt` = **25,876 行**、`MAFA_testing.txt` = **4,935 行**。
* 通用包对 `mafa` **0 命中**（ultralytics/yolov5/yolov3 + yolov7 + darknet + YOLOv6 全量 tree；`data/mafa.yaml`、`cfg/datasets/mafa.yaml` 等 5 条 raw 探针全 404；4 个落地页全文 `mafa` = 0）。
* 后续文献逐字（报告层）：AOFD（arXiv:1709.05188v6）**"Although the MAFA database dose not release its training set,
  we still obtain state-of-the-art results on the MAFA testing set"** + **"Table 1. Average precision on the MAFA testing set."**；
  FAN（arXiv:1711.07246v2）**"tested on MAFA test set"** + **"Table 6. Comparison of FAN with state-of-art detectors on the test set
  of the MAFA dataset."**（LLE-CNNs 76.4 / AOFD 77.3 / FAN 88.3）；Ryumina ISPRS 2021 **"the other two MAFA and RMFD databases were selected for testing"**。
* **数字漂移警示**：Ryumina 写 MAFA test = **4,934**（差 1）；CSDN 转述写 `train 约30,811 / test 约9,330`（错）；
  FAN **图题**把 MAFA *测试集*称作 `validation set`（表题仍为 test set）。**以官方 25,876 / 4,935 为准。**
* **别名污染警示**：`andrewmvd/face-mask-detection`（**853 图**）被 HiMFR（arXiv:2209.08930）当成 MAFA 引用（正文称 "MAFA[17] contains 6k data"）。

**卡 16 · Mendeley face-mask**
* **Mendeley Data 上不存在标题 "Face Mask Detection" 的记录**：DataCite 标题穷举 `total=29`，Mendeley 侧仅 8 条且无此标题；
  `api.data.mendeley.com/datasets?query=…` → **401** 需 OAuth；搜索页 HTTP 200 但为 **CSR 空壳**。
* 标题最接近的 Mendeley 件是 `Face Mask Dataset 2022`（`10.17632/7bt2d592b9`）：**20,347 图 / 2 类 / "Image Classification"，无划分、无规格段**。
* 853 图 / 3 类 / PASCAL-VOC 形态实为 **Kaggle `andrewmvd/face-mask-detection`（CC0）**；
  Kaggle API 逐字 **"853 images belonging to 3 classes"**，**无任何 split 声明**。其标注的原始出处 `makeml.app` 现为**域名停放页**。
* 生成器侧：`Prikshit7766/Face-Mask-Detection@ecd8be957c3a14e57d4f00cd9e62024d192479fd` 的 `convert_voc_to_yolo.py:17-18`
  （sha256 `75c5bf6055db`）把**同一个 `images_dir`** 写成两键；该仓 `data.yaml` **仅 4 行 / 110 B**
  （`train: ../train/images`、`val: ../test/images`，sha256 `d75e524c03ba`）。
  该仓 README 自认数据来自 Kaggle、**切分由用户手工完成、不发布切片清单**。
* 通用包对 `mask` / `mendeley` **0 命中**（Ultralytics 两仓全树关键词，yolov5 144 blob / ultralytics 1043 blob）。

**卡 17 · WIDER FACE**
* `wider_face_split.zip` 的中央目录**含 `wider_face_train_bbx_gt.txt` 与 `wider_face_val_bbx_gt.txt`，没有 test 的 `bbx_gt`**
  （test 侧只有 `_filelist.txt`）。官方页所链 HF 仓 `WIDER_test.zip` = **16,160 条全 `.jpg`**。
* 官方原句：**"we do not release bounding box ground truth for the test images. Users are required to submit final prediction files"**。
* 论文与官网同文：**"tested on WIDER FACE test partition"**。
* 通用包对 `wider` **0 命中**（`cfg/datasets/` 52 个 yaml · `docs/en/datasets/` · `docs/en/datasets/detect/` 三处目录穷举均无同名配置/文档）。

**卡 18 · CrowdHuman**
* 官方下载页**完整条目表只有 `annotation_train.odgt` 与 `annotation_val.odgt`**（全文 `test` 仅命中 `CrowdHuman_test.zip` 一行），
  并原句 **"We support annotation_train.odgt and annotation_val.odgt which contains the annotations of our dataset."**
* 一作本人 HF 仓 `sshao0516/CrowdHuman` 的 `CrowdHuman_test.zip` 中央目录 = **5,018 条全 `.jpg`、全在 `images_test/`、零标注**；
  `annotation_test.odgt` → **404**（对照 train01 **5,000** / val **4,370** 全 `.jpg`）。
* 论文 §4.2 原句：**"the results are evaluated in the validation subset … annotations of testing subset will not be made publicly available"**。
* 官方 **无独立评测页**（`crowdhuman.org/challenge.html`、`/evaluation.html` 均 **404**；Biendata **000** 不可达）。
* 通用包对 `crowdhuman` **0 命中**（同 WIDER FACE 的三处目录穷举）。

**卡 19 · D-Fire**
* 官方仓真身 **`gaia-solutions-on-demand/DFireDataset`**（`gaiasd/DFireDataset` 301 跳此处；
  `gaia-sensing/D-Fire` 与 `kauedg/D-Fire` **均 404**）。全树 `git/trees/master?recursive=1`（HTTP 200，**`truncated:false`**）
  **仅 6 条目**：`LICENSE` · `README.md` · `figures/` · `figures/dfire_examples.png` · `utils/` · `utils/utils.py`
  ⇒ **零 yaml、零 split 清单、零评测脚本**；`releases` 与 `tags` 均为 `[]`。
* README 逐字：**"including images, annotations, and pre-split training, validation, and test sets via the following links."**
  + 两个 `1drv.ms` 链接（实测 **301 → `onedrive.live.com:443` connect timeout → HTTP 000**，12.2–12.4 s）+ 一个 Kaggle 链接。
* 反证（独立复核）：Drones 2026（DOI `10.3390/drones10080635`）实测官方归档 **`D-Fire.zip, 3,036,222,313 bytes`**，逐字
  **"the official D-Fire distribution defines only a training list of 17,221 images and a test list of 4306; it ships no validation list"**
  与 **"Split method stated by the dataset authors: random 80/20 division into 17,221 train and 4306 test; no validation list is shipped"**。
* 作者本人文本：官方 NCAA 2022 期刊论文**闭源**（Unpaywall `is_oa:false, oa_status:"closed"`；S2 `isOpenAccess:false`）；
  同作者 **UFMG 硕士论文**（handle `1843/39452`，154 页 PDF）逐字 **"a base de dados foi dividida arbitrarily em dois conjuntos …
  80% para treinamento (17.221 imagens) e 20% para teste (4.306 imagens)"**，5-fold CV 只在 train 内做。
* 未发现任何 **D-Fire 专属数据集论文或 CVPR-W 版本**（arXiv `all:"D-Fire"` 0 entry；OpenAlex 164 条逐条筛，无）。
* HF 镜像（**非官方**）`badsaarow/d-fire` 的 `cardData.dataset_info.splits` = `train 17221 / test 4306`，**无 val**；
  `/size` 端点 `num_rows 21527 = 17221 + 4306`；label 为 YOLO 串，类 0/1 与官方 `0=smoke, 1=fire` 一致；
  文件名 `AoF00000.jpg`(train) 与 test 首行 `AoF06723.jpg` **交错**。该镜像 card **只有 `dataset_info` frontmatter、无出处散文**。
* 另四篇逐字说明划分的论文：Sci Rep 2025（`10.1038/s41598-025-86239-w`，PMC11742908）**"comprises two parts: a training set and a test set.
  The training set contains 17,221 images, while the test set includes 4306 images"**；Fire 2026（`10.3390/fire9090386`）Table 1
  `Train 14,122 / Validation 3,099 / Test 4306 / Total 21,527`；Sensors 2025（`10.3390/s25072044`，PMC11991653）**独立重切**
  **"21,527 images was split into a 70/15/15 ratio … 15,069 / 3229 / 3229"**（以 Kaggle 页为出处）。
* 通用包对 `fire`/`smoke`/`dfire` **0 命中**（Ultralytics 全仓树 **1,185 条目**；docs 索引 fire=0/smoke=0；legacy YOLOv5 14 个 yaml 无）。
* **易误引警示**：Chetoui & Akhloufi *Fire* 2024（`10.3390/fire7040135`）常被当本基准 baseline，
  但逐字是 **"11,667 RGB images … 8494, 2114, and 1059"** ⇒ **不是**本基准（21,527）。
* 边界：Drones 2026 逐字 **"Neither corpus has an independent test split. In D-Fire, 46.0% of test images have a near-duplicate in training."**

**仍未可判（诚实标出）**：Objects365 的 `release`/`protocol`（官方侧**取不到清单** ⇒ 只能记"官方未公开"）；
COCO · PASCAL VOC · DOTA v2.0 · WIDER FACE · CrowdHuman 的 `reported`（须文献扫描而非一手制品）；
CrowdHuman 的 `protocol` 缺一句与 WIDER FACE 等价的**成文禁则**；Mendeley 的 `reported`（Kaggle card 与一手陈述均未给评测比例）。

---

# 第三部分 · 输出格式

在对话里直接给出（或写成一个 `.md`）；**76 格都要有**：

```
ROW 1 | COCO
  release=gated      release_reason:   判定树 §2.1 第 3 步 | 「annotations for train and validation data will be released, but not for test」@E2
  protocol=gated     protocol_reason:  判定树 §2.2 第 3 步 | 「5 submissions per day」@E2
  yolo_dist=gated    yolo_dist_reason: 判定树 §2.3 第 3 步 | 「test: test-dev2017.txt」@E1
  reported=unknown   reported_reason:  判定树 §2.4 第 3 步 | 两条矛盾：「…reported on test-dev…」@E3:26 「…not acceptable…test-dev only」@E3:50
…（ROW 2 … ROW 19，同样四行）
```

* 取值只能是那**七个**字面量（小写；`not_recorded` 带下划线；`blocked` 全小写）。
* 锚点必须**逐字**（引号内原文），并给**行号 / 字符偏移 / 文件名**。
* 判 `not_recorded` 时，reason 里要**逐条写明**你检查了 E1/E2/E3/E4 的哪些位置、都没有。
* 判 `blocked` 时，reason 里要写明：**卡在判定树第几步** + **需要有但卡片里缺的那条证据** + 已检查的位置。

# 第四部分 · 纪律

* **不许联网**、不许打开其它文件、不许参考任何其它来源。**卡片即全部。**
* **不许**把四格"顺着写成一个"（如 `yolo_dist` 有 test 键就顺手把 `reported` 也写 `independent`）——四格各有自己的证据面。
* **不许留空。** 判不了就按第一部分 §3（→ `not_recorded`）或 §6·F5（→ `blocked`）二选一，并附检查记录。

# 第五部分 · 你的结果会被怎么用（如实告知）

* 你的 76 格会与**其他编码者的同一批 76 格**做一致性统计（Fleiss κ / 逐格一致率）；
* `blocked` 会**单列为"规则未覆盖格"、不计入一致率** —— 它是对**任务书**的反馈，不是"判错"；
* 也会与**作者此前的判定**逐格比对（**本任务书不含该判定**，以免影响你）；
* **无论与作者是否一致，都照实报告** —— 本任务的目的正是检验该判定**能否被独立复现**。
