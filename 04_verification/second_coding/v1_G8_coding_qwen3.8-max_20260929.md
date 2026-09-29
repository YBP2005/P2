# G8 · 19×4 盲编返回（第三批 · 多编码者）

ROW 1 | COCO | release=yes | protocol=no | yolo_dist=no | reported=no | reason: COCO 官方 test2017 件存在且结构上独立于 train/val，但其标注不发布、协议要求在 test server 提交（且 test2014/test-dev 需申请），故 release=yes 而 protocol=no；通用 YOLO 包（Ultralytics）发行件里 val 与 test 指向同一目录（val2017），无独立 test ⇒ yolo_dist=no；官方口径（Lin et al. 2014 与 COCO 官方榜单）的 test2017 mAP 是挑战赛中用验证集/离线评估选点后提交的 ⇒ reported=no。

ROW 2 | PASCAL VOC | release=yes | protocol=unknown | yolo_dist=no | reported=no | reason: 按读法 4 取官方榜单口径的 **VOC 2012**：官方发行件含 train/val/test（test 标注扣留在评测服务器，且 2009 起门控到 2011 才开），结构上独立 ⇒ release=yes；但"官方论文/榜单实际报告数字所用的那一版"在 2007（test 公开）与 2012（test 门控）之间可换读，两种读法给出相反的 protocol，故记 unknown；Ultralytics VOC.yaml 把 train 写成 train+val 的并集列表（train ⊇ val，即同一目录被复用）、test 亦不独立 ⇒ yolo_dist=no；官方协议明文允许（且多数论文实际使用）在 trainval 上做 epoch 数/阈值选择再报 test，选点与报告共用一半 ⇒ reported=no。

ROW 3 | Objects365 | release=unknown | protocol=no | yolo_dist=unknown | reported=unknown | reason: 官方发行件为 train/val/test **且 test 标注扣留**（挑战赛需提交），若以官方件为准则 release=yes、protocol=no、reported 需看选点用哪半；但我无法确认本行证据指针里的 mirror YAML 是否把 val 与 test 指向同一目录（Ultralytics objects365.yaml 我印象中的 test 键取值不确定），而读法未规定"规则 3 的发布件"指官方件还是被引 mirror，故 release/yolo_dist 记 unknown；reported 记 unknown（官方口径是否用 val 选点不可考）。

ROW 4 | Open Images v7 | release=yes | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: OID 官方事实页发布 train/validation/test 三件，test 件在结构上独立于 train 与选择侧 ⇒ release=yes；但 test 的标注是否全量公开可本地自评是我判不准的分歧点（我倾向 test 标注为抽样发布、全量需走评测服务），两种读法给出 protocol=yes 与 protocol=no，故记 unknown；官方数据记录报告 validation 上的 mAP、挑战赛另有 test 口径，且官方是否允许在 val 上选点未声明 ⇒ reported=unknown；yolo_dist=unknown（不确定通用发行包是否带 OID 的 YAML、其 test 键如何取值）。

ROW 5 | DOTA v1.0 | release=yes | protocol=yes | yolo_dist=unknown | reported=yes | reason: DOTA v1.0 官方下载页发布 train/val/test 三件，**test 件带标注可本地自评**（DOTA 无提交服务器门控）⇒ release=yes、protocol=yes；官方论文（Xia et al. CVPR 2018）与官方榜单报告的 test-set 结果在结构上独立于 val 选点 ⇒ reported=yes；但通用 YOLO 发行包不含 DOTA 的旋转框 YAML，mirror DOTAv1.yaml 属第三方转换件、其 test 键取值我判不准 ⇒ yolo_dist=unknown（此处填 unknown 的理由见歧义段①，若按"mirror 无独立 test 键"读则应为 no；我按"包无 YAML"读记 unknown）。

ROW 6 | DOTA v2.0 | release=yes | protocol=yes | yolo_dist=unknown | reported=yes | reason: v2.0 官方文档发布 train/val/test（另含 test-dev 变体），test 标注可下载、无提交门控 ⇒ release=yes、protocol=yes；官方 v2.0 文档与榜单报告的 test-set 数字在结构上独立于 val ⇒ reported=yes；通用 YOLO 发行包不带 DOTA v2.0 旋转框 YAML，第三方 mirror 的键值我判不准 ⇒ yolo_dist=unknown。

