from typer.testing import CliRunner
import pytest
from cvops.coco_operation import app
import os

runner = CliRunner()

@pytest.fixture
def coco_data_detections():
    return "data/detections_1/images", "data/detections_1/annotations.json"

@pytest.fixture
def coco_data_segmentations():
    return "data/segmentations_2/images", "data/segmentations_2/annotations.json"

def test_visualize_with_detections(coco_data_detections):
    img_dir, ann_file = coco_data_detections
    result = runner.invoke(app, ["visualize", img_dir, ann_file])
    assert result.exit_code == 0

def test_visualize_with_segmentations(coco_data_segmentations):
    img_dir, ann_file = coco_data_segmentations
    result = runner.invoke(app, ["visualize", img_dir, ann_file])
    assert result.exit_code == 0
    
def test_split_command_basic(coco_data_detections, tmp_path):
    _, ann_file = coco_data_detections
    os.makedirs(tmp_path / "ann", exist_ok=True)
    train_ann_path = tmp_path / "ann/train_annotations.json"
    test_ann_path = tmp_path / "ann/test_annotations.json"
    result = runner.invoke(app, ["split", ann_file, str(train_ann_path), str(test_ann_path), "0.8"])
    assert result.exit_code == 0
    assert train_ann_path.exists()
    assert test_ann_path.exists()

def test_split_with_image_location(coco_data_detections, tmp_path):
    img_dir, ann_file = coco_data_detections
    os.makedirs(tmp_path / "ann", exist_ok=True)
    train_ann_path = tmp_path / "ann/train_annotations.json"
    test_ann_path = tmp_path / "ann/test_annotations.json"
    result = runner.invoke(app, ["split", ann_file, str(train_ann_path), str(test_ann_path), "0.7", img_dir])
    assert result.exit_code == 0
    assert tmp_path.joinpath("images/new_train_images").exists()
    assert tmp_path.joinpath("images/new_val_images").exists()

# def test_merge_command(coco_data_detections, coco_data_segmentations, tmp_path):
#     img_dir1, ann_file1 = coco_data_detections
#     img_dir2, ann_file2 = coco_data_segmentations
#     merged_img_dir = tmp_path / "merged_images"
#     merged_ann_dir = tmp_path / "merged_annotations"

#     # Simulate copying or creating fragmented datasets in the tmp_path
#     # For simplicity, this step is abstracted

#     result = runner.invoke(app, ["merge", str(merged_img_dir), str(merged_ann_dir)])
#     assert result.exit_code == 0
#     # Perform checks to ensure datasets are merged correctly