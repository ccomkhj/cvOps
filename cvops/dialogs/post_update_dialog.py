import os
import yaml
import datetime

from cvops.coco_operation import postupdate as coco_postupdate
from cvops.coco_operation import visualize as coco_visualize
from tools.s3_handler import upload_s3_files, load_aws_credentials

from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QCheckBox,
    QInputDialog,
)


class PostUpdateDialog(QDialog):
    """
    A dialog window for performing post-update operations on COCO datasets.

    After a dataset has been updated with new annotations and images, certain post-update
    steps may be necessary. This dialog offers options for processing the updated dataset,
    such as reorganizing files, updating indices, or applying additional transformations.
    This is crucial for maintaining dataset integrity and ensuring compatibility with
    machine learning pipelines.
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
