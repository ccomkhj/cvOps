import json
import os
from typing import Optional

import funcy
import numpy as np
import typer
import yaml
from tqdm import tqdm
from coco_assistant import COCO_Assistant
from PIL import Image
from pycocotools.coco import COCO
from sklearn.model_selection import train_test_split
from skmultilearn.model_selection import iterative_train_test_split

from tools.helpers import filter_annotations, filter_images, locate_images, save_coco

app = typer.Typer(help="Awesome cvOps Tool.", rich_markup_mode="rich")


@app.command()
def visualize(
    img_dir: str = typer.Argument(..., help="directory of images"),
    ann_dir: str = typer.Argument(..., help="directory of annotations"),
):
    """
    [bold green]Visualize coco sample[/bold green]

    [blue]
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
    [/blue]
    """

    # Create COCO_Assistant object
    cas = COCO_Assistant(img_dir, ann_dir)
    cas.visualise()


@app.command()
def merge(
    img_dir: str = typer.Argument(..., help="directory of images"),
    ann_dir: str = typer.Argument(..., help="directory of annotations"),
):
    """
    [bold green]Merge coco sample[/bold green]

    [blue]
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
    [/blue]
    """

    # Create COCO_Assistant object
    cas = COCO_Assistant(img_dir, ann_dir)
    cas.merge()


@app.command()
def convert(
    ann_path: str = typer.Argument(..., help="Path to COCO annotations file."),
    mask_save_dir: str = typer.Argument(..., help="Path to COCO annotations file."),
    multi: bool = typer.Option(
        False,
        help="Make mask covering multi class. if false, it makes binary mask. (fore/background mask) by adding --multi",
    ),
):
    coco = COCO(ann_path)

    annsIds = coco.getAnnIds()
    imgsIds = coco.getImgIds()
    cat_ids = coco.getCatIds()

    for imgId in imgsIds:
        img = coco.imgs[imgId]
        imgFileName = img.get("file_name")
        imgShape = (img.get("height"), img.get("width"))
        anns_ids = coco.getAnnIds(imgIds=img["id"], catIds=cat_ids, iscrowd=None)
        anns = coco.loadAnns(anns_ids)

        mask = np.zeros(imgShape, dtype=np.uint8)
        for ann in anns:
            if multi:
                mask += coco.annToMask(ann) * ann["category_id"]
            else:
                # every mask has value 1. (binary)
                mask += coco.annToMask(ann)

        # save masks to BW images
        file_path = os.path.join(
            mask_save_dir,
            imgFileName,
        )
        Image.fromarray(mask).convert("P").save(file_path)
        print(f"Successfully generated mask file: {imgFileName}")


@app.command()
def split(
    ann_path: str = typer.Argument(..., help="Path to COCO annotations file."),
    train_path: str = typer.Argument(
        ..., help="Where to store COCO training annotations"
    ),
    test_path: str = typer.Argument(..., help="Where to store COCO test annotations"),
    split: float = typer.Argument(
        default=0.8, help="A ratio of a split; a number in (0, 1)"
    ),
    image_locate: Optional[str] = typer.Argument(
        default="", help="Locate images based on the split if the value is given."
    ),
    multi: bool = typer.Option(
        False,
        help="Make mask covering multi class. if false, it makes binary mask. (fore/background mask) by adding --multi",
    ),
):

    with open(ann_path, "rt", encoding="UTF-8") as annotations:
        coco = json.load(annotations)
        info = coco["info"]
        licenses = coco["licenses"]
        images = coco["images"]
        annotations = coco["annotations"]
        categories = coco["categories"]

        images_with_annotations = funcy.lmap(lambda a: int(a["image_id"]), annotations)

        images = funcy.lremove(lambda i: i["id"] not in images_with_annotations, images)

        if multi:

            annotation_categories = funcy.lmap(
                lambda a: int(a["category_id"]), annotations
            )

            # bottle neck 1
            # remove classes that has only one sample, because it can't be split into the training and testing sets
            annotation_categories = funcy.lremove(
                lambda i: annotation_categories.count(i) <= 1, annotation_categories
            )

            annotations = funcy.lremove(
                lambda i: i["category_id"] not in annotation_categories, annotations
            )

            X_train, y_train, X_test, y_test = iterative_train_test_split(
                np.array([annotations]).T,
                np.array([annotation_categories]).T,
                test_size=1 - split,
            )

            save_coco(
                train_path,
                info,
                licenses,
                filter_images(images, X_train.reshape(-1)),
                X_train.reshape(-1).tolist(),
                categories,
            )
            save_coco(
                test_path,
                info,
                licenses,
                filter_images(images, X_test.reshape(-1)),
                X_test.reshape(-1).tolist(),
                categories,
            )

            print(
                "Saved {} entries in {} and {} in {}".format(
                    len(X_train), train_path, len(X_test), test_path
                )
            )

        else:

            X_train, X_test = train_test_split(images, train_size=split)

            anns_train = filter_annotations(annotations, X_train)
            anns_test = filter_annotations(annotations, X_test)

            save_coco(train_path, info, licenses, X_train, anns_train, categories)
            save_coco(test_path, info, licenses, X_test, anns_test, categories)

            print(
                "Saved {} entries in {} and {} in {}".format(
                    len(anns_train), train_path, len(anns_test), test_path
                )
            )
    if image_locate != "":
        # if the path is given,

        # Create folder of images next to train and test file
        destDir_train = os.path.join(os.path.dirname(train_path), "train_images")
        os.makedirs(destDir_train, exist_ok=True)

        # Iterate the dictionary and send it to source and destination.
        for train_obj in X_train:
            file_name = train_obj.get("file_name")
            source = os.path.join(image_locate, file_name)
            destination = os.path.join(destDir_train, file_name)
            locate_images(source, destination)

        destDir_test = os.path.join(os.path.dirname(test_path), "test_images")
        os.makedirs(destDir_test, exist_ok=True)
        for test_obj in X_test:
            file_name = test_obj.get("file_name")
            source = os.path.join(image_locate, file_name)
            destination = os.path.join(destDir_test, file_name)
            locate_images(source, destination)


