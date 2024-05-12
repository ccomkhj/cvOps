import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QGridLayout,
    QPushButton,
    QWidget,
    QFrame,
)
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPalette, QColor, QIcon, QFont

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

        font = QFont("Arial", 12)
        icon_size = QSize(40, 40)

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        gridLayout = QGridLayout(self.centralWidget)

        # Button size
        buttonSize = QSize(200, 80)
        buttonSizeBig = QSize(200, 160)

        # Visualize Button (previously configured)
        self.visualizeButton = QPushButton("Visualize", self.centralWidget)
        self.visualizeButton.setFixedSize(buttonSize)
        self.visualizeButton.setIcon(QIcon("data/icons/visualization.png"))
        self.visualizeButton.setIconSize(icon_size)
        self.visualizeButton.setFont(font)
        self.visualizeButton.setToolTip("Visualize the annotations within the dataset.")
        self.visualizeButton.clicked.connect(self.showVisualizeDialog)

        # Remap Categories Button
        self.remapCategoriesButton = QPushButton("Remap Categories", self.centralWidget)
        self.remapCategoriesButton.setFixedSize(buttonSize)
        self.remapCategoriesButton.setIcon(QIcon("data/icons/remap.png"))
        self.remapCategoriesButton.setIconSize(icon_size)
        self.remapCategoriesButton.setFont(font)
        self.remapCategoriesButton.setToolTip("Remap the category ids.")
        self.remapCategoriesButton.clicked.connect(self.showRemapCategoriesDialog)
        gridLayout.addWidget(self.visualizeButton, 0, 0)
        gridLayout.addWidget(self.remapCategoriesButton, 0, 1)

        # Divider after row 0
        divider1 = QFrame()
        divider1.setFrameShape(QFrame.HLine)
        divider1.setFrameShadow(QFrame.Sunken)
        gridLayout.addWidget(divider1, 1, 0, 1, -1)  # Span all columns

        # Split Button
        self.splitButton = QPushButton("Split", self.centralWidget)
        self.splitButton.setFixedSize(buttonSize)
        self.splitButton.setIcon(QIcon("data/icons/split.png"))
        self.splitButton.setIconSize(icon_size)
        self.splitButton.setFont(font)
        self.splitButton.setToolTip("Split COCO into train and test.")
        self.splitButton.clicked.connect(self.showSplitDialog)

        # Merge Button
        self.mergeButton = QPushButton("Merge", self.centralWidget)
        self.mergeButton.setFixedSize(buttonSize)
        self.mergeButton.setIcon(QIcon("data/icons/merge.png"))
        self.mergeButton.setIconSize(icon_size)
        self.mergeButton.setFont(font)
        self.mergeButton.setToolTip("Merge COCO files.")
        self.mergeButton.clicked.connect(self.showMergeDialog)

        gridLayout.addWidget(self.splitButton, 2, 0)
        gridLayout.addWidget(self.mergeButton, 2, 1)

        # Divider after row 1
        divider2 = QFrame()
        divider2.setFrameShape(QFrame.HLine)
        divider2.setFrameShadow(QFrame.Sunken)
        gridLayout.addWidget(divider2, 3, 0, 1, -1)  # Span all columns

        # Update (Local) Button
        self.updateButton = QPushButton("Update (Local)", self.centralWidget)
        self.updateButton.setFixedSize(buttonSize)
        self.updateButton.setIcon(QIcon("data/icons/update_local.png"))
        self.updateButton.setIconSize(icon_size)
        self.updateButton.setFont(font)
        self.updateButton.setToolTip(
            "Update the existing COCO dataset with new COCO dataset on local machine."
        )
        self.updateButton.clicked.connect(self.showUpdateDialog)

        # Post Update Button (Noting it spans two rows)
        self.postUpdateButton = QPushButton("Post Update", self.centralWidget)
        self.postUpdateButton.setFixedSize(
            buttonSizeBig
        )  # As previously specified to be bigger
        self.postUpdateButton.setIcon(QIcon("data/icons/post_update.png"))
        self.postUpdateButton.setIconSize(icon_size)
        self.postUpdateButton.setFont(font)
        self.postUpdateButton.setToolTip(
            "After Update process, decide if you want to combine. It consists visualization of train and validation set. Afterwards, you can directly upload to S3 bucket."
        )
        self.postUpdateButton.clicked.connect(self.showPostUpdateDialog)

        # Update (S3) Button
        self.s3UpdateButton = QPushButton("Update (S3)", self.centralWidget)
        self.s3UpdateButton.setFixedSize(buttonSize)
        self.s3UpdateButton.setIcon(QIcon("data/icons/update_s3.png"))
        self.s3UpdateButton.setIconSize(icon_size)
        self.s3UpdateButton.setFont(font)
        self.s3UpdateButton.setToolTip(
            "Update the existing COCO dataset with new COCO dataset. File is in AWS S3."
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
    # Force the style to be the same on all OSs:
    app.setStyle("Fusion")

    # Now use a palette to switch to dark colors:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)

    app.setPalette(palette)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
