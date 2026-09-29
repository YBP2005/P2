# G8 独立第二编码 · v2（19 基准 × 4 单元 · 5 值刻度）

- **编码者标识**：Kimi（月之暗面 Kimi-K3 系模型）
- **日期**：2026-09-29
- **依据文件**：`03_任务v2_19x4盲编_给编码者.md`（规则以任务书 §2 为准，5 值刻度；空白表 `01` 中遗留的 v1 `yes/no/unknown` 措辞未采用）
- **作答方式**：本轮会话内仅打开协调者发来的两份给编码者的文件（任务书 v2 + 空白表），未打开任何其他文件、未联网、未使用任何 API key。既往暴露见文末盲法声明。

---

## 一、19 行编码结果

```
ROW 1  | COCO | release=independent | protocol=gated | yolo_dist=gated | reported=independent | reason: 发布件含 train/val/test-dev 三个不同切分；test-dev 标注扣留须提交服务器；镜像 coco.yaml 的 test 键指向 test-dev2017（有独立切分但本地不可评）；社区互相引用的主打数是 test-dev mAP，选点在 val，与该切分独立。
ROW 2  | PASCAL VOC | release=independent | protocol=independent(2007)/gated(2012) | yolo_dist=independent | reported=independent | reason: devkit 自带 train/val/test 不同目录；VOC2007 test 标注公开可本地自评，VOC2012 test 标注扣留须交服务器，按 v2 两版分列；镜像 VOC.yaml 的 test 键指向 test2007；社区（YOLO 系）常引数为 VOC2007 test mAP@.5，与选点用的 val 不同半。
ROW 3  | Objects365 | release=independent | protocol=gated | yolo_dist=absent | reported=alias | reason: 官方有 train/val/test 结构，test 须交评测服务器（门控）；Ultralytics Objects365.yaml 只有 train/val、无 test 键；社区引用的数多为 val 自评数，与选点同半（锚定 v1，v2 口径同类）。
ROW 4  | Open Images v7 | release=independent | protocol=independent | yolo_dist=absent | reported=alias | reason: 官方 train/validation/test 三个切分且 test 标注与评测代码公开、可本地自评；Ultralytics open-images-v7.yaml 仅 train/val、无 test 键；社区引用数多为 validation 自评数，与选点同半。
ROW 5  | DOTA v1.0 | release=independent | protocol=gated | yolo_dist=gated | reported=independent | reason: 官方 train/val/test 结构齐全，test 标注扣留、须交官方服务器；镜像 DOTAv1.yaml 的 test 键指向 images/test 但无标注、本地不可评；论文引用的主打数为官方 test 服务器 mAP，选点在 val。
ROW 6  | DOTA v2.0 | release=independent | protocol=gated | yolo_dist=absent | reported=independent | reason: 结构同 v1.0（train/val/test，test 标注扣留须服务器）；通用 YOLO 发行包无 DOTAv2 yaml；引用数为官方 test 服务器 mAP，与选点半独立。
ROW 7  | VisDrone-DET | release=independent | protocol=independent | yolo_dist=independent | reported=independent | reason: 官方发布 train/val/test-dev/test-challenge；test-dev 标注可经转换器本地评测（test-challenge 另属服务器门控，此处锚定社区主用的 test-dev）；镜像 VisDrone.yaml 的 test 键指向 test-dev 且标注可转换；社区引用数为 test-dev mAP，选点在 val。
ROW 8  | AI-TOD | release=unknown | protocol=unknown | yolo_dist=absent | reported=unknown | reason: 官方 README 内两处发布声明互相矛盾（test 标注是否随附/切分口径不一），按"来源矛盾记 unknown"处理；通用发行包无该 yaml；论文所报数来自哪一半由此不可核验。
ROW 9  | UAVDT | release=independent | protocol=independent | yolo_dist=absent | reported=independent | reason: 官方论文/发布件含 train 与 test 两个切分且 test GT 公开，社区本地自评；通用发行包无该 yaml（仅存两个社区镜像，审计注明此外未验证）；论文引用数为 test 自评数，与选点不同半。
ROW 10 | xView | release=independent | protocol=gated | yolo_dist=absent | reported=alias | reason: 官方 train+val+test 结构，test 扣留须挑战赛服务器；镜像 xView.yaml 用 autosplit 只有 train/val、无 test 键；社区经镜像跑出的引用数多在 autosplit val（即选点半）上——官方榜单 test 数另属门控。
ROW 11 | DIOR | release=independent | protocol=independent | yolo_dist=absent | reported=independent | reason: 锚定 DIOR 原版：官方 trainval/test 两个切分、test GT 公开可本地自评；通用发行包无 yaml（指针中的 DIOR-R 为社区旋转框变体，其键映射不可考，若锚定 DIOR-R 其 test 亦公开、结论不变）；论文引用数为 test mAP，与选点半不同。
ROW 12 | NWPU VHR-10 | release=absent | protocol=absent | yolo_dist=absent | reported=unknown | reason: 官方无 train/val/test 切分件，TorchGeo 的 split 字段指"正/负样本"而非训练-测试切分；协议层随之不存在；无发行包 yaml；各家自划分，引用数来自哪一半不可考。
ROW 13 | SHWD | release=absent | protocol=absent | yolo_dist=absent | reported=alias | reason: 官方 README 只发布数据、不随附固定切分件（社区自行划分）；协议层不存在；Reflective_vests.yaml 属社区镜像而非通用发行包自带，故该层记 absent；社区引用数报在自划分 val 上，与选点同半。
ROW 14 | SFCHD | release=unknown | protocol=unknown | yolo_dist=absent | reported=unknown | reason: 指针仅指向一方发布件与机比对脚本，盲编条件下证据不足以判定切分结构与协议，不猜；无通用发行包 yaml；引用数来源不可考。
ROW 15 | MAFA | release=independent | protocol=independent | yolo_dist=absent | reported=independent | reason: CVPR 论文/官方发布含 train（25,876）/test（4,935）两个切分，test GT 公开可本地自评；无发行包 yaml；论文引用数为 test AP，与选点半不同。
ROW 16 | Mendeley face-mask | release=absent | protocol=absent | yolo_dist=absent | reported=alias | reason: 官方数据记录按单目录发布、无切分件，切分由镜像生成器脚本现造；协议层不存在；通用发行包无 yaml；社区引用数报在自生成 val 上，与选点同半。
ROW 17 | WIDER FACE | release=independent | protocol=gated | yolo_dist=absent | reported=alias | reason: 官方有 train/val/test 结构，但 test GT 扣留（官网逐字核实）且无公开本地评测通道；发行包无 test 键；论文/社区引用的数是 val 上的 Easy/Medium/Hard AP，选点也在 val，同半。
ROW 18 | CrowdHuman | release=independent | protocol=independent | yolo_dist=absent | reported=alias | reason: 官方 train/val/test 三个切分且标注全公开、可本地自评；通用发行包无 yaml；论文引用数惯例报在 val（AP/MR），选点也在 val，同半。
ROW 19 | D-Fire (FireSmoke) | release=independent | protocol=independent | yolo_dist=absent | reported=independent | reason: 官方 README 随附 train/val/test 切分，标注公开可本地自评；通用发行包无 yaml；引用数为 test 上的数，与选点半（val）不同。
```