@app.command()
def delete(
    config: str = typer.Argument(..., help="Path to category manage config file"),
    ann_path: str = typer.Argument(..., help="Path to COCO annotations file")
):
    '''
    This code referes to COCO-Assistant > remove_cat.
    '''

    with open(config, 'r') as file:
        config_catman = yaml.safe_load(file)
    
    # list of cagetories to be removed
    rcats = config_catman['delete']

    coco = COCO(ann_path)

    # Gives you a list of category ids of the categories to be removed
    catids_remove = coco.getCatIds(catNms=rcats)

    if len(catids_remove) == 0:
        print('Nothing to be removed.')
        return

    # Gives you a list of ids of annotations that contain those categories
    annids_remove = coco.getAnnIds(catIds=catids_remove)

    # Get keep category ids
    catids_keep = list(set(coco.getCatIds()) - set(catids_remove))
    # Get keep annotation ids
    annids_keep = list(set(coco.getAnnIds()) - set(annids_remove))

    with open(ann_path) as it:
        ann = json.load(it)

    del ann["categories"]
    ann["categories"] = coco.loadCats(catids_keep)
    del ann["annotations"]
    ann["annotations"] = coco.loadAnns(annids_keep)

    directory = os.path.dirname(ann_path)
    filename = os.path.splitext(os.path.basename(ann_path))[0]
    with open(os.path.join(directory, filename + '_delete.json'), "w") as oa:
        json.dump(ann, oa, indent=4)

    print('Successfully deleted the desired categories.')


@app.command()
def process(
    config: str = typer.Argument(..., help="Path to category manage config file"),
    ann_path: str = typer.Argument(..., help="Path to COCO annotations file")
):
    with open(config, 'r') as file:
        config_catman = yaml.safe_load(file)
    
    # list of cagetories to be processed
    pcat = config_catman['process']

    with open(ann_path, 'r') as file:
        ann = json.load(file)
    
    unique_categories = {}
    convert_category_id = {}

    for category in ann['categories']:
        if category["name"] in pcat:
            category["name"] = pcat[category["name"]]

            # Check if category name already exists in the dictionary
            if category["name"] in unique_categories:
                # Category name already exists, update relevant attribute
                existing_category = unique_categories[category["name"]]
                existing_category_id = existing_category['id']

                convert_category_id[category["id"]] = existing_category_id
            else:
                # Category name is unique, add it to the dictionary
                cat_id = len(unique_categories)
                convert_category_id[category["id"]] = cat_id
                category["id"] = cat_id
                unique_categories[category["name"]] = category

    # Replace the categories in the Coco data
    ann['categories'] = list(unique_categories.values())

    for annotation in ann["annotations"]:
        annotation["category_id"] = convert_category_id[annotation["category_id"]]

    directory = os.path.dirname(ann_path)
    filename = os.path.splitext(os.path.basename(ann_path))[0]
    with open(os.path.join(directory, filename + '_process.json'), "w") as oa:
        json.dump(ann, oa, indent=4)

    print('Successfully processed the categories and annotations.')


