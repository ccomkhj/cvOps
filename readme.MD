## Introduction
cvOps is the open source tool to automate mask and annotation preprocessing before model training.

## Steps

1. Quality check of annotation

- Often annotation task is delegated to outsourcing company or freelancer.
- This repo provides the interactive tool to visualize and check if the quality of annotation is good.
- It supports COCO json and Mask format \


1-1. COCO samples
```bash
Example:
.
├── images_dir
│   ├── sample1
│   ├── sample2
|   ├── sample3
|   
├── anns_dir
│   ├── sample1.json
│   ├── sample2.json
│   ├── sample3.json

python3 COCO.py visualize {images_dir} {anns_dir}
```
:warning: It doesn't work if you link to external disk.

1-2. Mask samples :mask:
```bash
python3 Mask.py visualize {images_dir} {anns_dir}
```

2. Process annotations

2-1. Merge COCO sample

```bash
python3 COCO.py merge {images_dir} {anns_dir}
```

2-2. Split COCO sample

```bash
python3 COCO.py split {annotation path} {path to train annotation} {path to test annotation} {split ratio between 0 and 1}
# i.e. python3 COCO.py split anns/new.json results/train.json results/test.json 0.8
```


2-3. Convert Mask
First, configure config file at `config/mask.yaml`

```bash
python3 Mask.py convert {anns_dir} {mask_dir to save} 
```
After converting, show the mask.
```bash
python3 Mask.py show {mask_dir} 
```

## Install

COCO relevant parts heavily relies on `COCO-Assistant`
```bash
$ git clone https://github.com/ashnair1/COCO-Assistant.git
cd COCO-Assistant/
pip install .
```
`requirements.txt`
```bash
pip3 install -U scikit-learn
```