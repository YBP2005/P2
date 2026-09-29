# G8 独立编码 · v2（19×4 盲编）— GLM-5.2

> 口径以 `03_任务v2_19x4盲编_给编码者.md` 第 2 节为准（5 值：independent / alias / absent / gated / unknown）。
> `01_空白编码表` 顶部残留的「yes/no/unknown」为 v1 旧口径，按 v2 任务书声明「规则读法以任务书第 2 节为准」不予采用。
> 本文件为盲法下独立完成，未联网、未读其它编码者材料、未打开本任务两份文件以外的任何文件。

---

## 19 行判定

```
ROW 1 | COCO | release=independent | protocol=gated | yolo_dist=alias | reported=alias | reason: 发布件结构含 train/val/test 三套目录（结构独立、不看标注是否公开）；官方 test 评测需提交 COCO 服务器、test 标注扣留 → protocol=gated；YOLO 发行包实际在 val2017 自评（test 键指向无标注 test2017 或别名到 val，见歧义 §1）；社区主打引用数为 val2017 AP、而选点亦常在 val2017 → alias。
ROW 2 | PASCAL VOC | release=independent | protocol=independent | yolo_dist=independent | reported=independent | reason: 锚定 VOC 2007（社区主打引用数来自 07 test）：07 的 train/val/test 三件齐全且 test 标注公开、可本地自评；Ultralytics VOC.yaml 以 07+12 trainval 为 train、07 test 为 test（有标注）；引用数即 07 test、与 trainval 选点独立。注：VOC 2012 的 test 标注官方扣留，若锚 2012 则 protocol=gated。
ROW 3 | Objects365 | release=gated | protocol=gated | yolo_dist=alias | reported=alias | reason: 锚定 v1/v2 val（引用数为 val AP）：发布件随附 train/val（val 有标注），test 仅在挑战赛服务器、本地无 test → release/protocol=gated；YOLO 发行包在 val 自评（test 键缺或别名，置信度低）；引用数即 val、与选点同处 → alias。
ROW 4 | Open Images v7 | release=independent | protocol=gated | yolo_dist=alias | reported=alias | reason: 发布件结构含 train/val/test（结构独立）；官方 test 评测需提交 Kaggle 服务器 → gated；YOLO 发行包在 val 自评；引用数为 val AP、与选点同处 → alias。
ROW 5 | DOTA v1.0 | release=gated | protocol=gated | yolo_dist=alias | reported=alias | reason: 发布件随附 train/val（有标注），test 在官方服务器（gated）；协议 server-gated；YOLO DOTAv1.yaml 在 val 自评；引用数多为 val mAP、与选点同处 → alias。
ROW 6 | DOTA v2.0 | release=gated | protocol=gated | yolo_dist=alias | reported=alias | reason: 与 v1.0 同构：train/val 随附、test 在服务器（gated）；YOLO 发行包在 val 自评；引用数为 val。置信度中。
ROW 7 | VisDrone-DET | release=independent | protocol=gated | yolo_dist=alias | reported=alias | reason: 发布件结构含 train/val/test（独立）；官方 test 评测需提交服务器 → gated；YOLO 发行包在 val 自评；引用数多为 val、与选点同处 → alias。
ROW 8 | AI-TOD | release=unknown | protocol=unknown | yolo_dist=absent | reported=unknown | reason: 官方 README 存在两条互相矛盾的发布声明（证据指针已明示）→ release/protocol/reported 证据不足；YOLO 通用发行包未内置 AI-TOD → yolo_dist=absent。
ROW 9 | UAVDT | release=unknown | protocol=unknown | yolo_dist=absent | reported=unknown | reason: 证据指针明示“官方论文+两镜像、除此之外未核实” → release/protocol/reported 证据不足；YOLO 通用发行包未内置 UAVDT → yolo_dist=absent。
ROW 10 | xView | release=gated | protocol=gated | yolo_dist=unknown | reported=unknown | reason: xView 发布训练集+标注，test 在挑战赛服务器（gated）；镜像 xView.yaml 的 test/val 键配置不详 → yolo_dist=unknown；引用数是 server test 还是本地 val 不可考 → reported=unknown。
ROW 11 | DIOR | release=independent | protocol=independent | yolo_dist=independent | reported=independent | reason: 锚定 DIOR-R（证据指针为 DIOR-R yaml）：DIOR 标准 train/val/test 三件、标注全公开、可本地自评；镜像 DIOR-R yaml 提供 train/val/test（独立）；引用数为 test（或 val）AP、标注公开 → 与选点独立。
ROW 12 | NWPU VHR-10 | release=absent | protocol=absent | yolo_dist=absent | reported=unknown | reason: 其“切分”为正/负样本（650 正/150 负），非 train/val/test 留出体系 → release/protocol/yolo_dist=absent；引用数来自哪一半不可考（各论文自切）→ reported=unknown。
ROW 13 | SHWD | release=independent | protocol=independent | yolo_dist=unknown | reported=unknown | reason: SHWD 官方随附 train/test（test 标注公开、可本地自评）→ release/protocol=independent；是否存在 val、镜像 Reflective_vests.yaml 的 test/val 键配置、引用数来自哪一半均不详 → yolo_dist/reported=unknown。
ROW 14 | SFCHD | release=unknown | protocol=unknown | yolo_dist=absent | reported=unknown | reason: 对 SFCHD 一手发布细节无可靠记忆（证据指针为 first-party release + 比对脚本）→ release/protocol/reported 证据不足；YOLO 通用发行包未内置 → yolo_dist=absent。
ROW 15 | MAFA | release=unknown | protocol=unknown | yolo_dist=absent | reported=unknown | reason: 证据仅为 CVPR PDF（论文），是否随附独立切分件、协议本地自评能力不详 → unknown；YOLO 通用发行包未内置 MAFA → yolo_dist=absent。
ROW 16 | Mendeley face-mask | release=unknown | protocol=unknown | yolo_dist=absent | reported=unknown | reason: 证据为 data record + 镜像生成器，是否随附标准 train/val/test 切分不详 → unknown；YOLO 通用发行包未内置（需生成器）→ yolo_dist=absent。
ROW 17 | WIDER FACE | release=independent | protocol=gated | yolo_dist=alias | reported=alias | reason: 发布件结构含 train/val/test（独立）；官方 test GT 未发布、需提交服务器（gated，证据指针逐字核实）；YOLO 发行包在 val 自评；引用数多为 val AP、与选点同处 → alias。
ROW 18 | CrowdHuman | release=independent | protocol=gated | yolo_dist=alias | reported=alias | reason: 发布件结构含 train/val/test（独立）；官方 test 评测疑需服务器（GT 扣留，置信度中）→ gated；YOLO 发行包在 val 自评；引用数多为 val、与选点同处 → alias。
ROW 19 | D-Fire (FireSmoke) | release=independent | protocol=independent | yolo_dist=independent | reported=unknown | reason: D-Fire 以 YOLO 格式分发、随附 data.yaml（train/val/test 或 train/val）、标注公开、可本地自评 → release/protocol/yolo_dist=independent；但是否存在独立 test 键、引用数来自 test 还是 val 不详 → reported=unknown。置信度中低。
```

