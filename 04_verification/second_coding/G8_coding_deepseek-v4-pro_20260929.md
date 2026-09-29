# G8 盲编 · 编码结果

> 编码者标识：WorkBuddy（模型 deepseek-v4-pro）
> 盲法声明：联网＝否；读过其它编码者的材料＝否

## 19 行判定

ROW 1 | COCO | release=yes | protocol=no | yolo_dist=yes | reported=yes | reason: 官方发布件区分 train/val/test-dev/test-challenge，test 标注扣留（须提交服务器，不可本地自评）；coco.yaml 含独立 test 键；榜单数字来自 test-dev（与选点独立）。

ROW 2 | PASCAL VOC | release=yes | protocol=no | yolo_dist=unknown | reported=yes | reason: 发布件区分 trainval/test（2007/2012），test 标注扣留（评估服务器）；mirror VOC.yaml 仅 train+val（val 即 test2007 图像）无 test 键；官方报告数字来自扣留的 test2007。

ROW 3 | Objects365 | release=yes | protocol=no | yolo_dist=yes | reported=yes | reason: 发布 train/val（有标注）与 test（标注扣留、用于挑战赛）；mirror yaml 含独立 test 键；榜单数字来自扣留 test。

ROW 4 | Open Images v7 | release=yes | protocol=no | yolo_dist=yes | reported=yes | reason: 区分 train/val/test，test 标注扣留（Google 挑战赛）；open-images-v7.yaml 含独立 test 键；榜单来自扣留 test。

ROW 5 | DOTA v1.0 | release=yes | protocol=no | yolo_dist=yes | reported=yes | reason: 区分 train/val/test，test 标注扣留（官方评估服务器）；DOTAv1.yaml 含独立 test 键；报告数字来自扣留 test。

ROW 6 | DOTA v2.0 | release=yes | protocol=no | yolo_dist=yes | reported=yes | reason: 区分 train/val/test-dev/test-challenge，标注扣留；DOTAv2.yaml 含独立 test 键；榜单来自扣留 test。

ROW 7 | VisDrone-DET | release=yes | protocol=no | yolo_dist=yes | reported=yes | reason: 区分 train/val/test-dev/test-challenge，test 标注扣留（挑战赛）；VisDrone.yaml 含独立 test-dev 键；榜单来自扣留 test-challenge。

ROW 8 | AI-TOD | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: README 含两条关于 test 标注是否公开的互相矛盾声明，切分独立性无法判定；且不在通用 YOLO 包内。

ROW 9 | UAVDT | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 协调方注明除两个镜像外不可核实，我亦无法可靠判断 test 标注是否扣留；不在通用 YOLO 包内。

ROW 10 | xView | release=yes | protocol=no | yolo_dist=yes | reported=yes | reason: 区分 train/test，test 标注扣留（2018 挑战赛）；xView.yaml 含独立 test 键；榜单来自扣留 test。

ROW 11 | DIOR | release=yes | protocol=yes | yolo_dist=unknown | reported=yes | reason: 区分 train/val/test 且（据我所知）test 标注公开可本地自评；不在通用 Ultralytics 包（mirror 为旋转版 DIOR-R yaml）；论文报告扣留 test。

ROW 12 | NWPU VHR-10 | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 其"切分"是正样本/负样本而非 train/test，无留出切分配置，亦无官方固定 test。

ROW 13 | SHWD | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 社区数据集，我无法可靠回忆其确切切分结构；不在通用 YOLO 包；无官方榜单。

ROW 14 | SFCHD | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 该数据集我不熟悉，仅凭第一方评估脚本指针无法判定切分独立性。

ROW 15 | MAFA | release=yes | protocol=unknown | yolo_dist=unknown | reported=yes | reason: 区分 train/test（25876/4935），但我不确定 test 标注是否公开，故 protocol 记 unknown；不在通用 YOLO 包；论文报告扣留 test。

ROW 16 | Mendeley face-mask | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 该数据记录无固定 train/val/test 基准切分（切分由生成器现做），亦无官方榜单数字。

ROW 17 | WIDER FACE | release=yes | protocol=no | yolo_dist=unknown | reported=yes | reason: 区分 train/val/test，test 标注明确扣留（须提交服务器）；WiderFace.yaml 仅 train+val、无可评估 test 键；榜单来自扣留 test。

ROW 18 | CrowdHuman | release=yes | protocol=no | yolo_dist=yes | reported=yes | reason: 区分 train/val/test，test 标注扣留（服务器评估）；CrowdHuman.yaml 含独立 test 键；榜单来自扣留 test。

ROW 19 | D-Fire (FireSmoke) | release=yes | protocol=yes | yolo_dist=unknown | reported=yes | reason: 发布 train/val/test 且（据我所知）标注全公开可本地自评；不在通用 YOLO 包；论文报告扣留 test。

## 规则读法歧义（供协调者参考）

1. `yolo_dist` 对「yaml 有 `test:` 键、但 test 标注扣留」的基准（COCO、Objects365、Open Images v7、DOTA v1/v2、VisDrone、xView、CrowdHuman）：我按**结构读法**——`test:` 键指向独立目录即记 `yes`，与标注是否可用无关。若改为「须拿到可自评的标注才算独立测试」，这几行会翻成 `no`/`unknown`。这直接影响第 1、3、4、5、6、7、10、18 行的 `yolo_dist`。
2. `protocol=yes` 的几行（DIOR、D-Fire，以及 MAFA 我留了 `unknown`）依赖「test 标注公开」这一我仅有中等置信度的记忆；若实际 test 标注扣留，`protocol` 需改 `no`、`reported` 需复核。建议协调者对此三项的 `protocol` 做口径核对。
