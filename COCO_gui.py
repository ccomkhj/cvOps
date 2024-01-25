import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QAction,
    QFileDialog,
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QWidget,
    QMenu,
)
from PyQt5.QtCore import Qt

from coco_assistant import COCO_Assistant
from pycocotools.coco import COCO

# Placeholder for importing your script's functionalities
# from your_script import visualize, merge, split, ...


# Dialog for Visualize functionality
class VisualizeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Visualize")
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

        visualizeButton = QPushButton("Visualize")
        visualizeButton.clicked.connect(self.visualize)
        layout.addWidget(visualizeButton)

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

    def visualize(self):
        img_dir = self.imgDirLabel.text().replace("Image Directory: ", "")
        ann_dir = self.annDirLabel.text().replace("Annotation Directory: ", "")
        if not os.path.exists(img_dir) or not os.path.exists(ann_dir):
            QMessageBox.critical(self, "Error", "Please select valid directories.")
            return
        # Insert your visualization logic here. Example:
        # Create COCO_Assistant object
        cas = COCO_Assistant(img_dir, ann_dir)
        cas.visualise()
        QMessageBox.information(
            self, "Visualize", "Placeholder for visualization logic."
        )


# # Dialog for Merge functionality
# class MergeDialog(QDialog):
#     # Similar structure to VisualizeDialog, adapt for merging
#     ...


# # Dialog for Split functionality
# class SplitDialog(QDialog):
#     # Similar structure to VisualizeDialog, adapt for splitting
#     ...


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("COCO Tools")
        self.setGeometry(100, 100, 800, 600)

        menuBar = self.menuBar()
        toolsMenu = menuBar.addMenu("Tools")

        visualizeAction = QAction("Visualize", self)
        visualizeAction.triggered.connect(self.showVisualizeDialog)

        mergeAction = QAction("Merge", self)
        mergeAction.triggered.connect(self.showMergeDialog)

        splitAction = QAction("Split", self)
        splitAction.triggered.connect(self.showSplitDialog)

        toolsMenu.addAction(visualizeAction)
        toolsMenu.addAction(mergeAction)
        toolsMenu.addAction(splitAction)

    def showVisualizeDialog(self):
        dialog = VisualizeDialog(self)
        dialog.exec_()

    def showMergeDialog(self):
        dialog = MergeDialog(self)
        dialog.exec_()

    def showSplitDialog(self):
        dialog = SplitDialog(self)
        dialog.exec_()


def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
