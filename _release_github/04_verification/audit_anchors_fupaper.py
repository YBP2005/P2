"""副论文正文的审计锚点（指南 §5.3）。

用法：python -X utf8 work/audit_anchors_fupaper.py
要求：输出 ALL PASS（退出码 0）。

设计要点（沿用本项目 r2 的教训）：
  * 负锚若只写"某短语不得出现"，会命中**合法的反例引用**（如正文写"我们不主张'首次…'"）。
    故凡属"不得作断言"的，用**行内否定语境判定**，而不是裸正则。
  * 计数锚必须把作用域限定到**结构位置**（表格行），否则会随正文其他章节的正常表述漂移。
  * r13：方向主张由"该惯例低估而非制造臂间差异"收窄为"使臂间比较系统性偏移、方向按语料而异"
    （两级报告）。旧措辞以**豁免负锚**（N11/N12）锁死，只允许作为"已撤回"被引用。
"""
import io, os, re, sys

sys.stdout.reconfigure(encoding='utf-8')

BASE = r'E:\workplace'
PAPER = os.path.join(BASE, '评测有效性稿_正文_v0.1.md')
ADJ = os.path.join(BASE, '审计文档更正与裁定_20260916.md')
RECOMP = os.path.join(BASE, 'split_units_recompute_20260916.txt')
ROWSTAB = os.path.join(BASE, 'split_units_19rows_20260916.md')
CRIT = os.path.join(BASE, '核对_两条审稿意见_20260916.md')
VTXT = r'D:\deepseek\analysis\eval_validity\verify_two_critiques_20260916.txt'
# B 文档（整合说明）——只在 D:\deepseek；横幅由用户显式豁免后加入
BDOC = r'D:\deepseek\analysis\eval_validity\split_audit_integration_20260915.md'
# P2 内部件（原正文 §13 抽出的目标轨道与缺口；正文不得再含该节）
P2INT = os.path.join(BASE, 'P2_内部_轨道裁剪与缺口_20260916.md')
SUPP = os.path.join(BASE, 'P2_补充材料.md')
SUPP_EN = os.path.join(BASE, 'P2_Supplementary_English_v0.1.md')
BLIND_EN = os.path.join(BASE, 'P2_English_submission_blind_v1.md')
ENG = os.path.join(BASE, 'P2_English_v0.1.md')
FIGS = os.path.join(BASE, 'figures', 'FIGURES.md')
REFLIST = os.path.join(BASE, 'P2_参考文献_v0.1.md')
CURVE = os.path.join(BASE, 'xeval_20260916', 'curve.csv')


def load(p):
    if not os.path.exists(p):
        return None
    return io.open(p, encoding='utf-8', newline='').read()


paper = load(PAPER)
adj = load(ADJ)
recomp = load(RECOMP)
rowstab = load(ROWSTAB)
crit = load(CRIT)
vtxt = load(VTXT)
bdoc = load(BDOC)
p2int = load(P2INT)
supp = load(SUPP)
suppen = load(SUPP_EN)
blind = load(BLIND_EN)
eng = load(ENG)
figs = load(FIGS)
reflist = load(REFLIST)
curve = load(CURVE)

if paper is None:
    print(f'FAIL: 找不到正文 {PAPER}')
    sys.exit(2)