## 二、规则仍有歧义之处

1. **`yolo_dist` 的"拿到独立测试"有两种读法**：（a）只看配置键能否解析到独立切分（结构）→ COCO/DOTA 应记 `independent`；（b）要求本地可自评 → 记 `gated`（本编码者采用 b）。此歧义直接影响第 1、5 行。
2. **`yolo_dist` 是否纳入"社区镜像 yaml"**：若纳入，第 13/16/17/18 行可能从 `absent` 变为按镜像键判定；本编码者从严按"通用 YOLO 发行包（Ultralytics 自带 yaml）"解释，凡非内置一律 `absent`。
3. **`reported` 对"双口径流通"基准需先选锚**：COCO 的 test-dev 数与 val 自评数、xView 的榜单数与 autosplit val 数都在流通；本编码者锚定"社区互相引用的主打数"。若改锚另一口径，第 1 行会变 `alias`、第 10 行会变 `independent`。
4. **`release` 的"切分件"认定**：NWPU 的正/负样本字段、SHWD README 的口头划分口径是否算"切分件"——本编码者从严记 `absent`；若从宽（README 声明了划分口径即算），第 13 行 release 可读为 `independent`。
5. **`protocol` 对"官方声明的 test"与"社区实际协议"分离的基准**（VisDrone 的 test-dev 惯例、WIDER 的 val 惯例）：本编码者按"官方声明的 test"判；若按社区实际协议判，第 17 行 protocol 可读为 `independent`（以 val 为实际评测协议）。

## 三、标识与盲法声明（如实）

- **标识**：Kimi（月之暗面 Kimi-K3 系模型，作为独立盲编码者之一）。
- **联网**：否。
- **读过其它编码者的材料**：**是，须如实申报**——在**同日早些的另一个会话**中，本编码者曾被提供并阅读过协调者侧材料（`02_不要转发给编码者_...`、编码手册、第二编码 CSV 及结果诊断笔记），该暴露无法从记忆中消除，故本次作答**不能视为纯净盲编**。
- **本轮会话内**：仅打开协调者发来的两份给编码者的文件（任务书 v2 + 空白表），未再打开任何其他文件（含 returns 目录下其他编码者的 md，未曾读取）、未联网、未使用任何 API key；以上 19 行是依据任务书证据指针与模型既有知识作出的判断。
- 请协调者在汇总时对这本编码者的既往暴露如实标注。

## 四、流程建议（不影响编码，供协调者参考）

- 空白表 `01` 仍是 v1 措辞（`yes/no/unknown`，且引用旧文件名 `00_任务_...`），与 v2 任务书一起发出会造成口径混乱，建议发出前先同步。
- 为确保盲法，给每位编码者的文件最好在全新会话中发送。
