import sys
import os
import yaml
import atexit
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
    QCheckBox,
    QGridLayout
)
from PyQt5.QtCore import Qt, QSize

from coco_assistant import COCO_Assistant
from pycocotools.coco import COCO
from cvops.coco_operation import update as coco_update
from cvops.coco_operation import postupdate as coco_postupdate
from cvops.coco_operation import split as coco_split
from cvops.coco_operation import visualize as coco_visualize

# Placeholder for importing your script's functionalities
# from your_script import visualize, merge, split, ...

class VisualizeDialog(QDialog):
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

        self.setLayout(layout)

    def selectImgDir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Image Directory")
        if directory:
            self.imgDirLabel.setText(f"Image Directory: {directory}")

    def selectAnnPath(self): 
        annPath, _ = QFileDialog.getOpenFileName(self, "Select Annotation File", filter="JSON files (*.json)")
        if annPath:
            self.annPathLabel.setText(f"Annotation File: {annPath}")

    def visualize(self):
        img_dir = self.imgDirLabel.text().replace("Image Directory: ", "")
        ann_path = self.annPathLabel.text().replace("Annotation File: ", "")
        if not os.path.exists(img_dir) or not os.path.exists(ann_path):
            QMessageBox.critical(self, "Error", "Please select valid image directory and annotation file.")
            return
        coco_visualize(img_dir, ann_path)  # Assuming this is the correct name for the segmentation visualization function
        QMessageBox.information(self, "Visualize", "Visualization completed.")

# # Dialog for Merge functionality
class MergeDialog(QDialog):
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
        QMessageBox.information(self, "Merge", "Datasets merged successfully.")


# # Dialog for Split functionality
class SplitDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Split COCO Dataset")
        layout = QVBoxLayout()

        self.imgDirLabel = QLabel("Image Directory: Not Selected")  # Label for image directory
        layout.addWidget(self.imgDirLabel)

        self.annPathLabel = QLabel("Annotation File: Not Selected")
        layout.addWidget(self.annPathLabel)

        imgDirButton = QPushButton("Select Image Directory")  # Button for selecting the image directory
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
        img_dir = self.imgDirLabel.text().replace("Image Directory: ", "")  # Getting image directory for splitting
        ann_path = self.annPathLabel.text().replace("Annotation File: ", "")
        split_ratio = float(self.splitRatioLineEdit.text())

        if not os.path.exists(img_dir) or not os.path.exists(ann_path):
            QMessageBox.critical(
                self, "Error", "Please select a valid image directory and annotation file."
            )
            return

        train_path = os.path.join(os.path.dirname(ann_path) + "train.json")
        val_path = os.path.join(os.path.dirname(ann_path) + "val.json")

        # Include the image_locate argument when calling coco_split
        coco_split(
            ann_path=ann_path,
            train_path=train_path,
            test_path=val_path,
            split=split_ratio,
            image_locate=img_dir,  # Passing the selected image directory
            multi=False,
        )
        QMessageBox.information(self, "Split", "Dataset split successfully.")

class UpdateDialog(QDialog):
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
        new_image_locate = self.imgLocateLabel.text().replace("New Image Location: ", "")

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

