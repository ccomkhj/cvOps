import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QLineEdit,
    QMessageBox,
)
from pathlib import Path


class COCOGui(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("COCO Dataset Updater")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        # Labels
        self.new_ann_label = QLabel("New Annotations: None")
        self.train_ann_label = QLabel("Train Annotations: None")
        self.val_ann_label = QLabel("Validation Annotations: None")
        self.image_locate_label = QLabel("Image Locate Directory: None")

        # Line Edit for Split Ratio
        self.split_ratio_input = QLineEdit(self)
        self.split_ratio_input.setPlaceholderText("Enter split ratio (e.g., 0.8)")

        # Buttons
        self.select_new_ann_btn = QPushButton("Select New Annotations", self)
        self.select_train_ann_btn = QPushButton("Select Train Annotations", self)
        self.select_val_ann_btn = QPushButton("Select Validation Annotations", self)
        self.select_image_locate_btn = QPushButton(
            "Select Image Locate Directory", self
        )
        self.update_btn = QPushButton("Update COCO Dataset", self)

        # Button click events
        self.select_new_ann_btn.clicked.connect(self.selectNewAnnotations)
        self.select_train_ann_btn.clicked.connect(self.selectTrainAnnotations)
        self.select_val_ann_btn.clicked.connect(self.selectValAnnotations)
        self.select_image_locate_btn.clicked.connect(self.selectImageLocateDir)
        self.update_btn.clicked.connect(self.updateCOCO)

        # Layout arrangement
        layout.addWidget(self.new_ann_label)
        layout.addWidget(self.select_new_ann_btn)
        layout.addWidget(self.train_ann_label)
        layout.addWidget(self.select_train_ann_btn)
        layout.addWidget(self.val_ann_label)
        layout.addWidget(self.select_val_ann_btn)
        layout.addWidget(self.image_locate_label)
        layout.addWidget(self.select_image_locate_btn)
        layout.addWidget(self.split_ratio_input)
        layout.addWidget(self.update_btn)

        self.setLayout(layout)

    def selectNewAnnotations(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select New Annotations File", "", "JSON files (*.json)"
        )
        if path:
            self.new_ann_label.setText(f"New Annotations: {path}")

    def selectTrainAnnotations(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Train Annotations File", "", "JSON files (*.json)"
        )
        if path:
            self.train_ann_label.setText(f"Train Annotations: {path}")

    def selectValAnnotations(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Validation Annotations File", "", "JSON files (*.json)"
        )
        if path:
            self.val_ann_label.setText(f"Validation Annotations: {path}")

    def selectImageLocateDir(self):
        path = QFileDialog.getExistingDirectory(self, "Select Image Locate Directory")
        if path:
            self.image_locate_label.setText(f"Image Locate Directory: {path}")

    def updateCOCO(self):
        new_ann_path = self.new_ann_label.text().split(": ")[1]
        train_ann_path = self.train_ann_label.text().split(": ")[1]
        val_ann_path = self.val_ann_label.text().split(": ")[1]
        image_locate = self.image_locate_label.text().split(": ")[1]
        split_ratio_text = self.split_ratio_input.text()

        if (
            "None" in [new_ann_path, train_ann_path, val_ann_path]
            or not split_ratio_text
        ):
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please provide all annotation paths and a split ratio.",
            )
            return

        try:
            split_ratio = float(split_ratio_text)
            assert 0 < split_ratio < 1, "Split ratio must be between 0 and 1"

            # Here, you would call your update function with these parameters
            # For demonstration, we'll just show a message box.
            QMessageBox.information(
                self,
                "Update Started",
                "This would start the update process with provided info.",
            )

        except ValueError:
            QMessageBox.warning(self, "Invalid Value", "Split ratio must be a number.")
        except AssertionError as e:
            QMessageBox.warning(self, "Invalid Split Ratio", str(e))


def main():
    app = QApplication(sys.argv)
    ex = COCOGui()
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
