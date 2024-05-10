"""
Huijo Kim (huijo@hexafarms.com)
"""

import sys
import os
import time
import datetime
import atexit
import json

import yaml
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog,
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QLineEdit,
    QWidget,
    QCheckBox,
    QTextEdit,
    QGridLayout,
    QInputDialog,
    QFormLayout,
)
from PyQt5.QtCore import Qt, QSize

from coco_assistant import COCO_Assistant
from cvops.coco_operation import update as coco_update
from cvops.coco_operation import postupdate as coco_postupdate
from cvops.coco_operation import split as coco_split
from cvops.coco_operation import visualize as coco_visualize
from tools.s3_handler import download_s3_files, upload_s3_files, load_aws_credentials
from pycocotools.coco import COCO


class VisualizeDialog(QDialog):
    """
    A dialog window for visualizing annotations with COCO format.

    Allows users to select an image directory and an annotation file (in JSON format),
    and then visualizes the specified annotations on the images. This is useful for
    verifying the correctness of annotations or for data analysis purposes.

    Attributes:
        imgDirLabel (QLabel): Displays the selected image directory path.
        annPathLabel (QLabel): Displays the selected annotation file path.

    Methods:
        selectImgDir(): Opens a file dialog to select the image directory.
        selectAnnPath(): Opens a file dialog to select the annotation file.
        visualize(): Validates selected paths and initiates the visualization process.
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
        if not os.path.exists(img_dir) or not os.path.exists(ann_path):
            QMessageBox.critical(
                self,
                "Error",
                "Please select valid image directory and annotation file.",
            )
            return
        coco_visualize(
            img_dir, ann_path
        )  # Assuming this is the correct name for the segmentation visualization function
        QMessageBox.information(self, "Visualize", "Visualization completed.")


class MergeDialog(QDialog):
    """
    A dialog window for merging multiple COCO datasets into a single dataset.

    The dialog facilitates the merging process by allowing users to select directories
    for the images and annotations of the datasets they wish to merge. Users can
    optionally choose to merge the images as well. This feature is particularly useful
    for tasks that involve consolidating datasets from different sources to create a
    larger, comprehensive dataset for training or evaluation purposes.

    Attributes:
        imgDirLabel (QLabel): Displays the path of the selected image directory where the COCO images are located.
        annDirLabel (QLabel): Displays the path of the selected annotation directory where the COCO annotation files are stored.
        mergeImagesCheckBox (QCheckBox): Allows users to specify whether or not to merge the images from different datasets.

    Methods:
        selectImgDir(): Opens a file dialog to select the directory containing the images to be merged.
        selectAnnDir(): Opens a file dialog to select the directory containing the annotation files to be merged.
        merge(): Validates selected directories and initiates the merging process.
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


class RemapCategoriesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Remap COCO Category IDs")
        layout = QVBoxLayout()

        # Annotation Path Label
        self.annPathLabel = QLabel("Annotation File: Not Selected")
        layout.addWidget(self.annPathLabel)

        # Button to Select Annotation File
        self.selectAnnFileButton = QPushButton("Select Annotation File")
        self.selectAnnFileButton.clicked.connect(self.selectAnnPath)
        layout.addWidget(self.selectAnnFileButton)

        formLayout = QFormLayout()
        # JSON input QTextEdit
        self.jsonTextEdit = QTextEdit()
        layout.addWidget(self.jsonTextEdit)

        # Initialize the QTextEdit with pretty JSON, if needed
        initialJsonData = {"5": 6, "6": 7, "7": 5}  # Example data
        prettyJsonStr = json.dumps(initialJsonData, indent=4)  # Prettify the JSON
        self.jsonTextEdit.setText(prettyJsonStr)

        layout.addLayout(formLayout)

        remapButton = QPushButton("Remap Categories")
        remapButton.clicked.connect(self.remapCategories)
        layout.addWidget(remapButton)

        self.setLayout(layout)

    def selectAnnPath(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Annotation File", "", "JSON files (*.json)"
        )
        if path:
            self.annPathLabel.setText(f"Annotation File: {path}")

    def remapCategories(self):
        # Read the annotation file path from the QLabel after stripping the prefix
        ann_file_path = self.annPathLabel.text().replace("Annotation File: ", "")

        # Read the mapping string from QTextEdit
        mapping_str = self.jsonTextEdit.toPlainText()

        if not os.path.exists(ann_file_path):
            QMessageBox.critical(
                self, "Error", "Please specify a valid annotation file path."
            )
            return

        try:
            # Load mapping from the QTextEdit string
            mapping_dict = json.loads(mapping_str)
            mapping_dict = {int(k): int(v) for k, v in mapping_dict.items()}

            # Load the COCO annotation data
            with open(ann_file_path) as f:
                coco_data = json.load(f)

            # Apply the mapping to 'category_id' in all annotations
            for annotation in coco_data["annotations"]:
                if annotation["category_id"] in mapping_dict:
                    annotation["category_id"] = mapping_dict[annotation["category_id"]]

            # Also, consider if you want to update category IDs in the "categories" section

            # Generate the updated file name
            updated_file_name = f"{ann_file_path.rsplit('.', 1)[0]}_updated.json"

            # Save the updated COCO data back to the new file
            with open(updated_file_name, "w") as f:
                json.dump(coco_data, f, indent=4)

            QMessageBox.information(
                self,
                "Success",
                f"Categories remapped successfully.\nUpdated file: {updated_file_name}",
            )
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Error", "Invalid JSON format for mapping.")
        except ValueError as e:  # Catching conversion errors for IDs
            QMessageBox.critical(self, "Error", str(e))
        except Exception as e:  # General catch-all for unexpected errors
            QMessageBox.critical(self, "Error", str(e))


