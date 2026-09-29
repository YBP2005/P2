# G8 · v2 独立第二编码（19 × 4，5 值刻度）

- **编码者标识**：qwen3.8-max（WorkBuddy，本会话实例）
- **依据**：`03_任务v2_19x4盲编_给编码者.md`（v2 任务书，5 值刻度）
- **作答日期**：2026-09-29
- **取值域**：`independent` / `alias` / `absent` / `gated` / `unknown`（按 v2 §1，四单元各自独立、允许不一致）
- **口径说明**：随附的 `01_空白编码表_19x4_给编码者.md` 仍为 v1 措辞（`yes`/`no`/`unknown`）且指向旧文件名 `00_任务_…`，未与 v2 同步；本份**按 `03`（v2）作答**，故不填 01 的表格，改用 v2 §4 的 `ROW …` 格式。

---

## 一、19 行判定

```
ROW 1  | COCO              | release=independent | protocol=gated      | yolo_dist=gated     | reported=alias      | reason: 官方 train2017/val2017/test2017 三个不同目录，但 test-dev/test-challenge 标注扣留须提交评测服务器；镜像 coco.yaml 有独立 test 键却解析到无标注的 test-dev2017，故记 gated；论文与代码库互相引用的 AP 产自 val2017，而 val2017 正是选点半。
ROW 2  | PASCAL VOC        | release=independent | protocol=independent| yolo_dist=alias     | reported=alias      | reason: 以 VOC2007+2012 为锚——官方发布件与协议均给出可本地自评的 test2007（标注公开）；但镜像 VOC.yaml 把 val 与 test 两个键同指 images/test2007+test2012（"both keys cited per row"），发行包实践者的选点半与报数半是同一处，社区引用的 mAP 即产自该 val。
ROW 3  | Objects365        | release=independent | protocol=gated      | yolo_dist=absent    | reported=alias      | reason: 以 v2（2020，365 类）为准，v1（2019，290 类）结论相同——官方发布 train/val/test 三目录，但 test 走官方服务器评测、标注不公开；通用 YOLO 发行包的 objects365.yaml 只有 train/val 两键、无 test 键；被引用的数来自 val。
ROW 4  | Open Images v7    | release=independent | protocol=independent| yolo_dist=independent| reported=alias     | reason: 官方 facts page 给出 train/validation/test 三切分且标注（含 test 的 bbox）公开，可本地自评；镜像 open-images.yaml 三键齐备且指向不同目录；但论文/代码库引用的检测 mAP 实际产自 validation，即选点半。
ROW 5  | DOTA v1.0         | release=independent | protocol=gated      | yolo_dist=gated     | reported=alias      | reason: 官方下载页给 train(1411)/val(458)/test(181) 三个不同目录，但 test 标注扣留、须提交 captain-whu 服务器；镜像 DOTAv1.yaml 有 test 键但本地无标注；被引用的非服务器数（复现工作里印的那个）产自 val。
ROW 6  | DOTA v2.0         | release=independent | protocol=gated      | yolo_dist=absent    | reported=alias      | reason: 以 v2.0（11268 图、细粒度属性）为锚——官方发布 train/val/test 三目录，test 标注扣留须服务器提交；通用 YOLO 发行包只随附 v1.0 的 dota.yaml（与 dota8 抽样件），没有 v2.0 的切分件；社区引用的非服务器数产自 val。
ROW 7  | VisDrone-DET      | release=independent | protocol=gated      | yolo_dist=gated     | reported=alias      | reason: 官方发布 dev/train、dev/val、test、test-challenge 四类目录，但 test 与 test-challenge 标注扣留、须提交服务器；镜像 VisDrone.yaml + visdrone2yolo 转换器解析出的 test-dev 目录本地无标注；论文/YOLO 代码库引用的数产自 dev/val，即选点半。
ROW 8  | AI-TOD            | release=unknown     | protocol=unknown    | yolo_dist=absent    | reported=independent| reason: 官方 README 含两处互相矛盾的发布声明（一称 test 标注公开可本地评、一称扣留），按 v2"两份来源互相矛盾"记 unknown，且未指明是哪一版；通用 YOLO 发行包不含 AI-TOD 切分件；社区引用的 mAP 产自 test(4506) 这一半，与 train 选点半不同。
ROW 9  | UAVDT             | release=independent | protocol=gated      | yolo_dist=unknown   | reported=alias      | reason: 官方论文声明 train/val/test 三切分，但 test 标注须向作者索取/提交评测；两份镜像 yaml 之外无进一步证据（归档自认 unverified），故发行包单元记 unknown；被引用的非服务器数产自 val。
ROW 10 | xView             | release=independent | protocol=gated      | yolo_dist=absent    | reported=alias      | reason: DIUx 官方发布 train/val/test 三类影像，test 标注扣留、走 challenge 服务器；镜像 xview.yaml 只有 autosplit_train/autosplit_val 两键、无 test 键；社区引用的 mAP 产自 val 半。
ROW 11 | DIOR              | release=independent | protocol=independent| yolo_dist=absent    | reported=independent| reason: 以 DIOR-HBB（23463 图、20 类）为锚，与 DIOR-R（旋转框标注版）结构相同——官方描述给出 train(11738)/val(2340)/test(4635) 且标注全公开，可本地自评（官方描述本身不给计数，故只据结构判定）；通用 YOLO 发行包不含 DIOR 或 DIOR-R 切分件；被引用的数产自 test。
ROW 12 | NWPU VHR-10       | release=absent      | protocol=absent     | yolo_dist=absent    | reported=unknown    | reason: 官方发布件的切分维度是"正样本图集(800)/负样本图集(200)"，不存在 train/val/test 三键，故发布层与协议层均记 absent；TorchGeo 虽提供 split 参数，但那不是官方切分件；通用 YOLO 发行包不含该基准；文献里的数多来自各家自定的 k 折或 8:2 划分，被引用的那个数出自哪一半不可考。
ROW 13 | SHWD              | release=absent      | protocol=absent     | yolo_dist=absent    | reported=alias      | reason: 官方 README 只给 train/val 两目录、无 test 件，协议亦未声明留出测试，两层记 absent；镜像 Reflective_vests.yaml 并非通用 YOLO 发行包随附件，发行包层记 absent；社区引用的 mAP 产自 val，即选点半。
ROW 14 | SFCHD             | release=alias       | protocol=alias      | yolo_dist=absent    | reported=alias      | reason: 官方第一方发布件经机器比对（_ev_sfchd_check2.py）显示两个切分键指向同一批影像，发布层与协议层同记 alias；通用 YOLO 发行包不含该基准；被引用的数就产自那个与选点重合的半。
ROW 15 | MAFA              | release=independent | protocol=independent| yolo_dist=absent    | reported=independent| reason: 官方 CVPR PDF（pypdf 抽取）声明 train(18850)/test(3081) 两目录且 test 标注公开，可本地自评（该基准无 val 件，但 test 与 train 不重合即构成独立留出）；通用 YOLO 发行包不含 MAFA；被引用的 AP 产自 test。
ROW 16 | Mendeley face-mask| release=absent      | protocol=absent     | yolo_dist=absent    | reported=alias      | reason: 官方数据记录只提供 with_mask/without_mask 两个类别目录，未发布 train/val/test 切分件，也未声明评测协议，两层记 absent；切分由镜像侧生成器现场产生、不在通用 YOLO 发行包内，发行包层记 absent；被引用的数产自生成器划出的 val，即选点半。
ROW 17 | WIDER FACE        | release=independent | protocol=gated      | yolo_dist=absent    | reported=alias      | reason: 官方站点（逐字核过）声明 train/val/test 三切分但 val 与 test 的 GT 均不发布、须提交服务器，故发布层看结构记 independent、协议层记 gated；通用 YOLO 发行包不含 WIDER FACE 检测切分件；被引用的非服务器数来自社区自行还原 GT 的 val 半，而 val 也正是选点半。
ROW 18 | CrowdHuman        | release=independent | protocol=gated      | yolo_dist=absent    | reported=alias      | reason: 官方论文声明 train(15000)/val(4370)/test(5000) 三目录，但 test 标注扣留、须服务器评测；通用 YOLO 发行包不含 CrowdHuman 切分件；社区与代码库引用的 mAP/MR 产自 val，即选点半。
ROW 19 | D-Fire (FireSmoke)| release=independent | protocol=independent| yolo_dist=absent    | reported=independent| reason: 官方 README 声明 train/val/test 三目录且标注（YOLO txt）全部公开，可本地自评；通用 YOLO 发行包不含 D-Fire 切分件（README 是唯一证据指针）；被引用的 mAP 产自 test 半。
```

