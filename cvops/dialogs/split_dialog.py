import os
from PyQt5.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QLineEdit,
)
from cvops.coco_operation import split as coco_split


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
        # GPT: Add dummy function to upload files into S3
        QMessageBox.information(self, "Split", "Dataset split successfully.")
