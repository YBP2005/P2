# G8 盲编结果（第三批 · 多编码者）：19 × 4「切分计数单元」判定

- 编码者标识：Kimi（Moonshot AI，kimi-k3-1 会话模型）
- 日期：2026-09-29
- 盲法声明：联网：否；读过其它编码者的材料：否（本编码仅依据任务书/空白表文本与编码者自身对这些公开来源的了解；未打开 E:\workplace 下任何稿件、补充材料或其他编码结果）

```
ROW 1 | COCO | release=yes | protocol=no | yolo_dist=yes | reported=yes | reason: 发布含独立 test-dev2017（标注扣留、须评测服务器）；Ultralytics coco.yaml 有 test: test-dev2017.txt；官方榜单数字来自 test-dev 服务器，与 val 选点独立。
ROW 2 | PASCAL VOC | release=yes | protocol=yes | yolo_dist=unknown | reported=yes | reason: 按最常引用的 VOC2007 口径：test 标注公开、可本地自评；Ultralytics VOC.yaml 只有 train/val、无 test 键；官方结果被报告在 2007 test 上，与 trainval 侧独立。
ROW 3 | Objects365 | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: mirror yaml（Ultralytics Objects365.yaml）只有 train/val、无 test 键，按写死读法第 3 条前三项记 unknown；官方论文数字实际用哪一半不可考。
ROW 4 | Open Images v7 | release=yes | protocol=yes | yolo_dist=unknown | reported=unknown | reason: 官方发布独立 test 且框标注公开、可本地自评；OpenImagesV7.yaml 是否含 test 键不能确定；v7 无可考的单一官方榜单数字。
ROW 5 | DOTA v1.0 | release=yes | protocol=no | yolo_dist=unknown | reported=yes | reason: 发布含独立 test 影像但标注扣留、须评测服务器；DOTAv1.yaml 是否含 test 键不能确定；官方论文/榜单数字来自服务器 test。
ROW 6 | DOTA v2.0 | release=yes | protocol=no | yolo_dist=unknown | reported=yes | reason: 与 v1.0 同构（train/val/test，test 标注扣留走评测服务器）；通用 YOLO 发行包无 DOTA v2.0 的 YAML。
ROW 7 | VisDrone-DET | release=yes | protocol=no | yolo_dist=yes | reported=yes | reason: 发布含 test-challenge（标注扣留、Codalab 服务器）与公开的 test-dev；Ultralytics VisDrone.yaml 的 test 键指向独立的 test-dev；官方挑战赛数字来自扣留的 test-challenge。
ROW 8 | AI-TOD | release=unknown | protocol=unknown | yolo_dist=unknown | reported=yes | reason: 官方 README 含两处互相矛盾的发布声明、划分不可判，且通用 YOLO 发行包无其 YAML；ICPR'21 原论文基线数字报在其声明的 test 切分上。
ROW 9 | UAVDT | release=yes | protocol=yes | yolo_dist=unknown | reported=yes | reason: ECCV'18 论文发布独立 train/test 且 test 标注公开、可本地自评；通用 YOLO 发行包无 UAVDT 的 YAML；论文基线报在 test 上。
ROW 10 | xView | release=yes | protocol=no | yolo_dist=unknown | reported=yes | reason: 发布含独立 test 影像但标注扣留、走挑战赛服务器；Ultralytics xView.yaml 只有 autotrain/autoval、无 test 键；官方挑战赛榜单数字来自扣留 test。
ROW 11 | DIOR | release=yes | protocol=yes | yolo_dist=unknown | reported=yes | reason: 发布 train/val/test 且标注公开、可本地自评；DIOR-R yaml 属第三方镜像、不在通用 YOLO 发行包内；原论文基线报在 test 上。
ROW 12 | NWPU VHR-10 | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: TorchGeo 官方实现的 split 是 positive/negative（有无目标），不是 train/test 切分；无切分配置、无 YAML，官方报告数字的口径不可考。
ROW 13 | SHWD | release=yes | protocol=yes | yolo_dist=unknown | reported=yes | reason: 官方 README 发布 train/test 且标注公开、可本地自评；Reflective_vests.yaml 为镜像件、非通用 YOLO 发行包自带；README 报告的模型 mAP 在其 test 半边上。
ROW 14 | SFCHD | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 对该来源没有可信赖的一手了解，四个单元均不猜、按纪律记 unknown。
ROW 15 | MAFA | release=unknown | protocol=unknown | yolo_dist=unknown | reported=yes | reason: 数据集按申请分发、公开发布件中的切分配置与 YAML 均不可考；CVPR'17 原论文声明 train/test 划分并将 AP 报在 test 上。
ROW 16 | Mendeley face-mask | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 数据记录本身无官方切分配置（划分由镜像生成脚本产生）、无通用 YOLO 发行包 YAML，也无可考的官方论文/榜单数字。
ROW 17 | WIDER FACE | release=yes | protocol=no | yolo_dist=unknown | reported=unknown | reason: 官方站点确认 test GT 扣留、须评测服务器；通用 YOLO 发行包无其 YAML；论文基线口径(val)与官方榜单口径(服务器 test)不一致，reported 记 unknown（见下方歧义说明）。
ROW 18 | CrowdHuman | release=yes | protocol=no | yolo_dist=unknown | reported=unknown | reason: 发布 train/val（标注公开）与独立 test（标注扣留、须提交评测）；通用 YOLO 发行包无其 YAML；原论文数字报在 val 还是服务器 test 无法确定。
ROW 19 | D-Fire (FireSmoke) | release=yes | protocol=yes | yolo_dist=unknown | reported=yes | reason: 官方 README 发布 train/test 与 YOLO 格式标注、可本地自评；通用 YOLO 发行包无其 YAML；论文/仓库报告数字在其 test 半边上。
```

## 歧义说明（规则本身仍有两种读法之处）

1. **ROW 17 WIDER FACE 的 `reported`**：规则 2 把参照系写成"官方论文**或**官方榜单"，但未指明二者冲突时的优先级。以官方评测服务器榜单为参照 → `yes`（独立扣留 test）；以 CVPR'16 论文基线表（印象中报在 val）为参照 → `no`（选点与报告同半）。两读并存，故记 `unknown`。
2. **ROW 2 PASCAL VOC 的版本锚定**：规则 4 要求按"官方报告实际用的那一版"判。锚 VOC2007 → `protocol=yes`（test 标注公开）；锚 VOC2012 → `protocol=no`（test 服务器门控）。"哪一版是官方口径"本身依赖编码者对社区引用习惯的主观判断，规则未完全消除这一自由度；本编码按 2007 判并在 reason 中写明。
3. **ROW 14 SFCHD**：不是规则歧义，而是知识缺口声明——编码者对该来源无可靠一手了解，四个 `unknown` 是如实回答而非回避。
