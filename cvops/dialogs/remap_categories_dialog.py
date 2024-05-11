import os
import json

from PyQt5.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QTextEdit,
    QFormLayout,
)


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

            for category in coco_data["categories"]:
                if category["id"] in mapping_dict:
                    category["id"] = mapping_dict[category["id"]]

            # Optionally, sort categories by the new 'id' values
            coco_data["categories"] = sorted(
                coco_data["categories"], key=lambda x: x["id"]
            )

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
