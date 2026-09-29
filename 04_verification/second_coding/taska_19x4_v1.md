# 独立编码任务（第三批 · 多编码者）：19 个目标检测基准的「切分计数单元」判定

> **这份文件是自足的：你不需要、也不应该打开任何其他文件或稿件。**
> 任务 = 对 **19 个基准**各做 **4 个判定**（共 **76 个判定**），按第 3 节的格式输出。
>
> **输出方式：在对话框里直接打出你的 19 行就行——不要写文件、不要建文件。**
> （协调者会在你作答之后，把你**在对话里的原文逐字**记成文件；你不需要产出任何文件。）
>
> **这是盲编。** 我们不告诉你别人（或之前的编码者）怎么判，请你**不要去猜、不要去搜、不要推断"多数人会怎么判"**。
> **不要打开 `E:\workplace` 下的任何文件**——那里有稿件、补充材料和另一批编码结果，打开就破坏盲法。
> **不要联网、不要用任何 API key、不要读任何凭据文件。** 只凭这份文件与你自己对这些公开来源的了解来判。

---

## 1 你在判什么

一个检测基准会发布 train / val / test 的切分配置。我们要判的是：
**它"被报告的那个数字"，是不是来自一个与"检查点选择"相互独立的留出切分。**

同一个基准要在 **4 个不同的计数单元**上各判一次——这 4 个单元问的是**不同层次**的问题，**允许彼此不一致**。

## 2 四个单元与判定规则（**读法已写死，请直接照用**）

每行给 `release` / `protocol` / `yolo_dist` / `reported` 四个判定，取值只能是 **`yes` / `no` / `unknown`**。

| 单元 | 它问什么 | `yes` | `no` | `unknown` |
|---|---|---|---|---|
| **`release`** | 基准**自己发布的**切分件里，被报告的那一半是否与"选择"相互独立？ | 发布件提供了**一个与 `train`、与选择侧都不同的留出测试**（**不论其标注是否公开**） | 发布配置把两个键**指向同一目录**（`val == test`；或 `train == val`） | 发布件**根本没有**切分配置／无 YAML／划分不可判 |
| **`protocol`** | **官方协议**声明的那个测试，**能不能在本地自己评**？ | 协议声明了可在本地自评的留出测试 | 协议的测试**要提交服务器**、标注扣留、或明确门控 ⇒ **不能本地自评** | 协议**未声明**切分 |
| **`yolo_dist`** | 一个把**通用 YOLO 发行包**拿起来就用的实践者，会拿到独立测试吗？ | 该包配置解析到**独立**测试 | 该包把两个键**别名**（字面 `val == test`；或 `train == val`） | 该包**没有 `test:` 键**，或**根本没有 YAML** |
| **`reported`** | **官方论文／官方榜单**报告的那个数字，来自哪一半？ | 它来自**与检查点选择独立**的切分 | 它**不独立**（选点用的就是报告用的那一半） | **无法确定** |

### ★ 四条写死的读法（前两批独立编码者都报告过这些歧义，故在此固定）

1. **`release` 与 `protocol` 的分工**：`release` **只问结构上是否独立**（两个键是否同目录）；
   **"标注是否公开、能否本地自评"只影响 `protocol`，不影响 `release`。**
   ⇒ 所以"测试件存在但标注扣留／需提交服务器"的基准：`release=yes`、`protocol=no`。
2. **`reported` 的参照系固定为"官方论文或官方榜单"**：不要用某篇第三方论文自己选的切分，
   也不要用"社区习惯引用的数"。若官方口径本身不可考，记 `unknown`。
3. **只有 `train`/`val`、没有 `test` 的发布件**：`release`、`protocol`、`yolo_dist` 一律记 **`unknown`**
   （"没有该件"**不是** `no`）；`reported` 按第 2 条单独判。
4. **同族多版本（如 VOC 2007 / 2012）**：以**官方论文／榜单所报告数字实际用的那一版**为准，
   并在 reason 里写明是哪一版；无法确定就 `unknown`。

**两条通用纪律**：① **`unknown` 是合法且有价值的答案**——不确定就写 `unknown`，**不要猜**；
② 四个单元**各自独立**判断，同一基准允许 `release=yes` 而 `protocol=no`。