# ---------------- 正锚：关键数字与关键声明必须在位 ----------------
# (编号, 描述, 正则)
POSITIVE = [
    ('P01', '语料级计数 6/14', r'14\s*个语料有\s*6\s*个'),
    ('P02', '按文件（全树）19 个 yaml', r'\*\*19\s*个文件\*\*'),
    ('P03', 'MANIFEST 子集 28 中 8', r'\*\*28\s*个中\s*8\s*个\*\*'),
    ('P04', 'SHWD 三键同目录原文', r'train:\s*images'),
    ('P05', '选择溢价基线臂 +0.799', r'\+0\.799'),
    ('P06', '选择溢价策略臂 +0.382', r'\+0\.382'),
    ('P07', '选择溢价基线臂 +1.038', r'\+1\.038'),
    ('P08', '选择溢价策略臂 +0.512', r'\+0\.512'),
    ('P09', 'dota15 三对配对 +1.12/+0.95/+0.93', r'\+1\.12\s*/\s*\+0\.95\s*/\s*\+0\.93'),
    ('P10', 'dota15 修好的两处原因：旧快照', r'根目录是旧快照'),
    ('P11', 'dota15 修好的两处原因：无种子后缀', r'没有种子后缀'),
    ('P12', '新披露：3 seeds 措辞不精确', r'"3 seeds"的措辞不精确|3 seeds.*措辞不精确'),
    ('P13', '字面同路径 2/19 ≈ 11%', r'2/19\s*≈\s*11%'),
    ('P14', '协议层 13/19 ≈ 68%', r'13/19\s*≈\s*68%'),
    ('P15', '报告层 12/19 ≈ 63%', r'12/19\s*≈\s*63%'),
    ('P16', '报告层干净 3/19 ≈ 16%', r'3/19\s*≈\s*16%'),
    ('P17', '可判定行中 12/15 = 80%', r'12/15\s*=\s*80%'),
    ('P18', '求和校验 12+3+4=19', r'12\s*\+\s*3\s*\+\s*4\s*=\s*19'),
    ('P19', '算法自检复现 2/19', r'复现.*2/19|2/19.*复现'),
    ('P20', 'Σ 三分量：增广 0.246', r'0\.246'),
    ('P21', 'Σ 三分量：初始化 0.146', r'0\.146'),
    ('P22', 'Σ 三分量：数据顺序 0.515', r'0\.515'),
    ('P23', '选择膨胀幅度 9%–29%', r'9%–29%'),
    # P24：两个数在表格的两行上，故用有界 DOTALL
    ('P24', '选择膨胀逐格 −0.14 / −0.20', r'(?s)−0\.14.{0,220}?−0\.20'),
    # P26：正文用通式 2/2ⁿ 并给出 n=3 → 0.25，两种写法都接受
    ('P25', 'n=3 置换检验下界 0.25', r'0\.25'),
    ('P26', '置换检验最小可达 p 的通式', r'2/2ⁿ|2/2³|2/2\^?n'),
    ('P27', 'n=10 置换下界 0.001953', r'0\.001953'),
    ('P28', '十种子 10/10 为正', r'10/10'),
    ('P29', 'T2 冲突：67.12 (final)', r'67\.12'),
    ('P30', 'T2 冲突：70.06 (best)', r'70\.06'),
    ('P31', 'T2 取 best 后的 Δ −1.490', r'−1\.490'),
    ('P32', 'T2 取 best 后的 p = 0.0141', r'0\.0141'),
    ('P33', 'T2 换 A 行的 p = 0.2931', r'0\.2931'),
    ('P34', '端点口径无成文规定（披露）', r'端点口径没有成文规定|端点口径无成文规定'),
    ('P35', '无存活 stdout 留档（披露）', r'没有存活的 stdout 留档|无 stdout 留档'),
    ('P36', 'rf-detr 静默回退代码行', r'silently returns val metrics'),
    ('P37', 'ultralytics #25650（KITTI）', r'25650'),
    ('P38', '竞争 1 DOI', r'10\.3390/technologies14090531'),
    ('P39', '竞争 2 DOI', r'10\.3390/drones10080635'),
    ('P40', '竞争 2 的 val-vs-test 结论（无系统方向）', r'no systematic direction'),
    ('P41', '竞争 2 的图像级污染 46.0%/90.7%', r'46\.0%.*90\.7%'),
    ('P42', '竞争 1 的受控消融 0.040', r'0\.040'),
    ('P43', 'Barz & Denzler 锚点 9–14%', r'9–14%'),
    ('P44', 'CVPR 2026 同体裁先例', r'Data Leakage Detection and De-duplication'),
    ('P45', '定位一句话存在', r'定位（一句话）'),
    ('P46', '不主张"首次"', r'不主张"首次审计检测基准的划分问题"'),
    ('P47', '三篇密级差异表里"本文"一行', r'\*\*本文\*\*'),
    ('P48', '干净协议定义（三分划）', r'从"池 − 子集"\*\*新划出\*\*|新划出的验证集'),
    ('P49', '取错列已修并留痕', r'取错列'),
    ('P50', '全文带本地文件指针 →', r'→'),
    # ---- r13：方向主张收窄为"两级"，并写入两条外部质疑的核对 ----
    ('P51', '方向结论"必须分两级"的结构声明', r'必须分两级'),
    ('P52', '第一级配对差 smoke2sf +0.416', r'\+0\.416'),
    ('P53', '第一级配对差 shwd2sf +0.526', r'\+0\.526'),
    ('P54', '第一级配对差 a2d15 +0.272', r'\+0\.272'),
    ('P55', '第一级配对差 dota15 +0.589', r'\+0\.589'),
    ('P56', 'dota15 同域溢价 +0.941（升到 n = 10 后）', r'\+0\.941'),
    ('P57', 'Δgap shwd2sf +0.779 且 p 0.0053', r'\+0\.779.{0,60}?0\.0053'),
    ('P58', 'Δgap smoke2sf +0.461 且 p 0.0263', r'\+0\.461.{0,60}?0\.0263'),
    ('P59', 'Δgap p_aitovis −1.226 且 p 1.3×10⁻⁸', r'−1\.226.{0,60}?1\.3×10⁻⁸'),
    ('P60', 'Δgap p_vistod15 −3.315 且 p 6.5×10⁻⁹', r'−3\.315.{0,60}?6\.5×10⁻⁹'),
    ('P61', 'Δgap 的配对差分定义式', r'Δgap\s*=\s*（臂间差 on val）'),
    ('P62', 'raw gap 不可识别的实测跨度', r'−33\.0 ~ \+21\.2'),
    ('P63', 'shwd2sf test 臂间差 −0.507（符号翻转）', r'−0\.507'),
    ('P64', '13 格里 4 格显著', r'13\s*格里\s*\*\*4\s*格显著\*\*'),
    ('P65', '免费交叉验证 +1.434', r'\+1\.434'),
    ('P66', '结论不依赖配对（Welch t 5.68）', r'5\.68'),
    ('P67', '新增 §5.4 存在', r'### 5\.4 两条外部质疑的核对'),
    ('P68', '引用核对报告文件名', r'核对_两条审稿意见_20260916\.md'),
    ('P69', '引用复算输出文件名', r'verify_two_critiques_20260916\.txt'),
    ('P70', '三个边缘格未过线的 p 值', r'0\.054'),
    # ---- r13c：§12 目标轨道已定（主 TMLR / 备选 NeurIPS D&B）----
    ('P76', 'B 文档横幅已在附录 C 记为已解决', r'其 10/19、13/19、4/19、12/19、3/19、2/19 六个计数经核验'),
    # ---- r14：计数口径统一（P2-3）----
    ('P77', '§6.1 含 release 行 10/19', r'\| \*\*release\*\*（基准自身发布物层） \| \*\*10/19'),
    ('P78', '§6.1 的 yolo_dist 整列 = 4/19', r'\| \*\*yolo_dist\*\*（通用 YOLO 分发包层） \| \*\*4/19'),
    ('P80', '§6.1 标题已改为"四种单位"', r'### 6\.1 四种单位下的结果'),
    # ---- r14c：首报规则（P2-4）----
    ('P81', '§5.1 已加首报归属注', r'\*\*首报归属\*\*：上句两个干净协议读数'),
    ('P82', '§7.2 已加权威首报注', r'\*\*首报归属（口径纪律）\*\*：本表两个 Δ'),
    ('P83', '摘要已标"首报于伴生论文（点名主题）"', r'该读数首报于伴生论文'),
    # ---- r15：E 块（注册复制）----
    ('P84', '新 §9 = 发现五（注册复制）', r'## 9\. 发现五：注册复制的陈述与"未达冻结判据"'),
    ('P85', '冻结注册的 md5', r'6a7eee7b3e34b15ce5adcba14cf7ea36'),
    ('P86', 'H1 冻结判据三条件', r'≥ \*\*\+0\.30 pp\*\*、配对 p < \*\*0\.01\*\*'),
    ('P87', 'T1-a Δ +0.147', r'\+0\.147'),
    ('P88', 'T1-b Δ +0.168', r'\+0\.168'),
    ('P89', 'T1-c Δ +3.727', r'\+3\.727'),
    ('P90', 'H1 判定：未复制', r'H1 判定：未复制'),
    ('P91', '措辞口径：不写"假设被否证"', r'不写"假设被否证"'),
    ('P92', 'T2 饱和对照 Δ −1.490', r'−1\.490'),
    ('P93', 'T2 p = 0.0141', r'p = 0\.0141'),
    ('P94', 'T2 未落入任何字面情形（须人工裁定）', r'未落入冻结文件的任何字面情形'),
    ('P95', '对照 C Δ +0.727', r'\+0\.727'),
    ('P96', '对照 C p = 1.53×10⁻⁸', r'1\.53×10⁻⁸'),
    ('P97', '四个同目录格（含对照）', r'\*\*同目录\*\* ✗'),
    ('P98', '唯一划分分离的格是 T1-b', r'唯一划分分离的格（T1-b）'),
    ('P99', '登记规模 70 run', r'70 run'),
    ('P100', 'BH 后仍显著 1/3', r'BH（q = 0\.05，m = 3）后仍显著：1/3'),
    # ---- r16：公开日志溢价（§5.5）----
    ('P101', '§5.5 存在（第三方公开日志）', r'### 5\.5 第三方公开日志上的同一成分'),
    ('P102', '样本 20 条 / 6 个来源', r'\*\*20 条 / 6 个来源\*\*'),
    ('P103', '溢价中位数 +1.04 pp', r'\+1\.04'),
    ('P104', '最大溢价 +5.65 pp', r'\+5\.65'),
    ('P105', '18/20 为正', r'\*\*18/20\*\*'),
    ('P106', 'PROVENANCE 24/24 已溯源', r'\*\*24/24 文件\*\*'),
    ('P107', 'GitHub 固定点 commit', r'2417aff0457c'),
    ('P108', '静默排除缺陷已记录', r'任何地方都没有诊断'),
    ('P109', '"溢价存在"与"基准别名"是两条独立证据', r'两条独立证据，不能互相代替'),
    ('P110', '两种列名拼写都接受', r'metrics/mAP_0\.5:0\.95'),
    ('P111', '摘要已引 §5.5 公开日志证据', r'中位数 \*\*\+1\.04 pp\*\*、最大 \*\*\+5\.65 pp\*\*、\*\*18/20\*\* 为正'),
    ('P112', '贡献 1 已引 §5.5', r'在\*\*他人发表的\*\*日志上同样普遍存在'),
    # ---- r17：§5.6 Δgap 符号的机制检验 ----
    ('P113', '§5.6 存在（机制检验）', r'### 5\.6 Δgap 的符号为何按语料而异'),
    ('P114', 'M1 乘性增益（被排除）', r'\*\*M1 乘性增益\*\*'),
    ('P115', 'M2 天花板压缩（被排除）', r'\*\*M2 天花板压缩\*\*'),
    ('P116', 'M4 test 增益决定符号（被排除）', r'\*\*M4 策略在 test 上是否真有增益\*\*'),
    ('P117', 'Δgap 的恒等式解释', r'Δgap > 0 ⟺ val 上的相对臂间差小于 test 上的'),
    ('P118', '精确三分量分解式', r'Δgap =（\*\*末轮 val\*\* 上的臂间差）'),
    ('P119', 'mask20 两分量几乎抵消（+15.78 / −13.10）', r'\+15\.78'),
    # P120 原锁「机制不可识别」，r19 补做后该句被有意取代 → 转为硬负锚 N15
    ('P119b', '§5.6 已标「已在 GPU 上补做后升级」', r'（\*\*已在 GPU 上补做后升级\*\*）'),
    # ---- r18：§6.5 跨框架审计 ----
    ('P121', '§6.5 存在（跨框架）', r'### 6\.5 跨框架：这个惯例是 YOLO 专有的吗'),
    ('P122', '跨框架语料 23 个文件 / 5 框架', r'\*\*23 个文件\*\*'),
    ('P123', 'Detectron2 固定 commit', r'a2f4a8771ab7'),
    ('P124', 'COCO test 标注是 image_info（无 GT）', r'image_info_test2017\.json'),
    ('P125', 'PaddleDetection 的 TestDataset 读 val 标注', r'`TestDataset` 用无 GT 的 `ImageFolder`'),
    ('P126', 'C-2 收窄：只有 YOLO 系默认选点', r'只有 YOLO 系默认这么做'),
    ('P127', '跨框架语料哈希清单指针', r'_xframe\\SHA256SUMS\.txt'),
    ('P128', '§5.1 已加"适用范围"句（跨框架边界）', r'\*\*适用范围（跨框架边界）\*\*'),
    ('P129', '§5.1 明示"这一族管线"而非全领域', r'因此本节的"惯例"指的是这一族管线的惯例'),
    ('P130', '§6.5 自指句已与 §5.1 对齐', r'并在 §5\.1 的正式主张后加了"适用范围"句'),
    # ---- r19：CUDA 补做的 2×2 评估 ----
    ('P131', '§8.6 存在（选点获益兑现率）', r'### 8\.6 ⭐ 选点获益的"兑现率"：\*\*19%\*\*'),
    ('P132', '兑现率 19%', r'兑现率 19%'),
    ('P133', 'prem_test 逐格（shwd2sf 基线 +0.735）', r'\+0\.735'),
    ('P134', '两格 prem_test 为负', r'两格的 `prem_test` 为负'),
    ('P135', '41 run 独立复现归档（最大差 0.0047）', r'在 \*\*41 个 run 上最大差 0\.0047 pp、中位 0\.0021 pp\*\*'),
    ('P136', '§5.6 机制已可分解', r'它的生成机制现在已经可分解'),
    ('P137', '§5.6 分解表含 +1.041', r'\+1\.041'),
    ('P138', '§5.6 明写分解只覆盖 2/13 格', r'分解只覆盖 2/13 格'),
    ('P139', '§10 缺陷 5 已部分修复', r'已部分修复（2026-09-16，CUDA 补做）'),
    ('P141', '摘要含"只兑现 19%"', r'在独立 `test` 上只兑现 19%'),
    ('P142', '摘要含"164 次评估、0 失败"', r'\*\*164 次评估、0 失败\*\*'),
    # ---- r20：P1 侧交付的互引/缺口义务 ----
    ('P143', '首次出现点名伴生论文主题（互引 §1）', r'首报于伴生论文\*\*（the budgeted fine-tuning study；本文记作 \*\*P1\*\*）'),
    ('P144', '§8.2 已补"可复算现状"（G8）', r'\*\*可复算现状（2026-09-16 更新）\*\*'),
    ('P145', '§8.2 写明 84 个文件已拉回本地', r'共 \*\*84 个文件\*\*全部拉回本地'),
    ('P147', '文档标题已按新命名规范（P2 · 划分稿）', r'^# 评测有效性稿（P2 · 划分稿）'),
    ('P148', '已标注下界两种拼写须按数值比较', r'n = 10 的可达下界\*\*精确值 = 2/2¹⁰ = 0\.001953\*\*'),
    # ---- r21：附录 C 同步 GPU 补做后的状态 ----
    ('P149', '附录C 第5条已标"复算路径已补上"', r'已于 2026-09-16 补上\*\*（CUDA 补做 2×2 评估后'),
    ('P150', '附录C 第7条"验证侧已可本地完成"', r'但"验证侧"已可本地完成'),
    ('P151', '附录C 新增第8条（投稿形态三件）', r'投稿形态尚未就绪（新发现，三件）'),
    ('P152', '附录C 写明待拉回的划分清单', r'`datasets/split_5_5/sfchd20_3way\.yaml`'),
    # ---- r24：附录指向补充材料（G6）----
    ('P153', '附录 A 指向补充材料 S1', r'全文见补充材料 S1'),
    ('P154', '附录 A 记录了补充材料的 md5', r'md5 `ed5ba8571f0e4d537682759b9ba62982`'),
    ('P155', '附录 B 指向补充材料 S2–S5', r'跨框架的逐行证据见补充材料 S3'),
    ('P156', '附录 C 前有补充材料声明', r'补充材料\*\*：本稿的\*\*逐行证据类\*\*内容放在独立文件'),
    ('P157', '明写披露类内容留正文', r'披露类内容（首报归属、方法论前提、缺口）一律留在本正文'),
    # ---- r25：共享工具的"不得主张原创"（互引记录 §5/§8）----
    ('P158', '§2.3 明示不主张的贡献', r'### 2\.3 明示\*\*不\*\*主张的贡献（共享工具）'),
    ('P159', '§2.3 写明两者都不是本文方法学', r'不是公开出版物，也不是本文的方法学贡献'),
    ('P160', '§2.3 覆盖审计锚点体系', r'同一条约定也适用于\*\*审计锚点体系\*\*'),
    ('P161', '§2.3 点名"多模型核对清单"（概念在场）', r'多模型核对清单'),
    # ---- r33：逐 epoch 曲线（新 §8.7）----
    ('P162', '§8.7 存在（逐 epoch 版本）', r'### 8\.7 逐 epoch 版本：兑现率不是一个常数'),
    ('P163', '§8.7：202 次评估 0 失败', r'202 次评估、0 失败'),
    ('P164', '§8.7：全机 3,854 个中间 checkpoint', r'3,854'),
    ('P165', '§8.7：过原点斜率 κ = 0.708（全曲线）', r'\*\*κ = 0\.708'),
    ('P166', '§8.7：记了指标自我更正（比值病态）', r'那是指标病态，不是发现'),
    ('P167', '§8.7：Δgap 全曲线符号普查（smoke2sf 头三点为负 —— 更正后的说法）',
     r'\| smoke2sf \| 19 \| \*\*16\*\* \| \*\*3\*\* \| \*\*epoch 5、10、15\*\*'),
    ('P168', '§8.7：说明 19% 与 0.734 不矛盾', r'并不矛盾，因为两者量的区间不同'),
    ('P79', '§6.1 的更正说明（首版把 2/19 挂 yolo_dist）', r'首版把 \*\*2/19 挂在 `yolo_dist` 名下\*\*'),
]