class SplitDialog(QDialog):
    """
    A dialog window for splitting a COCO dataset into training and validation sets.

    This dialog allows users to select an image directory and an annotation file, then specify
    a ratio for splitting the dataset. The process facilitates dividing a dataset into separate
    parts for the purpose of training and validating machine learning models, ensuring that
    there is no overlap between the training and validation datasets.

    Attributes:
        imgDirLabel (QLabel): Displays the path of the selected image directory.
        annPathLabel (QLabel): Displays the path of the selected annotation file.
        splitRatioLineEdit (QLineEdit): Input field for specifying the train-validation split ratio.

    Methods:
        selectImgDir(): Opens a dialog to select the image directory for the dataset to be split.
        selectAnnPath(): Opens a dialog to select the annotation file corresponding to the dataset.
        split(): Validates inputs and initiates the dataset splitting process based on the specified ratio.
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
            multi=False,
        )
        QMessageBox.information(self, "Split", "Dataset split successfully.")


class UpdateDialog(QDialog):
    """
    A dialog window for updating COCO datasets with new images and annotations.

    The dialog provides a user-friendly interface for selecting new image locations and
    corresponding new annotations, in addition to existing training and validation
    annotation files. This functionality supports the iterative refinement and expansion
    of datasets - an essential task in machine learning workflows to improve model performance.

    Attributes:
        newAnnPathLabel (QLabel): Displays the path of the selected new annotation file.
        imgLocateLabel (QLabel): Displays the path of the selected new image location.
        trainAnnPathLabel (QLabel): Displays the path of the selected training annotation file.
        valAnnPathLabel (QLabel): Displays the path of the selected validation annotation file.
        splitRatioLineEdit (QLineEdit): Input field for specifying new data's train-validation split ratio.

    Methods:
        selectNewAnnPath(): Opens a dialog to select the new annotation file to be added to the dataset.
        selectImageLocation(): Opens a dialog to select the location of the new images to be added.
        selectTrainAnnPath(): Opens a dialog to select the existing training annotations file.
        selectValAnnPath(): Opens a dialog to select the existing validation annotations file.
        update(): Validates inputs and initiates the dataset updating process based on the specified inputs and ratio.
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