@app.command()
def convertjsonformat(
    json_aihub_dir: str = typer.Argument(..., help="directory of AI Hub json files"),
    json_coco_dir: str = typer.Argument(..., help="directory to save converted COCO json file"),
):
    json_files = [file for file in os.listdir(json_aihub_dir) if file.endswith(".json")]
    json_files.sort()

    coco = {
                "info": {},
                "licenses": [
                    {
                        "id": 0,
                        "name": "",
                        "url": ""
                    }
                ],
                "categories": [],
                "images": [],
                "annotations": []
            }

    for aihub_file in tqdm(json_files, desc='Processing', unit='item'):
        if os.path.isfile(os.path.join(json_aihub_dir, aihub_file)):
            # Load the JSON file
            with open(os.path.join(json_aihub_dir, aihub_file), "r") as file:
                aihub = json.load(file)

            # Add Info
            if "version" in aihub:
                coco["info"]["version"] = aihub["version"]
            if "flags" in aihub:
                coco["info"]["flags"] = aihub["flags"]

            # Add Image data
            image_data = {
                "id": len(coco["images"]),
                "license": 0
            }
            if "imagePath" in aihub:
                image_data["file_name"] = aihub["imagePath"]
            if "imageHeight" in aihub:
                image_data["height"] = aihub["imageHeight"]
            if "imageWidth" in aihub:
                image_data["width"] = aihub["imageWidth"]
            if "imageData" in aihub:
                image_data["data"] = aihub["imageData"]
            if "file_attributes" in aihub:
                image_data["date_captured"] = aihub["file_attributes"]["date"]
            if "growth_indicators" in aihub:
                image_data["growth_indicators"] = aihub["growth_indicators"]
            if "file_attributes" in aihub:
                image_data["file_attributes"] = aihub["file_attributes"]
            coco["images"].append(image_data)

            if "shapes" in aihub:
                for shape in aihub["shapes"]:
                    shape_label = shape["label"]

                    # Check if the shape label is already present in categories
                    category_id = None
                    for category in coco["categories"]:
                        if category["name"] == shape_label:
                            category_id = category["id"]
                            break
                    
                    # If the shape label is not present in categories, add it
                    if category_id is None:
                        category_id = len(coco["categories"])
                        coco["categories"].append({
                            "id": category_id,
                            "name": shape_label,
                            "supercategory": shape["group_id"]
                        })

                    # Add annotation
                    points = shape["points"]
                    annotation = {
                        "id": len(coco["annotations"]),
                        "image_id": image_data["id"],
                        "category_id": category_id,
                        "bbox": [],
                        "area": 0,
                        "segmentation": [],
                        "iscrowd": 0
                    }
                    if shape["shape_type"] == "rectangle":
                        annotation["bbox"] = [points[0][0], \
                                                points[0][1], \
                                                points[1][0] - points[0][0], \
                                                points[1][1] - points[0][1]]
                        annotation["area"] = (points[1][0] - points[0][0]) * \
                                             (points[1][1] - points[0][1])
                        annotation["segmentation"].append([
                            points[0][0], points[0][1],
                            points[1][0], points[0][1],
                            points[1][0], points[1][1],
                            points[0][0], points[1][1]
                        ])
                    elif shape["shape_type"] == "polygon":
                        minX = maxX = points[0][0]
                        minY = maxY = points[0][1]
                        segment = []
                        for point in points:
                            # For annotation > segmentation
                            segment.extend(point)

                            # For annotation > bbox
                            minX = min(minX, point[0])
                            minY = min(minY, point[1])
                            maxX = max(maxX, point[0])
                            maxY = max(maxY, point[1])
                        annotation["bbox"] = [minX, minY, maxX - minX, maxY - minY]
                        annotation["segmentation"].append(segment)

                        area = 0.0
                        for i in range(len(points)):
                            x1, y1 = points[i]
                            x2, y2 = points[(i + 1) % len(points)]
                            area += (x1 * y2 - x2 * y1)
                        annotation["area"] = abs(area) * 0.5
                        
                    coco["annotations"].append(annotation)    
        else:
            print(f"{os.path.join(json_aihub_dir, aihub_file)} does not exist.")

    # Save the Python object as JSON
    with open(os.path.join(json_coco_dir, f"{os.path.basename(json_aihub_dir)}.json"), "w") as file:
        json.dump(coco, file, indent=4)

    print("Successfully converted AiHub json format to COCO json format")


@app.command()
def replaceimgformat(
    annotation: str = typer.Argument(..., help="COCO json annotation file"),
    format: str = typer.Argument(..., help="Desired img format you want to replace")
):
    if os.path.isfile(annotation):
        with open(annotation, "r") as file:
            ann = json.load(file)
        
        # Replace the image extension to desired format
        for ann_img in ann["images"]:
            ann_img["file_name"] = ann_img["file_name"].split(".")[0] + "." + format

         # Save the Python object as JSON
        with open(annotation, "w") as file:
            json.dump(ann, file, indent=4)
    
    else:
        print(f"{annotation} does not exist.")

if __name__ == "__main__":
    app()
    # ann_path = "anns/oasis_new.json"
    # save_path = "results"
    # convert(ann_path, save_path)
