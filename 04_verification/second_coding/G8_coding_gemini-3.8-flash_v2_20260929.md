# 独立编码记录（v2）

**编码者标识**：gemini-3.8-flash  
**盲法声明**：联网：否 | 读过其它编码者的材料：否

---

## 编码表（19 行）

```
ROW 1 | COCO | release=independent | protocol=gated | yolo_dist=alias | reported=alias | reason: 官方发布包含独立的 train/val/test 目录（结构独立），但官方协议 test-dev 评测需提交服务器（标注扣留/门控）；YOLO 分发配置常态在 val 上做验证，文献与社区引用的主打指标普遍产生自 val2017（选点集与汇报集别名）。
ROW 2 | PASCAL VOC | release=independent | protocol=independent | yolo_dist=alias | reported=alias | reason: 锚定 VOC 2007 版（被引用主打数所用切分）：官方发布包含独立的 train/val/test，且 2007 test 标注已公开支持本地自评；但镜像 VOC.yaml 中 val 与 test 均指向 VOC2007 test，选点与最终汇报均落在该测试集上。
ROW 3 | Objects365 | release=absent | protocol=gated | yolo_dist=absent | reported=alias | reason: 锚定 Objects365 v1/v2：官方公开发行包仅提供 train 与 val，未发布独立公开的 test 结构件；官方挑战赛测试标注扣留需线上评测；YOLO 分发 YAML 未提供独立 test 键，学界与社区引用普遍在 val 上选点并汇报。
ROW 4 | Open Images v7 | release=independent | protocol=independent | yolo_dist=absent | reported=independent | reason: 官方发布提供独立的 train/val/test 数据及公开标注，支持本地自评；官方权威文献与基准引用报告独立的 test 指标；YOLO 通用镜像分发中常无独立 test 键。
ROW 5 | DOTA v1.0 | release=independent | protocol=gated | yolo_dist=alias | reported=independent | reason: 官方发布包含独立的 train/val/test 图像目录，但官方测试协议需提交在线服务器评测（标注扣留）；学术界主流文献按惯例向官方服务器提交并在 test 上汇报指标，部分 YOLO 镜像则在本地 val 上别名。
ROW 6 | DOTA v2.0 | release=independent | protocol=gated | yolo_dist=alias | reported=independent | reason: 官方发布具有独立的 train/val/test-dev 划分结构，但测试协议严格门控（需服务器评测）；学术论文主打指标来源于服务器返回的 test 独立评测。
ROW 7 | VisDrone-DET | release=independent | protocol=gated | yolo_dist=alias | reported=alias | reason: 官方划分包含 train/val/test-dev 等独立结构，但官方 challenge/test-dev 评测需提交服务器；YOLO 镜像分发及社区论文实际汇报的 mAP 普遍直接在 val 上评估并与选点混用。
ROW 8 | AI-TOD | release=unknown | protocol=unknown | yolo_dist=absent | reported=unknown | reason: 官方 README 存在相互矛盾的发布切分声明，证据指针自相冲突，不足以确切判定其发布与协议属性；无独立 YOLO 发行包。
ROW 9 | UAVDT | release=independent | protocol=independent | yolo_dist=unknown | reported=unknown | reason: 官方论文定义了 train 与 test 切分并支持本地自评，但两个主流镜像实现互不一致且未经独立验证，分发与实际引用来源依据不足。
ROW 10 | xView | release=gated | protocol=gated | yolo_dist=absent | reported=alias | reason: 官方发布仅开源 train 标注，val 标注扣留用于竞赛（门控）；YOLO 镜像配置无独立 test 键，使用者通常在 train 自划的验证集上调参并汇报指标。
ROW 11 | DIOR | release=independent | protocol=independent | yolo_dist=independent | reported=independent | reason: 官方描述包含 train/val/test 且公开全部标注，支持本地自评；遥感目标检测文献与 DIOR-R 镜像配置普遍直接在独立的 test 切分上评测并汇报指标。
ROW 12 | NWPU VHR-10 | release=absent | protocol=absent | yolo_dist=absent | reported=unknown | reason: 官方数据及 TorchGeo 证据表明该数据集仅有正负样本目录划分，官方根本未发布 train/val/test 结构切分与评测协议，文献各自随机划分。
ROW 13 | SHWD | release=absent | protocol=absent | yolo_dist=alias | reported=alias | reason: 官方开源仓库仅提供标注与图片，无官方基准切分件；社区 Reflective_vests.yaml 等镜像将数据自划或 val/test 别名，文献直接在验证集上汇报。
ROW 14 | SFCHD | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 依据给定的机器比对脚本证据指针，一手发布切分属性信息不足，按纪律不确定记为 unknown。
ROW 15 | MAFA | release=independent | protocol=independent | yolo_dist=absent | reported=independent | reason: CVPR 官方论文发布了明确划分且标注完全公开的 train 与 test，支持本地自评，论文主打数字直接在独立 test 上产生；无官方 YOLO 分发包。
ROW 16 | Mendeley face-mask | release=absent | protocol=absent | yolo_dist=absent | reported=unknown | reason: 官方仅为 Mendeley 平台上的原始数据文件包，无官方切分件及评测协议；分发依赖第三方生成器，缺乏统一独立的汇报测试集。
ROW 17 | WIDER FACE | release=independent | protocol=gated | yolo_dist=alias | reported=alias | reason: 官方发布随附 train/val/test 三个独立目录，但 test 标注逐字确认未公开且必须向服务器提交评测；YOLO 镜像配置及大量社区文献直接在公开标注的 val 集上做验证与指标汇报。
ROW 18 | CrowdHuman | release=independent | protocol=gated | yolo_dist=alias | reported=alias | reason: 官方论文发布 train/val/test 独立结构，但 test 标注扣留用于挑战赛评测（门控）；YOLO 分发包与绝大多数文献均在公开标注的 val 集上调参并汇报指标。
ROW 19 | D-Fire (FireSmoke) | release=independent | protocol=independent | yolo_dist=independent | reported=independent | reason: 官方 README 直接提供包含标注的独立 train 与 test 划分及 YOLO 格式配置，支持本地自评，报道指标产自独立 test。
```

---

## 规则歧义说明

1. **`release` 与 `protocol` 在"扣留标注/门控服务器"基准上的边界区分（如 COCO、DOTA、WIDER FACE、CrowdHuman）**：
   - **读法 A（本编码采纳，对齐任务书示例 X1）**：`release` 仅按物理发布件/目录结构判断（"只看结构，不看标注是否公开"），只要官方包随附独立的 test 图像目录就判为 `independent`；而能否本地自评完全由 `protocol` 承担，必须提交服务器或标注扣留的判为 `gated`。
   - **读法 B**：任务书第 40 行的典型值表格中把"官方发布了 test 但评测要提交服务器"也列为 `release` 下的典型 `gated`。若采纳读法 B，则 COCO、DOTA、WIDER FACE、CrowdHuman 的 `release` 单元将全部由 `independent` 转变为 `gated`。

2. **`reported` 在存在门控测试集基准上的双重口径（以 DOTA 为代表）**：
   - **读法 A（学术规范口径，本编码采纳）**：在面向对象/遥感检测的主流学术论文中，引用与对比的权威数字必须经由 DOTA 评估服务器测评并在 test 上生成，因此判定为 `independent`。
   - **读法 B（YOLO 实践者工程口径）**：在通用 YOLO 生态与 GitHub 镜像复现中，使用者通常无法即时获得服务器评测结果，社区和代码库实际报告的 mAP 往往直接产自本地 val 集，若按此工程实践口径则判定为 `alias`。
