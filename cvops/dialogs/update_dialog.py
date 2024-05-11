import os
import atexit
from PyQt5.QtWidgets import (
    QFileDialog,
    QDialog,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QLineEdit,
)
from cvops.coco_operation import update as coco_update


class UpdateDialog(QDialog):
    """
    A dialog window for updating COCO datasets with new images and annotations.

    The dialog provides a user-friendly interface for selecting new image locations and
    corresponding new annotations, in addition to existing training and validation
    annotation files. This functionality supports the iterative refinement and expansion
    of datasets - an essential task in machine learning workflows to improve model performance.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update COCO Dataset")
        layout = QVBoxLayout()

        self.newAnnPathLabel = QLabel("New Annotation File: Not Selected")
        layout.addWidget(self.newAnnPathLabel)

        self.imgLocateLabel = QLabel(
            "New Image Location: Not Selected"
        )  # Label for selecting image location
        layout.addWidget(self.imgLocateLabel)

        self.trainAnnPathLabel = QLabel("Train Annotation File: Not Selected")
        layout.addWidget(self.trainAnnPathLabel)

        self.valAnnPathLabel = QLabel("Validation Annotation File: Not Selected")
        layout.addWidget(self.valAnnPathLabel)

        newAnnPathButton = QPushButton("Select New Annotation File")
        newAnnPathButton.clicked.connect(self.selectNewAnnPath)
        layout.addWidget(newAnnPathButton)

        imgLocateButton = QPushButton("Select New Image Location")
        imgLocateButton.clicked.connect(
            self.selectImageLocation
        )  # Button to select image location
        layout.addWidget(imgLocateButton)

        trainAnnPathButton = QPushButton("Select Train Annotation File")
        trainAnnPathButton.clicked.connect(self.selectTrainAnnPath)
        layout.addWidget(trainAnnPathButton)

        valAnnPathButton = QPushButton("Select Validation Annotation File")
        valAnnPathButton.clicked.connect(self.selectValAnnPath)
        layout.addWidget(valAnnPathButton)

        self.splitRatioLineEdit = QLineEdit("0.8")
        layout.addWidget(QLabel("Split Ratio (New Data Train Size):"))
        layout.addWidget(self.splitRatioLineEdit)

        updateButton = QPushButton("Update Dataset")
        updateButton.clicked.connect(self.update)
        layout.addWidget(updateButton)

        self.setLayout(layout)

    def selectNewAnnPath(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select New Annotation File", "", "JSON files (*.json)"
        )
        if path:
            self.newAnnPathLabel.setText(f"New Annotation File: {path}")

    def selectTrainAnnPath(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Train Annotation File", "", "JSON files (*.json)"
        )
        if path:
            self.trainAnnPathLabel.setText(f"Train Annotation File: {path}")

    def selectValAnnPath(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Validation Annotation File", "", "JSON files (*.json)"
        )
        if path:
            self.valAnnPathLabel.setText(f"Validation Annotation File: {path}")

    def selectImageLocation(self):
        directory = QFileDialog.getExistingDirectory(self, "Select New Image Location")
        if directory:
            self.imgLocateLabel.setText(f"New Image Location: {directory}")

    def selectNewAnnPath(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select New Annotation File", "", "JSON files (*.json)"
        )
        if path:
            self.newAnnPathLabel.setText(f"New Annotation File: {path}")

    def selectTrainAnnPath(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Train Annotation File", "", "JSON files (*.json)"
        )
        if path:
            self.trainAnnPathLabel.setText(f"Train Annotation File: {path}")

    def selectValAnnPath(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Validation Annotation File", "", "JSON files (*.json)"
        )
        if path:
            self.valAnnPathLabel.setText(f"Validation Annotation File: {path}")

    def update(self):
        new_ann_path = self.newAnnPathLabel.text().replace("New Annotation File: ", "")
        train_ann_path = self.trainAnnPathLabel.text().replace(
            "Train Annotation File: ", ""
        )
        val_ann_path = self.valAnnPathLabel.text().replace(
            "Validation Annotation File: ", ""
        )
        split_ratio = float(self.splitRatioLineEdit.text())
        new_image_locate = self.imgLocateLabel.text().replace(
            "New Image Location: ", ""
        )

        if not (
            os.path.exists(new_ann_path)
            and os.path.exists(train_ann_path)
            and os.path.exists(val_ann_path)
        ):
            QMessageBox.critical(self, "Error", "Please select valid files.")
            return

        def run_update_and_exit():
            coco_update(
                new_ann_path=new_ann_path,
                train_ann_path=train_ann_path,
                val_ann_path=val_ann_path,
                split_ratio=split_ratio,
                new_image_locate=new_image_locate,
            )
            print("Update complete!")
            QApplication.quit()  # Quit the application

        # Register the update function to run on exit
        atexit.register(run_update_and_exit)

        # Close the dialog to proceed
        self.accept()