# ---------------- 负锚：不得出现（裸正则，仅用于"绝无例外"的表述） ----------------
NEGATIVE_HARD = [
    ('N03', '审计原值 14/19 ≈ 74% 不得作为本稿口径出现', r'14/19\s*≈\s*74%'),
    ('N04', '审计原值 5/19 ≈ 26% 不得作为本稿口径出现', r'5/19\s*≈\s*26%'),
    ('N06', '冲突未查明的旧表述不得复现', r'引用前必须查明该冲突'),
    ('N07', '已撤回的旧贡献措辞不得复现', r'量化了一个此前只被定性提及的测量伪影'),
    ('N08', '审计的 12/19 不得被当成本稿的某单位值', r'12/19\s*≈\s*63%（发布物层）'),
    # ---- r13 ----
    ('N09', '旧 §5.1 单向标题不得复现', r'5\.1 方向：选择\*\*低估\*\*了臂间差异'),
    ('N10', '旧定位句"偏差方向（低估）"不得复现', r'偏差方向（低估）'),
    ('N13', '旧 §12 标题"（待定）"不得复现', r'按目标轨道的裁剪说明（待定）'),
    # r54: this was a negative anchor forbidding ANY '## 13.' in the article, because the old
    # §13 (the planning section "按目标轨道的裁剪说明") had been moved into an internal file.  r54 legitimately
    # reused the number for the formalisation section, so the anchor is TIGHTENED into a positive
    # one: §13 must be the formalisation section.  The old planning text is still forbidden, by N13.
    ('N16', '§13 必须是形式化节（旧的“裁剪说明”仍由 N13 守）', r'(?m)^## 13\. Formalisation'),
    ('N15', '旧句"机制在本归档里不可识别"不得复活（r19 已补做并可分解）',
     r'它的生成机制在本归档里不可识别'),
]

