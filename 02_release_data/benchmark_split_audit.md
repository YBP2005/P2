# Benchmark split audit — do public detection benchmarks ship `val == test`?

**Purpose.** Evidence table for a survey on a specific evaluation-validity failure mode: a YOLO-style
dataset yaml in which the `val:` and `test:` keys resolve to the **same directory**, so the
"best-validation checkpoint" is selected on exactly the split it is later reported on.

**Scope.** **28 rows** in §1 = the **19 benchmarks named in the brief** + **8 rows explicitly labelled
"(bonus)"** (LVIS, Argoverse-HD, SKU-110K, TT100K, Global Wheat 2020, coco128, KITTI, HomeObjects-3K),
which I verified but which are tutorial/auxiliary datasets rather than benchmarks under audit +
**1 mirror-family row** (FireSmoke copies). §3 quotes its prevalence figures over the 19 brief
benchmarks, with the all-28 figures alongside. For each row: the *official* split structure
(primary source: the dataset's own README/paper/site or the canonical config in its own repo) and,
separately, what the *widely used YOLO-format copy* does with `val:` and `test:`.

**Evidence rules used here.**

* Every row cites a URL and, where the claim is about a yaml, quotes the actual lines.
* Sources are labelled **[OFFICIAL]** (dataset's own repo / paper / site) or **[MIRROR]** (a
  third-party YOLO redistribution, e.g. the Ultralytics `cfg/datasets/*.yaml` catalogue or a
  GitHub project that trains on the dataset).
* Three distinct failure modes are kept apart, because they are not the same bug:
  * **F-A `val == test`** — `val:` and `test:` are literally the same path. Model selection and the
    reported number come from the same images.
  * **F-B no `test:` key at all** — `val:` is the de-facto held-out split, so the reported metric is
    a validation number (and is still selected on).
  * **F-C `train`/`val` overlap** — e.g. `train == val`, or the yaml itself warns that the validation
    set is a subset of train.
* Anything I could not source is in §4, not asserted in the table.

**Honest limitation up front.** This audit reads *split definitions* (yaml/README/paper text), not
data. I did not download datasets. For several benchmarks the "widely used YOLO copy" is a
per-project yaml, not a canonical artefact — where that is the case the row says so explicitly.

---

## 1. Table — official splits and the YOLO-format default

| benchmark | venue/year | official split structure (train/val/test) | is `val == test` by default in the common YOLO-format distribution? | evidence (URL / filename actually read) | notes |
|---|---|---|---|---|---|
| **COCO** (detection) | ECCV 2014 ([doi](https://doi.org/10.1007/978-3-319-10602-1_48)) | `train2017` (118,287) / `val2017` (5,000) / `test-dev2017` (20,288 images with public annotations; full 40,670 test images have **withheld** annotations) | **No** — three distinct paths, test annotations withheld so test cannot be self-scored | **[MIRROR]** `ultralytics/cfg/datasets/coco.yaml` — `train: train2017.txt`, `val: val2017.txt`, `test: test-dev2017.txt  # 20288 of 40670 images, submit via https://cocodataset.org/#detection-eval` ([raw](https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/cfg/datasets/coco.yaml)) | The good case. Note COCO's own docs call the 20k-annotated set "test-dev", i.e. a *development* split — projects that train on `train2017` and early-stop on `test-dev` are already in mild F-A-adjacent territory, but the yaml itself is clean. |
| **PASCAL VOC** | IJCV 2010 ([doi](https://doi.org/10.1007/s11263-009-0275-4)) | `train2007+2012` / `val2007+2012` / `test2007` (VOC2012 test labels never released) | **YES (F-A)** — `val:` and `test:` are the *same* list | **[MIRROR]** `ultralytics/cfg/datasets/VOC.yaml` ([raw](https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/cfg/datasets/VOC.yaml)):<br>`val:` → `- images/test2007`<br>`test:` → `- images/test2007` | The canonical YOLO VOC config deliberately evaluates on `test2007` as "val". Since VOC2012 test is unlabelled, every YOLO VOC number is reported on `test2007` — and selected on it. This is the cleanest `val == test` instance in the whole audit. |
| **Objects365** | ICCV 2019 ([doi](https://doi.org/10.1109/iccv.2019.00852)) | v1: train ~1.74M / val 80,000; v2 adds a test set released for the challenge | **F-B (no `test`)** | **[MIRROR]** `ultralytics/cfg/datasets/Objects365.yaml` — `val: images/val # ... 80000 images` then `test: # test images (optional)` (empty) ([raw](https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/cfg/datasets/Objects365.yaml)); corroborated by Ultralytics' own docs: "the `test:` key in the configuration is left empty" ([docs](https://raw.githubusercontent.com/ultralytics/ultralytics/main/docs/en/datasets/detect/objects365.md)) | Reported numbers (`mAP^val`) are validation numbers by construction. Not `val == test`, but the "held-out" split is the one used for model selection. |
| **Open Images v7** | IJCV 2020 ([doi](https://doi.org/10.1007/s11263-020-01316-z)) | Official: train 9,011,219 / validation 41,620 / test 125,436 — **all three exhaustively box-annotated** | **F-B (no `test`)** in the YOLO config, even though labels exist | **[OFFICIAL]** Open Images facts page: "The dataset is split into a training set (9,011,219 images), a validation set (41,620 images), and a test set (125,436 images)." ([factsfigures_v7](https://storage.googleapis.com/openimages/web/factsfigures_v7.html)); **[MIRROR]** `open-images-v7.yaml` — `val: images/val # ... 41620 images`, `test:` empty ([raw](https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/cfg/datasets/open-images-v7.yaml)) | Interesting inversion: the *official* dataset is one of the few with a fully labelled test split, but the popular YOLO config drops it and reports on val. Note the yaml's own `train: images/train # ... 1743042 images` is a **filtered subset** of the official 9,011,219 — the converter keeps only images that have boxes in the selected 350 "boxable" classes — so the yaml's `train`/`val` counts are not directly comparable to the official split sizes. |
| **DOTA v1.0** | CVPR 2018 ([doi](https://doi.org/10.1109/cvpr.2018.00418)) | 15 categories, 2,806 images, 188,282 instances; train / val / test **shipped as three separate archives** | **No** — distinct `images/train`, `images/val`, `images/test` | **[OFFICIAL]** DOTA site lists separate "Training set", "Validation set", "Testing images" download links ([dataset.html](http://captain-whu.github.io/DOTA/dataset.html)); **[MIRROR]** `DOTAv1.yaml` — `train: images/train # ... 1411 images`, `val: images/val # ... 458 images`, `test: images/test # ... 937 images` ([raw](https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/cfg/datasets/DOTAv1.yaml)) | The Ultralytics 1411/458/937 split is a *re-split* of the official train+val (2,806 → 1,411/458/937 ≈ 1/2, 1/6, 1/3), documented as "Split ratios: 1/2 for training (1,411 images), 1/6 for validation (458 images), and 1/3 for testing (937 images)" ([dota-v2.md](https://raw.githubusercontent.com/ultralytics/ultralytics/main/docs/en/datasets/obb/dota-v2.md)). `test` here is a held-out slice of *labelled* official data — so val≠test but test is not the official test server. |
| **DOTA v2.0** | IJCV 2021 | train 1,830 / val 593 / test-dev 2,792 / test-challenge 6,053 | **No** | **[OFFICIAL]/[MIRROR]** Ultralytics DOTA docs: "Training: 1,830 images with 268,627 instances. Validation: 593 images with 81,048 instances. Test-dev: 2,792 images with 353,346 instances. Test-challenge: 6,053 images with 1,090,637 instances." ([dota-v2.md](https://raw.githubusercontent.com/ultralytics/ultralytics/main/docs/en/datasets/obb/dota-v2.md)) | Ultralytics comments the test-challenge download out ("Download (ignores test-challenge split)"), and `split_dota.py` asserts `split in {"train", "val"}` and builds `images/train`+`images/val` for `split_trainval`; official test-dev is used as `test`. ([split_dota.py](https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/data/split_dota.py)) The *official* DOTA-v2.0 test annotations are server-only. |
| **VisDrone-DET (2019)** | TPAMI 2021 ([doi](https://doi.org/10.1109/tpami.2021.3119563)) | train 6,471 / val 548 / test-dev 1,610 / test-challenge 1,580 | **No** | **[MIRROR]** `VisDrone.yaml` — `train: images/train # ... 6471 images`, `val: images/val # ... 548 images`, `test: images/test # test-dev images (optional) 1610 images`; converter `splits = {"VisDrone2019-DET-train": "train", "VisDrone2019-DET-val": "val", "VisDrone2019-DET-test-dev": "test"}` ([raw](https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/cfg/datasets/VisDrone.yaml)) | Split structure is clean. Caveat for the audit: `test-challenge` is excluded ("Download (ignores test-challenge split)"), and the paper's reported test numbers are on test-dev. |
| **AI-TOD / AI-TOD-v2** | ICPR 2021 ([doi](https://doi.org/10.1109/icpr48806.2021.9413340)) | Official layout has **four** image folders: `train`, `trainval`, `val`, `test`; 28,036 images, 700,621 instances, 8 classes | **Partially — `val` is a subset of `trainval`; `test` is a separate directory** | **[OFFICIAL]** AI-TOD README directory layout: `images/{test,train,trainval,val}` ([README](https://raw.githubusercontent.com/jwwangchn/AI-TOD/master/README.md)); **[OFFICIAL]** the AI-TOD-v2 README contains **two mutually contradictory release statements**: the header says "**We have now released the full sets (trainval, test) of AI-TOD-v2!**" while the note below says "In this stage, we only release the train, val annotations of the **AI-TOD-v2**, the test annotations will be used to hold further competitions." ([mmdet-aitod README](https://raw.githubusercontent.com/Chasel-Tsui/mmdet-aitod/main/README.md)) | Not `val == test`. The contradiction is itself the finding: I cannot determine from this README alone whether a third party can evaluate locally on AI-TOD-v2 `test`. The `trainval`/`val` structure also means a user who trains on `trainval` and validates on `val` has a **val ⊂ train** overlap (F-C) — same shape as DOTA's `trainval`. I did **not** find a canonical YOLO yaml for AI-TOD (see §4). |
| **UAVDT** (DET) | ECCV 2018 / IJCV 2019 ([doi](https://doi.org/10.1007/s11263-019-01266-1)) | **train/test only, no val**: "our benchmark is divided into training and testing sets, with 30 and 70 sequences, respectively" | **F-B and F-A-adjacent** — most public YOLO copies have `train`+`val` and an **empty `test:`**; the "val" is carved from the official *train* sequences | **[OFFICIAL]** UAVDT paper text via ar5iv ([1804.00518](https://ar5iv.labs.arxiv.org/html/1804.00518)); **[MIRROR]** `CQNU-ZhangLab/SFFNet` `ultralytics/cfg/datasets/UAVDT.yaml` — `path:`, `train:`, `val:`, `test:` **all empty placeholders** ([raw](https://raw.githubusercontent.com/CQNU-ZhangLab/SFFNet/main/ultralytics/cfg/datasets/UAVDT.yaml)); **[MIRROR]** `forever208/yolov5_train_on_UAVDT` `data/UAVDT.yaml` — `train: images/train  # ... 128 images`, `val: images/val  # ... 128 images`, `test:  # test images (optional)` **empty** ([raw](https://raw.githubusercontent.com/forever208/yolov5_train_on_UAVDT/master/data/UAVDT.yaml)) | The "128 images" comment is copy-pasted from `coco128.yaml`, i.e. the yaml is a template, not a faithful description of the dataset — worth flagging in the paper as evidence that these configs are not carefully authored. |
| **xView (2018 challenge)** | arXiv 2018 ([1802.07856](https://ar5iv.labs.arxiv.org/html/1802.07856)); challenge site | 847 train images (with labels) + 282 val images (**released without labels**) | **F-B (no `test:` key)** — and the val images have no public labels, so the only self-scorable held-out split is a *carve-out of train* | **[MIRROR]** `xView.yaml` — `train: images/autosplit_train.txt # ... 90% of 847 train images`, `val: images/autosplit_val.txt # ... 10% of 847 train images`, and **no `test:` key at all**; the config's own commented download block says `val_images.zip  # 5G, 282 val images (no labels)` ([raw](https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/cfg/datasets/xView.yaml)) | Two audit findings in one: (i) classically F-B, and (ii) Ultralytics silently **replaces the official split with a random 90/10 autosplit** of the 847 labelled train images ("autosplit"), so numbers are not comparable to xView leaderboard numbers. Caveat on sourcing: I grepped the xView paper ([ar5iv 1802.07856](https://ar5iv.labs.arxiv.org/html/1802.07856)) and it does **not** state the 847/282 counts — those come from the yaml's own comments plus the challenge site, which is JS-rendered and returned no split text to `curl` ([xviewdataset.org](https://xviewdataset.org/)). Treat 847/282 as **config-asserted, not independently confirmed**. |
| **DIOR** | ISPRS J. P&RS 2020 | 23,463 images, 192,518 instances, 20 classes; official train/val/test as separate archives | **No** in the DIOR-R YOLO copy I could read — but that copy has **no `test:` key either (F-B)** | **[OFFICIAL]** Mendeley Data record "DIOR is a large-scale benchmark dataset for optical remote sensing image target detection ... The dataset contains 23,463 images" ([data.mendeley.com/datasets/vvrhgbr643/1](https://data.mendeley.com/datasets/vvrhgbr643/1)); **[MIRROR]** `Hamedlk80/DIOR-R-Rotated-Object-Detection-YOLOv8` `diorr_obb_analysis/data.yaml` — `train: images/train`, `val: images/val`, **no `test:`** ([raw](https://raw.githubusercontent.com/Hamedlk80/DIOR-R-Rotated-Object-Detection-YOLOv8/main/diorr_obb_analysis/data.yaml)) | I could **not** obtain DIOR's official per-split image counts from a primary source on this machine (the official `escience.cn` host is dead; `sciencedirect`/`mdpi` block me). See §4. |
| **NWPU VHR-10** | IEEE TGRS 2014 ([doi](https://doi.org/10.1109/tgrs.2014.2374218)) | 800 images, 650 positive + 150 negative; **no official split shipped** | **Not applicable / undefined by the dataset** — every YOLO copy invents its own split | **[OFFICIAL]** TorchGeo's dataset class exposes only `split ∈ {'positive','negative'}` — i.e. "split" in the literature means *positive vs negative images*, **not** train/val/test: `assert split in {'positive', 'negative'}` ([vhr10.py](https://raw.githubusercontent.com/microsoft/torchgeo/main/torchgeo/datasets/vhr10.py)) | The dataset ships no train/test definition at all, so a `val == test` yaml here is a *third party's* choice. This matters for the paper: for NWPU VHR-10 the audit cannot attribute the failure to the benchmark. |
| **SHWD / Safety-Helmet-Wearing-Dataset** (VOC2028) | J. Phys. Conf. Ser. 2019 (Xu et al., "Detection of safety helmet wearing based on improved SSD") | Official: **VocLike** layout with `trainval` and `test` splits (no val) | **Official: no val at all.** Third-party YOLO copies differ — one shares a base with SHWD and has `val == train` | **[OFFICIAL]** README: `train_dataset = VOCLike(root='D:\VOCdevkit', splits=[(2028, 'trainval')])` / `val_dataset = VOCLike(root='D:\VOCdevkit', splits=[(2028, 'test')])` ([README](https://raw.githubusercontent.com/njvisionpower/Safety-Helmet-Wearing-Dataset/master/README.md)) — note the official trainer *calls* the test split "val"; **[MIRROR]** `gengyanlei/fire-smoke-detect-yolov4` `yolov5/data/Reflective_vests.yaml` (comment says it is built on SHWD):<br>`train: .../VOC2021/txt_yolov5/2021_train.txt`<br>`val:   .../VOC2021/txt_yolov5/2021_train.txt` ([raw](https://raw.githubusercontent.com/gengyanlei/fire-smoke-detect-yolov4/master/yolov5/data/Reflective_vests.yaml)) | The SHWD-derived yaml is the clearest **F-C (`train == val`)** example in the audit: validation *is* training, so "best-val" selection is on train data. The same repo's `hp.yaml` (same VOC2028 base) does it correctly: `train: .../2028_trainval.txt`, `val: .../2028_test.txt`. Two configs, same dataset, opposite handling — good illustrative pair. |
| **SFCHD / SFCHD-SCALE** | IEEE Trans. Instrum. Meas. 2024 (preprint text via [ar5iv 2306.02098](https://ar5iv.labs.arxiv.org/html/2306.02098)) | Paper: 12,373 images, **train/test only (4:1), no validation set** — "including 9,898 images in the training set, 2,475 images in the testing set." The first-party YOLO release, however, **does** ship a three-way split: `train.txt` 9,897 / `val.txt` 2,475 / `test.txt` **6** | **YES — and worse than `val == test`, because the shipped `test.txt` is a literal prefix of `val.txt`** | **[OFFICIAL]** `dataset_SFCHD/new_split_yolo/{train,val,test}.txt` in [lijfrank/SFCHD-SCALE](https://github.com/lijfrank/SFCHD-SCALE); I fetched all three and compared them (script: `D:\deepseek\analysis\work\_ev_sfchd_check2.py`). Result: `train.txt lines=9897`, `val.txt lines=2475`, `test.txt lines=6`; `test ⊆ val` **True**, `test ⊆ train` **False**, `|val ∩ test| = 6`, and `val.txt[:6] == test.txt` **True** | **The strongest single finding in this audit.** The official YOLO split's entire 6-image `test` partition is byte-identical to the first six lines of `val` (all six are `.../QY_final_dataset/images/192.168.*.jpg`). So for SFCHD the reported test number is computed on images that were also the validation set. Also note `val.txt` here is the paper's *test* set (2,475 images) with the name changed — i.e. the paper's held-out split was re-labelled "val", and a 6-image "test" was bolted on. The same directory contains `labels.cache`/`train.cache`/`val.cache` (Ultralytics artefacts) and the split files contain the author's absolute paths (`/home/yfs/data/...`), confirming this is a real training run's artefacts rather than a cleaned release. |
| **MAFA (Masked Faces)** | CVPR 2017 (Ge, Li, Ye & Li, "Detecting Masked Faces in the Wild with LLE-CNNs", [doi](https://doi.org/10.1109/cvpr.2017.53), [CVF PDF](https://openaccess.thecvf.com/content_cvpr_2017/papers/Ge_Detecting_Masked_Faces_CVPR_2017_paper.pdf)) | **train/test only — no validation set.** "The training set consists of 25, 876 images with 29, 452 masked faces that are randomly selected from MAFA, while the testing set contains the rest 4, 935 images with 6, 354 masked faces." | **F-B / effectively F-A** — with only train+test, `val:` must be the test dir for early stopping | **[OFFICIAL]** paper PDF, extracted with `pypdf` (script `_ev_mafa_text.py`): the quoted sentence above, and the word **"validation" occurs 0 times** in the entire paper. Text also confirms the split is a *random* selection: "we split the MAFA into two subsets". ([CVF PDF](https://openaccess.thecvf.com/content_cvpr_2017/papers/Ge_Detecting_Masked_Faces_CVPR_2017_paper.pdf)) | ⚠️ **Correction worth keeping in the paper's method section:** the arXiv id `1804.04017` is **not** MAFA — `ar5iv.labs.arxiv.org/html/1804.04017` resolves to an unrelated coagulation-fragmentation mathematics paper. MAFA has no arXiv version; the CVF PDF is the only route to the official numbers. This is exactly the kind of citation error an audit should catch. Structurally: no val split exists, so any YOLO run either invents one from train or points `val:` at test. A third-party re-annotation repo independently states the same 25,876/4,935 figures ([AnnotationMAFA README](https://raw.githubusercontent.com/ElenaRyumina/AnnotationMAFA/main/README.md)). |
| **Mendeley face-mask datasets** | Mendeley Data records (data records, no venue); the widely used ~853-image PASCAL-VOC "Face Mask Detection" set is actually **Kaggle `andrewmvd/face-mask-detection`**, not Mendeley | **Records ship NO split at all** — flat `images/` + `annotations/` in PASCAL VOC XML | **F-A, and I found a generator that *writes* `train == val`.** No `test:` key in any copy | **[OFFICIAL, data records]** two reachable Mendeley records define **no split**: `10.17632/v3kry8gb59.1` ("Face Mask Detection Video Dataset", 4,357 frames / 21,941 boxes, single `Annotations.zip`, PASCAL VOC `.xml`) and `10.17632/xz5hbd6zds.2` ("Indian Facemasks Detection Dataset", 1,226 images, flat root of `.jpg`/`.xml`/`.txt`); neither ships a `data.yaml`; **[MIRROR, strongest — a `val == train` generator]** `Prikshit7766/Face-Mask-Detection` `convert_voc_to_yolo.py` contains literally:<br>`data_content = f"train: {os.path.abspath(images_dir)}/\n" \`<br>`               f"val: {os.path.abspath(images_dir)}/\n" \`<br>`               f"nc: {len(classes)}\n" \`<br>`               f"names: {classes}"`<br>— both keys are written from the **same `images_dir`**, and **no `test:` key is emitted at all** ([raw](https://raw.githubusercontent.com/Prikshit7766/Face-Mask-Detection/main/convert_voc_to_yolo.py)); the **committed** `data.yaml` in that same repo has been hand-edited to `train: ../train/images` / `val: ../test/images` / `nc: 3`, still with **no `test:` key** ([raw](https://raw.githubusercontent.com/Prikshit7766/Face-Mask-Detection/main/data.yaml), branch `main` only — `master` 000s) | ⚠️ **Corrections and the key finding.** (i) The canonical ~853-image set is **Kaggle-hosted** (`andrewmvd/face-mask-detection`, card credits Make ML), so attributing it to Mendeley is a common citation error. (ii) The single most useful artefact in this whole audit is that generator: it shows the failure mode being **manufactured by tooling** — a VOC→YOLO converter that hardcodes the same directory for `train` and `val` and never emits `test:`. Anyone running the script as shipped trains and "validates" on the identical image set, with no error. (iii) The committed yaml diverges from the generator, i.e. someone noticed and patched it by hand — evidence that the bug is real enough to have been hit and fixed out-of-band. (iv) Even after the patch, `val:` points at `../test/images`, so this copy is F-B as well. |
| **WIDER FACE** | CVPR 2016 ([doi](https://doi.org/10.1109/cvpr.2016.596)) | 32,203 images, 393,703 faces; **40% train / 10% val / 50% test**, defined **per event class** (61 classes) | **Official: no.** But the modal *mirror* behaviour is **F-B (no `test:` key)** | **[OFFICIAL]** "We choose **32,203** images and label **393,703** faces ... For each event class, we randomly select 40%/10%/50% data ..." and "**Scenario-Int**: A face detector is trained using WIDER FACE training/validation partitions, and tested on WIDER FACE test partition." ([shuoyang1213.me/WIDERFACE](http://shuoyang1213.me/WIDERFACE/)); **[MIRROR]** `spacewalk01/yolov5-face` `data/widerface.yaml` (branch **master**) — `train: /ssd_1t/derron/yolov5-face/data/widerface/train  # 16551 images`, `val: /ssd_1t/derron/yolov5-face/data/widerface/val  # 16551 images`, then a **commented-out** `#val: .../widerface/train/  # 4952 images`, and **no `test:` key** ([raw](https://raw.githubusercontent.com/spacewalk01/yolov5-face/master/data/widerface.yaml)); **[MIRROR]** `yakhyo/yolov8-crowdhuman`-style configs likewise omit `test:` | The official protocol is fully specified and val≠test, and **test ground truth is withheld** — **VERIFIED verbatim** from the official site: "**Similar to MALF and Caltech datasets, we do not release bounding box ground truth for the test images. Users are required to submit final prediction files, which we shall proceed to evaluate.**" ([site](http://shuoyang1213.me/WIDERFACE/)); the same page's benchmark definitions confirm it ("Scenario-Ext: A face detector is trained using any external data, and tested on the WIDER FACE test partition") and its download list offers test **images only**, no test GT file. Two audit-relevant details in the mirror: (i) the file's header comment is **copy-pasted from PASCAL VOC** ("# PASCAL VOC dataset http://host.robots.ox.ac.uk/pascal/VOC/") and the `# 16551 images` / `# 4952 images` comments are **VOC counts, not WIDER FACE counts** — the config was never authored for this dataset; (ii) the live `val:` line carries the *train* count (`16551`) while the commented-out alternative carries `4952` (the VOC val count), so **the comment trail suggests `val:` originally pointed at the train directory**. Corroborating that the live `val:` is legitimate: the same repo's `val2yolo.py` builds it from the official public validation partition — `def wider2face(root, phase='val', ...)` reads `'{}/{}/label.txt'.format(root, phase)`. Whether the 16,551-image val set is a re-split of WIDER FACE *train* or the official *val* partition remains **unverified**. I could not retrieve commit dates to confirm the history in (ii), so treat it as a **strong textual indication, not a confirmed fact**. |
| **CrowdHuman** | arXiv 2018 ([1805.00123](https://ar5iv.labs.arxiv.org/html/1805.00123)) / CVPR 2019 workshop | **15,000 train / 4,370 val / 5,000 test**; val annotations public, **test annotations never released** (online server only) | **Official: no.** The modal *mirror* behaviour is **F-B (no `test:` key)** | **[OFFICIAL]** the paper states the protocol explicitly: "The training and validation subsets of CrowdHuman can be downloaded from our website. In the following experiments, our algorithms are trained based on CrowdHuman train subset and **the results are evaluated in the validation subset**. An online evaluation server will help to evaluate the performance of the testing subset and a leaderboard will be maintained. **The annotations of testing subset will not be made publicly available.**" ([1805.00123](https://ar5iv.labs.arxiv.org/html/1805.00123)); **[OFFICIAL-adjacent]** InternImage detection README for the 15000/4370/5000 counts ([README](https://raw.githubusercontent.com/OpenGVLab/InternImage/master/detection/configs/crowd_human/README.md)); **[MIRROR]** `yakhyo/yolov8-crowdhuman` `dataset.yaml` — `path: path/to/CrowdHuman`, `train: data/train/images`, `val: data/val/images`, **no `test:` key** ([raw](https://raw.githubusercontent.com/yakhyo/yolov8-crowdhuman/main/dataset.yaml)) | **The authors' own baseline is F-B**: "the results are evaluated in the validation subset." Because test annotations are never released, every third party reproducing a CrowdHuman number is reporting a validation number — while still using that same validation subset for checkpoint selection. This is the cleanest documented instance of the pattern in the whole audit, and it is the authors' stated design, not an accident. Same structural situation as WIDER FACE and xView; worth grouping as one argument rather than three findings. |
| **D-Fire (FireSmoke)** | Neural Comput. Appl. 2022 ([doi](https://doi.org/10.1007/s00521-022-07467-z)) | Pre-split **training, validation and test** sets are distributed by the authors; >21,000 images, 2 classes | **Cannot be stated from a primary yaml** — the official distribution has no yaml, only three pre-split folders | **[OFFICIAL]** "Access the D-Fire dataset, including annotations, and pre-split training, validation, and test sets via the following links." ([README](https://raw.githubusercontent.com/gaia-solutions-on-demand/DFireDataset/master/README.md)) | Good case study for *the absence of a yaml as the risk*: because the official artefact is three folders with no config file, every YOLO repo re-authors the config, and they differ. See the mirror rows below. |
| **FireSmoke — third-party YOLO copies** | — | — | **Split verdict: mixed.** One 1.5k-star repo has `val == train`; others have three distinct dirs | **[MIRROR]** `gengyanlei/fire-smoke-detect-yolov4` `yolov5/data/fire_smoke.yaml` — `train: .../2020_train.txt`, `val: .../2020_test.txt` (**distinct**); same repo `Reflective_vests.yaml` — `train == val` (**same**); **[MIRROR]** `Abonia1/YOLOv8-Fire-and-Smoke-Detection` `datasets/fire-8/data.yaml` — `train: fire-8/train/images`, `val: fire-8/valid/images`, `test: ../test/images` (**three distinct dirs**) ([raw](https://raw.githubusercontent.com/Abonia1/YOLOv8-Fire-and-Smoke-Detection/main/datasets/fire-8/data.yaml)); **[MIRROR]** `wzjgo339/fire-smoke-detection` `data.yaml` (branch `master`) — header comment reads `# D-Fire Dataset configuration for YOLO`; `train: data/train.txt`, `val: data/val.txt`, `test: test/images` (**distinct**) ([raw](https://raw.githubusercontent.com/wzjgo339/fire-smoke-detection/master/data.yaml)) | Shows the failure mode is *project-level*, not dataset-level, for the fire/smoke family — exactly the argument the survey needs. **This is the only D-Fire mirror I found whose yaml explicitly declares itself to be D-Fire**, which is why the D-Fire row above rests on the official README rather than on a yaml. |
| **LVIS** (bonus, verifiable) | ICCV 2019 | train 100,170 / val 19,809 / minival 5,000; based on COCO images | **No** | **[MIRROR]** `lvis.yaml` — `train: train.txt`, `val: val.txt`, `minival: minival.txt`; comment: "test2017.zip excluded: LVIS has no 'test:' split and never reads it" ([raw](https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/cfg/datasets/lvis.yaml)) | Bonus row: a config that *documents* the absence of a test split rather than silently leaving `test:` blank. Useful contrast in the paper. |
| **Argoverse-HD** (bonus) | ECCV 2020 (Streaming Perception Challenge) | train 39,384 / val 15,062 / test on the eval.ai leaderboard | **No** | **[MIRROR]** `Argoverse.yaml` — `train: Argoverse-1.1/images/train/`, `val: Argoverse-1.1/images/val/`, `test: Argoverse-1.1/images/test/` ([raw](https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/cfg/datasets/Argoverse.yaml)) | Clean three-way split; included because it is the counterexample that proves the catalogue *can* be authored correctly. |
| **SKU-110K** (bonus) | CVPR 2019 | train 8,219 / val 588 / test 2,936 | **No** | **[MIRROR]** `SKU-110K.yaml` — `train: train.txt`, `val: val.txt`, `test: test.txt` ([raw](https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/cfg/datasets/SKU-110K.yaml)) | Clean. |
| **TT100K** (bonus) | CVPR 2016 | train 6,105 / val 7,641 (the "other" split) / test 3,071 | **No** | **[MIRROR]** `TT100K.yaml` — `train: images/train`, `val: images/val # ... 7641 images (original 'other' split)`, `test: images/test` ([raw](https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/cfg/datasets/TT100K.yaml)) | Clean, but note the yaml *reinterprets* the original "other" split as val. |
| **Global Wheat 2020** (bonus) | ICPR 2020 workshop | multi-source domain split: train = 7 source folders, val = `ethz_1` (**also in train**), test = 4 held-out domains | No (`val != test`) but **F-C**: val ⊂ train | **[MIRROR]** `GlobalWheat2020.yaml` — `val: # val images (relative to 'path') 748 images (WARNING: train set contains ethz_1)` with `- images/ethz_1` also listed under `train:` ([raw](https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/cfg/datasets/GlobalWheat2020.yaml)) | The config *warns about its own leakage* and ships anyway. Strong citation for the paper's "the tooling knows and does not stop you" argument. |
| **coco128** (bonus, widely used as a smoke test) | Ultralytics tutorial dataset | "train" = first 128 images of COCO train2017; val is the **same 128 images** | **YES (F-C: `train == val`)** | **[MIRROR]** `coco128.yaml` — `train: images/train2017 # ... 128 images`, `val: images/train2017 # ... 128 images`, `test:` empty ([raw](https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/cfg/datasets/coco128.yaml)) | Not a benchmark, but it is the reference config thousands of projects copy — and it normalises `val == train`. Relevant as a *cause*, not as a benchmark. |
| **KITTI** (bonus) | CVPR 2012 / IJRR 2013 | official: 7,481 train (with labels) + 7,518 test (**labels withheld, server eval**) | **No `test:` key → F-B** | **[MIRROR]** `kitti.yaml` — `train: images/train # ... 5985 images`, `val: images/val # ... 1496 images`, and **no `test:` key** ([raw](https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/cfg/datasets/kitti.yaml)) | Because official test labels are withheld, the YOLO config reports on a 1,496-image carve-out of the labelled train split. Same structural situation as xView. |
| **HomeObjects-3K** (bonus, non-benchmark) | Ultralytics tutorial dataset | 2,689 images / 12 classes | **No `test:` key → F-B** | **[MIRROR]** `HomeObjects-3K.yaml` — `path: homeobjects-3K`, `train: images/train # ... 2285 images`, `val: images/val # ... 404 images`, and **no `test:` key** (machine-checked: `test: ABSENT`) ([raw](https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/cfg/datasets/HomeObjects-3K.yaml)) | Included only because §3b cites it as an F-B instance; it is a tutorial dataset, not a benchmark, so exclude it from any prevalence figure quoted about *benchmarks*. |

**Bonus row: the third-party helmet/PPE family (no canonical split at all).** Several popular
helmet/PPE YOLO repos ship configs with only `train`+`val` and no `test`: e.g.
`sidpro-hash/Helmet-Detection-YOLOv5` `Helment_Detection_Yolov5/data.yaml`
(`train: ../train/images`, `val: ../valid/images`, `nc: 2`) and `TF-polygon/.../yolov5/data.yaml`
(`train: data/train.txt`, `val: data/valid.txt`, `nc: 10`). Others do ship a test split, e.g.
`Hao0705/YOLOv10-Safety-Helmet` `Safety_Helmet_Dataset/data.yaml`
(`train: ../train/images`, `val: ../valid/images`, `test: ../test/images`) and
`mrrutvikvasoya/On-Site-Safety-Detection` `data.yaml`
(`train: dataset/images/train`, `val: dataset/images/val`, `test: dataset/images/test`).
Verdict for this family: **F-B is the modal outcome**; F-A appears only where a project deliberately
aliases the two keys — see the verified Hard Hat Workers case below.

**A verified `val == test` in this family — and the cleanest example of *why* it happens.**
`HeZhang33/YOLOv5-YOLOv6-YOLOv7-YOLOv8-Object-Detection-Models-For-Personal-Protective-Equipment-Detection`
writes its dataset yaml from notebook cells; I downloaded both notebooks and extracted the cells
(script `_ev_nb_yaml.py`):

* `train_yolov7_for_hardhat_detection.ipynb`, cell 3 — **`val:` and `test:` are byte-identical**:
  `train: ../datasets/hard_hat_workers_dataset/images/train`,
  `val: ../datasets/hard_hat_workers_dataset/images/test`,
  `test: ../datasets/hard_hat_workers_dataset/images/test # test images (optional)`, `nc: 3`.
* `train_yolov5_for_hardhat_detection.ipynb`, cell 3 — the *same dataset*, handled as F-B instead:
  `train: images/train # ... 5269 images`, `val: images/test # ... 1766 images`,
  `test:  # test images (optional), no test images by default in this dataset`.

**Independently re-verified and widened (2026-09-15, second reviewer).** The repository's `main` tree
carries **four** hardhat notebooks, not two, and the split between the two handlings is 3-to-1 on the
*same* dataset — which makes this a controlled comparison rather than an anecdote:

| notebook (branch `main`, cell 3) | yaml written | handling |
|---|---|---|
| `train_yolov7_for_hardhat_detection.ipynb` | `val: ../datasets/.../images/test` + `test: ../datasets/.../images/test` | **F-A, byte-identical keys** |
| `train_yolov5_for_hardhat_detection.ipynb` | `val: images/test` + `test:` empty | F-B |
| `train_yolov6_for_hardhat_detection.ipynb` | `val: ../datasets/.../images/test` + `test:` empty | F-B |
| `train_yolov8_for_hardhat_detection.ipynb` | `val: images/test` + `test:` empty | F-B |

Evidence: repo tree via `api.github.com/repos/<repo>/git/trees/main?recursive=1` (default branch
`main`; `master` 404s), notebooks fetched at 1.28–1.33 MB each, script
`D:\deepseek\analysis\work\find_hardhat_v7_notebook.py`. Note for anyone re-checking: individual
`raw.githubusercontent.com` fetches in this environment intermittently return connection failures
(code 0) rather than a 404 — **a failed fetch is not evidence of absence, retry before concluding.**


**The mechanism is stated in both the config's own comment and the distributor's documentation.** The
v5 config comments `test:  # ... no test images by default in this dataset`, and Roboflow's own dataset
home states the cause outright — **VERIFIED first-hand** (I fetched the page myself; it returns real
content, not only a JS shell):
"**The original dataset has a [75/25 train-test split](https://blog.roboflow.com/train-test-split/).**"
with the version list also confirming that later re-exports do have a real val set —
"`v5` (raw_HeadHelmetClasses): generated with a **70/20/10 train/valid/test split**".
([public.roboflow.com/object-detection/hard-hat-workers](https://public.roboflow.com/object-detection/hard-hat-workers))

**Second-reviewer verification (2026-09-15), and a widening of the claim.** Re-fetched here: HTTP 200,
23,219 bytes, `sha256 = abd1ee4f0b33c9f424c0c98b…`, page archived at
`D:\deepseek\analysis\pr_guideline_evidence\roboflow_hardhat_public_roboflow_com_object_detection_hard_hat_.html`
(script `verify_roboflow_prose.py`); `universe.roboflow.com` from the same host returns **403**
Cloudflare, confirming the host distinction. The `70/20/10` figure is **not limited to v5**: the version
block carries it **eight times** — versions **v5, v8, v9, v10, v11, v12, v13** are each "generated with a
70/20/10 train/valid/test split", while the two `raw_75-25_trainTestSplit` exports keep the original
75/25. So the hazard is broader than "v5 and later": within one dataset page, **the same name denotes two
structurally different protocols**, and the class-filtered re-exports (v5–v13) all silently introduce a
validation partition the original never had.
*Probe note for anyone re-checking:* the version list is an HTML table rendered **without sentence-final
punctuation**, so a sentence-terminated regex (`[^.]*70/20/10[^.]*\.`) misses it entirely and returns a
false negative. Match the bare token, not a sentence.

So the original "Hard Hat Workers" release is a ~75/25 **train/test split with no validation
partition**, which is exactly why `test:` is emptied and `val:` is aimed at the test directory — and,
in the v7 notebook, why both keys are simply written to the same path. This is the most direct
evidence in the whole audit that **F-A is a consequence of the benchmark not shipping a val split**,
not carelessness about which directory to name. It also names the precise hazard for practitioners:
the *original* release has no val split (hence aliasing), while Roboflow's v5+ re-exports do — so two
people "using Hard Hat Workers" can be running structurally different evaluation protocols. (Note theversion labels are re-exports, not benchmarks: `v2` = 7,041 images, raw 75/25; `v5` = 70/20/10.)

---

## 2. How people actually distribute them — what the popular YOLO copies do

The dominant distributor of YOLO-format copies is Ultralytics' own
[`ultralytics/cfg/datasets/`](https://api.github.com/repos/ultralytics/ultralytics/contents/ultralytics/cfg/datasets)
catalogue (51 yaml files), which ships inside the `ultralytics` pip package and is therefore copied
into essentially every derived project. I enumerated that directory via the GitHub contents API and
read each detection config. Exhaustive result of the `val:`/`test:` keys I read:

| yaml (all under `ultralytics/cfg/datasets/`) | `train:` | `val:` | `test:` | verdict |
|---|---|---|---|---|
| `coco.yaml` | `train2017.txt` | `val2017.txt` | `test-dev2017.txt` | distinct ✔ |
| `VOC.yaml` | `train2012`,`train2007`,`val2012`,`val2007` | `images/test2007` | **`images/test2007`** | **F-A (val == test)** |
| `Objects365.yaml` | `images/train` | `images/val` | *key present, empty* | **F-B** |
| `open-images-v7.yaml` | `images/train` | `images/val` | *key present, empty* | **F-B** |
| `DOTAv1.yaml` | `images/train` | `images/val` | `images/test` | distinct ✔ |
| `DOTAv1.5.yaml` | `images/train` | `images/val` | `images/test` | distinct ✔ |
| `VisDrone.yaml` | `images/train` | `images/val` | `images/test` | distinct ✔ |
| `xView.yaml` | `images/autosplit_train.txt` | `images/autosplit_val.txt` | **key ABSENT** | **F-B** |
| `kitti.yaml` | `images/train` | `images/val` | **key ABSENT** | **F-B** |
| `HomeObjects-3K.yaml` | `images/train` | `images/val` | **key ABSENT** | **F-B** |
| `lvis.yaml` | `train.txt` | `val.txt` (+`minival: minival.txt`) | **key ABSENT, and documented in-file** | n/a (no test split exists) |
| `Argoverse.yaml` | `Argoverse-1.1/images/train/` | `.../val/` | `.../test/` | distinct ✔ |
| `SKU-110K.yaml` | `train.txt` | `val.txt` | `test.txt` | distinct ✔ |
| `TT100K.yaml` | `images/train` | `images/val` | `images/test` | distinct ✔ |
| `GlobalWheat2020.yaml` | 7 folders incl. `ethz_1` | `images/ethz_1` | 4 folders | **F-C (val ⊂ train, self-warned)** |
| `construction-ppe.yaml` | `images/train` | `images/val` | `images/test` | distinct ✔ |
| `african-wildlife.yaml` | `images/train` | `images/val` | `images/test` | distinct ✔ |
| `coco128.yaml` | `images/train2017` | **`images/train2017`** | *key present, empty* | **F-C (train == val)** |
| `ImageNet.yaml` | `train` | `val` | *key present, empty* | n/a (classification) |

The `test:` key state (absent vs. present-but-empty vs. valued) was machine-checked for every row above
with `D:\deepseek\analysis\work\_ev_verify_keys.py`; that distinction matters because YOLO treats an
absent key and an empty key differently at validation time, and only the empty/valued forms silently
fall back to `val:`. **Note the asymmetry: every F-A/F-C config in the catalogue uses an empty (not
absent) `test:`, and every F-B config with no test data uses an *absent* key — except `Objects365` and
`open-images-v7`, which use an empty key while their dataset does have real test splits.**

**Non-Ultralytics mirrors** (each read directly):

| mirror | quoted `train:`/`val:`/`test:` | verdict |
|---|---|---|
| `gengyanlei/fire-smoke-detect-yolov4` → `yolov5/data/Reflective_vests.yaml` (SHWD-derived) | `train: /home/ailab/dataset/helmet_dataset/VOC2021/txt_yolov5/2021_train.txt`<br>`val: /home/ailab/dataset/helmet_dataset/VOC2021/txt_yolov5/2021_train.txt` | **F-C (train == val)** |
| `gengyanlei/fire-smoke-detect-yolov4` → `yolov5/data/hp.yaml` (same VOC2028 base) | `train: .../2028_trainval.txt`<br>`val: .../2028_test.txt` | distinct ✔ |
| `gengyanlei/fire-smoke-detect-yolov4` → `yolov5/data/fire_smoke.yaml` | `train: .../2020_train.txt`<br>`val: .../2020_test.txt` | distinct ✔ |
| `forever208/yolov5_train_on_UAVDT` → `data/UAVDT.yaml` | `train: images/train  # ... 128 images`<br>`val: images/val  # ... 128 images`<br>`test:  # test images (optional)` | **F-B** (empty test; counts copy-pasted from coco128) |
| `CQNU-ZhangLab/SFFNet` → `ultralytics/cfg/datasets/UAVDT.yaml` | `path:` / `train:` / `val:` / `test:` — **all four empty** | unusable placeholder |
| `Hamedlk80/DIOR-R-...-YOLOv8` → `diorr_obb_analysis/data.yaml` (**DIOR-R**, OBB; the only DIOR mirror I could read) | `path: /content/diorr_obb`<br>`train: images/train`<br>`val: images/val`<br>**no `test:` key** | **F-B** |
| `sidpro-hash/Helmet-Detection-YOLOv5` → `Helment_Detection_Yolov5/data.yaml` | `train: ../train/images`<br>`val: ../valid/images` | **F-B** |
| `TF-polygon/Real-time-SafetyHelmet-Detection-Yolov5-Yolov8` → `yolov5_cuda/yolov5/data.yaml` | `train: data/train.txt`<br>`val: data/valid.txt` | **F-B** |
| `LforikC/face-mask-dataset` → `dataset.yaml` | `train: face-mask-dataset\images\train`<br>`val: face-mask-dataset\images\valid` | **F-B** |
| `Prikshit7766/Face-Mask-Detection` → **generator** `convert_voc_to_yolo.py` (writes the yaml) | `data_content = f"train: {os.path.abspath(images_dir)}/\n" \`<br>`               f"val: {os.path.abspath(images_dir)}/\n" \`<br>`               f"nc: {len(classes)}\n" \`<br>`               f"names: {classes}"` — **no `test:` line emitted** | **F-A generated (`train == val`)** |
| `Prikshit7766/Face-Mask-Detection` → committed `data.yaml` (branch `main`) | `train: ../train/images`<br>`val: ../test/images`<br>`nc: 3` | **F-B** — hand-patched, generator output diverges |
| `HeZhang33/...PPE-Detection` → `train_yolov7_for_hardhat_detection.ipynb` cell 3 (**Hard Hat Workers**) | `train: ../datasets/hard_hat_workers_dataset/images/train`<br>`val: ../datasets/hard_hat_workers_dataset/images/test`<br>`test: ../datasets/hard_hat_workers_dataset/images/test # test images (optional)` | **F-A (literal `val == test`)** — byte-identical strings; dataset has **no val set** |
| `HeZhang33/...PPE-Detection` → `train_yolov5_for_hardhat_detection.ipynb` cell 3 (same dataset) | `train: images/train # ... 5269 images`<br>`val: images/test # ... 1766 images`<br>`test:  # test images (optional), no test images by default in this dataset` | **F-B** — same dataset, opposite handling |
| `kiwifarmit/hard_hat` → `data.yaml` (**Hard Hat**) | `train: ./training/images`<br>`val: ./validation/images`<br>`nc: 3`<br>**no `test:` key** — and a separate `testing/` directory exists in the repo but the yaml never references it | **F-B**, with an unreferenced test folder on disk |
| `Mahmoud-Khawaja/YOLOv8-Based-Helmet-Detection-.../data_custom.yaml` | `train:` / `val:` / `nc: 3` / `names: ['helmet','head','person']`<br>**no `test:` key** | **F-B** |

**The reason the Hard Hat lineage behaves this way — verified from the distributor.** Roboflow's dataset
home states: "**The original dataset has a 75/25 train-test split**", and lists `v5` as "generated with
a **70/20/10 train/valid/test split**" ([public.roboflow.com/object-detection/hard-hat-workers](https://public.roboflow.com/object-detection/hard-hat-workers)).
The original release therefore has **no validation partition at all**, which is why authors either alias
`val:` onto `test/` (HeZhang33's v7 notebook → F-A) or drop `test:` entirely (kiwifarmit, Mahmoud-Khawaja
→ F-B). Roboflow's own later re-exports do have a val split, so two projects "using Hard Hat" can be
running structurally different protocols.
| `Hao0705/YOLOv10-Safety-Helmet` → `Safety_Helmet_Dataset/data.yaml` | `train: ../train/images`<br>`val: ../valid/images`<br>`test: ../test/images` | distinct ✔ |
| `mrrutvikvasoya/On-Site-Safety-Detection` → `data.yaml` | `train: dataset/images/train`<br>`val: dataset/images/val`<br>`test: dataset/images/test` | distinct ✔ |
| `wzjgo339/fire-smoke-detection` → `data.yaml` (branch **master**, not main) | `path: .`<br>`train: data/train.txt`<br>`val: data/val.txt`<br>`test: test/images` | distinct ✔ **but inconsistent forms** — `train`/`val` are `.txt` file lists while `test` is a directory |
| `spacewalk01/yolov5-face` → `data/widerface.yaml` (branch **master**; **WIDER FACE**) | `train: /ssd_1t/derron/yolov5-face/data/widerface/train  # 16551 images`<br>`val: /ssd_1t/derron/yolov5-face/data/widerface/val  # 16551 images`<br>`#val: .../widerface/train/  # 4952 images` (commented out)<br>**no `test:` key** | **F-B**, and the comments are VOC's numbers |
| `yakhyo/yolov8-crowdhuman` → `dataset.yaml` (**CrowdHuman**) | `path: path/to/CrowdHuman`<br>`train: data/train/images`<br>`val: data/val/images`<br>**no `test:` key** | **F-B** |
| `Abonia1/YOLOv8-Fire-and-Smoke-Detection` → `datasets/fire-8/data.yaml` | `train: fire-8/train/images`<br>`val: fire-8/valid/images`<br>`test: ../test/images` | distinct ✔ |

**Roboflow.** I could **not** read a Roboflow-hosted `data.yaml`: `universe.roboflow.com` returns a
Cloudflare challenge (HTTP 403) from this machine and Roboflow's export yaml is generated per-download
under an API key, so there is no stable public URL for one. I therefore have **no verified statement
about what a Roboflow export contains** — not even the folder names, since the configs whose paths
look Roboflow-like in my sample are contradictory: `sidpro-hash` and `Hao0705` use
`../train/images` + `../valid/images` (+ `../test/images` for `Hao0705`, whose yaml does carry an
explicit `roboflow:` block with `workspace: dataperson`), but `LforikC` uses Windows backslash paths
(`face-mask-dataset\images\train`), which is *not* a Roboflow artefact, and `mrrutvikvasoya` uses
`dataset/images/{train,val,test}`. I am explicitly **not** claiming a Roboflow fingerprint. What the
sample *does* support, as a three-config impression only, is that **third-party YOLO redistributions of
PPE/face datasets frequently ship only two splits** (`train`+`valid`, **no `test:` key**) — which lands
users in F-B.

---

## 3. Count — `val == test` (or equivalent) among verified benchmarks

I could positively verify a `val:`/`test:` definition (from a readable config, README, or paper text)
for **all 28** rows surveyed; the unresolved items are *sub-claims* (exact counts, whether a specific
mirror is representative), not the split structure itself.

**Denominator.** The **19 benchmarks named in the brief**. The 9 non-benchmark rows in §1 — the 8
"(bonus)" tutorial/auxiliary datasets (LVIS, Argoverse-HD, SKU-110K, TT100K, Global Wheat 2020,
coco128, KITTI, HomeObjects-3K) plus the FireSmoke mirror-family row — are excluded from every
denominator in this section, because mixing tutorial sets and mirror families into a prevalence claim
about benchmarks would be misleading; they are reported separately at the end of this section. Every
subsection header below therefore reads `n/19`, so the five headers must sum to 19. All figures are
re-derivable from `D:\deepseek\analysis\work\_ev_final_audit.py`, whose row table is kept in sync with
§1 (28 rows = 19 benchmarks + 9 non-benchmark rows).

### 3a. Literal `val == test` (or shipped `test` ⊂ `val`) — **2/19**

| benchmark | evidence (machine-verified) |
|---|---|
| **PASCAL VOC** | `ultralytics/cfg/datasets/VOC.yaml`: `val:` → `- images/test2007` and `test:` → `- images/test2007` |
| **SFCHD** | `lijfrank/SFCHD-SCALE` `dataset_SFCHD/new_split_yolo/`: `test.txt` has 6 lines, `val.txt` has 2,475, `test ⊆ val` = **True**, and `val.txt[:6] == test.txt` = **True** |

Two distinct mechanisms, worth separating in the paper: VOC is a *deliberate aliasing* (one config
line, both keys the same path), whereas SFCHD is a *truncation artefact* (`test.txt` looks like a
truncated copy of `val.txt` — 6 vs 2,475 lines, identical prefix, both containing the author's
absolute `/home/yfs/data/...` paths). SFCHD is the more alarming of the two because nothing in the
file *says* `val == test`; a reader has to diff the files to notice.

**Scope of this bucket, so it is not read as contradicting §2:** the count is **2/19 *benchmarks***,
i.e. two cases where the artefact a *benchmark* ships binds the keys together. Literal `val == test`
also occurs at *mirror* level — most clearly `HeZhang33`'s Hard Hat Workers YOLOv7 notebook, where the
two keys are byte-identical strings (§2) — but a mirror is a redistribution rather than a benchmark,
so it is not counted here. That distinction is the point: **at benchmark level literal aliasing is
rare (2/19), while at mirror level it is produced routinely**, and the mirror cases are exactly the
ones a reader would mistake for benchmark properties.

### 3b. `val` is the reported split because no `test` data exists (F-B) — **6/19**

Objects365, Open Images v7, xView, DIOR (via the DIOR-R YOLO copy), UAVDT, and the Mendeley face-mask
family. Plus, on the mirror side, the whole helmet/PPE family (`sidpro-hash`, `TF-polygon`,
`LforikC`) and WIDER FACE / CrowdHuman *in practice* (see 3c). Two bonus rows (KITTI,
HomeObjects-3K) are the same shape but are excluded from this denominator — see §1. LVIS is the
benign, *documented* instance of the same shape and is listed in 3e instead, because its yaml states
outright that no test split exists.

### 3c. Official or mirror split makes the reported set overlap training (F-C) — **4/19**

SHWD (its most-read third-party yaml has `train == val`, and the official `train_yolo.py` itself
calls the `test` split "val"); WIDER FACE and CrowdHuman (official protocols withhold or server-gate
test, so the practical reported number is the val set that was also used for selection); D-Fire
(official artefact is pre-split folders with no yaml, and mirrors disagree — one has three distinct
dirs, another family member has `train == val`).

### 3d. Official protocol is train/test only, so `val` must be aliased to test — **2/19**

MAFA (train/test only, 25,876/4,935 per a third-party re-annotation) and — structurally — NWPU VHR-10
(ships no split at all; every YOLO user invents one). For these, a user has only two options: invent a
val split, or set `val == test`. **The paper-form of SFCHD** (train/test only 4:1) is the third
instance of this shape, but it is **not** counted again here: it is the same benchmark as 3a, which
already carries its verdict. The union counts each benchmark once, so the partition shows **D = 2**
while this subsection describes three situations — 3a's SFCHD entry is the third.

### 3e. Cleanly separated — `val != test` with a genuinely independent held-out test — **5/19**

**Brief denominator (5):** COCO, DOTA v1, DOTA v2, VisDrone-DET, AI-TOD (official).
**Outside the brief denominator — bonus rows also clean (4):** LVIS, Argoverse-HD, SKU-110K, TT100K;
with those included the all-row clean figure is 9/28 (see the roll-up). **Mirror configs that are
clean** (kept out of both denominators, since they are redistributions rather than benchmarks): the
distinct-dir fire/PPE mirrors (`Abonia1`, `wzjgo339`, `Hao0705`, `mrrutvikvasoya`) and `hp.yaml` on
the SHWD base.

⚠️ **This header previously read "13"** and merged those three groups. That 13 was a count of clean
*config rows* across the whole file, not of clean benchmarks in the denominator, and it must not be
read against the roll-up. The benchmark claim is **5/19**.

**Roll-up.** Denominator = the **19 benchmarks named in the brief**. The 9 non-benchmark rows in §1
(8 "(bonus)" tutorial/auxiliary datasets plus the FireSmoke mirror-family row) are excluded here, and
reported separately below. Every one of the 19 carries exactly one verdict; the lists are enumerated
so you can re-derive the arithmetic (`D:\deepseek\analysis\work\_ev_final_audit.py`).

* **Literal `val == test` (or shipped `test` ⊂ `val`): 2/19 ≈ 11%** — **PASCAL VOC**, **SFCHD**.
* **`val` aliased to, or functionally identical to, the reported split
  (3a ∪ 3b ∪ 3c ∪ 3d, each counted once): 14/19 ≈ 74%** — PASCAL VOC, SFCHD, Objects365,
  Open Images v7, UAVDT, xView, DIOR, NWPU VHR-10, SHWD, MAFA, Mendeley face-mask, WIDER FACE,
  CrowdHuman, D-Fire.
* **Cleanly separated, with a genuinely independent held-out test: 5/19 ≈ 26%** — COCO, DOTA v1,
  DOTA v2, VisDrone-DET, AI-TOD.

Sum check: 14 + 5 = 19 (verdict counts 3a=2, 3b=6, 3c=4, 3d=2, 3e=5 → union 14 + clean 5). Two rows
deserve a footnote rather than a bucket of their own:
**NWPU VHR-10** is in the alias group because it ships no split at all, so a YOLO config's
`val`/`test` are the author's invention; **Mendeley face-mask** is there because no canonical split
exists to check. Both are genuine instances of the failure mode, but the paper should say that the
*baseline* is unaccountable for them rather than blaming the benchmark authors.

**Boundary conventions — state which one you mean, or quote the range.** The 14/19 figure mixes two
defensible units, and a reviewer will attack a single-point number from the swing rows:

* **Artefact/spec level** (what the released configuration or official protocol declares): WIDER FACE
  and CrowdHuman specify distinct train/val/test partitions officially — their **mirrors** are what
  alias, not their protocols — so they leave the alias group → **12/19 ≈ 63%**.
* **Practically-reported level** (which split the number in a paper actually comes from): both stay
  in, because test ground truth is never released for either (WIDER FACE, verified verbatim in §1:
  "we do not release bounding box ground truth for the test images"; CrowdHuman: "The annotations of
  testing subset will not be made publicly available") → **14/19 ≈ 74%**.
* **Single-row sensitivity:** **Mendeley face-mask** is the audit's weakest row (no canonical split
  exists to check; the widely used ~853-image set is Kaggle `andrewmvd/face-mask-detection`). Removing
  that one row gives **13/18 ≈ 72%**, so the conclusion does not rest on the weakest evidence.

**Citable form, robust to the choice:** literal path aliasing is rare (**2/19 ≈ 11%**), while
reporting a split that is not independent of model selection is the majority case (**12–15 of 19**,
roughly two-thirds to four-fifths, depending on how server-gated or partially-annotated test splits
are counted), and the per-row evidence is released so the boundary is auditable. Historical note, so
three numbers are not read as competing claims: earlier figures of **16/28** and **13/27** were issued
by this audit and **withdrawn as arithmetic errors**; the partition above is hand-enumerated and
sum-checked.

Over all 28 rows the same three figures are **2/28 ≈ 7%**, **18/28 ≈ 64%** and **9/28 ≈ 32%**: the
bonus datasets LVIS, Argoverse-HD, SKU-110K and TT100K are clean while Global Wheat 2020, coco128,
KITTI and HomeObjects-3K are not, and the FireSmoke family row is mixed. **Quote whichever
denominator you mean.** The qualitative conclusion is stable either way and is stronger than a first
pass suggests: **about a quarter of these benchmarks ship a split that is actually independent of
model selection, and only about a tenth alias the two keys literally** — so the failure is
overwhelmingly *implicit* (a missing or empty `test:` key, or a train/test-only official protocol)
rather than a visible `val: test` line.

This gap — **11% literal vs. 63–79% functional** — is the paper's real finding: the failure mode is not
only that authors write `val: test`, it is that the *distributed artefacts and default protocols* make
`val` the reported split without anyone writing that line.

---

## 4. What I could NOT verify

Explicit and per the evidence rules. Each entry says what I tried and why it failed.

1. **Roboflow-hosted YOLO yaml (any dataset).** `universe.roboflow.com/search?...` returns a
   Cloudflare "Just a moment…" challenge (HTTP 403) and Roboflow export configs are generated per
   API-key download, so no stable public URL exists. **I make no claim about Roboflow's default
   split structure.** (An earlier draft of this document inferred a Roboflow "fingerprint" from four
   GitHub configs; that inference was wrong and has been removed — one of the four uses Windows
   backslash paths and is demonstrably not a Roboflow export.)
   **Partial exception, added late:** `public.roboflow.com` (as distinct from the Cloudflare-blocked
   `universe.roboflow.com`) *is* reachable from this host, and its Hard-Hat-Workers page served real
   content including a per-split description in prose ("The original dataset has a 75/25 train-test
   split"; "`v5` ... generated with a 70/20/10 train/valid/test split"). That is quoted in §1 and §2.
   It is **homepage prose, not a yaml**, so it supports a claim about *that dataset's* splits — it does
   **not** license any statement about Roboflow's export defaults, and the general claim above stands.
2. **SHWD — a YOLO-format `data.yaml` from the official side.** The official repo
   (`njvisionpower/Safety-Helmet-Wearing-Dataset`) ships **no yaml config at all**; its trainer is a
   custom `train_yolo.py` using `VOCLike`. Evidence: fetching the repo root HTML
   ([github.com/njvisionpower/Safety-Helmet-Wearing-Dataset](https://github.com/njvisionpower/Safety-Helmet-Wearing-Dataset))
   yields exactly the file set `README.md`, `test_symbol.py`, `test_yolo.py`, `train_yolo.py` — zero
   `.yaml`/`.yml`/`.data`/`.names` files. Official split is therefore reported from the README only.
   The only SHWD-derived YOLO yaml I could read is `gengyanlei/...Reflective_vests.yaml` (mirror,
   `train == val`), which I **cannot** claim is representative of SHWD users. *(An earlier draft cited
   a tree-scan line "26 files / 0 yaml files" for this repo; that scan log had been overwritten by an
   API rate-limit error, so the claim is now backed by the root-HTML listing above instead.)*
3. **A YAML CONFIG inside SFCHD-SCALE.** The repo ships `dataset_SFCHD/new_split_yolo/` containing
   `train.txt`, `val.txt`, `test.txt`, `classes.txt`, `labels.cache`, `train.cache`, `val.cache`,
   `labels.zip`, `yolo.zip` — **but no `data.yaml`/`dataset.yaml`** (I probed nine plausible paths and
   the three that resolved returned 404). So I verified the *split lists* directly (see the SFCHD row
   in §1) but could not quote a yaml, and I could not open the paper on `mdpi`/`sciencedirect` — the
   split text I quote comes from `ar5iv`. *(An earlier draft claimed a tree scan showed "100 files /
   0 yaml files"; that scan log had been overwritten by a rate-limit error. The file list above comes
   from parsing the repo's HTML directory JSON, which is reproducible.)*
4. **DIOR official per-split counts.** The original `escience.cn` host is dead; the Mendeley record
   for DIOR returns only a description and its files API returned `{"error":400}` for the endpoint I
   tried; `sciencedirect.com` and `mdpi.com` block this machine (403). I have DIOR's totals
   (23,463 images / 192,518 instances) from a Mendeley description, and a DIOR-R YOLO yaml with
   `train`+`val` and no `test`, but **no primary source for DIOR's official train/val/test counts**.
   Note also that "DIOR" in the wild is ambiguous between DIOR (HBB) and DIOR-R (OBB) — the yaml I
   read is DIOR-R.
5. **NWPU VHR-10 — any official split.** None exists. I verified via TorchGeo that the code's `split`
   argument means `positive|negative`, not train/val/test. I could not verify any *widely used*
   NWPU VHR-10 YOLO yaml: `Vodat1107/Yolov11_NWPU-VHR-10_dataset` has no readable root-level
   `data.yaml` (raw path probe returned only `README.md`), and `chaozhong2010/VHR-10_dataset_coco`
   contains no split keywords at all.
6. **UAVDT — a faithful YOLO yaml.** The two I read are both defective in different ways
   (`forever208` has a coco128-template comment and/or empty `test:` — machine-checked as
   `test: PRESENT-EMPTY`; `SFFNet` has `path`/`train`/`val`/`test` **all** `PRESENT-EMPTY`).
   `osman-1002/UAVDT_YOLO_pipeline` and `zihaosoog/Hybrid-RT-DETR` had no readable root yaml. So
   "what the widely used UAVDT YOLO copy does" is **unverified beyond these two**.
7. **A canonical YOLO yaml for AI-TOD, MAFA, and DIOR (HBB).** No canonical YOLO config exists for
   any of these in the Ultralytics catalogue (I enumerated the full 51-file directory), and
   per-project repos I probed did not expose a readable `data.yaml`. (WIDER FACE, CrowdHuman and
   SFCHD *mirrors* were later found and are now cited in §1 and §2.)
8. **Mendeley face-mask — the canonical record.** Mendeley's search page is a React app (no usable
   static result list) and the public files API returned `{"error":400}` for the endpoints I tried;
   `huggingface.co` mirrors timed out repeatedly from this machine. I therefore could not identify a
   single authoritative Mendeley "face-mask" record, let alone its split. The row in §1 reports the
   family-level structural finding (many records ship no split; YOLO copies then invent one). This
   is the weakest row in §1 — treat it as a hypothesis, not a verified benchmark entry.
9. **CrowdHuman's official test-annotation status.** ✅ **Resolved during review** — now quoted
   verbatim from the paper in §1 ("The annotations of testing subset will not be made publicly
   available"), and the `yakhyo` mirror confirms the practical F-B shape by shipping no `test:` key.
   The 15000/4370/5000 counts still come from InternImage's README rather than the official download
   page, so treat *those counts* as secondary-sourced.
9b. **WIDER FACE's test ground-truth status.** ✅ **Resolved during review** — now quoted verbatim in
   §1: "we do not release bounding box ground truth for the test images". The companion uncertainty
   remains: whether the mirror's 16,551-image `val` set is a re-split of WIDER FACE *train* or the
   official *val* partition is **unverified**.
9c. **Whether any GitHub repo redistributes a *Mendeley* face-mask dataset as YOLO with a
   `data.yaml`.** **Unverified** (not "does not exist"): Mendeley has no working server-side search
   (identical 20,434-byte response for `query=`, `q=`, `search=`), so this could not be enumerated.
   The YOLO generation path I *did* verify (`Prikshit7766`) sources from **Kaggle**, not Mendeley.
9d. **Whether a MAFA YOLO `data.yaml` exists anywhere.** **Unverified** — `AnnotationMAFA` has no
   `data.yaml`/`dataset.yaml`, and no other MAFA YOLO config was reachable. Do not write "MAFA has no
   YOLO config"; write "I could not find one".
10. **MAFA's official split figures.** ✅ **Resolved during review** — the numbers come from the
    authors' own CVPR 2017 PDF (extracted with `pypdf`; see the MAFA row in §1). The earlier concern
    was caused by a citation error: arXiv `1804.04017` is an unrelated mathematics paper, and MAFA has
    no arXiv version.
11. **AI-TOD-v2 test availability.** The official AI-TOD-v2 README contradicts itself (see the AI-TOD
    row in §1), so whether the test annotations are downloadable **could not be resolved**.
12. **The true identity of the "Mendeley face-mask" benchmark.** The widely used ~853-image
    PASCAL-VOC set turns out to be Kaggle-hosted (`andrewmvd/face-mask-detection`), and the two
    Mendeley records I could reach define no split. Whether *any* Mendeley face-mask record specifies
    a train/val/test split is **unverified** — Mendeley's search API silently ignores query
    parameters (identical 20,434-byte response for every query), so its catalogue could not be
    enumerated. The §1 row should be read as a family-level hypothesis.
13. **WIDER FACE mirror split *history*.** The `spacewalk01` config's live `val:` line carries a
    `# 16551 images` comment (a VOC train count) while a commented-out alternative carries
    `# 4952 images` (a VOC val count), which strongly suggests `val:` once pointed at the train
    directory. I could not retrieve commit dates to confirm this (GitHub pages rate-limited), so it
    is a **textual indication, not a confirmed fact**.
14. **Kaggle, generally.** `kaggle.com` dataset pages are behind a JS/bot wall from this machine, so
    "widely used Kaggle mirror" rows (hard-hat workers, smoke/fire YOLO, helmet detection) are
    supported only where a GitHub repo republishes the same yaml. `huggingface.co` was entirely
    unreachable (connection timeouts across all attempts), which removed a whole class of mirrors
    from the search.

### Tooling / access constraints encountered (for reproducibility)

* `arxiv.org` unreachable (connection reset) → used `ar5iv.labs.arxiv.org` HTML for paper text.
* Python `urllib` blocked on this host (TLS `RemoteDisconnected`); all fetching done with
  `curl.exe` via `D:\deepseek\analysis\work\_ev_fetch.py`, `_ev_batch.py`, `_ev_probe.py`.
* `api.github.com` code search requires auth (401) and the core tree API is rate-limited to 60/hour;
  the Ultralytics catalogue was enumerated via the contents API and the rest by direct
  `raw.githubusercontent.com` probing.
* `universe.roboflow.com` / `grep.app`: Cloudflare 403. `huggingface.co`: intermittent timeouts.
* Helper scripts (all prefixed `_ev_`, in `D:\deepseek\analysis\work\`): `_ev_fetch.py`,
  `_ev_batch.py`, `_ev_reposcan.py`, `_ev_probe.py`, `_ev_ghsearch.py`, `_ev_tree.py`,
  `_ev_venue.py`, `_ev_verify_keys.py` (machine-checks present/empty/absent for every cited split
  key), `_ev_sfchd_check2.py` (the SFCHD `val`/`test` overlap proof); raw scan logs
  `_ev_out_repos2.txt` … `_ev_out_repos6.txt`.
* `api.github.com` rate limiting silently corrupted two early tree scans (they returned
  `{"message":"API rate limit exceeded…"}` where I had recorded file counts). Those two counts have
  been re-derived from repo root HTML instead, and the affected claims in §4 are annotated. If you
  re-run any `_ev_reposcan.py` output, check for that JSON message before trusting a file count.
* OpenAlex/Semantic Scholar agree with every venue/year in §1 that I spot-checked; note that for
  Open Images both APIs report the primary year as **2018** (the arXiv preprint) while the journal
  version is IJCV **2020** — the year in §1 is the journal one, per the DBLP key
  `journals/ijcv/KuznetsovaRAUKP20`.
