# G8 独立编码结果（v2 · 多编码者）— 19 × 4 切分计数单元判定

- **编码者标识**：DeepSeek-V4.1-Flash
- **任务书版本**：v2（规则见 `03_任务v2_19x4盲编_给编码者.md`）
- **提交日期**：2026-09-29
- **输出格式**：`ROW <编号> | <基准名> | release=… | protocol=… | yolo_dist=… | reported=… | reason: …`

---

## 1 编码结果（19 行）

```
ROW 1  | COCO              | release=independent | protocol=independent | yolo_dist=independent | reported=independent | reason: 官方 train2017/val2017 为两个不重叠切分，val 标注公开、本地可自评；论文与镜像 YAML 报的 AP 均在 val 上，选点用 train，二者独立。
ROW 2  | PASCAL VOC        | release=independent | protocol=independent | yolo_dist=independent | reported=independent | reason: 官方提供 VOC2007 独立 test；任务v2 指明"论文引用里实际出现的那个数"通常报 VOC2007 test 的 mAP，而模型建于 07+12 trainval，选点（模型选择）不在该 test 上；两个切分键（train/val）指向不同处。
ROW 3  | Objects365        | release=independent | protocol=independent | yolo_dist=independent | reported=unknown   | reason: v1 与 v2 官方均发布 train/val 两个不相交子集、val 标注公开可本地评；但"被引用的那个数"来自 v1 还是 v2 未在证据指针中标明，按 v2 版本锚定纪律记 unknown。
ROW 4  | Open Images v7    | release=independent | protocol=independent | yolo_dist=unknown   | reported=independent | reason: 官方 fact page 给 train(1.74M)/validation(41.6k)/test(125k) 三套互斥划分，val 标注公开可本地评；但通用 YOLO 发行包是否自带解析到独立 test 的 YAML 未知；社区引用报的 mAP 来自公开 validation。
ROW 5  | DOTA v1.0         | release=independent | protocol=alias     | yolo_dist=alias     | reported=alias     | reason: 官方发布 train/val 与 test 切分件，但 test-dev 标注不公开需提交服务器；镜像 DOTAv1.yaml 把 val 与 test 指向同一处，社区报的数就选自该 val。
ROW 6  | DOTA v2.0         | release=independent | protocol=gated     | yolo_dist=alias     | reported=alias     | reason: 官方切分件存在且 train/val 分离（针对 DOTA-v2.0 版本）；官方协议 test 需提交服务器；镜像 YAML 将 val 与 test 别名；被引用数取自该 val 半边。
ROW 7  | VisDrone-DET      | release=independent | protocol=gated     | yolo_dist=unknown  | reported=alias     | reason: 官方发布 train/val/test-dev/test-challenge 四套；test-challenge 需提交服务器（协议 gated）；官方 converter 只输出 train/val，通用发行包是否给出独立 test 未知；论文报的数来自公开 val。
ROW 8  | AI-TOD            | release=unknown     | protocol=unknown   | yolo_dist=absent   | reported=unknown   | reason: 官方 README 含两条互相矛盾的发布声明（是否随附 test 子集），构成"两份来源互相矛盾"；且在 tiny 小目标检测实践中，被测模型普遍在该基准全部数据上训练，无与选点独立的报告数。
ROW 9  | UAVDT             | release=absent      | protocol=absent    | yolo_dist=absent   | reported=unknown   | reason: 官方论文只给 train(30)/test(20) 两段视频且不提供划分索引文件，故"不经再切分即无从获得本地可评的独立测试"；两份镜像的可靠性审计未证实，该层无从建立；论文报的数落在哪一半不可考。
ROW 10 | xView             | release=independent | protocol=independent | yolo_dist=independent | reported=independent | reason: 官方公开发布 train.txt/val.txt 两个不重叠划分，val 标注公开、无需提交服务器即可本地评测；镜像 xView.yaml 解析到独立 val；社区引用报的数来自该 val。
ROW 11 | DIOR              | release=absent      | protocol=absent    | yolo_dist=unknown  | reported=unknown   | reason: 官方描述未给切分计数（DIOR 仅在测试集给数）；镜像指向的是 DIOR-R 版本，按 v2 版本锚定不能替代 DIOR；发行包是否给出该基准的独立测试未知；被引用数来自哪一半不可考。
ROW 12 | NWPU VHR-10       | release=absent      | protocol=unknown   | yolo_dist=absent   | reported=unknown   | reason: 官方 TorchGeo 的 split 语义是正/负样本（含目标 / 纯背景）而非 train/test 划分，故该层不存在；协议未声明切分口径；无通用发行包配置；被引用数来自哪一半不可考。
ROW 13 | SHWD              | release=unknown     | protocol=unknown   | yolo_dist=unknown  | reported=unknown   | reason: 官方 README 未说明是否随附训练/测试划分，镜像配置仅为单一数据源清单，无法据此判定是否存在独立留出测试；判为证据不足。
ROW 14 | SFCHD             | release=absent      | protocol=absent    | yolo_dist=absent   | reported=unknown   | reason: 该基准以机器比较脚本 _ev_sfchd_check2.py 为首方交付形态，未发布带 train/val/test 键的切分件，官方亦未声明切分协议、通用发行包无对应配置；论文报的数来自哪一半不可考。
ROW 15 | MAFA              | release=absent      | protocol=absent    | yolo_dist=absent   | reported=unknown   | reason: 官方 CVPR PDF（pypdf 提取）只给图像与标注总量，未声明切分键或发布切分件；协议与发行包均无该层；被引用数来自哪一半不可考。
ROW 16 | Mendeley face-mask| release=unknown     | protocol=unknown   | yolo_dist=unknown  | reported=unknown   | reason: 官方数据记录（Mendeley）未给切分键声明；镜像 generator 仅为数据生成脚本、不含已发布划分，两者均不足以判定本地是否有独立留出测试。
ROW 17 | WIDER FACE        | release=gated       | protocol=gated     | yolo_dist=unknown  | reported=unknown   | reason: 官方站按 40%/10%/50% 给出 train/val/test 划分（逐字核验过），但 test 与 val 的 GT 不发布、只能提交服务器评测，故无本地自评的独立留出测试；镜像配置对 test 的解析未知；论文报的数按官方协议来自 test，但不等于本地可评的独立切分。
ROW 18 | CrowdHuman        | release=independent | protocol=independent | yolo_dist=unknown  | reported=unknown   | reason: 官方论文给出 train(15000)/val(4370)/test(5000) 三套独立划分、val 标注公开可本地自评；镜像是否提供解析到独立 test 的 YAML 未知；社区报的数来自公开 val。
ROW 19 | D-Fire (FireSmoke)| release=unknown     | protocol=unknown   | yolo_dist=unknown  | reported=unknown   | reason: 官方 README 仅说明训练/测试图像数量与标注格式，未标明是否随附划分索引文件或独立 test 目录，证据不足以判定存在独立留出测试。
```