ROW 7 | VisDrone-DET | release=yes | protocol=yes | yolo_dist=no | reported=no | reason: VisDrone-DET 官方发布 train/val/test-dev/test-challenge，test-dev 带标注可本地自评（test-challenge 需提交）⇒ release=yes、protocol=yes；官方挑战赛协议明文允许在 train/val 上做模型与超参选择再提交 test-challenge，选点与报告共用同一族 ⇒ reported=no；通用 YOLO 发行包无 VisDrone YAML，而 mirror+converter 路线通常把 val 目录同时充当 test（无独立 test 件）⇒ yolo_dist=no。

ROW 8 | AI-TOD | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 官方 README 被证据指针明示"含两条互相矛盾的发布声明"，我无从判定哪条为准，故 release/protocol/yolo_dist 一律 unknown（规则 3 精神：不可判即 unknown，不猜）；官方论文（Wang et al. ECCV 2020）报告的 test-set mAP 是否建立在 val 选点之上同样不可考 ⇒ reported=unknown。

ROW 9 | UAVDT | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 证据指针自陈"审计只用到官方论文 + 两个 mirror，且这两个 mirror 未经进一步核验"；我对 UAVDT 官方发行件是否发布独立 test 件、其标注是否可本地自评均无可靠认知，两个 mirror 的 test 键取值亦未知 ⇒ 四格全 unknown，不猜。

ROW 10 | xView | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 证据指针只给"mirror xView.yaml"而无官方件；xView 官方（Lam et al. 2018 / DIUx）以 train + **无标注** val 发布、test 需走官方评测服务，若按官方件读应为 release=yes、protocol=no、reported=no，但若按规则 3 的"发布件=被引 mirror"读，mirror 通常只有 train/val、无 test 键 ⇒ release/protocol/yolo_dist=unknown、reported=no；两种读法答案完全不同，我不确定规则指哪一件，故四格记 unknown（此格是本批最需协调者裁定的一条）。

ROW 11 | DIOR | release=yes | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: DIOR 官方描述（Li et al. 2020）发布 train/val/test 三件且无提交门控（标注随件下载）⇒ release=yes；但我无法确认官方是否声明 test 为"可本地自评的留出测试协议"（证据指针只说"官方描述，不计数"），协议未明确声明切分的读法会给出 protocol=unknown；mirror 为 DIOR-R（旋转框）而非水平框版，与官方水平框 test 是否同一件不明 ⇒ yolo_dist=unknown；官方论文报告的 test-set 数字是否用 val 选点不可考 ⇒ reported=unknown。

ROW 12 | NWPU VHR-10 | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 证据指针明示"官方 TorchGeo 的 split 含义是正样本/负样本（positive/negative），不是 train/val/test"；VHR-10 的 800 张含目标图 + 200 张背景图并不构成官方发布的"留出测试件"，社区用法各异，故 release/protocol/yolo_dist 均不可判；官方来源（Cheng et al. 2010 及 TorchGeo 数据页）未声明统一的 test 口径，报告数字来自哪一半无法确定 ⇒ reported=unknown。

ROW 13 | SHWD | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 官方 README（安全背心/安全帽数据集）与 mirror `Reflective_vests.yaml` 是否发布一个与 train、与选择侧都不同的留出 test 件，我无可靠认知；此类小数据集常见做法是只发 train/val 且 YOLO 包把 val 兼作 test，但我不确定 SHWD 属于哪种，故四格全 unknown（不猜）。

ROW 14 | SFCHD | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 证据指针为"官方第一方发行件（机器比对 `_ev_sfchd_check2.py`）"，但本编码者对 SFCHD 这一基准的第一方发行件没有任何可靠先验认知，无法判断其是否发布独立 test 件、是否可本地自评、通用 YOLO 包键值如何、官方口径报的是哪一半 ⇒ 四格全 unknown，并请协调者把本行记为"本编码者无覆盖"，不计入一致性证据。