class PostUpdateDialog(QDialog):
    """
    A dialog window for performing post-update operations on COCO datasets.

    After a dataset has been updated with new annotations and images, certain post-update
    steps may be necessary. This dialog offers options for processing the updated dataset,
    such as reorganizing files, updating indices, or applying additional transformations.
    This is crucial for maintaining dataset integrity and ensuring compatibility with
    machine learning pipelines.

    Attributes:
        useLatestConfigCheckbox (QCheckBox): Checkbox for opting to use the latest update configurations automatically.

    Methods:
        toggleDirSelection(state): Enables or disables directory selection based on the checkbox state.
        selectDirectory(labelWidget, dialogTitle): Opens a dialog to select directories for new samples, existing samples, or results.
        postUpdate(): Initiates the post-update operation based on the selected directories and configurations.
    """

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
        self.existingSamplesDirLabel = QLabel(
            "Existing Samples Directory: Not Selected"
        )
        self.resultsDirLabel = QLabel("Results Directory: Not Selected")

        self.labelsAndButtons = [
            (self.newSamplesDirLabel, "Select New Samples Directory"),
            (self.existingSamplesDirLabel, "Select Existing Samples Directory"),
            (self.resultsDirLabel, "Select Results Directory"),
        ]

        for label, dialogTitle in self.labelsAndButtons:
            layout.addWidget(label)
            button = QPushButton(dialogTitle)
            button.clicked.connect(
                lambda _, lbl=label, title=dialogTitle: self.selectDirectory(lbl, title)
            )
            layout.addWidget(button)

        # Button to execute post update
        postUpdateButton = QPushButton("Post Update Dataset")
        postUpdateButton.clicked.connect(self.postUpdate)
        layout.addWidget(postUpdateButton)

        self.setLayout(layout)
        self.toggleDirSelection(
            self.useLatestConfigCheckbox.checkState()
        )  # Ensure correct initial state

    def toggleDirSelection(self, state):
        shouldHide = state == Qt.Checked
        for label, _ in self.labelsAndButtons:
            # This loop adjusts visibility based on the checkbox state
            label.setVisible(not shouldHide)
            label.nextInFocusChain().setVisible(
                not shouldHide
            )  # Adjusts the visibility of the button

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
                existing_samples_dir = os.path.dirname(config.get("train_ann_path", ""))
                results_path = os.path.dirname(
                    os.path.dirname(config.get("outcome_train_ann", ""))
                )

                # Validate paths are valid directories
                if not (
                    os.path.isdir(existing_samples_dir) and os.path.isdir(results_path)
                ):
                    raise ValueError(
                        "One or more directories from the config don't exist."
                    )

            except FileNotFoundError:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Configuration file 'latest_update_configs.yaml' not found.",
                )
                return
            except ValueError as ve:
                QMessageBox.critical(self, "Error", str(ve))
                return
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to read the configuration file: {str(e)}"
                )
                return
        else:
            # Extract directly provided paths from the dialog's fields
            existing_samples_dir = (
                self.existingSamplesDirLabel.text().split(": ")[1].strip()
            )
            results_path = self.resultsDirLabel.text().split(": ")[1].strip()

            # Direct paths validation
            if not (
                os.path.isdir(existing_samples_dir) and os.path.isdir(results_path)
            ):
                QMessageBox.critical(self, "Error", "Please select valid directories.")
                return

        try:
            train_json, train_img_dir, val_json, val_img_dir = coco_postupdate(
                existing_samples_dir=existing_samples_dir, results_path=results_path
            )
            QMessageBox.information(
                self, "Post-update", "Dataset post-update completed successfully."
            )

            # Ask the user if they want to visualize data after post-update
            reply = QMessageBox.question(
                self,
                "Visualize Data",
                "Do you want to visualize the updated dataset?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                self.visualize(train_img_dir, train_json)
                self.visualize(val_img_dir, val_json)
                QMessageBox.information(
                    self, "Visualization", "Visualization completed."
                )
            else:
                QMessageBox.information(self, "Visualization", "Visualization skipped.")

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed during post-update operation: {str(e)}"
            )

        # Prompt the user for S3 upload
        upload_reply = QMessageBox.question(
            self,
            "Upload to S3",
            "Would you like to upload the results to an AWS S3 bucket?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if upload_reply == QMessageBox.Yes:
            s3_uri, ok = QInputDialog.getText(
                self,
                "S3 URI",
                "Enter the S3 base URI (e.g., s3://hexa-cv-dataset/Fragaria × ananassa/fruit_detection/):",
            )
            if ok and s3_uri:
                try:
                    # Extract bucket name and path from s3_uri
                    if not s3_uri.startswith("s3://"):
                        raise ValueError("Invalid S3 URI. Must start with 's3://'.")

                    processed_results_path = os.path.dirname(train_json)
                    # Extract epoch time from the path
                    epoch_time = processed_results_path.split("/")[-1]

                    # Convert epoch time to a datetime object
                    time_obj = datetime.datetime.fromtimestamp(int(epoch_time))

                    # Format the datetime object into a human-readable string, e.g., "YYYY-MM-DD_HH-MM-SS"
                    # You can adjust the formatting to your needs
                    time_str = time_obj.strftime("%Y-%m-%d_%H-%M-%S")

                    bucket_name, s3_key = s3_uri[5:].split("/", 1)
                    aws_access_key_id, aws_secret_access_key = load_aws_credentials()

                    # Assuming results_path contains the path to the results you want to upload
                    upload_s3_files(
                        aws_access_key_id,
                        aws_secret_access_key,
                        bucket_name,
                        processed_results_path,
                        s3_key + f"{time_str}",
                    )

                    QMessageBox.information(
                        self, "S3 Upload", "Results successfully uploaded to S3."
                    )
                except ValueError as ve:
                    QMessageBox.critical(self, "S3 Upload Error", str(ve))
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "S3 Upload Error",
                        f"Failed to upload results to S3: {str(e)}",
                    )

    def visualize(self, img_dir, ann_path):
        try:
            coco_visualize(img_dir, ann_path)

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to process the annotations file: {str(e)}"
            )


