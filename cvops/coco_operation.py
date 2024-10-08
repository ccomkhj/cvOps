import json
import os
from typing import Optional, List

import funcy
import numpy as np
import typer
import time
import shutil
import yaml
from tqdm import tqdm
from coco_assistant import COCO_Assistant
from coco_assistant import coco_visualiser as cocovis
from PIL import Image
from pycocotools.coco import COCO
from sklearn.model_selection import train_test_split

from tools.helpers import (
    filter_annotations,
    check_coco_sanity,
    locate_images,
    save_coco,
    get_image_files,
    has_segmentation_data,
)

import tkinter as tk
from tools.cocoviewer import (
    Data,
    StatusBar,
    SlidersBar,
    ObjectsPanel,
    Menu,
    ImagePanel,
    Controller,
)

app = typer.Typer(help="Awesome cvOps Tool.", rich_markup_mode="rich")


@app.command()
def visualize(
    img_dir: str = typer.Argument(..., help="directory of images"),
    ann: str = typer.Argument(..., help="path of annotations"),
    only_box: bool = typer.Option(False),
):
    """
    [bold green]Visualize coco sample[/bold green]

    [blue]
    Example:
    .
    ├── images_dir
    │   ├── image1
    │   ├── image2
    |   ├── image3
    |
    ├── ann_path
    [/blue]
    """

    try:
        print("Loading fiftyone, it may takes 30 secs, please wait.")
        import fiftyone as fo

        base_dir = os.getcwd()
        dataset = fo.Dataset.from_dir(
            dataset_dir=os.path.join(base_dir, img_dir),
            data_path=".",
            dataset_type=fo.types.COCODetectionDataset,
            labels_path=os.path.join(base_dir, ann),
            label_field="detections",
        )
        print(dataset)

        session = fo.launch_app(dataset)
        session.wait()

        print("Closing FiftyOne session...")
        session.close()
        # try:
        #     while True:
        #         # Your main script logic goes here
        #         user_input = input("Press 'q' to quit, or any other key to continue: ")
        #         if user_input.lower() == "q":
        #             break
        # except KeyboardInterrupt:
        #     print("\nKeyboardInterrupt detected. Exiting gracefully...")
        # finally:
        #     # Ensure graceful session closure
        #     print("Closing FiftyOne session...")
        #     session.close()

        #     print("Session closed.")

    except Exception as e:
        print(f"fiftyone failed to lunch. use pyqt based visualizer. Error: {e}")
        if has_segmentation_data(ann) and not only_box:
            cocovis.visualise_all(COCO(ann), img_dir)

        else:
            print("No segmentation found in annotation, so draw bboxes.")
            visualizebox(img_dir, ann)


@app.command()
def visualizebox(
    img_dir: str = typer.Argument(..., help="directory of images"),
    ann_path: str = typer.Argument(..., help="json file of annotations"),
):
    """
    [bold green]Visualize coco sample with only bounding box[/bold green]

    [blue]
    Example:
    .
    ├── images_dir
    │   ├── image1
    │   ├── image2
    |   ├── image3
    |
    ├── ann_path
    [/blue]
    """

    # Create COCO_Assistant object
    root = tk.Tk()
    root.title("COCO Viewer")

    print("img_dir:", img_dir)
    print("ann_path:", ann_path)
    data = Data(img_dir, ann_path)
    statusbar = StatusBar(root)
    sliders = SlidersBar(root)
    objects_panel = ObjectsPanel(root)
    menu = Menu(root)
    image_panel = ImagePanel(root)
    Controller(data, root, image_panel, statusbar, menu, objects_panel, sliders)
    root.mainloop()


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
    print("update merged.json into right format.")
    merged_coco_path = os.path.join(
        os.path.dirname(ann_dir), "results", "merged", "annotations", "merged.json"
    )
    check_coco_sanity(merged_coco_path)


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
    independent: bool = typer.Option(
        False, help="False if it's dependent to other pipeline."
    ),
):

    def save_annotations(path, info, licenses, images, annotations, categories):
        save_coco(path, info, licenses, images, annotations, categories)
        print(f"Saved {len(annotations)} entries in {path}")

    def create_image_dirs(parent_dir, subdir, images_list):
        os.makedirs(subdir, exist_ok=True)
        for img_obj in images_list:
            file_name = img_obj.get("file_name")
            source = os.path.join(image_locate, file_name)
            destination = os.path.join(subdir, file_name)
            locate_images(source, destination)

    with open(ann_path, "rt", encoding="UTF-8") as annotations_file:
        coco = json.load(annotations_file)
        info, licenses, images, annotations, categories = (
            coco["info"],
            coco.get("licenses"),
            coco["images"],
            coco["annotations"],
            coco["categories"],
        )

    images_with_annotations = funcy.lmap(lambda a: int(a["image_id"]), annotations)
    images = [i for i in images if i["id"] in images_with_annotations]

    X_train, X_test = train_test_split(images, train_size=split, shuffle=True)
    anns_train = filter_annotations(annotations, X_train)
    anns_test = filter_annotations(annotations, X_test)

    save_annotations(train_path, info, licenses, X_train, anns_train, categories)
    save_annotations(test_path, info, licenses, X_test, anns_test, categories)

    if image_locate:
        parent_train_dir = (
            os.path.dirname(train_path)
            if independent
            else os.path.dirname(os.path.dirname(train_path))
        )
        parent_val_dir = (
            os.path.dirname(test_path)
            if independent
            else os.path.dirname(os.path.dirname(test_path))
        )

        train_dir = os.path.join(
            parent_train_dir,
            "train_images" if independent else "images/new_train_images",
        )
        test_dir = os.path.join(
            parent_val_dir, "val_images" if independent else "images/new_val_images"
        )

        create_image_dirs(parent_train_dir, train_dir, X_train)
        create_image_dirs(parent_val_dir, test_dir, X_test)