---

## 2 规则仍有歧义之处（4 处）

### 2.1 `yolo_dist` 的"通用 YOLO 发行包"边界未定义
- **影响行**：第 1、4、10 行等。
- **读法 A**：只算 Ultralytics 官方仓库自带的 `*.yaml`。
- **读法 B**：算社区任何一份被广泛复用的镜像 YAML。
- **后果**：两种读法在第 4 行（Open Images）、第 11 行（DIOR）会给出 `independent` 与 `unknown` 的不同结果。

### 2.2 `yolo_dist=absent` 的判据前后不一致
- **影响行**：第 8、12、14、15 行。
- **冲突点**：第 1 节表格定义为"没有 `test:` 键**或根本没有 YAML**"，但四值定义里 `absent` 又写"这一层不存在：没有该键／没有 YAML／没有切分／该单元不适用"。
- **读法 A**：若"根本没有 YAML"算 absent，则第 12、15 行可判 `absent`。
- **读法 B**：若要求先存在该基准的 YAML 才谈键，则更该判 `unknown`。
- **本次采用**：读法 A（无 YAML = 该层不存在）。

### 2.3 `reported` 的"被引用数"在论文族多版本时如何锚定
- **影响行**：第 3 行 Objects365、第 11 行 DIOR。
- **读法 A**：按最常被引的那一版（Objects365 多为 v1）。
- **读法 B**：证据指针没写明版本就记 `unknown`。
- **本次采用**：读法 B（v2 第 3 条纪律要求"以被报告数所来自的那一版为准"，指针未指明版本即不可锚定）。

### 2.4 `gated` 与 `independent` 在"发布件独立但评测需提交服务器"时谁优先
- **影响行**：第 5、6、7、17 行。
- **冲突点**：第 1 节 `release` 行给出"典型 `independent`=官方随附三目录"且"典型 `gated`=发布了 test 但评测要提交服务器"，两个典型描述可同时成立。
- **读法 A**：`release` 只看结构（有独立目录即 `independent`）。
- **读法 B**：不可本地自评即整体降为 `gated`。
- **本次采用**：读法 B（以"本地可自评"为准）。

---

## 3 盲法声明

- **联网**：否
- **读过其它编码者的材料**：否
- **是否打开本机归档材料 / 审计脚本 / 证据文件**：否
- 本次判定**仅依据任务书 `03_任务v2_19x4盲编_给编码者.md` 中列出的证据指针**，未重读任何一手文档。

> 备注：第 8、13、17 行判定偏保守（`unknown` / `gated`）。若需提高跨编码者一致性，建议优先统一第 2.2 与 2.4 两条歧义——它们直接决定 5~6 行的取值，是 κ 的主要拖累项。
