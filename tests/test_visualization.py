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


def test_visualize_with_detections(coco_data_detections):
    """
    Test the 'visualize' CLI command on a dataset with detections to ensure it executes successfully.

    Args:
    - coco_data_detections: fixture - Paths for the detection dataset's images and annotation.
    """
    img_dir, ann_file = coco_data_detections
    result = runner.invoke(app, ["visualize", img_dir, ann_file])
    assert result.exit_code == 0


def test_visualize_with_segmentations(coco_data_segmentations):
    """
    Test the 'visualize' CLI command on a dataset with segmentations to ensure it executes successfully.

    Args:
    - coco_data_segmentations: fixture - Paths for the segmentation dataset's images and annotation.
    """
    img_dir, ann_file = coco_data_segmentations
    result = runner.invoke(app, ["visualize", img_dir, ann_file])
    assert result.exit_code == 0
