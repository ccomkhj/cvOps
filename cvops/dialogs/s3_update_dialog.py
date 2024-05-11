import os
import time
from PyQt5.QtWidgets import (
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QInputDialog,
)
from cvops.coco_operation import update as coco_update
from tools.s3_handler import download_s3_files, load_aws_credentials


class S3UpdateDialog(QDialog):
    """
    A dialog window for updating datasets stored on AWS S3 with new images and annotations.

    This dialog facilitates specifying S3 paths for new images and annotations, as well as the existing dataset's S3 base path.
    It assists in planning how new data can be merged into an existing dataset, considering a specified train-validation split ratio.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update S3 Dataset")
        layout = QVBoxLayout()

        # Initialize labels for displaying selected paths
        self.newAnnPathLabel = QLabel("New Annotation File (S3 Path): Not Selected")
        self.imgLocateLabel = QLabel("New Image Location (S3 Path): Not Selected")
        self.existingPathLabel = QLabel("Existing Dataset S3 Path: Not Specified")
        self.splitRatioLineEdit = QLineEdit("0.8")  # Default split ratio value

        # Add widgets to layout
        layout.addWidget(self.newAnnPathLabel)
        layout.addWidget(self.imgLocateLabel)
        layout.addWidget(self.existingPathLabel)
        layout.addWidget(QLabel("Split Ratio (New Data Train Size):"))
        layout.addWidget(self.splitRatioLineEdit)

        # Buttons for selecting S3 paths
        selectNewAnnPathButton = QPushButton("Select New Annotation S3 Path")
        selectImgLocateButton = QPushButton("Select New Image S3 Location")
        selectExistingPathButton = QPushButton("Select Existing Dataset S3 Path")
        updateButton = QPushButton("Update S3 Dataset")

        # Connection signals to slots
        selectNewAnnPathButton.clicked.connect(self.selectNewAnnPath)
        selectImgLocateButton.clicked.connect(self.selectImageLocation)
        selectExistingPathButton.clicked.connect(self.selectExistingPath)
        updateButton.clicked.connect(self.updateDataset)

        # Add buttons to layout
        layout.addWidget(selectNewAnnPathButton)
        layout.addWidget(selectImgLocateButton)
        layout.addWidget(selectExistingPathButton)
        layout.addWidget(updateButton)

        self.setLayout(layout)

    def selectNewAnnPath(self):
        # This method would ideally open a dialog to specify or select an S3 path.
        # Implement according to how you wish to input or select S3 paths.
        # For example, you might use a simpler QInputDialog to enter the path manually.
        path, ok = QInputDialog.getText(
            self, "Enter S3 Path", "New Annotation File S3 Path:"
        )
        if ok:
            self.newAnnPathLabel.setText(f"New Annotation File (S3 Path): {path}")

    def selectImageLocation(self):
        # Similar to selectNewAnnPath; gets S3 path for images.
        path, ok = QInputDialog.getText(
            self, "Enter S3 Path", "New Image Location S3 Path:"
        )
        if ok:
            self.imgLocateLabel.setText(f"New Image Location (S3 Path): {path}")

    def selectExistingPath(self):
        # User inputs the S3 base path of their existing dataset.
        path, ok = QInputDialog.getText(
            self, "Enter S3 Path", "Existing Dataset S3 Path:"
        )
        if ok:
            self.existingPathLabel.setText(f"Existing Dataset S3 Path: {path}")

    def updateDataset(self):
        aws_access_key_id, aws_secret_access_key = load_aws_credentials(
            "config/s3_credentials.yaml"
        )

        # Generate a unique directory for this update session based on the current timestamp
        now = int(time.time())
        current_path = os.getcwd()  # Get the current working directory
        outcome_path = os.path.join(
            current_path, f"downloads_s3/{now}"
        )  # Make outcome_path absolute

        # Prepare directories for new data
        new_data_path = os.path.join(outcome_path, "new")
        os.makedirs(
            new_data_path, exist_ok=True
        )  # Ensure the new data directory exists

        new_images_path = os.path.join(
            new_data_path, "images"
        )  # Specific path for new images
        new_ann_path = os.path.join(
            new_data_path, "annotations.json"
        )  # Assuming a single new annotation file

        # New dataset paths (assuming they are received from the Qt dialog)
        new_ann_s3_path = self.newAnnPathLabel.text().replace(
            "New Annotation File (S3 Path): ", ""
        )
        new_img_dir_s3_path = self.imgLocateLabel.text().replace(
            "New Image Directory (S3 Path): ", ""
        )
        new_bucket_name, new_ann_key = new_ann_s3_path.replace("s3://", "").split(
            "/", 1
        )
        _, new_img_dir_key = new_img_dir_s3_path.replace("s3://", "").split("/", 1)

        # Adjust download_s3_files function calls to use correct paths

        # Download new annotation file directly to its specific path
        download_s3_files(
            aws_access_key_id,
            aws_secret_access_key,
            new_bucket_name,
            new_ann_key,
            os.path.dirname(new_ann_path),  # Use the parent directory of new_ann_path
        )

        # Download new images into their specific directory
        download_s3_files(
            aws_access_key_id,
            aws_secret_access_key,
            new_bucket_name,
            new_img_dir_key,
            new_images_path,  # Use new_images_path for storing new images
        )

        new_ann_path = os.path.join(
            outcome_path, "new", os.path.basename(new_ann_key)
        )  # Path to new annotation file
        new_image_path = os.path.join(
            outcome_path, "new/images"
        )  # New images are within this directory

        # Existing dataset paths (assumed to be provided through the dialog)
        existing_dataset_s3_path = self.existingPathLabel.text().replace(
            "Existing Dataset S3 Path: ", ""
        )
        existing_bucket_name, existing_dataset_key = existing_dataset_s3_path.replace(
            "s3://", ""
        ).split("/", 1)

        # Directory for existing data within outcome_path
        existing_data_path = os.path.join(outcome_path, "existing_dataset")
        os.makedirs(
            existing_data_path, exist_ok=True
        )  # Ensure the existing data directory exists

        # Assuming download_s3_files has been adapted to accommodate directory downloads
        download_s3_files(
            aws_access_key_id,
            aws_secret_access_key,
            existing_bucket_name,
            existing_dataset_key,
            existing_data_path,  # Download everything into existing_data_path
        )

        coco_update(
            new_ann_path=new_ann_path,
            train_ann_path=os.path.join(existing_data_path, "train.json"),
            val_ann_path=os.path.join(existing_data_path, "val.json"),
            split_ratio=0.8,
            new_image_locate=new_image_path,
        )
        # MessageBox or logging
        print("Update Complete", "Dataset has been updated with files from S3.")

        QMessageBox.information(
            self, "Update Initiated", "Dataset update process has been initiated."
        )
