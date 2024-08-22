import os
import json
import shutil
from typing import List
from pycocotools.coco import COCO
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QFileDialog,
    QTextEdit,
)

# Import the separate_by_name function
from cvops.coco_operation import separate_by_name


class SplitNameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Separate By Name")
        self.setGeometry(100, 100, 400, 300)
        self.layout = QVBoxLayout(self)

        self.imgPathLabel = QLabel("Image Path:", self)
        self.imgPathEdit = QLineEdit(self)
        self.annPathLabel = QLabel("Annotations Path:", self)
        self.annPathEdit = QLineEdit(self)
        self.nameKeysLabel = QLabel("Name Keys (comma-separated):", self)
        self.nameKeysEdit = QTextEdit(self)

        # Initial data for the example (formatted as a pretty list)
        initialListData = ["cam_A", "cam_B"]
        self.setInitialNameKeys(initialListData)

        self.browseImagePathButton = QPushButton("Browse...", self)
        self.browseImagePathButton.clicked.connect(self.browse_image_path)
        self.browseAnnPathButton = QPushButton("Browse...", self)
        self.browseAnnPathButton.clicked.connect(self.browse_ann_path)

        self.executeButton = QPushButton("Execute", self)
        self.executeButton.clicked.connect(self.execute)

        self.layout.addWidget(self.imgPathLabel)
        self.layout.addWidget(self.imgPathEdit)
        self.layout.addWidget(self.browseImagePathButton)
        self.layout.addWidget(self.annPathLabel)
        self.layout.addWidget(self.annPathEdit)
        self.layout.addWidget(self.browseAnnPathButton)
        self.layout.addWidget(self.nameKeysLabel)
        self.layout.addWidget(self.nameKeysEdit)
        self.layout.addWidget(self.executeButton)

    def browse_image_path(self):
        file_name = QFileDialog.getExistingDirectory(self, "Select Image Directory")
        if file_name:
            self.imgPathEdit.setText(file_name)

    def browse_ann_path(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Annotations File", filter="JSON files (*.json)"
        )
        if file_name:
            self.annPathEdit.setText(file_name)

    def setInitialNameKeys(self, initial_data: List[str]):
        pretty_list = ",".join(initial_data)
        self.nameKeysEdit.setPlainText(pretty_list)

    def execute(self):
        img_path = self.imgPathEdit.text()
        ann_path = self.annPathEdit.text()
        name_keys = self.nameKeysEdit.toPlainText().split(",")

        # Clean up any extra spaces
        name_keys = [key.strip() for key in name_keys]

        if not img_path or not ann_path or not name_keys:
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return

        try:
            separated_cocos = separate_by_name(img_path, ann_path, name_keys)
            QMessageBox.information(self, "Success", "Files separated successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
