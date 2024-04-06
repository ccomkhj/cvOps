import glob
import os
import numpy as np
from pathlib import Path
from PIL import Image
from typing import Dict, List
import json
import funcy
from pycocotools.coco import COCO
import shutil

def load(path: str) -> List[str]:
    """load files

    Args:
        path (str): path of directory

    Returns:
        List[str]: list of file location
    """
    anns = sorted(glob.glob(os.path.join(path, "*")), key=os.path.basename)

    return anns


def palette2mask(ann: str, conv: Dict[int, List[int]]) -> np.ndarray:
    """
    Convert 3channel array to 1 channel array using conv

    Args:
        ann (str): annotation file path
        conv (Dict[int, List[int]]): dictionary with mask_value as keys and lists of RGB values as values

    Returns:
        np.ndarray: 1-channel mask
    """

    # Check if file exists
    try:
        img = Image.open(ann)
    except FileNotFoundError:
        print(f"No file found at {ann}")
        return np.array([])

    img = img.convert('RGB')
    palette = np.array(img)

    drawing = np.zeros(palette.shape[:2], dtype=int)

    for key, value in conv.items():
        region = np.all(palette == np.array(value), axis=-1)
        drawing[region] = key

    return drawing


def save_coco(file, info, licenses, images, annotations, categories):
    with open(file, "wt", encoding="UTF-8") as coco:
        json.dump(
            {
                "info": info,
                "licenses": licenses,
                "images": images,
                "annotations": annotations,
                "categories": categories,
            },
            coco,
            indent=2,
            sort_keys=True,
        )


def filter_annotations(annotations, images):
    image_ids = funcy.lmap(lambda i: int(i["id"]), images)
    return funcy.lfilter(lambda a: int(a["image_id"]) in image_ids, annotations)


def filter_images(images, annotations):

    annotation_ids = funcy.lmap(lambda i: int(i["image_id"]), annotations)

    return funcy.lfilter(lambda a: int(a["id"]) in annotation_ids, images)

def locate_images(source: str, destination: str) -> None:
    """locate images based on source and destination path."""
    
    try:
        shutil.copy(source, destination)
        print(f"File copied successfully at {destination}")
    
    # If source and destination are same
    except shutil.SameFileError:
        print("Source and destination represents the same file.")
    
    # If there is any permission issue
    except PermissionError:
        print("Permission denied.")
    
    # For other errors
    except:
        print("Error occurred while copying file.")
        
        
def get_image_files(directory):
    image_extensions = ['.jpg', '.jpeg', '.png']
    directory_path = Path(directory)

    image_files = [file.__str__() for file in directory_path.glob(
        '*') if file.suffix.lower() in image_extensions]

    return image_files

def has_segmentation_data(ann_path: str) -> bool:
    """
    Checks if the COCO annotation file contains segmentation data.
    """
    coco = COCO(ann_path)
    catIds = coco.getCatIds()
    imgIds = coco.getImgIds()
    for imgId in imgIds:
        annIds = coco.getAnnIds(imgIds=imgId, catIds=catIds, iscrowd=None)
        anns = coco.loadAnns(annIds)
        for ann in anns:
            if 'segmentation' in ann and any(ann['segmentation']):
                # segmentation exists and it's not empty, then return True.
                return True
    return False