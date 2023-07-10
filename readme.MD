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
(Specify file name, check the example)

```bash
python3 COCO.py split {annotation path} {path to train annotation} {path to test annotation} {split ratio between 0 and 1} {images path, optional}
# i.e. python3 COCO.py split anns/new.json results/train/train.json results/test/test.json 0.8 images
```
If your source doesn't include license, include the blank license.
```json
# blank case
"licenses": [
        {
            "id": 0,
            "name": "",
            "url": ""
        }
    ],
    ...
```

2-3. Convert Mask (pallete to binary mask)
First, configure config file at `config/mask.yaml`

```bash
python3 Mask.py convert {anns_dir} {mask_dir to save} 
```

2-4. Convert Mask (COCO to binary mask)
```bash
python3 Mask.py convert {anns_dir} {mask_dir to save} 
```
if you want to consider all instances, add `--multi` tag in command.


After converting, show the mask.
```bash
python3 Mask.py show {mask_dir} 
```

## Additional Function

1. Convert AiHub Json format to COCO Json format
- If you have AiHub json files, you can convert it to COCO json format.
```bash
python3 COCO.py convertjsonformat {json_aihub_dir} {json_coco_dir}
```

2. Replace the image extension
- If you have converted your image format, you should change the extension in the annotation file too. You can simply replace it using this function.
```bash
python3 COCO.py replaceimgformat {ann_file_path} {desired_extension}
# i.e. python3 COCO.py replaceimgformat ann.json jpg
```

## Install

COCO relevant parts heavily relies on `COCO-Assistant`
```bash
git clone https://github.com/ashnair1/COCO-Assistant.git
cd COCO-Assistant/
pip install .
```
`requirements.txt`
```bash
pip3 install -r requirements.txt
```