@app.command()
def update(
    new_ann_path: str = typer.Argument(..., help="Path to new COCO annotations file."),
    train_ann_path: str = typer.Argument(
        ..., help="Path to existing train COCO annotations file."
    ),
    val_ann_path: str = typer.Argument(
        ..., help="Path to existing val COCO annotations file."
    ),
    split_ratio: float = typer.Argument(
        default=0.8, help="A ratio of a split; a number in (0, 1)"
    ),
    new_image_locate: Optional[str] = typer.Argument(
        default="", help="Locate images based on the split if the value is given."
    ),
):
    assert (
        validate(new_image_locate, new_ann_path) is True
    ), "Images in coco and image DIR doesn't match."

    now = int(time.time())
    current_path = os.getcwd()  # Get the current working directory
    outcome_path = os.path.join(
        current_path, f"results/{now}"
    )  # Make outcome_path absolute

    # Setup paths
    outcome_train_ann = os.path.join(outcome_path, "train", "ann")
    outcome_val_ann = os.path.join(outcome_path, "val", "ann")
    outcome_train_img = os.path.join(outcome_path, "train", "images")
    outcome_val_img = os.path.join(outcome_path, "val", "images")

    # Store the configurations
    config = {
        "time_created": time.ctime(now),
        "new_ann_path": new_ann_path,
        "new_image_locate": new_image_locate,
        "train_ann_path": train_ann_path,
        "val_ann_path": val_ann_path,
        "split_ratio": split_ratio,
        "outcome_train_ann": outcome_train_ann,
        "outcome_val_ann": outcome_val_ann,
    }

    with open("latest_update_configs.yaml", "w") as file:
        yaml.dump(config, file)

    typer.echo("Update configurations saved to latest_update_configs.yaml")

    # Create relevant folders
    os.makedirs(outcome_train_ann, exist_ok=True)
    os.makedirs(outcome_val_ann, exist_ok=True)

    # place holders to run COCO Assistant successfully. no images will be actually located to run memory efficiently.
    os.makedirs(os.path.join(outcome_train_img, "existing_train"), exist_ok=True)
    os.makedirs(os.path.join(outcome_train_img, "new_train_images"), exist_ok=True)
    os.makedirs(os.path.join(outcome_val_img, "existing_val"), exist_ok=True)
    os.makedirs(os.path.join(outcome_val_img, "new_val_images"), exist_ok=True)

    split(
        new_ann_path,
        os.path.join(outcome_train_ann, "new_train_images.json"),
        os.path.join(outcome_val_ann, "new_val_images.json"),
        split_ratio,
        new_image_locate,
    )

    # Move splitted images
    locate_images(
        train_ann_path, os.path.join(outcome_train_ann, "existing_train.json")
    )
    locate_images(val_ann_path, os.path.join(outcome_val_ann, "existing_val.json"))

    # Merge train and val coco json
    # path of outcome_train/val_img is not effective. just a place holder.
    merge(outcome_train_img, outcome_train_ann)
    merge(outcome_val_img, outcome_val_ann)


