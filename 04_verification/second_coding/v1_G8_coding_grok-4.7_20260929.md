ROW 1 | COCO | release=yes | protocol=no | yolo_dist=yes | reported=yes | reason: COCO 2017 官方发布的 train/val/test-dev 彼此分离，test-dev 标注不公开且须交服务器；通用包 coco.yaml 的 test 指向 test-dev2017、与 val2017 不同；官方榜单数字来自与 val 选点独立的 test-dev。
ROW 2 | PASCAL VOC | release=yes | protocol=yes | yolo_dist=no | reported=yes | reason: 以 VOC2007 为准：官方 ImageSets 中 test 与 train/val 分离且测试标注已公开、可本地评；镜像 VOC.yaml 的 val 与 test 都指向 images/test2007；官方挑战报告的是独立 test。
ROW 3 | Objects365 | release=yes | protocol=no | yolo_dist=unknown | reported=unknown | reason: 官方切分含与 train/val 不同的测试集，但测试标注不公开、须交服务器；Ultralytics Objects365.yaml 无可用 test 键；论文主表与挑战榜是否同一半无法确定。
ROW 4 | Open Images v7 | release=yes | protocol=no | yolo_dist=yes | reported=yes | reason: 官方 facts 页有独立 test，检测框标注不公开、挑战须交服务器；镜像 yaml 的 test 与 val 分目录；官方挑战榜单报告的是与 val 独立的 test。
ROW 5 | DOTA v1.0 | release=yes | protocol=no | yolo_dist=yes | reported=yes | reason: 官方下载含独立 test，标注扣留且须服务器评测；DOTAv1.yaml 的 test 与 val 分目录；官方论文与榜单报告的是与 val 选点独立的 test。
ROW 6 | DOTA v2.0 | release=yes | protocol=no | yolo_dist=unknown | reported=yes | reason: 官方 v2.0 有独立 test-dev/test-challenge 且须服务器评测；通用 YOLO 发行包无 DOTA v2 YAML；官方榜单数字来自与 val 独立的测试集。
ROW 7 | VisDrone-DET | release=yes | protocol=no | yolo_dist=yes | reported=yes | reason: 官方 test-challenge 与 train/val 分离，标注扣留且须交服务器；镜像 yaml 的 test 指向 test-dev、与 val 不同；官方榜单报告的是独立的 test-challenge。
ROW 8 | AI-TOD | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 官方 README 对发布切分有两条互相矛盾的陈述，划分不可判；通用 YOLO 包无对应 YAML；官方报告数字所依切分因此也无法确定。
ROW 9 | UAVDT | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 证据仅限官方论文与两份未被进一步核验的镜像，发布件结构、能否本地评、以及报告数字是否独立于选点均无法确定；通用包无 YAML。
ROW 10 | xView | release=yes | protocol=no | yolo_dist=unknown | reported=yes | reason: 官方挑战测试集与训练发布件分离，标注不公开、由组织方计分；镜像 xView.yaml 无可用独立 test 键（val 为训练集 autosplit）；官方榜单数字来自扣留测试集。
ROW 11 | DIOR | release=yes | protocol=yes | yolo_dist=unknown | reported=yes | reason: 官方描述含与 train/val 不同且标注公开的 test，可本地评；通用 YOLO 包无 DIOR/DIOR-R YAML；官方论文报告的是与 val 独立的 test。
ROW 12 | NWPU VHR-10 | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: TorchGeo 的官方切分是 positive/negative，不是检测用的 train/val/test 留出；协议未声明评测切分，通用包无 YAML，也无官方榜单口径。
ROW 13 | SHWD | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 不能确定官方 README 是否给出与选点独立的 test；Reflective_vests.yaml 也不是通用 YOLO 发行包中可判定的独立测试配置，官方报告口径不可考。
ROW 14 | SFCHD | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 仅知存在第一方发布，无法确定其切分结构、能否本地评测、通用包是否含 YAML，以及官方报告数字来自哪一半。
ROW 15 | MAFA | release=yes | protocol=yes | yolo_dist=unknown | reported=unknown | reason: CVPR 论文与发布件给出标注公开的独立 test，可本地评；通用 YOLO 包无 YAML；论文未说明检查点选择是否使用了报告所用的 test。
ROW 16 | Mendeley face-mask | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 官方数据记录没有可判定的检测留出协议，镜像只是生成器而非通用包中的独立 test 键；也没有可考的官方榜单数字。
ROW 17 | WIDER FACE | release=yes | protocol=no | yolo_dist=unknown | reported=yes | reason: 官方站点将 test 与 train/val 分开且明确不发布 test GT、须交服务器；通用 YOLO 包无 YAML；官方榜单报告的是与 val 选点独立的 test。
ROW 18 | CrowdHuman | release=yes | protocol=no | yolo_dist=unknown | reported=unknown | reason: 官方发布含独立 test 且测试标注不公开、不能本地评；通用包无 YAML；论文主结果在 val 而挑战榜在 test，报告口径无法确定。
ROW 19 | D-Fire (FireSmoke) | release=yes | protocol=yes | yolo_dist=unknown | reported=unknown | reason: 官方 README 给出标注公开、可本地评的 train/test 留出；通用 YOLO 包无该 YAML；未见与检查点选择相互独立的官方报告口径。

标识: grok-4.7
盲法声明: 联网：否；读过其它编码者的材料：否

歧义（规则仍有两种读法）：
ROW 2 的 protocol：若以 VOC2007（镜像 VOC.yaml 实际指向的 test2007，标注已公开）为准，protocol=yes；若以 VOC2012 挑战协议为准，protocol=no。release 两种读法都是 yes，reported 都是 yes。
ROW 3 的 release/protocol：按规则 1（测试集存在但标注扣留）为 release=yes、protocol=no；若认定公开下载件只有 train/val、测试只在服务器上，规则 3 则把 release 与 protocol 都改成 unknown。yolo_dist 两种读法都是 unknown。
ROW 7 的 protocol：若“官方协议的那个测试”指 test-challenge，protocol=no；若指可本地评的 test-dev，protocol=yes。yolo_dist 不受影响，仍是 yes（yaml 指向 test-dev，且与 val 不同）。
ROW 10 的 yolo_dist：test 键缺失或为空则为 unknown（本次采用）；若镜像把 test 字面别名到 autosplit val，则为 no。
ROW 18 的 reported：以官方论文主表（val）为准则为 no；以挑战榜（扣留 test）为准则为 yes。本次因规则 2 同时点名二者且二者不一致，记 unknown。
ROW 15 与 ROW 19 的 reported：若“报告数字来自与训练集不同的留出 test”即算独立，则为 yes；若必须确认检查点选择没有用报告的那一半、而论文未写选点切分，则为 unknown（本次采用）。
