## Introduction
cvOPs is the open source tool to automate mask and annotation preprocessing before model training.

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
│   ├── train
│   ├── val
|   ├── test
|   
├── anns_dir
│   ├── train.json
│   ├── val.json
│   ├── test.json

python3 COCO.py visualize {images_dir} {anns_dir}
```
` It doesn't work if you link to external disk.`

1-2. Mask samples
```bash
python3 COCO.py visualize {images_dir} {anns_dir}
```

2. Process annotations

2-1. Merge COCO sample

2-2. Convert Mask
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