---

## 编码者标识与盲法声明

- **编码者标识**：GLM-5.2（经 WorkBuddy 调用）
- **盲法声明**：
  - 联网：否
  - 读过其它编码者的材料：否
  - 是否打开本任务两份文件以外的文件：否

---

## 规则仍有歧义之处（按价值排序）

1. **COCO 的 `yolo_dist`**：Ultralytics `coco.yaml` 的 `test:` 键究竟指向无标注的 `test2017`（按结构看像 `gated`——有 test 但不能本地自评），还是被别名到 `val2017`（`alias`）？两种读法各给：指向 test2017 → `gated`；从业者为自评改用 val、且 `test:`=`val` 路径 → `alias`。我取 `alias`（从业者实际自评在 val）。

2. **Objects365 / DOTA 的 `release`**：本地发布件只有 train/val、无 test 文件——记 `gated`（test 在服务器、对该基准“存在但门控”）还是 `absent`（release 这一层的 test 键不存在）？我取 `gated`；若按“release 层有无 test 键”严格字面读则为 `absent`。同列推及 OpenImages/VisDrone/WIDER FACE/CrowdHuman 凡“结构有 test 目录但标注扣留”者，release 一律按结构记 `independent`（依任务书“只看结构、不看标注是否公开”），与 protocol 的 `gated` 分开——这条口径若改读“标注扣留即不算独立留出”，则这些行的 release 会下移到 `gated`。

3. **`reported` 的“非服务器数”口径**：对 COCO/Objects365/OpenImages/DOTA/VisDrone/WIDER FACE/CrowdHuman 等服务器门控基准，任务书 v2 明确 reported≠官方服务器数，故主打引用数按 val 记、选点亦在 val → `alias`。若某基准的社区主打数实为 test-dev/server（如 COCO test-dev 被广泛引用），则该行应记 `independent`（test 与选点独立）而非 `alias`——我对“主打数究竟是 val 还是 test-dev”无法逐行确证，`alias` 是按“val 更常被引”的先验给的。

4. **SHWD**：是否存在独立 val（我记忆里仅 train/test）不确。若有 val 且选点在 val、报 test → `reported=independent`；若无 val、在 test 上选点 → `reported=alias`。故 `reported=unknown`。

5. **CrowdHuman**：是否存在独立 test 切分、test GT 是否扣留我记忆不确；若 test GT 实为公开则 `protocol=independent`。故 `protocol` 标 `gated` 但置信度低。

6. **通则（影响多行 `yolo_dist`）**：对所有“Ultralytics 内置且官方 test 为服务器门控”的基准，其 `yolo_dist=alias` 是由“服务器门控数据集在 YOLO 发行包里普遍把 `test:` 键别名到 val”这一模式推断而来，**非逐一确证每个 yaml 的 `test:` 取值**。若任一 yaml 的 `test:` 实际指向真实（虽无标注）的 test 目录，则该行应为 `gated` 而非 `alias`。