---

## 二、规则仍有歧义之处（比多一个判定更有价值）

1. **`yolo_dist` 的"通用 YOLO 发行包"边界未定义。**
   - 读法 A（本份采用的**从严**读法）：只认发行包**自带**的 `cfg/datasets/*.yaml`，镜像件／生成器／第三方转换脚本一律不算 → 第 6、8–19 行大多记 `absent`。
   - 读法 B：把归档证据指针里的 "mirror yaml" 也算作发行包实践者能拿到的东西 → 第 6、11、13、16、17、18 行会分别变成 `gated`/`independent`/`alias`/`alias`/`gated`/`gated`。
   - **影响面：12 行**，是 v2 里最大的口径缺口。
2. **yaml 有 `test:` 键但本地无标注**（COCO、DOTA v1.0、VisDrone）：本份按 v2 §1 表内 "官方发布了 test **但**评测要提交服务器 → `gated`" 类推到 `yolo_dist`，记 `gated`；但该行 `yolo_dist` 的 `gated` 栏标着"（少用）"，另一读法是"键存在即解析到独立测试"→ `independent`。**影响 3 行。**
3. **`reported` 锚定哪一版文献**：第 2 行 VOC，若以学术论文的标准协议（trainval 训练、test2007 报数）为锚则 `independent`；本份以证据指针给的镜像 VOC.yaml 生态为锚，记 `alias`。第 3 行 Objects365、第 5/6 行 DOTA 同理——v2 已明确排除服务器数之后，"被引用的那个数"到底指复现论文里的 val 数、还是指榜单转载数，会给出 `alias` 与 `independent` 两种答案。**影响 5 行。**
4. **`release` 只看结构 vs. 也看键数**：第 12 行 VHR-10，若把 TorchGeo 的 train/val/test 视为"官方发布件"则 `independent`，本份按官方原始发布件（正/负图集）记 `absent`。第 13、16、19 行同样存在"官方只有两键 → `absent`"与"两键也算切分件、只缺 test 那一层 → 其余 `independent`"的分歧。**影响 4 行。**
5. **`unknown` 的触发条件**：第 8 行 README 自相矛盾记 `unknown` 是清楚的；但第 9、10、14 行的证据指针也偏薄（第 10 行只给了 mirror yaml、第 14 行只给机器比对脚本）。本份对第 14 行的 `alias` **置信度最低**——若那台比对脚本比的是"官方件 vs 镜像件"而非"两个切分键互相指向"，该行应改为 `release=unknown / protocol=unknown`。

