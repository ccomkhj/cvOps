import glob
import os
import numpy as np
from PIL import Image
from typing import Dict, List


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
