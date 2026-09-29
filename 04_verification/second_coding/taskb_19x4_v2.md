# 独立编码任务（**v2** · 多编码者）：19 个目标检测基准的「切分计数单元」判定

> **v1 的结果已如实记录在案**：8 位独立编码者按 v1 规则作答后，与已印表的一致性只有"轻微"，
> 且分歧被查明来自 **v1 三处口径没写清**（见下）。**v2 把这三处写死**，请**按 v2 重编一遍**。
> 这份文件自足：**不要打开任何其他文件、不要读别的编码者的结果、不要联网、不要用任何 API key**。
> **输出方式：在对话框里直接打出来就行，不要写文件。** 协调者会把你**在对话里的原文逐字**记下来。

---

## 0 v1 里被证实写得不清楚的三处（v2 的改动理由）

1. **`reported` 问的是"文献/社区报的那个数"，不是"官方榜单/服务器的那个数"。**
   —— v1 把它写成"官方论文或官方榜单"，于是 VOC 这类基准里，8 位里 7 位答"独立"（因为**官方**榜单的数是干净的），
   而我们要问的其实是：**论文里印出来、大家互相引用的那个数**，是在哪一半上选出来的。
   **v2 明确：`reported` = 论文/代码库/社区引用里实际出现的那个数**（不是官方服务器上的数）。
2. **多了一类：`absent`（这一层不存在／不适用）**。
   —— v1 只有 yes/no/unknown，于是"这个基准压根没有该层"被塞进 `unknown`，系统性拉低一致性。
   **v2 给 5 个取值**（见下），"没有该件"必须记 `absent`，**不是** `unknown`、更**不是** `alias`。
3. **版本锚定要落到"被引用的那个数"**。
   —— 同一族有多版（Objects365 v1/v2、VOC 2007/2012、DIOR/DIOR-R）时：
   以**你要判的那个"被报告的数"所来自的那一版**为准，并在 `reason` 里写明是哪一版；两版都可能就写清各版答案。

## 1 你在判什么

同一个基准要在 **4 个计数单元**上各判一次。**四个单元各自独立，允许不一致。**
每个单元给 **5 个取值之一**：

| 取值 | 含义 |
|---|---|
| `independent` | 该层提供了**与检查点选择独立**的留出测试 |
| `alias` | 该层把两个切分键**指到同一处**（`val == test`，或 `train == val`） |
| `absent` | 该层**不存在**：没有该键／没有 YAML／没有切分／该单元对这个基准不适用 |
| `gated` | 该层**有**留出测试，但**不能本地自评**（需提交服务器／标注扣留／明确门控） |
| `unknown` | 证据指针**不足以判定**（含"两份来源互相矛盾"） |

### 四个单元各问什么

| 单元 | 它问什么 | 典型 `independent` | 典型 `alias` | 典型 `absent` | 典型 `gated` |
|---|---|---|---|---|---|
| **`release`** | 基准**自己发布**的切分件，是否提供独立留出测试（**只看结构**，不看标注是否公开） | 官方随附 train/val/test 三个不同目录 | 官方配置把 `val` 与 `test` 指向同一目录 | 官方根本没有切分件／无 YAML | 官方发布了 test **但**评测要提交服务器 |
| **`protocol`** | **官方协议**声明的那个测试，**能不能在本地自己评** | 协议给出可本地自评的留出测试 | 协议的两个键指到同一处 | 协议**没有**声明切分 | 协议要求提交服务器／标注扣留 |
| **`yolo_dist`** | 一个把**通用 YOLO 发行包**拿起来就用的实践者，会拿到独立测试吗 | 该包配置解析到独立测试 | 该包把两个键别名 | 该包**没有** `test:` 键，或**根本没有 YAML** | （少用） |
| **`reported`** | **论文／代码库／社区引用里实际出现的那个数**，是在哪一半上产生的（**不是**官方服务器上的数） | 那个数来自与选点独立的切分 | 那个数就是在选点用的那一半上选出来的 | （少用；该单元通常不会 `absent`） | （少用） |

**两条通用纪律**：① 不确定就写 `unknown`（合法且有价值），**不要猜**；② `absent` 是"没有这一层"，
`unknown` 是"有，但证据不够"——**别混**。

### 三个示例（**虚构基准，不代表 19 行里任何一行**）

```
ROW X1 | ExampleAlpha | release=independent | protocol=gated | yolo_dist=alias | reported=alias | reason: 发布件随附三个不同目录，但官方评测要提交服务器、社区 YAML 把 val 与 test 指到同一处，社区引用的数就选自 val。
ROW X2 | ExampleBeta  | release=absent      | protocol=absent | yolo_dist=absent | reported=unknown | reason: 官方只发 train/val 两键、没有 test；协议与发行包都没有该层；论文报的数来自哪一半不可考。
ROW X3 | ExampleGamma | release=independent | protocol=independent | yolo_dist=independent | reported=independent | reason: 官方 train/val/test 三目录、标注全公开、镜像配置也解析到独立 test，引用的数来自该 test。
```

## 2 要判的 19 行

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

## 3 输出格式（**在对话里直接给**：19 行 + 可选一段歧义说明）

```
ROW <编号> | <基准名> | release=<independent|alias|absent|gated|unknown> | protocol=<…> | yolo_dist=<…> | reported=<…> | reason: <一句话；涉及版本请写明是哪一版>
```

19 行之后可另起一段写**规则仍有歧义之处**（哪一行、哪两种读法、各会给出什么答案）——比多一个判定更有价值。

## 4 纪律

1. **独立完成**：不要与其它编码者讨论、不要看别人的输出、不要推断"多数人怎么判"。
2. **只用这份文件**（或协调者贴给你的同样文本）：**不要打开任何文件**，尤其**不要读别的编码者的回答**；
   若已看到过，请在末尾**如实写明**。
3. **不要联网、不要用任何 API key、不要读任何凭据文件。**
4. 输出只有那 19 行（加可选的一段歧义说明）。

## 5 你的结果会被怎么用（如实告知）

* 与**其他独立编码者**及**已印标记**一起算逐单元与总体的 **Cohen's κ / Fleiss' κ**（5 值刻度）；
* 结果会**如实**写进论文补充材料，措辞是"**一次独立的第二编码，由 N 个语言模型在盲法下完成**"，
  并**明说**：编码者**依据归档记录的证据指针**判断、**没有重读一手文档**；**不会**被写成"独立的人工编码者"；
* 若某单元（尤其 `reported`）仍只有弱一致，我们**照实报告**，并把该处的主打数字**印成区间**。
