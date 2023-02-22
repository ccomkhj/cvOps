import glob
import os
import numpy as np
from PIL import Image
from typing import Dict, List
import json
import funcy


def load(path: str) -> List[str]:
    """load files

    Args:
        path (str): path of directory

    Returns:
        List[str]: list of file location
    """
    anns = sorted(glob.glob(os.path.join(path, "*")), key=os.path.basename)

    return anns


def palette2mask(ann: str, conv: Dict[int, List]) -> np.ndarray:
    """convert 3channel array to 1 channel array using conv

    Args:
        ann (str): annotation file path
        conv (Dict[int, List]): {mask_value}: [R, G, B]

    Returns:
        np.ndarray: 1C mask
    """
    palette = np.array(Image.open(ann))[..., :3]  # get rid of transparency

    drawing = np.zeros(palette.shape[:2])
    for key, value in conv.items():
        region = np.all(palette == value, axis=-1)
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