ROW 15 | MAFA | release=yes | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: MAFA 官方 CVPR 2017 论文（Ge et al.）声明 train/test 两分且 test 标注随件可得（无提交服务器）⇒ release=yes（test 与 train、与选择侧均不同）；但论文是否把 test 明确定义为"可在本地自评的留出测试协议"、以及其 20k/3k 量级切分口径，我据 PDF 提取件判不准 ⇒ protocol=unknown；通用 YOLO 发行包不含 MAFA（遮挡人脸）YAML，mirror 键值未知 ⇒ yolo_dist=unknown；官方论文报告的 test 结果是否用同一 test 做过阈值/epoch 选择，论文未声明 ⇒ reported=unknown。

ROW 16 | Mendeley face-mask | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 官方数据记录（Mendeley Data）通常只发布图像 + 标注而**不发布 train/val/test 切分件**，切分由 mirror generator（脚本）自行生成；按读法这属于"发布件根本没有切分配置"⇒ release/protocol/yolo_dist=unknown；该数据记录为数据发布而非评测协议，不存在"官方论文/官方榜单报告的那个数字"，参照系缺失 ⇒ reported=unknown。

ROW 17 | WIDER FACE | release=yes | protocol=no | yolo_dist=unknown | reported=no | reason: 官方站点发布 train/val/test 三件且 **test 的 GT 不发布**（证据指针注明"逐字核验"），结构上 test 独立于 train 与选择侧 ⇒ release=yes；GT 扣留 ⇒ 不能本地自评、须走官方评测服务 ⇒ protocol=no；官方协议（Yang et al. CVPR 2016）明文规定在 val 上做模型选择、在 test 上报告，选点与报告共用 val 这一族、且官方榜单数字来自提交 test ⇒ reported=no；通用 YOLO 发行包是否带 WIDER FACE YAML 及其 test 键取值我判不准 ⇒ yolo_dist=unknown。

ROW 18 | CrowdHuman | release=yes | protocol=no | yolo_dist=unknown | reported=unknown | reason: 官方（Shao et al. 2018）发布 train/val/test，**test 标注扣留**、须在官方评测服务提交 ⇒ release=yes、protocol=no；通用 YOLO 发行包不含 CrowdHuman YAML，mirror 键值未知 ⇒ yolo_dist=unknown；官方论文报告的 test 数字是否建立在 val 选点之上，论文未明确声明（与 COCO/WIDER FACE 那种"明文允许 val 选点"不同），故 reported=unknown。

ROW 19 | D-Fire (FireSmoke) | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 官方 README（D-Fire / fire-smoke 检测集）是否发布一个与 train、与选择侧都不同的留出 test 件，我无可靠认知；此类 GitHub 小数据集常见只发 train/val（YOLO 包把 val 兼作 test）或发 train/val/test 三种做法都出现过，我不确定 D-Fire 属于哪一种，且该基准无"官方论文/官方榜单"口径可参照 ⇒ 四格全 unknown（不猜）。

---

**编码者标识**：Qwen（qwen3.8-max）。

**盲法声明**：联网：**否**；读过其它编码者的材料：**否**（未打开 `E:\workplace` 下除协调者给的两份任务件以外的任何文件，未读任何稿件/补充材料/其他编码结果）。

**但有一项需如实申报的潜在污染**：作答前我按本机惯例读了当前工作区（`E:\WorkBuddy`）的当日工作日志，其中含我本人此前 P2/P3 盲审笔记的若干**汇总性**表述（"19 行审计是单一评分员、κ 0.272–0.437、`reported` 单元最弱约 0.10"、"6 of 14 混了别名与 SHWD 的真实污染"、"headline 率 23.3% / 12 of 19–13 of 19"）。这些是汇总数与措辞，**不含逐行取值**；我在编码时未去反推任何一格以使结果落在这些汇总数上，但无法保证零影响，故如实写明，请记进盲法声明。

**规则读法歧义（8 条，按价值排序）**：

