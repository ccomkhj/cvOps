import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QGridLayout,
    QPushButton,
    QWidget,
    QFrame,
)
from PyQt5.QtCore import QSize

# Assuming dialogs are in a package named "dialogs"
from dialogs import (
    VisualizeDialog,
    MergeDialog,
    SplitDialog,
    UpdateDialog,
    PostUpdateDialog,
    S3UpdateDialog,
    RemapCategoriesDialog,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("COCO Tools")
        self.setGeometry(100, 100, 800, 600)

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        gridLayout = QGridLayout(self.centralWidget)

        # Button size
        buttonSize = QSize(150, 80)
        buttonSizeBig = QSize(150, 160)

        # Visualize and Remap Categories Buttons
        self.visualizeButton = QPushButton("Visualize", self.centralWidget)
        self.visualizeButton.setFixedSize(buttonSize)
        self.visualizeButton.setToolTip("Visualize the annotations within the dataset.")
        self.visualizeButton.clicked.connect(self.showVisualizeDialog)
        self.remapCategoriesButton = QPushButton("Remap Categories", self.centralWidget)
        self.remapCategoriesButton.setFixedSize(buttonSize)
        self.remapCategoriesButton.setToolTip("Remap the category ids.")
        self.remapCategoriesButton.clicked.connect(self.showRemapCategoriesDialog)

        gridLayout.addWidget(self.visualizeButton, 0, 0)
        gridLayout.addWidget(self.remapCategoriesButton, 0, 1)

        # Divider after row 0
        divider1 = QFrame()
        divider1.setFrameShape(QFrame.HLine)
        divider1.setFrameShadow(QFrame.Sunken)
        gridLayout.addWidget(divider1, 1, 0, 1, -1)  # Span all columns

        # Split and Merge Buttons
        self.splitButton = QPushButton("Split", self.centralWidget)
        self.splitButton.setFixedSize(buttonSize)
        self.splitButton.setToolTip("Split COCO into train and test.")
        self.splitButton.clicked.connect(self.showSplitDialog)
        self.mergeButton = QPushButton("Merge", self.centralWidget)
        self.mergeButton.setFixedSize(buttonSize)
        self.mergeButton.setToolTip("Merge COCO files.")
        self.mergeButton.clicked.connect(self.showMergeDialog)

        gridLayout.addWidget(self.splitButton, 2, 0)
        gridLayout.addWidget(self.mergeButton, 2, 1)

        # Divider after row 1
        divider2 = QFrame()
        divider2.setFrameShape(QFrame.HLine)
        divider2.setFrameShadow(QFrame.Sunken)
        gridLayout.addWidget(divider2, 3, 0, 1, -1)  # Span all columns

        # Update, Post Update (spanning two rows), and S3 Update Buttons
        self.updateButton = QPushButton("Update (Local)", self.centralWidget)
        self.updateButton.setFixedSize(buttonSize)
        self.updateButton.setToolTip(
            "Update the existing COCO dataset with new COCO dataset. File is in the local machine."
        )
        self.updateButton.clicked.connect(self.showUpdateDialog)

        self.postUpdateButton = QPushButton("Post Update", self.centralWidget)
        self.postUpdateButton.setFixedSize(buttonSizeBig)
        self.postUpdateButton.setToolTip(
            """After Update process, decide if you want to combine. 
It consists visualization of train and validation set. 
Afterwards, you can directly upload to S3 bucket."""
        )
        self.postUpdateButton.clicked.connect(self.showPostUpdateDialog)

        self.s3UpdateButton = QPushButton("Update (S3)", self.centralWidget)
        self.s3UpdateButton.setFixedSize(buttonSize)
        self.s3UpdateButton.setToolTip(
            "Update the existing COCO dataset with new COCO dataset. File is in AWS S3. Configure under `config/s3_credentials.yaml`"
        )
        self.s3UpdateButton.clicked.connect(self.showS3UpdateDialog)

        gridLayout.addWidget(self.updateButton, 4, 0)
        gridLayout.addWidget(self.postUpdateButton, 4, 1, 2, 1)
        gridLayout.addWidget(self.s3UpdateButton, 5, 0)

    def showVisualizeDialog(self):
        dialog = VisualizeDialog(self)
        dialog.exec_()

    def showMergeDialog(self):
        dialog = MergeDialog(self)
        dialog.exec_()

    def showSplitDialog(self):
        dialog = SplitDialog(self)
        dialog.exec_()

    def showUpdateDialog(self):
        dialog = UpdateDialog(self)
        dialog.exec_()

    def showPostUpdateDialog(self):
        dialog = PostUpdateDialog(self)
        dialog.exec_()

    def showS3UpdateDialog(self):
        dialog = S3UpdateDialog(self)
        dialog.exec_()

    def showRemapCategoriesDialog(self):
        dialog = RemapCategoriesDialog(self)
        dialog.exec_()


def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