@app.command()
def separate_by_name(
    img_path: str = typer.Argument(..., help="Path to image files"),
    ann_path: str = typer.Argument(..., help="Path to COCO annotations file"),
    name_keys: List[str] = typer.Argument(...),
):
    # Load COCO annotations
    coco = COCO(ann_path)
    separated_cocos = []
    covered_img_ids = set()
    new_coco_dicts = {}

    # Get the initial counts
    initial_image_count = len(coco.getImgIds())
    initial_annotation_count = len(coco.getAnnIds())

    for name_key in name_keys:
        # Filter image ids that contain the name_key in their file name
        img_ids = [
            img_id
            for img_id in coco.getImgIds()
            if name_key in coco.loadImgs(img_id)[0]["file_name"]
        ]
        covered_img_ids.update(img_ids)

        # Load images and annotations for these image ids
        images = coco.loadImgs(img_ids)
        annotations = coco.loadAnns(coco.getAnnIds(imgIds=img_ids))
        categories = coco.loadCats(coco.getCatIds())

        # Create separate COCO annotation
        separated_coco = {
            "images": images,
            "annotations": annotations,
            "categories": categories,
        }

        # Collect the changes in a dictionary
        new_coco_dicts[name_key] = separated_coco

    # Check for uncovered images
    all_img_ids = set(coco.getImgIds())
    uncovered_img_ids = all_img_ids - covered_img_ids
    if uncovered_img_ids:
        uncovered_images = coco.loadImgs(list(uncovered_img_ids))
        uncovered_filenames = [img["file_name"] for img in uncovered_images]
        raise ValueError(f"Uncovered images found: {uncovered_filenames}")

    # Verify the counts
    post_image_count = sum(
        len(sep_coco["images"]) for sep_coco in new_coco_dicts.values()
    )
    post_annotation_count = sum(
        len(sep_coco["annotations"]) for sep_coco in new_coco_dicts.values()
    )

    if initial_image_count != post_image_count:
        raise ValueError(
            f"Image count mismatch: {initial_image_count} != {post_image_count}"
        )

    if initial_annotation_count != post_annotation_count:
        raise ValueError(
            f"Annotation count mismatch: {initial_annotation_count} != {post_annotation_count}"
        )

    # Apply the changes after validation
    parent_dir = os.path.dirname(img_path)
    for name_key, separated_coco in new_coco_dicts.items():
        # Create directory for name_key if it doesn't exist
        os.makedirs(os.path.join(parent_dir, name_key), exist_ok=True)

        # Move images to respective directories
        for img in separated_coco["images"]:
            src = os.path.join(img_path, img["file_name"])
            dst = os.path.join(parent_dir, name_key, img["file_name"])
            if os.path.exists(src):  # Ensure the file exists before copying
                shutil.copy(src, dst)

        # Save separate COCO file
        coco_file_name = f"{name_key}.json"
        with open(os.path.join(parent_dir, coco_file_name), "w") as f:
            json.dump(separated_coco, f, indent=2)
        separated_cocos.append(coco_file_name)

    return separated_cocos


@app.command()
def validate(
    img_path: str = typer.Argument(..., help="Path to image files"),
    ann_path: str = typer.Argument(..., help="Path to COCO annotations file"),
):
    """
    This code validates if all images in coco exist in img_path.
    """

    filenames_in_folder = get_image_files(img_path)
    filenames_in_folder = [os.path.basename(i) for i in filenames_in_folder]

    coco = COCO(ann_path)

    img_ids = coco.getImgIds()

    # Get filenames for each image
    filenames_in_coco = [
        os.path.basename(coco.loadImgs(image_id)[0]["file_name"])
        for image_id in img_ids
    ]

    if sorted(filenames_in_folder) == sorted(filenames_in_coco):
        print("Filenames in folder and filenames in coco exactly matches!!")
        return True
    else:
        # Convert lists to sets
        set_coco = set(filenames_in_coco)
        set_folder = set(filenames_in_folder)

        # Elements unique to filenames_in_coco
        unique_to_coco = set_coco - set_folder

        # Elements unique to filenames_in_folder
        unique_to_folder = set_folder - set_coco

        # Combine the unique elements from both lists
        result = list(unique_to_coco.union(unique_to_folder))

        print("This files are not matching!! Please double check!!", result)
        return False


@app.command()
def delete(
    config: str = typer.Argument(..., help="Path to category manage config file"),
    ann_path: str = typer.Argument(..., help="Path to COCO annotations file"),
):
    """
    This code referes to COCO-Assistant > remove_cat.
    """

    with open(config, "r") as file:
        config_catman = yaml.safe_load(file)

    # list of cagetories to be removed
    rcats = config_catman["delete"]

    coco = COCO(ann_path)

    # Gives you a list of category ids of the categories to be removed
    catids_remove = coco.getCatIds(catNms=rcats)

    if len(catids_remove) == 0:
        print("Nothing to be removed.")
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
    with open(os.path.join(directory, filename + "_delete.json"), "w") as oa:
        json.dump(ann, oa, indent=4)

    print("Successfully deleted the desired categories.")