class S3UpdateDialog(QDialog):
    """
    A dialog window for updating datasets stored on AWS S3 with new images and annotations.

    This dialog facilitates specifying S3 paths for new images and annotations, as well as the existing dataset's S3 base path.
    It assists in planning how new data can be merged into an existing dataset, considering a specified train-validation split ratio.

    Attributes:
        newAnnPathLabel (QLabel): Displays the s3 path of the selected new annotation file.
        imgLocateLabel (QLabel): Displays the s3 path of the selected new image location.
        existingPathLabel (QLabel): Displays the s3 path of the project.
        splitRatioLineEdit (QLineEdit): Entry for specifying new data's train-validation split ratio.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update S3 Dataset")
        layout = QVBoxLayout()

        # Initialize labels for displaying selected paths
        self.newAnnPathLabel = QLabel("New Annotation File (S3 Path): Not Selected")
        self.imgLocateLabel = QLabel("New Image Location (S3 Path): Not Selected")
        self.existingPathLabel = QLabel("Existing Dataset S3 Path: Not Specified")
        self.splitRatioLineEdit = QLineEdit("0.8")  # Default split ratio value

        # Add widgets to layout
        layout.addWidget(self.newAnnPathLabel)
        layout.addWidget(self.imgLocateLabel)
        layout.addWidget(self.existingPathLabel)
        layout.addWidget(QLabel("Split Ratio (New Data Train Size):"))
        layout.addWidget(self.splitRatioLineEdit)

        # Buttons for selecting S3 paths
        selectNewAnnPathButton = QPushButton("Select New Annotation S3 Path")
        selectImgLocateButton = QPushButton("Select New Image S3 Location")
        selectExistingPathButton = QPushButton("Select Existing Dataset S3 Path")
        updateButton = QPushButton("Update S3 Dataset")

        # Connection signals to slots
        selectNewAnnPathButton.clicked.connect(self.selectNewAnnPath)
        selectImgLocateButton.clicked.connect(self.selectImageLocation)
        selectExistingPathButton.clicked.connect(self.selectExistingPath)
        updateButton.clicked.connect(self.updateDataset)

        # Add buttons to layout
        layout.addWidget(selectNewAnnPathButton)
        layout.addWidget(selectImgLocateButton)
        layout.addWidget(selectExistingPathButton)
        layout.addWidget(updateButton)

        self.setLayout(layout)

    def selectNewAnnPath(self):
        # This method would ideally open a dialog to specify or select an S3 path.
        # Implement according to how you wish to input or select S3 paths.
        # For example, you might use a simpler QInputDialog to enter the path manually.
        path, ok = QInputDialog.getText(
            self, "Enter S3 Path", "New Annotation File S3 Path:"
        )
        if ok:
            self.newAnnPathLabel.setText(f"New Annotation File (S3 Path): {path}")

    def selectImageLocation(self):
        # Similar to selectNewAnnPath; gets S3 path for images.
        path, ok = QInputDialog.getText(
            self, "Enter S3 Path", "New Image Location S3 Path:"
        )
        if ok:
            self.imgLocateLabel.setText(f"New Image Location (S3 Path): {path}")

    def selectExistingPath(self):
        # User inputs the S3 base path of their existing dataset.
        path, ok = QInputDialog.getText(
            self, "Enter S3 Path", "Existing Dataset S3 Path:"
        )
        if ok:
            self.existingPathLabel.setText(f"Existing Dataset S3 Path: {path}")

    def updateDataset(self):
        aws_access_key_id, aws_secret_access_key = load_aws_credentials(
            "config/s3_credentials.yaml"
        )

        # Generate a unique directory for this update session based on the current timestamp
        now = int(time.time())
        current_path = os.getcwd()  # Get the current working directory
        outcome_path = os.path.join(
            current_path, f"downloads_s3/{now}"
        )  # Make outcome_path absolute

        # Prepare directories for new data
        new_data_path = os.path.join(outcome_path, "new")
        os.makedirs(
            new_data_path, exist_ok=True
        )  # Ensure the new data directory exists

        new_images_path = os.path.join(
            new_data_path, "images"
        )  # Specific path for new images
        new_ann_path = os.path.join(
            new_data_path, "annotations.json"
        )  # Assuming a single new annotation file

        # New dataset paths (assuming they are received from the Qt dialog)
        new_ann_s3_path = self.newAnnPathLabel.text().replace(
            "New Annotation File (S3 Path): ", ""
        )
        new_img_dir_s3_path = self.imgLocateLabel.text().replace(
            "New Image Directory (S3 Path): ", ""
        )
        new_bucket_name, new_ann_key = new_ann_s3_path.replace("s3://", "").split(
            "/", 1
        )
        _, new_img_dir_key = new_img_dir_s3_path.replace("s3://", "").split("/", 1)

        # Adjust download_s3_files function calls to use correct paths

        # Download new annotation file directly to its specific path
        download_s3_files(
            aws_access_key_id,
            aws_secret_access_key,
            new_bucket_name,
            new_ann_key,
            os.path.dirname(new_ann_path),  # Use the parent directory of new_ann_path
        )

        # Download new images into their specific directory
        download_s3_files(
            aws_access_key_id,
            aws_secret_access_key,
            new_bucket_name,
            new_img_dir_key,
            new_images_path,  # Use new_images_path for storing new images
        )

        new_ann_path = os.path.join(
            outcome_path, "new", os.path.basename(new_ann_key)
        )  # Path to new annotation file
        new_image_path = os.path.join(
            outcome_path, "new/images"
        )  # New images are within this directory

        # Existing dataset paths (assumed to be provided through the dialog)
        existing_dataset_s3_path = self.existingPathLabel.text().replace(
            "Existing Dataset S3 Path: ", ""
        )
        existing_bucket_name, existing_dataset_key = existing_dataset_s3_path.replace(
            "s3://", ""
        ).split("/", 1)

        # Directory for existing data within outcome_path
        existing_data_path = os.path.join(outcome_path, "existing_dataset")
        os.makedirs(
            existing_data_path, exist_ok=True
        )  # Ensure the existing data directory exists

        # Assuming download_s3_files has been adapted to accommodate directory downloads
        download_s3_files(
            aws_access_key_id,
            aws_secret_access_key,
            existing_bucket_name,
            existing_dataset_key,
            existing_data_path,  # Download everything into existing_data_path
        )

        coco_update(
            new_ann_path=new_ann_path,
            train_ann_path=os.path.join(existing_data_path, "train.json"),
            val_ann_path=os.path.join(existing_data_path, "val.json"),
            split_ratio=0.8,
            new_image_locate=new_image_path,
        )
        # MessageBox or logging
        print("Update Complete", "Dataset has been updated with files from S3.")

        QMessageBox.information(
            self, "Update Initiated", "Dataset update process has been initiated."
        )


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
        buttonSize = QSize(150, 100)  # Adjust size as needed

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

        # Button for S3 Update
        self.s3UpdateButton = QPushButton("S3 Update")
        self.s3UpdateButton.setFixedSize(buttonSize)
        self.s3UpdateButton.clicked.connect(self.showS3UpdateDialog)

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
        gridLayout.addWidget(self.s3UpdateButton, 2, 0)  # Example position

        # Enable stretching to push the buttons to the corners
        gridLayout.setColumnStretch(0, 1)
        gridLayout.setColumnStretch(1, 1)
        gridLayout.setRowStretch(0, 1)
        gridLayout.setRowStretch(1, 1)

        gridLayout.addWidget(self.postUpdateButton, 1, 2)  # Adjust position as needed
        self.remapCategoriesButton = QPushButton("Remap Categories")
        self.remapCategoriesButton.setFixedSize(buttonSize)
        self.remapCategoriesButton.clicked.connect(self.showRemapCategoriesDialog)

        gridLayout.addWidget(
            self.remapCategoriesButton, 2, 1
        )  # Choose appropriate row and column

        self.centralWidget.setLayout(gridLayout)

    def showRemapCategoriesDialog(self):
        dialog = RemapCategoriesDialog(self)
        dialog.exec_()

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

    def showS3UpdateDialog(self):
        dialog = S3UpdateDialog(self)
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


def setPrettyJson(self):
    try:
        # Read the current text from QTextEdit
        currentJsonStr = self.jsonTextEdit.toPlainText()
        # Parse it as JSON
        jsonData = json.loads(currentJsonStr)
        # Prettify and set it back to QTextEdit
        prettyJsonStr = json.dumps(jsonData, indent=4)
        self.jsonTextEdit.setText(prettyJsonStr)
    except json.JSONDecodeError:
        QMessageBox.warning(self, "Invalid JSON", "The JSON input is invalid.")


def main():
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
