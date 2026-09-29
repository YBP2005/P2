# G8 独立编码结果（19 × 4 盲编 · 第三批）

- 编码者标识：**Hy4-preview**
- 日期：2026-09-29
- 依据：`00_任务_19x4盲编_给编码者.md` + `01_空白编码表_19x4_给编码者.md`（仅此两份）
- 盲法声明：联网：**否**；读过其它编码者的材料：**否**（除任务书与空白编码表外，未打开 `E:\workplace` 下任何文件）

---

## 1 判定（19 行）

```
ROW 1 | COCO | release=yes | protocol=no | yolo_dist=yes | reported=yes | reason: 2017 发布件含 train2017/val2017/test2017 三个不同目录（release 只看结构），但 test2017 标注扣留、须经 eval server ⇒ protocol=no；镜像 coco.yaml 有指向 test2017 的独立 `test:` 键；官方 leaderboard 报的数是 test-dev，选点在 val/minival 一侧。
ROW 2 | PASCAL VOC | release=yes | protocol=yes | yolo_dist=yes | reported=yes | reason: 按官方报告口径所用的那一版判——VOC2007：release 结构上是独立留出 test，且 test2007 标注公开发布可本地自评；镜像 VOC.yaml 的 val/test 分别指向 val2012 与 test2007，两键不同目录；论文/榜单报的是 test2007。
ROW 3 | Objects365 | release=yes | protocol=no | yolo_dist=unknown | reported=yes | reason: 官方发布含 train/val 与须提交 server 的无标注 test；Ultralytics objects365.yaml 我只回忆到 train/val 两键（无 `test:` 键即不适用 yes/no，记 unknown）；榜单数字来自无标注 test-dev，选点用已标注 val。
ROW 4 | Open Images v7 | release=yes | protocol=yes | yolo_dist=yes | reported=unknown | reason: train/validation/test 三目录且框标注公开发布可本地自评；Open-Images-v7.yaml 三键各自独立；但官方 facts page / 数据集论文本身不报告任何检测器数字，故 reported 不可考。
ROW 5 | DOTA v1.0 | release=yes | protocol=no | yolo_dist=yes | reported=yes | reason: 官方下载页给 train/val/test 三份、test 无标注须提交 DOTA 评测 server；镜像 DOTAv1.yaml 的 `test:` 键指向独立目录；官方榜单数字来自该 test。
ROW 6 | DOTA v2.0 | release=yes | protocol=no | yolo_dist=unknown | reported=yes | reason: v2.0 同样有无标注的 test-dev/test-challenge 并须 server 提交；通用 YOLO 发行包里是否有 DOTAv2 的 YAML、其键是否独立，我无法确认（候选三值都难排除）⇒ unknown；榜单数字来自 test-dev。
ROW 7 | VisDrone-DET | release=yes | protocol=no | yolo_dist=yes | reported=yes | reason: 官方给 train/val/test-dev 三份、test-dev 标注扣留须经 VisDrone server；常见 VisDrone.yaml 的 `test:` 指向独立的 test-dev 目录；VisDrone2019 挑战榜/论文报的是 test-dev。
ROW 8 | AI-TOD | release=yes | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 发布件确有独立 train/val/test 三 split（release 只看结构），但官方 README 对 test 标注是否公开自相矛盾 ⇒ protocol 不可判；无通用 YOLO 发行包中的标准 AI-TOD.yaml；论文数字来自哪一半、按哪一半选点均无据可考。
ROW 9 | UAVDT | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 据我所知官方只发布视频序列与标注、没有官方 train/val/test 切分件，也没有通用 YOLO 发行包 YAML ⇒ 前三项 unknown；既然没有官方切分，"官方论文所报数字"也无从锁定。
ROW 10 | xView | release=yes | protocol=no | yolo_dist=yes | reported=yes | reason: 官方发布 train/validation/test 三份、test 无标注须经 DIUx 评测 server；镜像 xView.yaml 三键指向不同目录；挑战榜数字来自该无标注 test。
ROW 11 | DIOR | release=yes | protocol=yes | yolo_dist=unknown | reported=unknown | reason: DIOR(-R) 的 ImageSets 含独立 test 且标注公开可本地评；镜像 DIOR-R.yaml 的键映射是否真的三键独立我记不牢 ⇒ unknown；主流做法是同一个 test 兼作选点用的 val，但官方无报数口径可考 ⇒ reported=unknown。
ROW 12 | NWPU VHR-10 | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: TorchGeo 中该集的 split 语义是 positive/negative 图像集而非 train/val/test 留出，官方没有留出切分件也没有通用 YAML；官方本身不报告检测数字。
ROW 13 | SHWD | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 官方 README 我只记得规模约 7.5k 图而不记得有官方留出切分件；通用发行包里 Reflective_vests 类 YAML 是否含独立 `test:` 键无法确认；官方亦无报告数字。
ROW 14 | SFCHD | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 我没有关于 SFCHD 一手发布件内部结构的可靠记忆，任务书所指的第一方比对脚本也读不到，四项均不可判。
ROW 15 | MAFA | release=yes | protocol=yes | yolo_dist=unknown | reported=unknown | reason: MAFA（CVPR 2017）发布件含独立 train/test 且标注公开可本地评；无通用 YOLO 发行包 YAML；数字来自其 test 半可以判定，但官方未说明按哪一半选检查点 ⇒ reported=unknown。
ROW 16 | Mendeley face-mask | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 同名 Mendeley record 有多个、我不确定任务书指的是哪一个，也不知其是否含独立留出 test、镜像生成脚本为何 ⇒ 四项均 unknown。
ROW 17 | WIDER FACE | release=yes | protocol=no | yolo_dist=unknown | reported=yes | reason: 官方明确 test 的 GT 不发布、须提交官网评测（easy/medium/hard）；镜像 wider_face.yaml 我只记得 train/val 两键（无 `test:` ⇒ unknown）；榜单数字来自扣留 test，选点用已标注 val。
ROW 18 | CrowdHuman | release=yes | protocol=no | yolo_dist=unknown | reported=yes | reason: 官方发布 train(15k)/val(4,375)/test(5,000)、test GT 扣留须提交评测；社区 CrowdHuman.yaml 是否有独立 `test:` 键我无法确认 ⇒ unknown；榜单数字来自扣留 test，选点用已标注 val。
ROW 19 | D-Fire (FireSmoke) | release=yes | protocol=yes | yolo_dist=unknown | reported=unknown | reason: README/仓库按 YOLO 格式给 train 与 test 两份且都带标签 ⇒ 结构独立、可本地评；随包 data.yaml 通常只有 train/val 两键（val 指向那个 test）⇒ yolo_dist=unknown；只有两个半分且无选点协议文档，"报告=选点同一半"（no）与"另有内部划分"（yes）两读法都成立 ⇒ reported=unknown。
```

