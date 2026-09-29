# G8 独立编码 v2（19×4）

标识：grok-4.7
联网：否
读过其它编码者的材料：否（只读了任务书 `03_任务v2_19x4盲编_给编码者.md` 与空白表 `01_空白编码表_19x4_给编码者.md`；曾看到同目录文件名，未打开、未读内容）
取值按 v2 五值，不按空白表里过时的 yes/no/unknown。

ROW 1 | COCO | release=independent | protocol=gated | yolo_dist=independent | reported=alias | reason: 官方 train2017/val2017/test2017 是三个不同图像集（只看结构），test-dev 协议要交服务器且标注扣留；镜像 yaml 的 test 与 val 指向不同文件；代码库和社区互引的数是 val2017，不是榜单上的 test-dev。
ROW 2 | PASCAL VOC | release=independent | protocol=independent | yolo_dist=alias | reported=alias | reason: 被引数锚在 VOC2007（2012 的 test 协议是 gated，不是这个数的版本）；2007 的 train/val/test 分集且 test 可本地评，但镜像 VOC.yaml 的 val 与 test 都指向 test2007，印出来的数就在选点那一半上。
ROW 3 | Objects365 | release=independent | protocol=gated | yolo_dist=absent | reported=alias | reason: 锚在 Ultralytics 文档和镜像 yaml 对应的公开版：train/val 分目录，另有独立 test 图像集但官方测试要交服务器；该 yaml 没有可用 test 键，文档和代码库印出的数是 val。
ROW 4 | Open Images v7 | release=independent | protocol=gated | yolo_dist=unknown | reported=unknown | reason: facts 页上 train/validation/test 是不同图像集，test 标注不公开、评测走服务器；镜像 yaml 的键指向，以及论文和社区互引的那个数在哪一半，指针都不够判。
ROW 5 | DOTA v1.0 | release=independent | protocol=gated | yolo_dist=independent | reported=unknown | reason: v1.0 的 train/val/test 分目录，test 标注扣留、协议要交服务器；DOTAv1.yaml 的 test 与 val 不同目录；论文榜单数和代码库 val 数并存，被引数在哪一半不能定。
ROW 6 | DOTA v2.0 | release=independent | protocol=gated | yolo_dist=unknown | reported=unknown | reason: v2.0 的 train/val/test-dev/test 分目录发布，测试协议要交服务器；指针只到文档、没有发行包 yaml 的键，论文榜和本地 val 哪个是被引数也不足判定。
ROW 7 | VisDrone-DET | release=independent | protocol=gated | yolo_dist=independent | reported=unknown | reason: 官方 train/val/test-dev/test-challenge 分目录，排名协议的测试要交服务器；镜像把 test 指到 test-dev、与 val 不同；论文挑战数和仓库 val 数并存，被引数在哪一半不足判定。
ROW 8 | AI-TOD | release=unknown | protocol=unknown | yolo_dist=absent | reported=unknown | reason: 官方 README 有两处互相矛盾的发布声明，release 和 protocol 都不能判；通用 YOLO 发行包没有该基准 YAML，被引数在哪一半也不可考。
ROW 9 | UAVDT | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 指针写明除官方论文和两处镜像外，审计视为未经验证，四层都不足判定，不能把「有镜像」写成 alias 或 independent。
ROW 10 | xView | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 指针只点名 mirror xView.yaml，没给出两键是否同指、发布件有没有独立 test、被引数在哪一半。
ROW 11 | DIOR | release=independent | protocol=independent | yolo_dist=unknown | reported=independent | reason: 锚在 DIOR（水平框）官方 train/val/test 分集、标注可本地评，互引数来自该 test 而不是选点用的 val；官方描述无计数不改变结构；镜像是 DIOR-R yaml，键指向未给出。
ROW 12 | NWPU VHR-10 | release=absent | protocol=absent | yolo_dist=absent | reported=unknown | reason: TorchGeo 的切分是正样本/负样本，不是留出测试；协议和通用 YOLO 包都没有这一层；论文自定义切分上的数在哪一半不可考。
ROW 13 | SHWD | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 指针只有官方 README 和名为 Reflective_vests.yaml 的镜像，没给出官方切分或两键是否同指。
ROW 14 | SFCHD | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 只知道有第一方发布和机器比对脚本 `_ev_sfchd_check2.py`，脚本结论和切分结构都没给出；有发布件，所以不是 absent。
ROW 15 | MAFA | release=independent | protocol=independent | yolo_dist=absent | reported=unknown | reason: 锚在 CVPR 论文的官方 train/test 两套不同集、标注可本地评，且没有单独 val；通用 YOLO 包没有该 YAML；被引的 test 数是不是选点那一半，PDF 指针没写明。
ROW 16 | Mendeley face-mask | release=absent | protocol=absent | yolo_dist=unknown | reported=unknown | reason: 官方数据记录没有切分件，协议也没声明测试；镜像是生成器而不是已解析的 yaml，生成结果有没有独立 test、被引数在哪一半，都不足判定。
ROW 17 | WIDER FACE | release=independent | protocol=gated | yolo_dist=unknown | reported=unknown | reason: 官方 train/val/test 图像分目录，指针已写明 test GT 未发布，所以协议不能本地评；按「只看结构」release 仍是独立；镜像键未给出，本地互引的 val 数和论文 test 榜数并存。
ROW 18 | CrowdHuman | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 指针是官方论文加镜像，没写明 test 是否独立目录、标注是否扣留、yaml 两键是否同指。
ROW 19 | D-Fire (FireSmoke) | release=unknown | protocol=unknown | yolo_dist=unknown | reported=unknown | reason: 指针只有 Official README，切分结构和被引数所在半都没给出。

## 规则仍有歧义之处

1. release 的两种读法。我按示例 X1：三个不同目录就是 independent，交服务器只记在 protocol。若按表里「发布了 test 但要交服务器」把 release 记成 gated，则 COCO、Objects365、Open Images v7、DOTA v1.0、DOTA v2.0、WIDER FACE 的 release 会从 independent 改成 gated。VisDrone 因为另有可本地评的 test-dev，两种读法我都仍记 independent；只有把「主测试=挑战服务器」硬套到 release 上，才会变成 gated。
2. yolo_dist 的「拿到独立测试」。我按「配置解析到与 val 不同的 test」记 independent，所以 COCO、DOTA v1.0、VisDrone 是 independent，即使不能本地打分。若还必须能本地打分，这三行会改成 gated。
3. reported 不取服务器榜、取印出来被引用的那个数。COCO、Objects365、VOC2007 因此是 alias。若改取论文里的服务器 test 数，COCO 和 Objects365 会变成 independent；VOC 若锚在「2007 官方 test 相对单独的 val 是真留出」也会变成 independent，那就是 v1 里多数人的读法。DOTA、VisDrone、WIDER 是论文榜和仓库 val 并存，所以我记 unknown：只取仓库 val 则是 alias，只取论文 test 榜则是 independent。
4. 版本。VOC 这一行按 2007；2012 的 protocol 会是 gated。DIOR 这一行按水平框官方 test；若被引数来自 DIOR-R，且该 yaml 把 val 和 test 指到同一处，则 yolo_dist 会是 alias，reported 也可能改成 alias。
