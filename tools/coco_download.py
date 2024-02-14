from pathlib import Path
import fiftyone.zoo as foz
import fiftyone.types.dataset_types as fot 
from pathlib import Path
import tempfile

# Download coco samples
def coco_data():
    # Use FiftyOne to download the dataset
    dataset = foz.load_zoo_dataset(
        "coco-2017",
        split="train",
        label_types=["detections", "segmentations"],
        classes=["potted plant", "apple"],
        # classes=["person", "car"],
        max_samples=10,
    )

    # FiftyOne stores the dataset in its own directory structure. For this test,
    # we need the path to the downloaded images and the annotations.

    # Create a temporary directory to store images
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        img_dir = Path(tmp_dir_name) / 'images'
        img_dir.mkdir(parents=True, exist_ok=True)

        # Copy the images from the FiftyOne dataset to the temporary directory
        for sample in dataset.take(10):
            img_path = sample.filepath
            new_img_path = img_dir / Path(img_path).name
            new_img_path.write_bytes(Path(img_path).read_bytes())

        # Prepare annotations in COCO format. FiftyOne can export datasets in various formats,
        # including COCO. Here, we're simulating an export to a temporary JSON file.
        ann_file = img_dir.parent / "annotations.json"
        dataset.export(
            export_dir=str(img_dir.parent),  # Convert Path object to str
            dataset_type=fot.COCODetectionDataset(),
            labels_path=str(ann_file),  # Convert Path object to str
            split="train",
            label_field="detections",
        )

        yield str(img_dir), str(ann_file)