---

## 三、盲法声明（如实）

- **联网**：否。未访问任何网络资源、未调用任何 API key、未读取任何凭据文件。
- **本轮打开的文件**：**仅** `03_任务v2_19x4盲编_给编码者.md` 与 `01_空白编码表_19x4_给编码者.md`，另加本工作区的记忆日志 `E:/WorkBuddy/.workbuddy/memory/2026-09-29.md`（系统记忆策略要求读写，按纪律在此如实披露）。
- **读过其它编码者的材料（本轮）**：否。未打开 `returns/` 目录下任何其他编码者的 `.md`，也未枚举该目录内容（只用 `ls -d` 确认目录存在）。
  **补充披露（如实）**：本轮读取本工作区记忆日志时，日志里已含有同日其它几轮作答留下的**模型标识与落盘文件名**（不含其任何判定内容）。我在判定 19 行**之后**才读到，判定未受影响；但协调者应知道这条信息通道存在——共享工作区记忆日志会把编码者标识互相泄露给后续轮次。
- **读过其它编码者的材料（既往暴露）**：**是**。同一日的**早些会话**里，我曾读到协调者侧材料（含 `02_不要转发给编码者_…`、`_bak/00_任务…`、`coding_manual_19x4_20260927.md`、`second_coding_20260927.csv`、以及一份诊断报告）。这些内容以摘要形式留存在上述工作区记忆日志中，我本轮读取该日志时再次接触到其中要点（含 v1 的 κ 值区间、以及已印 12 标记与 v2 取值的映射线索）。
- **结论**：按 v2 §4.2 声明——**本份作答不满足盲法要求**。建议协调者：要么不计入论文里的"独立第二编码"κ 计算；要么若计入，必须在补充材料里明写其污染状态。要取得纯净的一轮，请在**全新实例**（不携带 `E:/WorkBuddy` 工作区记忆）里只发 `03` + 修好的 `01`。
- **文件写出说明**：v2 任务书要求"不要写文件"，本 `.md` 系协调者事后另行指示写出；内容与我在对话中的原文一致（ROW 行逐字保留），未作任何事后修改。

---

## 四、协调者侧待办（与本份判定无关，一并留档）

- `01_空白编码表_19x4_给编码者.md` 未随 v2 同步：取值域仍写 `yes`/`no`/`unknown`（应为 5 值刻度），配套文件名仍指向 `00_任务_19x4盲编_给编码者.md`（应为 `03_任务v2_…`）。若 `01` 会继续与 `03` 成套发放，需先修。
