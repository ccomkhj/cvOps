import os
from PyQt5.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QCheckBox,
    QDialog,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
)
from cvops.coco_operation import visualize as coco_visualize


class VisualizeDialog(QDialog):
    """
    A dialog window for visualizing annotations with COCO format.

    Allows users to select an image directory and an annotation file (in JSON format),
    and then visualizes the specified annotations on the images. This is useful for
    verifying the correctness of annotations or for data analysis purposes.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Visualize")
        layout = QVBoxLayout()

        self.imgDirLabel = QLabel("Image Directory: Not Selected")
        layout.addWidget(self.imgDirLabel)

        self.annPathLabel = QLabel("Annotation File: Not Selected")
        layout.addWidget(self.annPathLabel)

        imgDirButton = QPushButton("Select Image Directory")
        imgDirButton.clicked.connect(self.selectImgDir)
        layout.addWidget(imgDirButton)

        annPathButton = QPushButton("Select Annotation File")
        annPathButton.clicked.connect(self.selectAnnPath)
        layout.addWidget(annPathButton)

        # Button for visualizing segmentations
        visualizeButton = QPushButton("Visualize")
        visualizeButton.clicked.connect(self.visualize)
        layout.addWidget(visualizeButton)

        self.showOnlyBoxCheckBox = QCheckBox("Show Only Bounding Boxes")
        layout.addWidget(self.showOnlyBoxCheckBox)

        # Add QLabel for additional information
        additional_info_label = QLabel(
            "By default, the application uses FiftyOne for visualization. "
            "However, if FiftyOne is unavailable, "
            "cvops native visualizer is used instead."
        )
        additional_info_label.setWordWrap(True)
        layout.addWidget(additional_info_label)

        self.setLayout(layout)

    def selectImgDir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Image Directory")
        if directory:
            self.imgDirLabel.setText(f"Image Directory: {directory}")

    def selectAnnPath(self):
        annPath, _ = QFileDialog.getOpenFileName(
            self, "Select Annotation File", filter="JSON files (*.json)"
        )
        if annPath:
            self.annPathLabel.setText(f"Annotation File: {annPath}")

    def visualize(self):
        img_dir = self.imgDirLabel.text().replace("Image Directory: ", "")
        ann_path = self.annPathLabel.text().replace("Annotation File: ", "")
        show_only_box = self.showOnlyBoxCheckBox.isChecked()
        if not os.path.exists(img_dir) or not os.path.exists(ann_path):
            QMessageBox.critical(
                self,
                "Error",
                "Please select valid image directory and annotation file.",
            )
            return
        coco_visualize(
            img_dir, ann_path, show_only_box
        )  # Assuming this is the correct name for the segmentation visualization function
        QMessageBox.information(self, "Visualize", "Visualization completed.")
