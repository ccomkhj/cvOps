import os
from PyQt5.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QCheckBox,
)

from coco_assistant import COCO_Assistant
from pycocotools.coco import COCO


class MergeDialog(QDialog):
    """
    A dialog window for merging multiple COCO datasets into a single dataset.

    The dialog facilitates the merging process by allowing users to select directories
    for the images and annotations of the datasets they wish to merge. Users can
    optionally choose to merge the images as well. This feature is particularly useful
    for tasks that involve consolidating datasets from different sources to create a
    larger, comprehensive dataset for training or evaluation purposes.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Merge COCO Datasets")
        layout = QVBoxLayout()

        self.imgDirLabel = QLabel("Image Directory: Not Selected")
        layout.addWidget(self.imgDirLabel)

        self.annDirLabel = QLabel("Annotation Directory: Not Selected")
        layout.addWidget(self.annDirLabel)

        imgDirButton = QPushButton("Select Image Directory")
        imgDirButton.clicked.connect(self.selectImgDir)
        layout.addWidget(imgDirButton)

        annDirButton = QPushButton("Select Annotation Directory")
        annDirButton.clicked.connect(self.selectAnnDir)
        layout.addWidget(annDirButton)

        self.mergeImagesCheckBox = QCheckBox("Merge Images")
        layout.addWidget(self.mergeImagesCheckBox)

        mergeButton = QPushButton("Merge")
        mergeButton.clicked.connect(self.merge)
        layout.addWidget(mergeButton)

        self.setLayout(layout)

    def selectImgDir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Image Directory")
        if directory:
            self.imgDirLabel.setText(f"Image Directory: {directory}")

    def selectAnnDir(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Select Annotation Directory"
        )
        if directory:
            self.annDirLabel.setText(f"Annotation Directory: {directory}")

    def merge(self):
        img_dir = self.imgDirLabel.text().replace("Image Directory: ", "")
        ann_dir = self.annDirLabel.text().replace("Annotation Directory: ", "")

        if not os.path.exists(img_dir) or not os.path.exists(ann_dir):
            QMessageBox.critical(self, "Error", "Please select valid directories.")
            return

        cas = COCO_Assistant(img_dir, ann_dir)
        cas.merge()
        print("update merged.json into right format.")
        merged_coco_path = os.path.join(
            os.path.dirname(ann_dir), "results", "merged", "annotations", "merged.json"
        )
        try:
            coco_file = COCO(merged_coco_path)
            # Iterate over annotation IDs
            for ann_id in coco_file.anns:
                ann = coco_file.anns[ann_id]
                # Check if the 'segmentation' key exists and if it's empty
                if "segmentation" in ann and ann["segmentation"] == [[]]:
                    # Replace empty segmentation with an empty list
                    ann["segmentation"] = []

            # Now coco_file.anns should have empty segmentations replaced with []
            QMessageBox.information(self, "Merge", "Datasets merged successfully.")
        except TypeError:
            QMessageBox.information(self, "Merge", "Datasets merge fail!")
