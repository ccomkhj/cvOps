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

1-2. COCO samples with only bounding box (no segmentation)
```bash
Example:
    .
    ├── images_dir
    │   ├── image1
    │   ├── image2
    |   ├── image3
    |
    ├── ann_path

python3 COCO.py visualizebox {images_dir} {anns_path}
```

1-3. Mask samples :mask:
```bash
python3 Mask.py visualize {images_dir} {anns_dir}
```

1. Process annotations

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

2-3. Update COCO sample

When updating computer vision projects, existing train and validation samples needs to be updated.

Split New Annotations: It splits the new annotations (specified by new_ann_path) into train and validation sets based on the split_ratio and optionally reorganizes images using the image_locate directory. The result is saved as "new_train_images.json" and "new_val_images.json" in the output directories.

Locate Existing Images: The function locates existing images specified by train_img_path and val_img_path based on the split and saves them in the corresponding output directories. Note that the image files must be provided in the appropriate directory structure.

Merge Annotations: Finally, it merges the located images with their corresponding annotations for both the train and validation sets.
When the coco merge process is successfully done, merge images manually. (To handle with the massive image size.)

Example Usage:
```bash
python your_script.py update \
    --new_ann_path /path/to/new_annotations.json \
    --train_ann_path /path/to/train_annotations.json \
    --val_ann_path /path/to/val_annotations.json \
    --split_ratio 0.8 \
    --image_locate /path/to/images/
```
`python COCO.py update data/new/annotations/instances_default.json data/original/train.json data/original/val.json 0.8 data/new/images`

This command will update and split the datasets as specified and store the results in timestamped directories under "results/{epoch time}".

2-4. Delete irrelevant categories
- First, configure config file at `config/category_manage.yaml`

``` bash
python3 COCO.py delete {config_file} {annotation_path}
# i.e. python3 COCO.py delete config/category_manage.yaml ann.json
```

2-5. Process category & annotation
- Convert category name and merge duplicated categories

```bash
python3 COCO.py process {config_file} {annotation_path}
# i.e. python3 COCO.py process config/category_manage.yaml ann.json
```

2-6. Validate COCO if it matches with image path.
```bash
python COCO.py validate /path/to/images /path/to/coco.json
# i.e. python COCO.py validate data/new/images data/new/annotations/instances_default.json
```

2-7. Convert Mask (pallete to binary mask)
- First, configure config file at `config/mask.yaml`

```bash
python3 Mask.py convert {anns_dir} {mask_dir to save} 
```

2-8. Convert Mask (COCO to binary mask)
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
