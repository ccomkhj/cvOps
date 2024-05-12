"""
Huijo Kim (huijo@hexafarms.com)
"""

from typer.testing import CliRunner
import pytest
from cvops.coco_operation import app
import os
import json
import shutil
from pathlib import Path

runner = CliRunner()


@pytest.fixture
def coco_data_detections():
    return "data/detections_1/images", "data/detections_1/annotations.json"


@pytest.fixture
def coco_data_segmentations():
    return "data/segmentations_2/images", "data/segmentations_2/annotations.json"


def test_merge_command(coco_data_detections, coco_data_segmentations, tmp_path):
    """
    Test the 'merge' CLI command to ensure it successfully merges COCO datasets.
    This test creates a merged image and annotation directory from two sample COCO datasets and
    then runs the 'merge' command. It verifies successfully execution and the presence of expected
    merged contents.

    Args:
    - coco_data_detections: fixture - Paths for the detection dataset's images and annotation.
    - coco_data_segmentations: fixture - Paths for the segmentation dataset's images and annotations.
    - tmp_path: fixture - Temporary directory provided by pytest for test file creation.
    """

    def copy_directory_contents(src_dir, dst_dir):
        """
        Copies all files from source directory to destination directory.

        Args:
        - src_dir (Union[str, Path]): Source directory, can be a string path or a Path object.
        - dst_dir (Union[str, Path]): Destination directory, can be a string path or a Path object.
        """
        # Ensure src_dir and dst_dir are Path objects
        src_dir = Path(src_dir)
        dst_dir = Path(dst_dir)

        # Making sure the dst_dir exists
        dst_dir.mkdir(parents=True, exist_ok=True)

        for item in src_dir.iterdir():
            if item.is_file():
                shutil.copy(item, dst_dir / item.name)

    # Parsing directories and files
    img_dir1, ann_file1 = coco_data_detections
    img_dir2, ann_file2 = coco_data_segmentations
    img_dir1, ann_file1, img_dir2, ann_file2 = (
        Path(img_dir1),
        Path(ann_file1),
        Path(img_dir2),
        Path(ann_file2),
    )

    merged_img_dir = tmp_path / "merged_images"
    merged_ann_dir = tmp_path / "merged_annotations"

    # Copy image directories to their respective subdirectories within the merged directory
    copy_directory_contents(img_dir1, merged_img_dir / "part1")
    copy_directory_contents(img_dir2, merged_img_dir / "part2")

    merged_ann_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(ann_file1, merged_ann_dir / "part1.json")
    shutil.copy(ann_file2, merged_ann_dir / "part2.json")

    # Your CLI command to merge (placeholder for actual function call)
    result = runner.invoke(app, ["merge", str(merged_img_dir), str(merged_ann_dir)])

    # Verify the command executed successfully
    assert result.exit_code == 0

    # Assertions to ensure datasets are merged correctly should be adjusted based on the new structure
    # Since we now have separate subdirectories, we may want to check the counts individually in each subdirectory

    total_img_count_dir1 = sum(
        1 for _ in (merged_img_dir / "part1").iterdir() if _.is_file()
    )
    total_img_count_dir2 = sum(
        1 for _ in (merged_img_dir / "part1").iterdir() if _.is_file()
    )
    original_img_count_dir1 = sum(1 for _ in img_dir1.iterdir() if _.is_file())
    original_img_count_dir2 = sum(1 for _ in img_dir2.iterdir() if _.is_file())

    assert total_img_count_dir1 == original_img_count_dir1
    assert total_img_count_dir2 == original_img_count_dir2

    # Load the merged.json file to check its contents
    merged_ann_file_path = tmp_path / "results/merged/annotations/merged.json"

    # Check if the file exists first
    assert merged_ann_file_path.exists(), "Merged annotation file does not exist."

    # Load the json content
    with open(merged_ann_file_path, "r") as f:
        merged_data = json.load(f)

    # For simplicity, let's say we expect at least one image and one annotation
    assert len(merged_data["images"]) > 0, "Expected at least one image in 'images'."
    assert (
        len(merged_data["annotations"]) > 0
    ), "Expected at least one annotation in 'annotations'."


def test_split_command_basic(coco_data_detections, tmp_path):
    """
    Test the 'split' CLI command's basic functionality to ensure it successfully splits a COCO dataset.
    It divides the dataset based on a provided ratio and checks if the split resulted in the creation
    of expected training and testing annotation files.

    Args:
    - coco_data_detections: fixture - Paths for the detection dataset's images and annotation.
    - tmp_path: fixture - Temporary directory provided by pytest for test file creation.
    """
    _, ann_file = coco_data_detections
    os.makedirs(tmp_path / "ann", exist_ok=True)
    train_ann_path = tmp_path / "ann/train_annotations.json"
    test_ann_path = tmp_path / "ann/test_annotations.json"
    result = runner.invoke(
        app, ["split", ann_file, str(train_ann_path), str(test_ann_path), "0.8"]
    )
    assert result.exit_code == 0
    assert train_ann_path.exists()
    assert test_ann_path.exists()


def test_split_with_image_location(coco_data_detections, tmp_path):
    """
    Test the 'split' CLI command with image location specified to ensure it successfully splits a COCO dataset
    and relocates images accordingly. It checks for the successful split of annotations and the creation
    of new training and validation image directories.

    Args:
    - coco_data_detections: fixture - Paths for the detection dataset's images and annotation.
    - tmp_path: fixture - Temporary directory provided by pytest for test file creation.
    """
    img_dir, ann_file = coco_data_detections
    os.makedirs(tmp_path / "ann", exist_ok=True)
    train_ann_path = tmp_path / "ann/train_annotations.json"
    test_ann_path = tmp_path / "ann/test_annotations.json"
    result = runner.invoke(
        app,
        ["split", ann_file, str(train_ann_path), str(test_ann_path), "0.7", img_dir],
    )
    assert result.exit_code == 0
    assert tmp_path.joinpath("images/new_train_images").exists()
    assert tmp_path.joinpath("images/new_val_images").exists()
