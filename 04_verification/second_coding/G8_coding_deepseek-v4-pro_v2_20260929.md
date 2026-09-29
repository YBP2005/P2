# 独立编码结果（v2 · 19×4 切分计数单元判定）

- **模型标识**：WorkBuddy（deepseek-v4-pro）
- **盲法声明**：联网：否；读过其它编码者的材料：否（仅读本次提供的两份任务文件）。
- **口径说明**：`01_空白编码表` 页眉写 v1 规则（`yes/no/unknown`），`03_任务v2` 为 v2（5 值）。本结果按 **v2 的 5 值**作答。

## 19 行判定

```
ROW 1  | COCO            | release=independent | protocol=gated | yolo_dist=independent | reported=independent | reason: 官方 train2017/val2017/test-dev 三分互异；test-dev GT 扣留须提交服务器；mirror coco.yaml 的 val2017 有标注且与 train 独立；被引数在 test-dev（与选点 val 独立的扣留半）。
ROW 2  | PASCAL VOC      | release=independent | protocol=independent | yolo_dist=alias | reported=independent | reason: 官方 VOC2007/2012 均有 train/val/test（2007 test 标注公开）；协议主评 VOC2007 test 可本地自评（2012 test 须服务器）；mirror VOC.yaml 把 val 与 test 都指向 VOC2007 test（别名）；被引数在 VOC2007 test。
ROW 3  | Objects365      | release=independent | protocol=independent | yolo_dist=independent | reported=alias | reason: v1/v2 均只发 train+val（val 公开、无独立 test 目录）；协议与报告均在 val；mirror yaml 仅 train/val、无 test 键；被引数即 val（=选点半）。
ROW 4  | Open Images v7  | release=independent | protocol=gated | yolo_dist=independent | reported=independent | reason: train/val/test 三分；test GT 扣留须提交；mirror 的 val 有标注、独立于 train；被引数在 test。
ROW 5  | DOTA v1.0       | release=independent | protocol=gated | yolo_dist=independent | reported=independent | reason: train/val/test 三分；test GT 扣留须服务器；mirror val 有标注；被引数在 test。
ROW 6  | DOTA v2.0       | release=independent | protocol=gated | yolo_dist=independent | reported=independent | reason: 同 DOTA v1.0，test GT 扣留、val 公开。
ROW 7  | VisDrone-DET    | release=independent | protocol=gated | yolo_dist=independent | reported=independent | reason: train/val/test-dev/test-challenge；test-dev/challenge GT 扣留须服务器；mirror val 有标注；被引数在 test-dev/test-challenge。
ROW 8  | AI-TOD          | release=unknown | protocol=unknown | yolo_dist=absent | reported=unknown | reason: 官方 README 两处发布声明互相矛盾→release/protocol 无法判定；无 YOLO 发行 yaml；报告来源不可考。
ROW 9  | UAVDT           | release=independent | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 论文描述 train/test 结构（release 独立）；但两 mirror 被审计记为"未验证"，协议/发行/报告证据不足。
ROW 10 | xView           | release=independent | protocol=gated | yolo_dist=independent | reported=independent | reason: train/test 两分；test GT 扣留经 eval.ai；mirror 把 train 拆出 val 作本地留出；被引数在 test（部分论文用自制 val，见歧义）。
ROW 11 | DIOR            | release=independent | protocol=independent | yolo_dist=absent | reported=independent | reason: train/val/test 三分、test 标注公开可本地自评；mirror 是 DIOR-R（旋转版、异类），DIOR 本体无匹配 yaml；被引数在 test。
ROW 12 | NWPU VHR-10     | release=absent | protocol=absent | yolo_dist=absent | reported=unknown | reason: 官方只有正/负样本划分、无 train/test 切分→release/protocol/发行均无该层；论文用自制随机切分，被引数来源不可考。
ROW 13 | SHWD            | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: README 切分信息不足；唯一 mirror 是 Reflective_vests.yaml（异类数据集）→证据不足以判定。
ROW 14 | SFCHD           | release=unknown | protocol=unknown | yolo_dist=absent | reported=unknown | reason: 我对该基准不熟悉，官方首方发布信息不足以判定；无 YOLO yaml。
ROW 15 | MAFA            | release=independent | protocol=independent | yolo_dist=absent | reported=independent | reason: 论文给出 train(约3.1万)/test(约7千)、test 标注公开可本地自评；无 YOLO yaml；被引数在 test。
ROW 16 | Mendeley face-mask | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 数据记录切分信息不足、mirror 生成器口径不明→证据不足以判定。
ROW 17 | WIDER FACE      | release=independent | protocol=gated | yolo_dist=independent | reported=independent | reason: train/val/test 三分、test GT 明确不公开须服务器；mirror val 有标注；被引数在 test。
ROW 18 | CrowdHuman      | release=independent | protocol=gated | yolo_dist=independent | reported=independent | reason: train/val/test 三分、test GT 扣留须服务器；mirror val 有标注；被引数在 test。
ROW 19 | D-Fire (FireSmoke) | release=independent | protocol=independent | yolo_dist=absent | reported=unknown | reason: README 有 train/test 两分、test 标注公开；无标准 YOLO yaml；被引数来源（test 或自制切分）不可考。
```

## 规则歧义说明

1. **两份文件口径冲突**：`01` 空白表写 yes/no/unknown，`03` v2 写 5 值。我按 v2 作答；这非歧义而是版本错位，请协调者确认以哪个为准。
2. **"只有 train/val、无 test 键"时，`release` 与 `yolo_dist` 的 `independent` 有两种读法**（涉及 ROW 3 Objects365、ROW 10 xView）：把 val 当"独立留出测试"→`independent`；严格按"无 `test:` 键"→`absent`。我统一取前者，但会是跨编码者分歧点。
3. **`reported` 对"服务器门控基准"的读法（最大潜在分歧点）**：COCO/Open Images/DOTA/VisDrone/xView/WIDER/CrowdHuman 的被引数都在"扣留的 test 半"，我据此判 `independent`（该数来自与选点独立的切分）；但若强调"不能本地自评"，亦可判 `gated`。尤其 xView：部分论文实际用自制 val 报数，则 `reported` 会是 `alias`。v1→v2 只澄清了"不是官方服务器的数"，未澄清"门控 vs 独立半"。
4. ROW 9 UAVDT、ROW 13 SHWD、ROW 14 SFCHD、ROW 16 Mendeley、ROW 19 D-Fire 依据有限记忆判的确定性较低，已尽量用 `unknown` 兜底；如这些行一致性差属预期内（证据指针本身标记了"未验证"或证据单薄）。