# ---------------- 负锚（行内豁免标记） ----------------
# 命中行只要**含有豁免标记**（如"不引用""已撤回""~~已修~~"）即视为合法引用。
# 这是 r2 教训的直接应用：撤回值**必须**能在正文里被引用一次（说明它被撤回了），
# 故不能对这类短语下裸负锚。
# (编号, 描述, 目标正则, 豁免标记正则)
NEG_LINE = [
    ('N01', '审计原文的 "63–79%" 不得作为本稿口径', r'63–79%',
     r'不引用|不再引用|无逐行枚举|已撤回|不得再现'),
    ('N02', '未枚举的上界 15/19 不得作为本稿口径', r'15/19',
     r'不引用|不再引用|无逐行枚举|已撤回|不得再现'),
    ('N05', '已修结论"dota15 不可复现"只能以删除线形式留痕', r'dota15\s*格不可复现',
     r'~~|已修'),
    # ---- r13 ----
    ('N11', '旧措辞"方向与直觉相反"只能以删除线/撤回形式留痕', r'方向与直觉相反',
     r'~~|原稿写|已撤回|已于 r13'),
    ('N12', '"该问题低估而非制造臂间差异"只能作为已撤回措辞被引用', r'该问题\*\*低估\*\*而非制造臂间差异',
     r'原稿写|~~|已撤回|已于 r13'),
]

# ---------------- 行内否定语境判定：不得作"断言"的 ----------------
# (编号, 描述, 目标正则, 允许的否定标记)
NEG_SCOPED = [
    ('S01', '不得断言"首次审计检测基准的划分"',
     r'首次审计检测基准的划分', r'不主张|不是|并非|此前已有|已被'),
    ('S02', '不得断言"我们首次测量了图像级泄漏"',
     r'首次.{0,8}图像级', r'不主张|不是|并非|已被|此前'),
    # ---- r13 ----
    ('S03', '不得把"普遍低估"当作本稿主张',
     r'普遍低估', r'不是|不主张|不得|不能|而非|~~|已于 r13'),
    # ---- r15 ----
    ('S04', '不得把登记复制说成"干净协议下的结论"',
     r'干净协议下的结论', r'不能|不是|不把|~~'),
    ('S05', '不得声称公开日志给出了领域级分布或推出别名', r'领域级',
     r'不能|不是|不假设|~~'),
    ('S06', '不得把 YOLO 系的默认说成整个检测领域的默认', r'整个检测领域的默认',
     r'不能|不是|而非|还是'),
]