class PostUpdateDialog(QDialog):
    def __init__(self, parent=None):
        super(PostUpdateDialog, self).__init__(parent)
        self.setWindowTitle("Post Update COCO Dataset")
        layout = QVBoxLayout()

        # Checkbox for using the latest update configuration
        self.useLatestConfigCheckbox = QCheckBox("Use Latest Update Configurations")
        layout.addWidget(self.useLatestConfigCheckbox)
        self.useLatestConfigCheckbox.stateChanged.connect(self.toggleDirSelection)

        # Initialization of labels and buttons for directory selection
        self.newSamplesDirLabel = QLabel("New Samples Directory: Not Selected")
        self.existingSamplesDirLabel = QLabel("Existing Samples Directory: Not Selected")
        self.resultsDirLabel = QLabel("Results Directory: Not Selected")
        
        self.labelsAndButtons = [
            (self.newSamplesDirLabel, "Select New Samples Directory"),
            (self.existingSamplesDirLabel, "Select Existing Samples Directory"),
            (self.resultsDirLabel, "Select Results Directory"),
        ]
        
        for label, dialogTitle in self.labelsAndButtons:
            layout.addWidget(label)
            button = QPushButton(dialogTitle)
            button.clicked.connect(lambda _, lbl=label, title=dialogTitle: self.selectDirectory(lbl, title))
            layout.addWidget(button)

        # Button to execute post update
        postUpdateButton = QPushButton("Post Update Dataset")
        postUpdateButton.clicked.connect(self.postUpdate)
        layout.addWidget(postUpdateButton)

        self.setLayout(layout)
        self.toggleDirSelection(self.useLatestConfigCheckbox.checkState())  # Ensure correct initial state

    def toggleDirSelection(self, state):
        shouldHide = state == Qt.Checked
        for label, _ in self.labelsAndButtons:
            # This loop adjusts visibility based on the checkbox state
            label.setVisible(not shouldHide)
            label.nextInFocusChain().setVisible(not shouldHide)  # Adjusts the visibility of the button

    def selectDirectory(self, labelWidget, dialogTitle):
        directory = QFileDialog.getExistingDirectory(self, dialogTitle)
        if directory:
            labelWidget.setText(f"{dialogTitle}: {directory}")

    def postUpdate(self):
        if self.useLatestConfigCheckbox.isChecked():
            try:
                with open("latest_update_configs.yaml", "r") as file:
                    config = yaml.safe_load(file)
                
                # Using full paths from the configuration
                new_samples_dir = os.path.dirname(config.get('new_image_locate', ''))
                existing_samples_dir = os.path.dirname(config.get('train_ann_path', ''))
                results_path = os.path.dirname(os.path.dirname(config.get('outcome_train_ann', '')))

                # Validate paths are valid directories
                if not (os.path.isdir(new_samples_dir) and os.path.isdir(existing_samples_dir) and os.path.isdir(results_path)):
                    raise ValueError("One or more directories from the config don't exist.")
            
            except FileNotFoundError:
                QMessageBox.critical(self, "Error", "Configuration file 'latest_update_configs.yaml' not found.")
                return
            except ValueError as ve:
                QMessageBox.critical(self, "Error", str(ve))
                return
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read the configuration file: {str(e)}")
                return
        else:
            # Extract directly provided paths from the dialog's fields
            new_samples_dir = self.newSamplesDirLabel.text().split(": ")[1].strip()
            existing_samples_dir = self.existingSamplesDirLabel.text().split(": ")[1].strip()
            results_path = self.resultsDirLabel.text().split(": ")[1].strip()

            # Direct paths validation
            if not (os.path.isdir(new_samples_dir) and os.path.isdir(existing_samples_dir) and os.path.isdir(results_path)):
                QMessageBox.critical(self, "Error", "Please select valid directories.")
                return

        try:
            train_json, train_img_dir, val_json, val_img_dir = coco_postupdate(
                new_samples_dir=new_samples_dir, 
                existing_samples_dir=existing_samples_dir, 
                results_path=results_path)
            QMessageBox.information(self, "Post-update", "Dataset post-update completed successfully.")

            # Ask the user if they want to visualize data after post-update
            reply = QMessageBox.question(
                self, 
                "Visualize Data", 
                "Do you want to visualize the updated dataset?", 
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.visualize(train_img_dir, train_json) 
                self.visualize(val_img_dir, val_json)
                QMessageBox.information(self, "Visualization", "Visualization completed.")
            else:
                QMessageBox.information(self, "Visualization", "Visualization skipped.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed during post-update operation: {str(e)}")

    def visualize(self, img_dir, ann_path):
        try:
            coco_visualize(img_dir, ann_path)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process the annotations file: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("COCO Tools")
        self.setGeometry(100, 100, 800, 600)

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        gridLayout = QGridLayout()  # Use a grid layout

        # Button size
        buttonSize = QSize(100, 100)  # Adjust size as needed

        # Create buttons for each functionality and set text
        self.visualizeButton = QPushButton("Visualize")
        self.visualizeButton.setFixedSize(buttonSize)
        
        self.mergeButton = QPushButton("Merge")
        self.mergeButton.setFixedSize(buttonSize)
        
        self.splitButton = QPushButton("Split")
        self.splitButton.setFixedSize(buttonSize)

        self.updateButton = QPushButton("Update")
        self.updateButton.setFixedSize(buttonSize)
        
        self.postUpdateButton = QPushButton("Post Update")
        self.postUpdateButton.setFixedSize(buttonSize)
        self.postUpdateButton.clicked.connect(self.showPostUpdateDialog)

        # Connect buttons to their actions
        self.visualizeButton.clicked.connect(self.showVisualizeDialog)
        self.mergeButton.clicked.connect(self.showMergeDialog)
        self.splitButton.clicked.connect(self.showSplitDialog)
        self.updateButton.clicked.connect(self.showUpdateDialog)
        
        # Adding buttons to the grid layout at desired positions
        gridLayout.addWidget(self.visualizeButton, 0, 0)  # Top-left
        gridLayout.addWidget(self.mergeButton, 0, 1)  # Top-right
        gridLayout.addWidget(self.splitButton, 1, 0)  # Bottom-left
        gridLayout.addWidget(self.updateButton, 1, 1)  # Bottom-right
 
        # Enable stretching to push the buttons to the corners
        gridLayout.setColumnStretch(0, 1)
        gridLayout.setColumnStretch(1, 1)
        gridLayout.setRowStretch(0, 1)
        gridLayout.setRowStretch(1, 1)
        
        gridLayout.addWidget(self.postUpdateButton, 1, 2)  # Adjust position as needed

        self.centralWidget.setLayout(gridLayout)
    
    def showPostUpdateDialog(self):
        dialog = PostUpdateDialog(self)
        dialog.exec_()
        
    # Method implementations for showing the dialogs
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


def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
