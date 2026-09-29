# G8 编码结果 · 模型标识 `hy4-preview` · v2（19 × 4）

> 依据：`03_任务v2_19x4盲编_给编码者.md`（v2 五值口径）。
> 注：`01_空白编码表_19x4_给编码者.md` 仍为 v1 三值口径（`yes`/`no`/`unknown`）并指向旧任务书；本次按 **v2 五值**作答。
> 盲法声明：**联网：否**；**读过其它编码者的材料：否**；除协调者给的两份文件外，**未打开任何其它文件**；未使用任何 API key 或凭据文件。

---

## 1 编码结果（19 行）

```
ROW 1  | COCO               | release=independent | protocol=gated       | yolo_dist=independent | reported=independent | reason: 官方发布 train2017/val2017/test2017 三个不同目录；官方 test-dev/test-challenge 需提交服务器；镜像 coco.yaml 解析到独立 test2017；SOTA 表里被互相引用的 COCO 数是提交服务器所得的 test-dev 数，选点与消融在 val2017。
ROW 2  | PASCAL VOC         | release=independent | protocol=independent | yolo_dist=alias       | reported=alias       | reason: 锚定 VOC2007——官方三个不同子集、2007 test 标注已公开可本地自评（2012 才是 test 走服务器）；镜像 VOC.yaml 的 val/test 都落在 VOC2007 test、且 train 里的 07/12 trainval 含 val 图；社区引用的 VOC mAP 就产自 VOC2007 test，而该集标注公开、调参选点也在其上。
ROW 3  | Objects365         | release=independent | protocol=gated       | yolo_dist=absent      | reported=alias       | reason: 官方 train/val/test 三切分（v1 与 v2 同结构），test 标注扣留须提交；镜像 Objects365.yaml 只有 train/val 两个键；mmdet/YOLO 系列报的 AP 就是 val 上的数，选点也在 val（文献多不标 v1/v2，两版答案相同）。
ROW 4  | Open Images v7     | release=independent | protocol=gated       | yolo_dist=independent | reported=independent | reason: 官方 train/validation/test 三切分齐全，test 标注扣留、须经挑战赛/服务器提交；镜像 open-images-v7.yaml 解析到独立 test 目录（无标注）；公开引用的 mAP 主要来自提交所得的 test 数，选点在 validation。
ROW 5  | DOTA v1.0          | release=independent | protocol=gated       | yolo_dist=independent | reported=independent | reason: 官方 train/val/test 三套不同切分，test 标注扣留须提交 DOTA 评测服务器；镜像 DOTAv1.yaml 三键解析到不同目录；旋转检测论文主打的数是提交服务器得到的 test mAP，选点在 val。
ROW 6  | DOTA v2.0          | release=independent | protocol=gated       | yolo_dist=unknown     | reported=independent | reason: v2.0 官方给出 train/val/test-dev/test-challenge，两类 test 标注均扣留须提交；是否有镜像 yaml 未核实；报的数来自提交评测，与选点的 val 不同。
ROW 7  | VisDrone-DET       | release=independent | protocol=gated       | yolo_dist=independent | reported=independent | reason: 官方 train/val/test-dev/test-challenge 四个切分，test 类标注扣留须提交；镜像 VisDrone.yaml 解析到 test-dev；挑战赛/论文报的是提交服务器所得的 test-dev 数，选点在 val。
ROW 8  | AI-TOD             | release=unknown     | protocol=unknown     | yolo_dist=unknown     | reported=unknown     | reason: 官方 README 关于是否发布 test 及 test 标注是否公开的两处表述互相矛盾，四层均不可可靠判定；是否有镜像 yaml 亦未核实。
ROW 9  | UAVDT              | release=independent | protocol=independent | yolo_dist=unknown     | reported=unknown     | reason: 官方论文给出 train/val/test 切分、标注随数据集公开可本地自评；两个镜像是否含独立 test 键未核实；社区报的数来自哪一半不可考。
ROW 10 | xView              | release=independent | protocol=gated       | yolo_dist=unknown     | reported=alias       | reason: 官方 train/val 带标注、test 无标注须提交挑战赛服务器；镜像 xView.yaml 是否含独立 test 键不可考；挑战赛已结束，社区报的 mAP 多在 val 上，而 val 也正是选点用的那半。
ROW 11 | DIOR               | release=independent | protocol=independent | yolo_dist=independent | reported=independent | reason: 官方给 train/val/test 三个不同子集、标注全公开可本地自评；镜像 DIOR-R yaml 解析到独立 test；论文报的数在官方 test 上、选点在 val（证据混入 DIOR-R 版，锚定 DIOR 或 DIOR-R 结论相同）。
ROW 12 | NWPU VHR-10        | release=absent      | protocol=absent      | yolo_dist=absent      | reported=alias       | reason: TorchGeo 里的 split 指"正样本/负样本"而非 train/val/test，官方没有发布切分件、也没有评测协议；社区报的数来自研究者自造的随机切分，因不存在独立 val，选点与报数都在同一半上。
ROW 13 | SHWD               | release=independent | protocol=independent | yolo_dist=unknown     | reported=alias       | reason: 官方只发布 train/test 两个不同切分、标注公开可本地自评；镜像 Reflective_vests.yaml 与 SHWD 的对应关系及是否含独立 test 键不可考；无独立 val，社区报的 mAP 在 test 上、选点也在其上。
ROW 14 | SFCHD              | release=unknown     | protocol=unknown     | yolo_dist=unknown     | reported=unknown     | reason: 我不掌握 SFCHD 一手发布的内容（证据指针只有"机器比对脚本"），四层均不可判。
ROW 15 | MAFA               | release=independent | protocol=independent | yolo_dist=absent      | reported=alias       | reason: CVPR 论文所示发布件给 train/test 两个不同切分、标注公开可本地自评；没有通用 YOLO 镜像 yaml；无独立 val，报的 AP 在 test 上、选点也在其上（若属跨数据集评测则另当别论）。
ROW 16 | Mendeley face-mask | release=absent      | protocol=absent      | yolo_dist=absent      | reported=alias       | reason: 数据记录本身只给图与标注、无官方切分件也无评测协议；镜像生成器产出的 yaml 通常只有 train/val 两键；社区报的 mAP 就在那一份自造的 val(=test) 上，选点亦然。
ROW 17 | WIDER FACE         | release=independent | protocol=gated       | yolo_dist=absent      | reported=independent | reason: 官方 train/val/test 三切分，test 标注扣留、必须提交官方服务器（站点已逐字核实）；镜像 WiderFace.yaml 通常只有 train/val；论文报的 Easy/Medium/Hard 是提交服务器所得的 test 数，调参选点在 val。
ROW 18 | CrowdHuman         | release=independent | protocol=gated       | yolo_dist=unknown     | reported=alias       | reason: 官方 train/val/test 三切分、test 标注扣留须提交；镜像 yaml 是否含独立 test 键不可考；CrowdDet 一系论文报的 AP/mMR 都在 val 上，选点也在 val。
ROW 19 | D-Fire (FireSmoke) | release=independent | protocol=independent | yolo_dist=unknown     | reported=alias       | reason: 官方 README 只给 train/test 两个切分、标注公开可本地自评；镜像 yaml 情况未核实；无独立 val，报的 mAP 在 test 上、选点也在其上。
```