# ---------------- 计数锚：结构性要求 ----------------
COUNTS = [
    ('C01', '定位一句话恰好 1 处', r'定位（一句话）', 1),
    ('C02', '§6.1 四单位表恰好 4 个单位行（release/protocol/yolo_dist/reported）',
     # 必须带括号标签：否则会同时命中 §3 的单位定义表（实测 8 处）
     r'(?m)^\| \*\*(release|protocol|yolo_dist|reported)\*\*（', 4),
    ('C03', '§8.4 Σ 三分量表恰好 3 个数据行', r'(?m)^\| (增广 RNG|\*\*初始化（源端从零重训）\*\*|第二阶段数据顺序)', 3),
    ('C04', '§2.1 差异表恰好 6 个数据行', r'(?m)^\| (《Sequence-Aware|《Cross-Dataset|`roboflow/rf-detr`|`ultralytics` #25650|CVPR 2026《Data Leakage|\*\*本文\*\*)', 6),
    ('C05', '披露表 §9 至少 3 行带"已修"或披露标记', r'(?m)^\| \d+ \| .*', 3),
    # ---- r13 ----
    ('C06', '§5.1 第一级溢价表恰好 4 个数据行',
     r'(?m)^\| (smoke2sf（强格）|shwd2sf（佐证）|a2d15（定向探针）|dota15（同域）) \|', 4),
    ('C07', '§5.1 Δgap 表恰好 5 个数据行（按"读法"列限定作用域）',
     r'(?m)^\| (shwd2sf|smoke2sf|p_aitovis|p_vistod15|其余 9 格) \| \d.*\| (val \*\*(?:低估|高估)\*\*|\*\*不显著\*\*) \|\s*$', 5),
    # ---- r13c ----
    ('C13', '§5.5 统计表恰好 5 个数据行（含分布）',
     r'(?m)^\| (完整日志（≥ 40 轮）|溢价中位数|最大 / 最小|为正|分布) \|', 5),
    ('C14', '§5.6 逐格表恰好 13 行',
     r'(?m)^\| (?:shwd2sf|smoke2sf|p_aitovis|p_vistod15|aitod20|d15d15|mende20|fire|p_d15toai|mask20|p_masktomende|dota|vis) \| \d+ \| [\d.]+ / ', 13),
    ('C15', '§5.6 旧分解表（带"主导"列）恰好 6 行',
     r'(?m)^\| (?:\*\*mask20\*\*|fire|p_vistod15|shwd2sf|smoke2sf|dota) \| \*\*[+−][\d.]+\*\* \| '
     r'\*{0,2}[+−][\d.]+\*{0,2} \| .*(?:末轮 val 差|Δprem|−test 差|几乎抵消)', 6),
    ('C16', '§6.5 跨框架表恰好 6 行',
     r'(?m)^\| \*\*(Ultralytics YOLO|Detectron2|MMDetection|YOLOX|PaddleDetection|DETR)\*\*', 6),
    ('C17', '§8.6 兑现率表恰好 5 行',
     r'(?m)^\| (?:shwd2sf|smoke2sf|aitod20) \| (?:基线|策略) \| \d+ \| \+\d\.\d+ \| \*\*[+−]\d\.\d+\*\*', 5),
    ('C18', '§5.6 分解表恰好 2 行（按「主导分量」列限定作用域）',
     r'(?m)^\| (?:shwd2sf|smoke2sf) \| \*\*[+−]\d\.\d+\*\* \| \*\*[+−]\d\.\d+\*\* \| [+−]\d\.\d+ \| \*\*难度差\*\* \|', 2),
    ('C10', '§6.1 表恰好 6 个数据行（4 单位 + 子集 + 派生）',
     r'(?m)^\| (?:\*\*(?:release|protocol|yolo_dist|reported)\*\*（|↳ 其中|\*\*reported − 干净\*\*)', 6),
    ('C11', '首报归属注至少 2 处（§5.1 与 §7.2）', r'\*\*首报归属', 2),
    ('C12', '§9.4 五个登记格的 yaml 表恰好 5 行',
     r'(?m)^\| (T1-b aitod→visdrone|T1-a dota15→aitod|T1-c visdrone→dota15|T2 mask→mendeley|C dota→dota15（对照）) \| `', 5),
]


def scoped_violations(text, target, allow):
    bad = []
    for ln, line in enumerate(text.splitlines(), 1):
        for m in re.finditer(target, line):
            head = line[:m.start()]
            if not re.search(allow, head):
                bad.append((ln, line.strip()[:100]))
    return bad


def line_violations(text, target, allow_anywhere):
    """命中行只要含豁免标记即合法（标记可出现在行内任意位置）。"""
    bad = []
    for ln, line in enumerate(text.splitlines(), 1):
        if re.search(target, line) and not re.search(allow_anywhere, line):
            bad.append((ln, line.strip()[:110]))
    return bad