1. **第 5/6/7/13/19 行 · `yolo_dist`**：当 `test:` 键**存在但指向一个无标注（或空）目录**时，该记 `yes`（键在结构上解析到另一个路径，字面不是 `val == test`）还是 `no`（实践者拿不到可用的独立测试，实质等同别名）？规则表只写了"字面 `val == test`"为 `no`、"没有 `test:` 键"为 `unknown`，把"键在但无标注"这一常见情形留空。我在 DOTA 两行按"包无 YAML"读记了 `unknown`，但若协调者的 mirror 件确实写了 `test:` 键指向 images/ 而无标注，按字面读应为 `yes`，按实质读应为 `no`——三格答案互不相同。
2. **第 2 行 · `release` 与 `yolo_dist` 的 `train ⊇ val`**：Ultralytics VOC.yaml 把 `train` 写成 `images/train2012` 与 `images/val2012` 的并集列表，同时 `test` 也指 `val2012`。这算规则里的 `train == val` 吗？按"同一目录被复用"读算（⇒ `release=no`），按"键值字面不相等"读不算（⇒ `release=yes`、只 `yolo_dist=no`）。我取了后者，但两种读法会给出相反的 `release`，而 VOC 是本批少数几行之一，影响很大。
3. **第 18 行（也影响 1/4）· `reported` 的口径分叉**：当官方**论文**与官方**榜单**报的不是同一半（CrowdHuman 论文报 test、榜单另有一套；COCO 论文报 test2017、榜单同时挂 val 与 test-dev），读法 2 只说"参照系固定为官方论文或官方榜单"，没说两者冲突时取谁。取论文 ⇒ `reported=no/unknown`；取榜单 ⇒ 可能变 `yes`。建议在规则里加一句优先级。
4. **第 2 行 · 读法 4 与 `protocol` 的耦合**：读法 4 让"以官方论文/榜单实际用的那一版为准"，但没说 `protocol` 是否也跟随换版。VOC 2007 的 test 公开可本地自评（`protocol=yes`），VOC 2012 的 test 在评测服务器且门控（`protocol=no`）——同一个"VOC"行会因是否换版而翻转。我记了 `unknown` 并把两读法写进 reason，但这其实是规则空缺而非我的无知。
5. **第 10 行（也影响 3）· 规则 3 的"发布件"指哪一件**：规则 3 说"只有 train/val、没有 test 的发布件 ⇒ 三格记 unknown"，但没说"发布件"是**官方第一方发行件**还是**证据指针所引的 mirror YAML**。xView 官方有 test（需提交服务器）而 mirror 常只有 train/val：按官方件读 `release=yes`/`protocol=no`/`reported=no`，按 mirror 读三格全 `unknown`。这一条是本批最大的单格分歧源。
6. **全批 · `yolo_dist` 的 `unknown` overloaded**：`unknown` 同时覆盖"该包确实没有 `test:` 键/没有 YAML"（客观事实）与"我无法确定该包有没有这个键"（编码者无知）。前者应记 `no`/`unknown` 已定，后者才是真 `unknown`。把两者塞进同一格会让 κ 虚高或虚低——建议在规则里区分"事实无键"与"不可判"，或要求 reason 里标注是哪一种（我已在每行 reason 里写明，但机器抽取时会被抹平）。
7. **第 4 行 · OID 的 `protocol` 取决于一个事实**：Open Images v7 的 **test 全量标注是否可下载**（我倾向"抽样发布、全量走评测服务"但不确定）。若可下载 ⇒ `protocol=yes`，若扣留 ⇒ `protocol=no`。这一格不是读法问题而是事实问题，按纪律不能联网核实，故只能 `unknown`；协调者若有归档证据，这格可由证据直接定，不必进一致性统计。
8. **第 7 行（也影响 9/18）· `reported` 的"独立"是否包含内容级泄漏**：规则把"独立"定义为切分层面的独立（不是同一半）。但 VisDrone/UAVDT/CrowdHuman 这类**同源视频抽帧后随机切分**的基准，train 与 test 帧来自同一段视频，存在内容级泄漏。这算不算 `reported=no`？按字面（"选点用的就是报告用的那一半"）不算，按实质（"与检查点选择不独立"）算。我按字面处理（VisDrone 记 `no` 是因为挑战赛明文允许 val 选点，不是因为泄漏），但规则应明说是否把内容级泄漏纳入 `reported` 单元。

**一行无覆盖申报**：第 14 行 SFCHD 我四格全 `unknown` 且**无任何实质判断依据**（对该基准第一方发行件零认知）。请协调者把该行记为"本编码者无覆盖"，在算逐单元一致性时按缺失处理，或至少在补充材料里注明该行不是"判断为 unknown"而是"无从判断"。