## 2 汇总表（便于机器抽取）

| # | 基准 | release | protocol | yolo_dist | reported |
|---|---|---|---|---|---|
| 1 | COCO | independent | gated | independent | independent |
| 2 | PASCAL VOC | independent | independent | alias | alias |
| 3 | Objects365 | independent | gated | absent | alias |
| 4 | Open Images v7 | independent | gated | independent | independent |
| 5 | DOTA v1.0 | independent | gated | independent | independent |
| 6 | DOTA v2.0 | independent | gated | unknown | independent |
| 7 | VisDrone-DET | independent | gated | independent | independent |
| 8 | AI-TOD | unknown | unknown | unknown | unknown |
| 9 | UAVDT | independent | independent | unknown | unknown |
| 10 | xView | independent | gated | unknown | alias |
| 11 | DIOR | independent | independent | independent | independent |
| 12 | NWPU VHR-10 | absent | absent | absent | alias |
| 13 | SHWD | independent | independent | unknown | alias |
| 14 | SFCHD | unknown | unknown | unknown | unknown |
| 15 | MAFA | independent | independent | absent | alias |
| 16 | Mendeley face-mask | absent | absent | absent | alias |
| 17 | WIDER FACE | independent | gated | absent | independent |
| 18 | CrowdHuman | independent | gated | unknown | alias |
| 19 | D-Fire (FireSmoke) | independent | independent | unknown | alias |

## 3 规则仍有歧义之处（按价值排序）

1. **"两键"数据集的 `release` 读数分裂**（SHWD / MAFA / D-Fire）：官方只发 train/test、没有 val。
   按"`release` 只看结构"→ 确有留出 test = `independent`；按"是否与检查点选择独立"→ 无 val 意味着选点必然落在 test 上 = `alias`。
   本次统一取前者，并把这些行的 `reported` 判为 `alias`；若协调者取后一种读法，13/15/19 行的 `release` 应改判为 `alias`。
2. **`reported` 的"被引用数"取自哪一类文本**：学术 SOTA 表（提交服务器所得 → `independent`）还是代码库/发行包文档（在 val 上自评 → `alias`）。
   COCO（test-dev vs val2017）、Open Images、DOTA v1.0/v2.0、VisDrone 都可能整体翻面；本次取前者，理由是"互相引用的数"通常指 SOTA 表里那个。
   **这一条是 v2 最可能仍只有弱一致的单元。**
3. **`yolo_dist` 的 `independent` vs `absent/gated`**：当镜像有独立 `test:` 键但该 test 无标注时（COCO、Open Images、DOTA），
   按"配置解析到独立测试"→ `independent`；按"实践者能否真的自评"→ 应为 `gated` 或 `absent`。本次取前者。
4. **同族多版的锚定**：VOC 2007 vs 2012（2012 的 `protocol` 应为 `gated`，本次锚定被引用数所在的 2007）；
   Objects365 v1/v2 与 DIOR/DIOR-R 两版答案相同，但文献常不标版本，不同编码者可能各自锚定不同版。
5. **镜像 yaml 是否真含 `test:` 键**：Objects365 / xView / CrowdHuman 分别判 `absent` / `unknown` / `unknown`；
   若实际含键，应改判 `independent` 或 `alias`。

## 4 提交信息

* **编码者标识**：`hy4-preview`（WorkBuddy）
* **盲法**：联网 `否`；读过其它编码者的材料 `否`；只读协调者给出的 `03_任务v2_19x4盲编_给编码者.md` 与 `01_空白编码表_19x4_给编码者.md`，未打开任何其它文件
* **日期**：2026-09-29
