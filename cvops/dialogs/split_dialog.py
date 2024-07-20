import os
import datetime
from PyQt5.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QInputDialog,
)
from cvops.coco_operation import split as coco_split
from tools.s3_handler import upload_s3_files, load_aws_credentials


class SplitDialog(QDialog):
    """
    A dialog window for splitting a COCO dataset into training and validation sets.

    This dialog allows users to select an image directory and an annotation file, then specify
    a ratio for splitting the dataset. The process facilitates dividing a dataset into separate
    parts for the purpose of training and validating machine learning models, ensuring that
    there is no overlap between the training and validation datasets.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Split COCO Dataset")
        layout = QVBoxLayout()

        self.imgDirLabel = QLabel(
            "Image Directory: Not Selected"
        )  # Label for image directory
        layout.addWidget(self.imgDirLabel)

        self.annPathLabel = QLabel("Annotation File: Not Selected")
        layout.addWidget(self.annPathLabel)

        imgDirButton = QPushButton(
            "Select Image Directory"
        )  # Button for selecting the image directory
        imgDirButton.clicked.connect(self.selectImgDir)
        layout.addWidget(imgDirButton)

        annPathButton = QPushButton("Select Annotation File")
        annPathButton.clicked.connect(self.selectAnnPath)
        layout.addWidget(annPathButton)

        self.splitRatioLineEdit = QLineEdit("0.8")
        layout.addWidget(QLabel("Split Ratio (Train Size):"))
        layout.addWidget(self.splitRatioLineEdit)

        splitButton = QPushButton("Split")
        splitButton.clicked.connect(self.split)
        layout.addWidget(splitButton)

        self.setLayout(layout)

    def selectImgDir(self):  # Method to select the image directory
        directory = QFileDialog.getExistingDirectory(self, "Select Image Directory")
        if directory:
            self.imgDirLabel.setText(f"Image Directory: {directory}")

    def selectAnnPath(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Annotation File", "", "JSON files (*.json)"
        )
        if path:
            self.annPathLabel.setText(f"Annotation File: {path}")

    def split(self):
        img_dir = self.imgDirLabel.text().replace(
            "Image Directory: ", ""
        )  # Getting image directory for splitting
        ann_path = self.annPathLabel.text().replace("Annotation File: ", "")
        split_ratio = float(self.splitRatioLineEdit.text())

        if not os.path.exists(img_dir) or not os.path.exists(ann_path):
            QMessageBox.critical(
                self,
                "Error",
                "Please select a valid image directory and annotation file.",
            )
            return

        train_path = os.path.join(os.path.dirname(ann_path), "train.json")
        val_path = os.path.join(os.path.dirname(ann_path), "val.json")

        # Include the image_locate argument when calling coco_split
        coco_split(
            ann_path=ann_path,
            train_path=train_path,
            test_path=val_path,
            split=split_ratio,
            image_locate=img_dir,  # Passing the selected image directory
            independent=True,
        )

        self.prompt_s3_upload(train_path, val_path)

        QMessageBox.information(self, "Split", "Dataset split successfully.")

    def prompt_s3_upload(self, train_path, val_path):
        # Prompt the user for S3 upload
        upload_reply = QMessageBox.question(
            self,
            "Upload to S3",
            "Would you like to upload the results to an AWS S3 bucket?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if upload_reply == QMessageBox.Yes:
            s3_uri, ok = QInputDialog.getText(
                self,
                "S3 URI",
                "Enter the S3 base URI (e.g., s3://hexa-cv-dataset/Fragaria × ananassa/fruit_detection/):",
            )
            if ok and s3_uri:

                dataset_description, ok = QInputDialog.getText(
                    self,
                    "Dataset Description",
                    "Enter a one-line sentence to describe this dataset:",
                )

                try:
                    # Extract bucket name and path from s3_uri
                    if not s3_uri.startswith("s3://"):
                        raise ValueError("Invalid S3 URI. Must start with 's3://'.")

                    processed_results_path = os.path.dirname(train_path)
                    # Extract epoch time from the path
                    epoch_time = os.path.getmtime(train_path)

                    # Convert epoch time to a datetime object
                    time_obj = datetime.datetime.fromtimestamp(epoch_time)

                    # Format the datetime object into a human-readable string, e.g., "YYYY-MM-DD_HH-MM-SS"
                    time_str = time_obj.strftime("%Y-%m-%d_%H-%M-%S")

                    bucket_name, s3_key = s3_uri[5:].split("/", 1)
                    aws_access_key_id, aws_secret_access_key = load_aws_credentials()

                    # Upload files to S3
                    upload_s3_files(
                        aws_access_key_id,
                        aws_secret_access_key,
                        bucket_name,
                        processed_results_path,
                        s3_key + f"{time_str}_{dataset_description}",
                    )

                    QMessageBox.information(
                        self, "S3 Upload", "Results successfully uploaded to S3."
                    )
                except ValueError as ve:
                    QMessageBox.critical(self, "S3 Upload Error", str(ve))
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "S3 Upload Error",
                        f"Failed to upload results to S3: {str(e)}",
                    )