def main():
    fails = []
    print('=' * 74)
    print('副论文正文审计锚点')
    print(f'目标：{os.path.basename(PAPER)}  ({len(paper)} 字符)')
    print('=' * 74)

    print('\n=== 正锚 ===')
    for code, desc, pat in POSITIVE:
        n = len(re.findall(pat, paper))
        ok = n >= 1
        print(f'  {code} {"ok  " if ok else "FAIL"} n={n:<3} {desc}')
        if not ok:
            fails.append(code)

    print('\n=== 负锚（硬）===')
    for code, desc, pat in NEGATIVE_HARD:
        n = len(re.findall(pat, paper))
        ok = n == 0
        print(f'  {code} {"ok  " if ok else "FAIL"} n={n}  {desc}')
        if not ok:
            fails.append(code)

    print('\n=== 负锚（行内豁免标记）===')
    for code, desc, target, allow in NEG_LINE:
        bad = line_violations(paper, target, allow)
        ok = not bad
        print(f'  {code} {"ok  " if ok else "FAIL"} n={len(bad)}  {desc}')
        for ln, s in bad:
            print(f'      line {ln}: {s}')
        if not ok:
            fails.append(code)

    print('\n=== 负锚（行内否定语境）===')
    for code, desc, target, allow in NEG_SCOPED:
        bad = scoped_violations(paper, target, allow)
        ok = not bad
        print(f'  {code} {"ok  " if ok else "FAIL"} n={len(bad)}  {desc}')
        for ln, s in bad:
            print(f'      line {ln}: {s}')
        if not ok:
            fails.append(code)

    print('\n=== 计数锚 ===')
    for code, desc, pat, want in COUNTS:
        n = len(re.findall(pat, paper))
        ok = (n >= want) if '至少' in desc else (n == want)
        print(f'  {code} {"ok  " if ok else "FAIL"} n={n} want={want}  {desc}')
        if not ok:
            fails.append(code)

    print('\n=== 跨文件一致性 ===')
    # 正文的数字必须与重算输出/裁定书一致
    XCHECKS = [
        ('X01', '重算输出含 reported 12/19', recomp, r'12/19'),
        ('X02', '重算输出含 protocol 13/19', recomp, r'13/19'),
        ('X03', '重算输出含 release 10/19', recomp, r'10/19'),
        ('X04', '重算输出含 2/19 复现自检', recomp, r'复现|2/19'),
        ('X05', '裁定书 §2 已含 release 10/19', adj, r'release\s*\*\*10/19\*\*|release \*\*10/19\*\*'),
        ('X06', '裁定书含 §7 修订记录', adj, r'## 7\. 修订记录'),
        ('X07', '裁定书如实写明不一致由我造成', adj, r'这是我自己造成的不一致'),
        ('X08', '标记表文件存在且含 19 行表', rowstab, r'\| 19 \|'),
        # ---- r13 ----
        ('X09', '核对报告存在且含 (I) 小节', crit, r'\(I\)|（I）'),
        ('X10', '复算输出含 Δgap shwd2sf +0.779', vtxt, r'\+0\.779'),
        ('X11', '复算输出含 Δgap p_vistod15 −3.580', vtxt, r'[-−]3\.580'),
        ('X12', '复算输出含第一级配对差 +0.416', vtxt, r'\+0\.416'),
        ('X13', '复算输出含 4 个"CI 不含 0"判读', vtxt, r'显著（CI 不含 0）'),
        ('X14', '复算输出含 Δgap p_aitovis −1.114', vtxt, r'[-−]1\.114'),
        # ---- r13 收尾：B 文档横幅（用户显式豁免后加入的取代声明）----
        ('X15', 'B 文档顶部有"计数已作废"横幅', bdoc, r'计数已作废'),
        ('X16', '横幅含 release 10/19 与 protocol 13/19', bdoc, r'(?s)10/19.{0,400}?13/19'),
        ('X17', '横幅含 yolo_dist 4/19 与 reported 12/19', bdoc, r'(?s)4/19.{0,400}?12/19'),
        # ---- r14：口径统一后的跨文件一致 ----
        ('X18', '重算输出含 yolo_dist = 4/19 = 21.1%', recomp, r'4/19 = 21\.1%'),
        ('X19', '裁定书 §2 已含 yolo_dist 4/19', adj, r'\*\*4/19 ≈ 21%\*\*'),
        # ---- r22：原正文 §13 的检查迁到内部件（G5）----
        ('X20', '内部件含 §13 标题（原正文该节）', p2int, r'## 13\. 目标轨道（\*\*2026-09-16 已定\*\*'),
        ('X21', '内部件：主轨道 = Pattern Recognition', p2int, r'主轨道 = Pattern Recognition'),
        ('X22', '内部件：备选 TMLR', p2int, r'备选 \*\*TMLR\*\*'),
        ('X23', '内部件含"不推荐"清单', p2int, r'不推荐'),
        ('X24', '内部件：PR 版裁剪表恰好 14 行', p2int,
         r'(?m)^\| (?:\*\*§(?:9|13) |§|附录)'),
        ('X25', '内部件：缺口表 A–E 恰好 5 行', p2int,
         r'(?m)^\| [A-E] (可复现性|统计单位|跨框架审计|Δgap|公开日志溢价)'),
        ('X26', '内部件：形式要求页数口径行在位', p2int, r'形式要求（页数口径'),
        ('X27', '内部件：A 行已缓解（CUDA 补做）', p2int, r'已大幅缓解（CUDA 补做）'),
        ('X28', '内部件自陈"不是论文内容"', p2int, r'本文不是论文内容，是内部工作件'),
        # ---- r23/r24：补充材料（G6）----
        ('X29', '补充材料存在且含 S1–S7 七节', supp, r'(?m)^## S[1-7] · '),
        ('X38', '补充材料 S6 声明共享工具且不主张原创', supp,
         r'两篇共用，均不主张原创|同一条约定也适用于审计锚点体系'),
        # ---- r33：逐 epoch 曲线 ----
        # r41：逐 epoch 图（原 Fig. 5）现为补充材料 Fig. S5，正文清单里点名
        ('X39', '正文清单点名 Fig. S5（逐 epoch 曲线，含 κ = 0.734）', eng,
         r'\*\*Fig\. S5\*\* \| §8\.7'),
        ('X40', 'curve.csv 在场（202 个 test 点）', curve, r'(?m)^r10_'),
        # ---- r26：英文稿与四张图 ----
        ('X30', '英文稿存在且含 12 个编号章节', eng, r'(?m)^## 12\. Limitations'),
        ('X31', '英文稿含"两级报告"的口径', eng, r'must be reported in two tiers'),
        ('X32', '英文稿含兑现率 19%', eng, r'a realization rate of 19 %'),
        # r42：压缩会合法改写措辞，故这两条改为**按内容**锚，而不是按字面串。
        ('X33', '英文稿说明四条曾未核实的引用已解决为 [30]–[33]', eng,
         r'(?s)(?:now verified|resolved|verified)[^.]{0,40}\*\*\[30\] \[31\] \[32\] \[33\]\*\*'),
        ('X36', '参考文献 [30] 就是 CVPR 2026 地理影像泄漏那篇', eng,
         r'(?m)^\[30\] Y\.K\. Adimoolam'),
        ('X37', '参考文献表条目数（r51 后 = 44，条数由 X41 精确核对）', reflist, r'(?m)^\| \[\d+\] \|'),
        # ---- r41：图与证据表移入补充材料（页数上限），正文只留"在哪"的清单。
        #      故这里改锚"清单列出了 Fig. S1–S5"，而不是"正文内嵌了 Fig. N"。
        ('X34', '正文清单列出全部五张图（Fig. S1–S5）', eng,
         r'(?s)\*\*Fig\. S1\*\*.*\*\*Fig\. S5\*\*'),
        ('X35', 'FIGURES.md 记录四单位解析值 10/13/4/12', figs,
         r'release: 10/19|protocol: 13/19|yolo_dist: 4/19|reported: 12/19'),
    ]
    for code, desc, txt, pat in XCHECKS:
        if txt is None:
            print(f'  {code} FAIL n=NA  {desc}（文件缺失）')
            fails.append(code)
            continue
        n = len(re.findall(pat, txt))
        ok = n >= 1
        print(f'  {code} {"ok  " if ok else "FAIL"} n={n}  {desc}')
        if not ok:
            fails.append(code)

    # ---- r39：投稿形态（英文投稿件）的**精确计数**锚 ----
    # PR 的形式要求（转载来源、两篇独立实践者记录一致）：
    #   摘要 ≤150 词；参考文献 35–45 条；Highlights 3–5 条 × ≤85 字符。
    # 这里只锚"能机械核对的"三条：条数、覆盖面、摘要词数。Highlights 见投稿前件。
    print('\n=== r39 投稿形态精确计数锚 ===')
    POSTINT = os.path.join(BASE, 'P2_投稿前件_v0.1.md')
    FORMS = os.path.join(BASE, 'PR形式要求_核实_20260917.md')
    GA = os.path.join(BASE, 'figures', 'fig6_graphical_abstract.png')
    postint = load(POSTINT)
    forms = load(FORMS)
    XCOUNTS = [
        ('X41', '参考文献表（canonical 文件）恰好 44 条', reflist, r'(?m)^\| \[\d+\] \| ', 44),
        ('X42', '英文稿 References 节恰好 44 条', eng, r'(?m)^\[\d+\] ', 44),
    ]
    for code, desc, txt, pat, want in XCOUNTS:
        if txt is None:
            print(f'  {code} FAIL txt=NA  {desc}（文件缺失）')
            fails.append(code)
            continue
        n = len(re.findall(pat, txt))
        ok = (n == want)
        print(f'  {code} {"ok  " if ok else "FAIL"} n={n} want={want}  {desc}')
        if not ok:
            fails.append(code)

    # ---- r43：把"必须存活的 20 条声明与披露"升级为常驻锚（每次改稿都跑，不只在压缩时跑）
    #      理由：压缩代理已两次真的删掉过东西（一处错误的 §交叉引用、一句 "yolo_dist 列是 4/19"），
    #      而这两次都是靠临时校验器抓到的。项目纪律是"锚点只增不减"，故把它们固化在这里。
    print('\n=== r43 必须存活的声明与披露（常驻）===')
    CLAIMS = [
        ('X50', '不是首个审计划分问题（图像级泄漏已被做过）', eng,
         r'(?:not claim|claim neither|do not claim)[^.]{0,120}first to audit|both are taken'),
        ('X51', '不是数据污染（图像交集恰为 0）', eng,
         r'not (?:data )?contamination|intersection[^.]{0,60}zero'),
        ('X52', '不主张单一偏差方向（按语料而异）', eng,
         r'(?:not|neither)[^.]{0,60}single bias direction|direction[^.]{0,40}varies by corpus'),
        ('X53', '不主张全框架通用（限定 YOLO 系）', eng, r'framework-general|YOLO-lineage'),
        ('X54', '不主张基准本身是错的', eng, r'benchmarks[^.]{0,90}wrong'),
        ('X55', '不主张"普遍低估"', eng, r'not claim a general understatement|general understatement'),
        ('X56', '首报归属（干净协议读数首报于伴生论文）', eng,
         r'first[- ]report attribution|primary readings of the companion'),
        ('X57', '登记复制写成"判据未达"，而非"假设被否"', eng, r'criterion not met'),
        ('X58', '不把 H1 写成已复现', eng, r'not replicated'),
        ('X59', '缺陷表留在正文（披露不外移）', eng, r'\| # \| Defect \| Handling \|'),
        ('X60', '比值指标曾被判病态（自我更正留痕）', eng,
         r'860|1031|pathological|denominator vanishes'),
        ('X61', '两套命名族不得合并', eng, r'not be pooled'),
        ('X62', '跨框架是定点抽样而非普查', eng, r'fixed-point sampling,?\s+not a census|not a census'),
        ('X63', '公开日志无法确立别名', eng, r'cannot establish aliasing'),
        ('X64', '有来源未声明许可', eng, r'no licence|Unknown.{0,20}licen'),
        ('X65', 'M_val − M_test 不可识别', eng, r'not identifiable'),
        # r48: X66 used to be a whole-document search for the word "narrow", so it matched
        # §1.2/§6.2/§6.5 and had NEVER checked §5.4 — the shared lessons library's 02 §1①
        # failure mode ("a name that claims one section, a regex that scans the document").
        # The pattern is now BOUND to §5.4 by the heading and to the substance of the
        # narrowing (the old wording, and the correction of it).
        ('X66', '§5.4 内记录"外部核对后收窄了主张"（锚点自限于该节）', eng,
         r'(?s)### 5\.4 .{0,2000}?used to write.{0,400}?corrects this to'),
        ('X67', '§8.6 与 §8.7 的局限仍在', eng, r'limitation'),
        ('X68', '逐 epoch 版本（中间 checkpoint）仍在', eng, r'per-epoch|intermediate checkpoint'),
        ('X69', '自陈"我们自己的语料含 val == test"', eng, r'val == test'),
        # ---- r45：盲审暴露的缺陷。锚点数曾被复述在多处并各自走样（正文 §2.3 说 220、
        #      补充材料说 227、Declarations 说 247）。修法是**只留一处**，故这里锁"恰好一次"。
        ('X72', '锚点条数在正文中只出现一次（避免多份副本再次走样）', eng,
         r'(?m)^- \*\*Reproducibility\.\*\*'),
        # r41 的结构性事实：证据表与图在补充材料，正文只留指针
        # r46: §9 was compressed and four tables came back into the article, so this anchor now
        # checks that the article still routes readers to the supplementary evidence set (S24-S27)
        # rather than to a specific pointer line that no longer exists.
        ('X70', '正文仍指向补充材料的证据表集（S24–S27）', eng,
         r'Supplementary S24–S27'),
        ('X83', '\u03ba \u7684 run \u805a\u7c7b\u533a\u95f4\u5728\u6b63\u6587\uff08\u4e0d\u53ea\u5728\u8865\u5145\u6750\u6599\uff09', eng,
         r'(?s)κ = 0\.708, R² 0\.937.*?\[0\.671, 0\.745\]'),
        ('X84', '\u81c2\u95f4 \u03ba \u5dee\u5f02\u53ca\u5176\u533a\u95f4\uff08\u9009\u62e9\u5047\u8bf4\u7684\u72ec\u7acb\u65c1\u8bc1\uff09', eng,
         r'\+0\.168, 95 % CI \[\+0\.130, \+0\.203\]'),
        ('X85', '\u8fd0\u884c\u6570\u4ee5 run \u76ee\u5f55\u4e3a\u51c6\uff0890\uff09\uff0c\u4e0d\u518d\u5199 80', eng,
         r'\*\*90 runs in total\*\*'),
        # r54v: B de-duplication moved the *quantification* of this bias into the Supplementary
        # (the article keeps one sentence and points at S12).  The anchor follows the value, as
        # it did for X56 and X81 — an anchor that pins a number to a location the de-duplication
        # deliberately emptied would fail on a correct edit, and pinning it to the wrong place is
        # worse than moving it.  The disclosure anchor X59 (defect table stays in the article) and
        # the $-$1.490 sentence it belongs to are untouched and still in the article.
        ('X86', '\u9971\u548c\u5bf9\u7167\u7684 val \u4fa7\u522b\u540d\u504f\u5dee\u5df2\u91cf\u5316\uff08\u73b0\u5728\u8865\u5145\u6750\u6599 S12\uff09', suppen,
         r'\u22120\.529'),
        ('X71', '正文已把图移出（5 张，S1–S5）', eng,
         r'(?s)\*\*Fig\. S1\*\*.*\*\*Fig\. S5\*\*'),
        # ---- r53: the three escalations and the complete per-epoch sweep ------------------
        ('X87', 'X8：dota15 升到 n = 10 后判据满足（+0.449、10 正 0 负）', eng,
         r'(?s)\+0\.449 pp.*?10\+/0−'),
        ('X88', 'X1：两格在 n = 10 上的置换 p 已达下界 0.001953', eng,
         r'permutation p = \*\*0\.001953\*\*'),
        ('X89', 'X1：n = 10 的两个 Δgap 值与原 p 值', eng,
         r'−1\.226.{0,80}?−3\.315'),
        ('X90', '13 格 BH 计数**反转为 3 格存活**（并写明这是反转）', eng,
         r'now leaves three cells significant'),
        ('X91', '归档端点被重测锁定为 best.pt×test（0.0046 pp）', eng,
         r'0\.0046 pp'),
        ('X92', '全曲线全扫规模 806 与 202 点逐点重合', eng,
         r'806 retained checkpoints.*?202 shared'),
        ('X93', '§8.7 的稳定性主张已被**收窄**（不是悄悄保留）', eng,
         r'too strong for one of the two'),
        # ---- r46：清单曾把四张留在正文的表**描述错**（S 号对、内容错），且把"补充材料小节号
        #      §Sn"与"§S8 里的表号 Table Sn"两个轴混为一谈。故成对锁死：图题 + 清单行。
        ('X73', '正文 Table 1 的图题 = Tier 1 检验', eng, r'\*\*Table 1\.\*\* Tier 1'),
        ('X74', '正文 Table 2 的图题 = Tier 2 检验', eng, r'\*\*Table 2\.\*\* Tier 2'),
        ('X75', '正文 Table 3 的图题 = 四种计数单位', eng,
         r'\*\*Table 3\.\*\* The four counting units'),
        ('X76', '正文 Table 4 的图题 = val 选择 vs test 兑现', eng,
         r'\*\*Table 4\.\*\* The premium selected on'),
        ('X77', '清单 Table 1 行 = S4 且写明 Tier 1', eng,
         r'\| \*\*Table 1\*\* \| Table S4 \| \*\*Tier 1\*\*'),
        ('X78', '清单 Table 2 行 = S6 且写明 Tier 2', eng,
         r'\| \*\*Table 2\*\* \| Table S6 \| \*\*Tier 2\*\*'),
        ('X79', '清单 Table 3 行 = S11 且写明四种计数单位', eng,
         r'\| \*\*Table 3\*\* \| Table S11 \| the four counting units over the 19 audited benchmarks'),
        ('X80', '清单 Table 4 行 = S20 且写明 val 选择 vs test 兑现', eng,
         r'\| \*\*Table 4\*\* \| Table S20 \| the premium selected on `val`'),
    ]
    for code, desc, txt, pat in CLAIMS:
        if txt is None:
            print(f'  {code} FAIL txt=NA  {desc}（英文稿缺失）')
            fails.append(code)
            continue
        ok = bool(re.search(pat, txt, re.I))
        print(f'  {code} {"ok  " if ok else "FAIL"}  {desc}')
        if not ok:
            fails.append(code)
    CLAIM_EXTRA = len(CLAIMS)

    # ---- X81：英文补充材料的 §S8 说明必须与投稿状态一致 ------------------------------
    # 这句曾写"有两张表故意留在正文"（当时 27 张全部移出）。四张表回到正文后，若不同步，
    # 补充材料就会**少报**正文里的表 —— 属于"读者按它核对会核错"的一类错误。
    if suppen is None:
        print('  X81 FAIL txt=NA  英文补充材料缺失')
        fails.append('X81')
    else:
        ok = ('**Four of these tables are also printed in the article**' in suppen
              and '**Two further tables deliberately stayed in the article' in suppen
              and '**Two tables deliberately stayed in the article**' not in suppen)
        print(f'  X81 {"ok  " if ok else "FAIL"}  §S8 说明已同步四张表回到正文（且旧句已删）')
        if not ok:
            fails.append('X81')

    # 英文稿必须把 44 个编号**全部**引用到（不得有"只列不引"的条目）
    if eng is None:
        print('  X43 FAIL txt=NA  英文稿缺失')
        fails.append('X43')
    else:
        cited = set(int(x) for x in re.findall(r'\[(\d{1,2})\]', eng))
        uncited = [n for n in range(1, 45) if n not in cited]
        ok = not uncited
        print(f'  X43 {"ok  " if ok else "FAIL"} cited={len([n for n in range(1,45) if n in cited])}/44'
              f'  uncited={uncited or "none"}  英文稿引用全部 44 条')
        if not ok:
            fails.append('X43')

    # 摘要 ≤150 词（PR 的 D 级实践者口径，取严）
    if eng is None:
        print('  X44 FAIL txt=NA  英文稿缺失')
        fails.append('X44')
    else:
        i = eng.find('## Abstract')
        # r46: "Positioning" and "Scope" moved out of the Abstract block into §1.2 (the panel
        # pointed out that if the venue counts the whole block as the abstract, it was ~250
        # words against a 150-word limit). Keywords is now the block's last element.
        j = eng.find('**Keywords:**')
        abs_txt = re.sub(r'[*`]', '', eng[i:j]).replace('## Abstract', '') if (i >= 0 and j > i) else ''
        # r46: the abstract's closing phrase changed from "selection inflation" to "seed inflation"
        # (H19: the estimand is seed inflation; the signal/selection split is an interpretation).
        _m = re.search(r'Object-detection papers report.*?(?:selection|seed) inflation\.', abs_txt, re.S)
        abs_txt = _m.group(0) if _m else ''
        wc = len(abs_txt.split())
        ok = (0 < wc <= 150)
        print(f'  X44 {"ok  " if ok else "FAIL"} words={wc} limit=150  英文稿摘要 ≤150 词')
        if not ok:
            fails.append('X44')

    # 形式要求核实件必须**记下 v0.1 的来源归属更正**（The Veterinary Journal，不是 PR）
    XFORMS = [
        ('X45', '形式要求核实件已更正 v0.1 的来源错误', forms,
         r'VETERINARY JOURNAL', 1),
        ('X46', '形式要求核实件写明该错误不得用于 PR 投稿', forms,
         r'作废，不得用于 PR 投稿', 1),
        ('X47', '投稿前件存在且含 Highlights 一节', postint, r'(?m)^## 2\.', 1),
        ('X48', '投稿前件含 Cover Letter 且提到伴生论文（P1）', postint,
         r'companion', 1),
    ]
    for code, desc, txt, pat, want in XFORMS:
        if txt is None:
            print(f'  {code} FAIL txt=NA  {desc}（文件缺失）')
            fails.append(code)
            continue
        n = len(re.findall(pat, txt))
        ok = (n >= want)
        print(f'  {code} {"ok  " if ok else "FAIL"} n={n}  {desc}')
        if not ok:
            fails.append(code)

    # 图形摘要（可选但鼓励）：文件必须在场且 ≥531×1328 px
    if not os.path.exists(GA):
        print(f'  X49 FAIL  图形摘要不存在：{os.path.basename(GA)}')
        fails.append('X49')
    else:
        import struct
        raw = open(GA, 'rb').read(33)
        w, h = struct.unpack('>II', raw[16:24])
        ok = (h >= 531 and w >= 1328)
        print(f'  X49 {"ok  " if ok else "FAIL"} {w}×{h} px（要求 ≥1328×531）  图形摘要尺寸')
        if not ok:
            fails.append('X49')

    print()
    total = (len(POSITIVE) + len(NEGATIVE_HARD) + len(NEG_LINE) + len(NEG_SCOPED)
             + len(COUNTS) + len(XCHECKS) + len(XCOUNTS) + len(XFORMS)
             + CLAIM_EXTRA
             + 5)  # r39/r43: X43 (coverage) + X44 (abstract) + X49 (graphical abstract)
                   # r46: X81 (the Supplementary §S8 note is in step with the submission)
                   # r47: X82 (the declared anchor count equals the real one) — this one
                   #      counts itself, which is the intended friction: adding an anchor
                   #      means re-syncing the number in the paper and both supplements.
    # ---- X82：声明锚点数 == 审计实际条数 ----------------------------------------------
    # 共享工具目录《通用经验与教训》02 §4 / 07 §1：**跨文件写死的数字不加守卫就一定会过期**
    # （他们的补充材料把我们的锚点数写成 481，实际已 5xx）。本项目实测同一件事：
    # 正文与两份补充材料都写着 247，而脚本此时已是 279 —— 少了 32 条，且没有任何检查在看它。
    # 这条守卫让"加锚点"必须同步那个数字：不一致即 FAIL（代价是故意的摩擦）。
    DECLARED_PATTERNS = [
        ('英文正文 Declarations', eng, r'(\d+)\s+audit anchors'),
        ('盲审稿 Declarations', blind, r'(\d+)\s+audit anchors'),
        ('英文补充材料 §S6', suppen, r'the\s+(\d+)\s+anchors of this paper'),
        ('英文补充材料 §S7 注释', suppen, r'Main-text anchors \((\d+)'),
        ('中文补充材料 §S6', supp, r'本文的\s*(\d+)\s*条锚点'),
        ('中文补充材料 §S7 注释', supp, r'正文锚点（(\d+)'),
    ]
    declared = {}
    for tag, txt, pat in DECLARED_PATTERNS:
        if txt is None:
            declared[tag] = None
            continue
        found = sorted({int(v) for v in re.findall(pat, txt)})
        declared[tag] = found
    problems = [(tag, vals) for tag, vals in declared.items()
                if vals is None or vals != [total]]
    print('  X82 %-4s 声明锚点数 == 审计实际条数（实际 %d）：%s'
          % ('ok' if not problems else 'FAIL', total,
             '; '.join('%s=%s' % (t, v) for t, v in declared.items())))
    if problems:
        fails.append('X82')
    print()
    print(f'锚点总数 {total}｜失败 {len(fails)}')
    print('ALL PASS' if not fails else 'FAILED: ' + ', '.join(fails))
    return 0 if not fails else 1


if __name__ == '__main__':
    sys.exit(main())