@app.command()
def postupdate(
    config_file: bool = typer.Option(
        False, "--use-config", help="Use the latest_update_configs.yaml for parameters"
    ),
    existing_samples_dir: str = typer.Option(
        None, help="Path to the existing samples directory"
    ),
    results_path: str = typer.Option(
        None, help="Path to results directory containing the merged JSON annotations"
    ),
):
    """
    Combines new and existing image datasets from specified directories and moves corresponding annotations to the processed_result directory.
    """

    if not all([existing_samples_dir, results_path]):
        typer.echo(
            "Missing required directories information. Ensure you provide all paths or a valid YAML configuration file."
        )
        raise typer.Exit(code=1)

    # Following the original script logic using provided or YAML-specified paths
    new_train_images_dir = os.path.join(results_path, "train/images/new_train_images")
    new_val_images_dir = os.path.join(results_path, "val/images/new_val_images")
    prev_train_images_dir = os.path.join(existing_samples_dir, "train_images")
    prev_val_images_dir = os.path.join(existing_samples_dir, "val_images")

    new_train_ann_path = os.path.join(
        results_path, "train/results/merged/annotations/merged.json"
    )
    new_val_ann_path = os.path.join(
        results_path, "val/results/merged/annotations/merged.json"
    )

    now = int(time.time())
    processed_result_dir = os.path.join("processed_results", str(now))
    processed_train_dir = os.path.join(processed_result_dir, "train_images")
    processed_val_dir = os.path.join(processed_result_dir, "val_images")

    # Implemented logic remains as original
    os.makedirs(processed_train_dir, exist_ok=True)
    os.makedirs(processed_val_dir, exist_ok=True)

    # Function to copy images
    def copy_images(source_dir, dest_dir):
        # Handling possible non-existent source directory
        if not os.path.isdir(source_dir):
            print(f"Source directory not found: {source_dir}")
            return False
        for filename in os.listdir(source_dir):
            source_path = os.path.join(source_dir, filename)
            dest_path = os.path.join(dest_dir, filename)
            if not os.path.exists(dest_path):
                shutil.copy(source_path, dest_path)
        return True

    # Copy images from sources to destinations
    if (
        not copy_images(new_train_images_dir, processed_train_dir)
        or not copy_images(prev_train_images_dir, processed_train_dir)
        or not copy_images(new_val_images_dir, processed_val_dir)
        or not copy_images(prev_val_images_dir, processed_val_dir)
    ):
        typer.echo("One or more errors occurred during image copying.")
        raise typer.Exit(code=1)

    shutil.copy(new_train_ann_path, os.path.join(processed_result_dir, "train.json"))
    shutil.copy(new_val_ann_path, os.path.join(processed_result_dir, "val.json"))

    typer.echo("Post-processing completed successfully.")

    return (
        os.path.join(processed_result_dir, "train.json"),
        processed_train_dir,
        os.path.join(processed_result_dir, "val.json"),
        processed_val_dir,
    )


@app.command()
def process(
    config: str = typer.Argument(..., help="Path to category manage config file"),
    ann_path: str = typer.Argument(..., help="Path to COCO annotations file"),
):
    with open(config, "r") as file:
        config_catman = yaml.safe_load(file)

    # list of cagetories to be processed
    pcat = config_catman["process"]

    with open(ann_path, "r") as file:
        ann = json.load(file)

    unique_categories = {}
    convert_category_id = {}

    for category in ann["categories"]:
        if category["name"] in pcat:
            category["name"] = pcat[category["name"]]

            # Check if category name already exists in the dictionary
            if category["name"] in unique_categories:
                # Category name already exists, update relevant attribute
                existing_category = unique_categories[category["name"]]
                existing_category_id = existing_category["id"]

                convert_category_id[category["id"]] = existing_category_id
            else:
                # Category name is unique, add it to the dictionary
                cat_id = len(unique_categories)
                convert_category_id[category["id"]] = cat_id
                category["id"] = cat_id
                unique_categories[category["name"]] = category

    # Replace the categories in the Coco data
    ann["categories"] = list(unique_categories.values())

    for annotation in ann["annotations"]:
        annotation["category_id"] = convert_category_id[annotation["category_id"]]

    directory = os.path.dirname(ann_path)
    filename = os.path.splitext(os.path.basename(ann_path))[0]
    with open(os.path.join(directory, filename + "_process.json"), "w") as oa:
        json.dump(ann, oa, indent=4)

    print("Successfully processed the categories and annotations.")


@app.command()
def replaceimgformat(
    annotation: str = typer.Argument(..., help="COCO json annotation file"),
    format: str = typer.Argument(..., help="Desired img format you want to replace"),
):
    """
    This function opens a provided COCO JSON annotation file, changes the format of the image filenames
    included in the 'images' key of the JSON. The new format is based on the format argument provided
    by the user. Once changes are made, it saves the Python object back as a JSON file.

    If the annotation file does not exist at the specified path, a printed message will indicate so.

    Parameters:
    annotation (str): The path to a .json file containing COCO format annotations.
    format (str): The desired image format to replace the current image format in the annotation file.

    Returns:
    None. The function operates in-place on the provided JSON file.
    """
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