## 3 要判的 19 行

每行给**基准名**与**证据指针**（应当去哪里读到它的切分配置）。**这就是你判断的全部依据**：
请按你对该公开来源的了解来判；不确定就写 `unknown`。

| # | 基准 | 证据指针 |
|---|---|---|
| 1 | COCO | Official counts + mirror yaml |
| 2 | PASCAL VOC | mirror VOC.yaml (both keys cited per row) |
| 3 | Objects365 | mirror yaml + Ultralytics docs |
| 4 | Open Images v7 | Official facts page + mirror yaml |
| 5 | DOTA v1.0 | Official download page + mirror DOTAv1.yaml |
| 6 | DOTA v2.0 | Official/mirror documentation |
| 7 | VisDrone-DET | mirror + converter |
| 8 | AI-TOD | Official README (contains two mutually contradictory release statements) |
| 9 | UAVDT | Official paper + two mirrors (the audit calls these unverified beyond these two) |
| 10 | xView | mirror xView.yaml |
| 11 | DIOR | Official description (no counting) + mirror DIOR-R yaml |
| 12 | NWPU VHR-10 | Official TorchGeo (the split means positive/negative) |
| 13 | SHWD | Official README + mirror Reflective_vests.yaml |
| 14 | SFCHD | Official first-party release (machine comparison `_ev_sfchd_check2.py`) |
| 15 | MAFA | Official CVPR PDF (extracted with pypdf) |
| 16 | Mendeley face-mask | Official data record + mirror generator |
| 17 | WIDER FACE | Official site (GT not released, verified word by word) + mirror |
| 18 | CrowdHuman | Official paper + mirror |
| 19 | D-Fire (FireSmoke) | Official README |

## 4 输出格式（**直接在对话里给出**：19 行 + 可选的一段歧义说明）

**只在回答里输出这 19 行**；**不要写文件、不要建文件、不要把你答案之外的内容贴进来。**

一行一条，共 19 行，**不要写别的**（不要写解释性前言、不要分节）：

```
ROW <编号> | <基准名> | release=<yes|no|unknown> | protocol=<yes|no|unknown> | yolo_dist=<yes|no|unknown> | reported=<yes|no|unknown> | reason: <一句话，说明依据；若涉及版本/口径请写明>
```

**格式示例**（示范格式，不代表任何真实基准的答案）：

```
ROW 20 | ExampleBench | release=yes | protocol=no | yolo_dist=unknown | reported=no | reason: The release ships a held-out test script, but the official protocol gates the test server and the community YAML has no test key, while the paper reports a value selected on its val half.
```

19 行之后，**如果你在编码时发现规则本身仍有读法不明确之处**，请另起一段写出来
（哪一行、哪两个单元、两种读法各会给出什么答案）——**这比多一个判定更有价值**。

## 5 纪律

1. **独立完成**：不要与其他编码者讨论、不要看别人的输出、不要推断"多数人会怎么判"。
2. **只用这份文件**（或协调者贴给你的同样文本）：**不要打开任何文件**，尤其**不要读别的编码者的回答／对话／结果**；
   若你确实已经看到过任何别人的编码，请在回答末尾**如实写明**（这会记进论文的盲法声明，不影响采用）。
3. **不要联网、不要用任何 API key、不要读任何凭据文件。**
4. 输出**只有那 19 行**（加可选的一段歧义说明）。

## 6 你的结果会被怎么用（如实告知）

* 我们会把你的 19 行与**其他独立编码者**（包括前两批）的结果合起来，算**逐单元与总体的一致性（Cohen's κ）**；
* 结果会**如实**写进论文补充材料，措辞是"**一次独立的第二编码，由 N 个语言模型在盲法下完成**"，
  并**明说**：编码者是**依据归档记录的证据指针**判断的、**没有重读一手文档**；
  **不会**被写成"独立的人工编码者"（这一点对你我都重要）；
* 若各家在某个单元上仍只有弱一致（例如 `reported` 单元），我们**照实报告**，并把该处的主打数字改印成**区间**；
* **你不需要产出文件**：协调者会把你**在对话里的原文逐字**抄录，md5 与原文一并留档，谁都不能事后改一个字。