---

## 2 编码中发现的规则歧义

1. **`reported` 缺兜底读法（影响第 8/11/15/19 行）**：写死的第 3 条只规定了"只有 train/val、没有 test"时 release/protocol/yolo_dist 记 `unknown`，**没说 reported 怎么办**。当数据集只有两个半分、官方文档又没写"按哪一半选点"时，两种读法给出不同答案：(a) 无法证实 ⇒ `unknown`（我采用了这种）；(b) 没有第三个独立半分 ⇒ 报告用的那一半必然同时被拿来选点 ⇒ `no`。建议明确采用哪一种，否则该单元的 κ 会被系统性拉低——它恰好是 headline 所依赖的单元。
2. **`yolo_dist` 的"通用 YOLO 发行包"边界未定义（影响第 3/6/7/11/17/18 行）**：若只指 `ultralytics/cfg/datasets` 下的官方 YAML，则无此文件的应记 `unknown`；若允许任意社区 converter，则几乎每一行都存在"该 converter 可能 alias、也可能没 test 键"的替身答案，`unknown` 会吞掉整个单元。同理，同族多镜像（DOTA v1.0/v2.0、VisDrone converter、DIOR-R）应以哪一版为准，规则里只有针对 VOC 的第 4 条。
3. **第 7 行 VisDrone / 第 5 行 DOTA v1.0**：我按"Ultralytics 文档的 test→test-dev 写法"判 `yolo_dist=yes`；但若实际镜像把 `test:` 别名到 val，答案就是 `no`。这一位的分歧来源纯粹是"取哪一版镜像"，不是理解差异。
4. **第 9/12/13/14/16 行的证据指针指向我读不到的一手文件**（UAVDT 两份镜像、SFCHD 的第一方比对脚本、某个具体的 Mendeley record 等）。我一律给了 `unknown`；这几行的信息量因此很低。若希望这批编码仍有判别力，建议把这几份证据的关键摘录（几行即可）直接贴进任务书第 3 节。

---

## 3 我自己的一致性做法（供后续批次对齐）

- 写死的第 1 条 ⇒ "test 存在但 GT 扣留 / 须 server" 一律 `release=yes`、`protocol=no`（适用 COCO / Objects365 / DOTA v1.0 / DOTA v2.0 / VisDrone / xView / WIDER FACE / CrowdHuman）。
- `reported` 只认官方论文或官方榜单，且要能说出"按哪一半选点"；说不出就记 `unknown` —— 因此这一单元 unknowns 最多。
- 证据指针指向我读不到的一手文件时一律 `unknown`：宁可丢信息，不猜。
