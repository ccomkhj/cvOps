import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QGridLayout,
    QPushButton,
    QWidget,
    QFrame,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QComboBox,
    QStyleFactory,
    QStatusBar,
    QSplashScreen,
    QProgressBar,
    QToolBar,
    QAction,
    QMenu,
    QMessageBox,
)
from PyQt5.QtCore import QSize, Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QPalette, QColor, QIcon, QFont, QPixmap, QLinearGradient, QGradient

# Assuming dialogs are in a package named "dialogs"
from dialogs import (
    VisualizeDialog,
    MergeDialog,
    SplitDialog,
    UpdateDialog,
    PostUpdateDialog,
    S3UpdateDialog,
    RemapCategoriesDialog,
    SplitNameDialog,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set window properties
        self.setWindowTitle("COCO Vision Tools")
        self.setGeometry(100, 100, 900, 700)
        self.setWindowIcon(QIcon("demo/icons/app_icon.png"))
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Create central widget with tabs
        self.centralWidget = QTabWidget(self)
        self.setCentralWidget(self.centralWidget)
        
        # Create tabs for different functionality groups
        self.visualizationTab = QWidget()
        self.dataManagementTab = QWidget()
        self.processingTab = QWidget()
        
        # Add tabs to the central widget
        self.centralWidget.addTab(self.visualizationTab, "Visualization")
        self.centralWidget.addTab(self.dataManagementTab, "Data Management")
        self.centralWidget.addTab(self.processingTab, "Processing")
        
        # Set up layouts for each tab
        self.setupVisualizationTab()
        self.setupDataManagementTab()
        self.setupProcessingTab()
        
        # Apply modern styling
        self.applyModernStyle()
    
    def applyModernStyle(self):
        # Set application style
        QApplication.setStyle(QStyleFactory.create("Fusion"))
        
        # Create a custom dark palette
        dark_palette = QPalette()
        
        # Set colors for the dark theme
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        
        # Apply the palette
        QApplication.setPalette(dark_palette)
        
        # Set stylesheet for buttons
        button_style = """
            QPushButton {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border: 1px solid #4d4d4d;
            }
            QPushButton:pressed {
                background-color: #4a4a4a;
            }
            QTabWidget::pane {
                border: 1px solid #3d3d3d;
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: white;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #3d3d3d;
            }
            QTabBar::tab:hover {
                background-color: #454545;
            }
        """
        self.setStyleSheet(button_style)
    
    def setupVisualizationTab(self):
        # Create layout for visualization tab
        layout = QVBoxLayout(self.visualizationTab)
        
        # Create a header label
        header = QLabel("Dataset Visualization Tools")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Create button grid layout
        buttonLayout = QGridLayout()
        layout.addLayout(buttonLayout)
        
        # Common properties for buttons
        buttonSize = QSize(200, 100)
        icon_size = QSize(40, 40)
        font = QFont("Arial", 11)
        
        # Visualize Button
        self.visualizeButton = QPushButton("Visualize Dataset", self.visualizationTab)
        self.visualizeButton.setFixedSize(buttonSize)
        self.visualizeButton.setIcon(QIcon("demo/icons/visualization.png"))
        self.visualizeButton.setIconSize(icon_size)
        self.visualizeButton.setFont(font)
        self.visualizeButton.setToolTip("Visualize the annotations within the dataset.")
        self.visualizeButton.clicked.connect(self.showVisualizeDialog)
        buttonLayout.addWidget(self.visualizeButton, 0, 0)
        
        # Advanced Visualization Button (new)
        self.advVisualizeButton = QPushButton("Advanced Visualization", self.visualizationTab)
        self.advVisualizeButton.setFixedSize(buttonSize)
        self.advVisualizeButton.setIcon(QIcon("demo/icons/visualization.png"))
        self.advVisualizeButton.setIconSize(icon_size)
        self.advVisualizeButton.setFont(font)
        self.advVisualizeButton.setToolTip("Advanced visualization with filtering options.")
        self.advVisualizeButton.clicked.connect(self.showAdvancedVisualizeDialog)
        buttonLayout.addWidget(self.advVisualizeButton, 0, 1)
        
        # Validate Dataset Button (new)
        self.validateButton = QPushButton("Validate Dataset", self.visualizationTab)
        self.validateButton.setFixedSize(buttonSize)
        self.validateButton.setIcon(QIcon("demo/icons/validate.png"))
        self.validateButton.setIconSize(icon_size)
        self.validateButton.setFont(font)
        self.validateButton.setToolTip("Validate dataset integrity and completeness.")
        self.validateButton.clicked.connect(self.showValidateDialog)
        buttonLayout.addWidget(self.validateButton, 1, 0)
        
        # Statistics Button (new)
        self.statsButton = QPushButton("Dataset Statistics", self.visualizationTab)
        self.statsButton.setFixedSize(buttonSize)
        self.statsButton.setIcon(QIcon("demo/icons/statistics.png"))
        self.statsButton.setIconSize(icon_size)
        self.statsButton.setFont(font)
        self.statsButton.setToolTip("View statistics about your dataset.")
        self.statsButton.clicked.connect(self.showStatsDialog)
        buttonLayout.addWidget(self.statsButton, 1, 1)
        
        # Add some spacing
        layout.addStretch()
    
    def setupDataManagementTab(self):
        # Create layout for data management tab
        layout = QVBoxLayout(self.dataManagementTab)
        
        # Create a header label
        header = QLabel("Dataset Management Tools")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Create button grid layout
        buttonLayout = QGridLayout()
        layout.addLayout(buttonLayout)
        
        # Common properties for buttons
        buttonSize = QSize(200, 100)
        icon_size = QSize(40, 40)
        font = QFont("Arial", 11)
        
        # Split Button
        self.splitButton = QPushButton("Split Dataset", self.dataManagementTab)
        self.splitButton.setFixedSize(buttonSize)
        self.splitButton.setIcon(QIcon("demo/icons/split.png"))
        self.splitButton.setIconSize(icon_size)
        self.splitButton.setFont(font)
        self.splitButton.setToolTip("Split COCO into train and test.")
        self.splitButton.clicked.connect(self.showSplitDialog)
        buttonLayout.addWidget(self.splitButton, 0, 0)
        
        # Separate by Name Button
        self.splitNameButton = QPushButton("Separate by Name", self.dataManagementTab)
        self.splitNameButton.setFixedSize(buttonSize)
        self.splitNameButton.setIcon(QIcon("demo/icons/split_name.png"))
        self.splitNameButton.setIconSize(icon_size)
        self.splitNameButton.setFont(font)
        self.splitNameButton.setToolTip("Split images into separate folders based on name keys.")
        self.splitNameButton.clicked.connect(self.showSplitNameDialog)
        buttonLayout.addWidget(self.splitNameButton, 0, 1)
        
        # Merge Button
        self.mergeButton = QPushButton("Merge Datasets", self.dataManagementTab)
        self.mergeButton.setFixedSize(buttonSize)
        self.mergeButton.setIcon(QIcon("demo/icons/merge.png"))
        self.mergeButton.setIconSize(icon_size)
        self.mergeButton.setFont(font)
        self.mergeButton.setToolTip("Merge COCO files.")
        self.mergeButton.clicked.connect(self.showMergeDialog)
        buttonLayout.addWidget(self.mergeButton, 1, 0)
        
        # Remap Categories Button
        self.remapCategoriesButton = QPushButton("Remap Categories", self.dataManagementTab)
        self.remapCategoriesButton.setFixedSize(buttonSize)
        self.remapCategoriesButton.setIcon(QIcon("demo/icons/remap.png"))
        self.remapCategoriesButton.setIconSize(icon_size)
        self.remapCategoriesButton.setFont(font)
        self.remapCategoriesButton.setToolTip("Remap the category ids.")
        self.remapCategoriesButton.clicked.connect(self.showRemapCategoriesDialog)
        buttonLayout.addWidget(self.remapCategoriesButton, 1, 1)
        
        # Format Conversion Button (new)
        self.formatConversionButton = QPushButton("Format Conversion", self.dataManagementTab)
        self.formatConversionButton.setFixedSize(buttonSize)
        self.formatConversionButton.setIcon(QIcon("demo/icons/convert.png"))
        self.formatConversionButton.setIconSize(icon_size)
        self.formatConversionButton.setFont(font)
        self.formatConversionButton.setToolTip("Convert between different annotation formats.")
        self.formatConversionButton.clicked.connect(self.showFormatConversionDialog)
        buttonLayout.addWidget(self.formatConversionButton, 2, 0)
        
        # Add some spacing
        layout.addStretch()
    
    def setupProcessingTab(self):
        # Create layout for processing tab
        layout = QVBoxLayout(self.processingTab)
        
        # Create a header label
        header = QLabel("Dataset Processing Tools")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Create button grid layout
        buttonLayout = QGridLayout()
        layout.addLayout(buttonLayout)
        
        # Common properties for buttons
        buttonSize = QSize(200, 100)
        icon_size = QSize(40, 40)
        font = QFont("Arial", 11)
        
        # Update (Local) Button
        self.updateButton = QPushButton("Update (Local)", self.processingTab)
        self.updateButton.setFixedSize(buttonSize)
        self.updateButton.setIcon(QIcon("demo/icons/update_local.png"))
        self.updateButton.setIconSize(icon_size)
        self.updateButton.setFont(font)
        self.updateButton.setToolTip("Update the existing COCO dataset with new COCO dataset on local machine.")
        self.updateButton.clicked.connect(self.showUpdateDialog)
        buttonLayout.addWidget(self.updateButton, 0, 0)
        
        # Update (S3) Button
        self.s3UpdateButton = QPushButton("Update (S3)", self.processingTab)
        self.s3UpdateButton.setFixedSize(buttonSize)
        self.s3UpdateButton.setIcon(QIcon("demo/icons/update_s3.png"))
        self.s3UpdateButton.setIconSize(icon_size)
        self.s3UpdateButton.setFont(font)
        self.s3UpdateButton.setToolTip("Update the existing COCO dataset with new COCO dataset. File is in AWS S3.")
        self.s3UpdateButton.clicked.connect(self.showS3UpdateDialog)
        buttonLayout.addWidget(self.s3UpdateButton, 0, 1)
        
        # Post Update Button
        self.postUpdateButton = QPushButton("Post Update", self.processingTab)
        self.postUpdateButton.setFixedSize(buttonSize)
        self.postUpdateButton.setIcon(QIcon("demo/icons/post_update.png"))
        self.postUpdateButton.setIconSize(icon_size)
        self.postUpdateButton.setFont(font)
        self.postUpdateButton.setToolTip("After Update process, decide if you want to combine. It consists of visualization of train and validation set. Afterwards, you can directly upload to S3 bucket.")
        self.postUpdateButton.clicked.connect(self.showPostUpdateDialog)
        buttonLayout.addWidget(self.postUpdateButton, 1, 0)
        
        # Add some spacing
        layout.addStretch()

    def showVisualizeDialog(self):
        dialog = VisualizeDialog(self)
        dialog.setWindowIcon(QIcon("demo/icons/visualization.png"))
        apply_palette_to_dialog(dialog, color=(220, 220, 240))  # Light blue
        dialog.exec_()

    def showMergeDialog(self):
        dialog = MergeDialog(self)
        dialog.setWindowIcon(QIcon("demo/icons/merge.png"))
        apply_palette_to_dialog(dialog, color=(220, 240, 220))  # Light green
        dialog.exec_()

    def showSplitDialog(self):
        dialog = SplitDialog(self)
        dialog.setWindowIcon(QIcon("demo/icons/split.png"))
        apply_palette_to_dialog(dialog, color=(240, 220, 220))  # Light red
        dialog.exec_()

    def showUpdateDialog(self):
        dialog = UpdateDialog(self)
        dialog.setWindowIcon(QIcon("demo/icons/update_local.png"))
        apply_palette_to_dialog(
            dialog, color=(220, 230, 250)
        )  # Different shade of light blue
        dialog.exec_()

    def showPostUpdateDialog(self):
        dialog = PostUpdateDialog(self)
        dialog.setWindowIcon(QIcon("demo/icons/post_update.png"))
        apply_palette_to_dialog(dialog, color=(250, 220, 230))  # Light pink
        dialog.exec_()

    def showS3UpdateDialog(self):
        dialog = S3UpdateDialog(self)
        dialog.setWindowIcon(QIcon("demo/icons/update_s3.png"))
        apply_palette_to_dialog(
            dialog, color=(230, 250, 220)
        )  # Different shade of light green
        dialog.exec_()

    def showRemapCategoriesDialog(self):
        dialog = RemapCategoriesDialog(self)
        dialog.setWindowIcon(QIcon("demo/icons/remap.png"))
        apply_palette_to_dialog(dialog, color=(240, 240, 220))  # Light yellow
        dialog.exec_()

    def showSplitNameDialog(self):
        dialog = SplitNameDialog(self)
        dialog.setWindowIcon(QIcon("demo/icons/split_name.png"))
        apply_palette_to_dialog(dialog, color=(240, 220, 230))  # Light pink
        dialog.exec_()
        
    def showAdvancedVisualizeDialog(self):
        # This will be implemented with a new dialog that offers more visualization options
        try:
            from dialogs.advanced_visualize_dialog import AdvancedVisualizeDialog
            dialog = AdvancedVisualizeDialog(self)
            dialog.setWindowIcon(QIcon("demo/icons/visualization.png"))
            apply_palette_to_dialog(dialog, color=(200, 220, 255))  # Light blue
            dialog.exec_()
        except ImportError:
            QMessageBox.information(
                self,
                "Feature Not Available",
                "Advanced visualization is not yet implemented. This feature will be available in a future update."
            )
            self.statusBar.showMessage("Advanced visualization not available", 3000)
    
    def showValidateDialog(self):
        # This will use the validate function from coco_operation.py
        try:
            from dialogs.validate_dialog import ValidateDialog
            dialog = ValidateDialog(self)
            dialog.setWindowIcon(QIcon("demo/icons/validate.png"))
            apply_palette_to_dialog(dialog, color=(255, 240, 220))  # Light orange
            dialog.exec_()
        except ImportError:
            # If the dialog doesn't exist yet, create a simple implementation
            from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDialog, QVBoxLayout, QPushButton, QLabel
            import os
            from cvops.coco_operation import validate as coco_validate
            
            class SimpleValidateDialog(QDialog):
                def __init__(self, parent=None):
                    super().__init__(parent)
                    self.setWindowTitle("Validate Dataset")
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
                    
                    validateButton = QPushButton("Validate")
                    validateButton.clicked.connect(self.validate)
                    layout.addWidget(validateButton)
                    
                    self.setLayout(layout)
                
                def selectImgDir(self):
                    directory = QFileDialog.getExistingDirectory(self, "Select Image Directory")
                    if directory:
                        self.imgDirLabel.setText(f"Image Directory: {directory}")
                
                def selectAnnPath(self):
                    annPath, _ = QFileDialog.getOpenFileName(self, "Select Annotation File", filter="JSON files (*.json)")
                    if annPath:
                        self.annPathLabel.setText(f"Annotation File: {annPath}")
                
                def validate(self):
                    img_dir = self.imgDirLabel.text().replace("Image Directory: ", "")
                    ann_path = self.annPathLabel.text().replace("Annotation File: ", "")
                    
                    if not os.path.exists(img_dir) or not os.path.exists(ann_path):
                        QMessageBox.critical(self, "Error", "Please select valid image directory and annotation file.")
                        return
                    
                    try:
                        coco_validate(img_dir, ann_path)
                        QMessageBox.information(self, "Validation", "Validation completed. Check the terminal for results.")
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Validation failed: {str(e)}")
            
            dialog = SimpleValidateDialog(self)
            dialog.setWindowIcon(QIcon("demo/icons/validate.png"))
            apply_palette_to_dialog(dialog, color=(255, 240, 220))  # Light orange
            dialog.exec_()
    
    def showStatsDialog(self):
        # This will display statistics about the dataset
        try:
            from dialogs.stats_dialog import StatsDialog
            dialog = StatsDialog(self)
            dialog.setWindowIcon(QIcon("demo/icons/statistics.png"))
            apply_palette_to_dialog(dialog, color=(220, 255, 220))  # Light green
            dialog.exec_()
        except ImportError:
            # If the dialog doesn't exist yet, create a simple implementation
            from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDialog, QVBoxLayout, QPushButton, QLabel, QTextEdit
            import json
            from pycocotools.coco import COCO
            
            class SimpleStatsDialog(QDialog):
                def __init__(self, parent=None):
                    super().__init__(parent)
                    self.setWindowTitle("Dataset Statistics")
                    self.setMinimumSize(600, 400)
                    layout = QVBoxLayout()
                    
                    self.annPathLabel = QLabel("Annotation File: Not Selected")
                    layout.addWidget(self.annPathLabel)
                    
                    annPathButton = QPushButton("Select Annotation File")
                    annPathButton.clicked.connect(self.selectAnnPath)
                    layout.addWidget(annPathButton)
                    
                    analyzeButton = QPushButton("Analyze Dataset")
                    analyzeButton.clicked.connect(self.analyzeDataset)
                    layout.addWidget(analyzeButton)
                    
                    self.statsText = QTextEdit()
                    self.statsText.setReadOnly(True)
                    layout.addWidget(self.statsText)
                    
                    self.setLayout(layout)
                
                def selectAnnPath(self):
                    annPath, _ = QFileDialog.getOpenFileName(self, "Select Annotation File", filter="JSON files (*.json)")
                    if annPath:
                        self.annPathLabel.setText(f"Annotation File: {annPath}")
                
                def analyzeDataset(self):
                    ann_path = self.annPathLabel.text().replace("Annotation File: ", "")
                    
                    if not ann_path or not os.path.exists(ann_path):
                        QMessageBox.critical(self, "Error", "Please select a valid annotation file.")
                        return
                    
                    try:
                        # Load COCO dataset
                        coco = COCO(ann_path)
                        
                        # Get basic statistics
                        num_images = len(coco.imgs)
                        num_annotations = len(coco.anns)
                        num_categories = len(coco.cats)
                        
                        # Get category distribution
                        category_counts = {}
                        for cat_id, cat in coco.cats.items():
                            category_counts[cat['name']] = 0
                        
                        for ann_id, ann in coco.anns.items():
                            cat_id = ann['category_id']
                            if cat_id in coco.cats:
                                cat_name = coco.cats[cat_id]['name']
                                category_counts[cat_name] += 1
                        
                        # Format statistics
                        stats_text = f"Dataset Summary:\n"
                        stats_text += f"Total Images: {num_images}\n"
                        stats_text += f"Total Annotations: {num_annotations}\n"
                        stats_text += f"Total Categories: {num_categories}\n\n"
                        
                        stats_text += f"Category Distribution:\n"
                        for cat_name, count in category_counts.items():
                            stats_text += f"  {cat_name}: {count} annotations\n"
                        
                        # Calculate average annotations per image
                        avg_anns_per_img = num_annotations / num_images if num_images > 0 else 0
                        stats_text += f"\nAverage Annotations per Image: {avg_anns_per_img:.2f}\n"
                        
                        self.statsText.setText(stats_text)
                        
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Analysis failed: {str(e)}")
                        self.statsText.setText(f"Error: {str(e)}")
            
            dialog = SimpleStatsDialog(self)
            dialog.setWindowIcon(QIcon("demo/icons/statistics.png"))
            apply_palette_to_dialog(dialog, color=(220, 255, 220))  # Light green
            dialog.exec_()
    
    def showFormatConversionDialog(self):
        # This will handle format conversion between different annotation formats
        try:
            from dialogs.format_conversion_dialog import FormatConversionDialog
            dialog = FormatConversionDialog(self)
            dialog.setWindowIcon(QIcon("demo/icons/convert.png"))
            apply_palette_to_dialog(dialog, color=(255, 220, 255))  # Light purple
            dialog.exec_()
        except ImportError:
            QMessageBox.information(
                self,
                "Feature Not Available",
                "Format conversion is not yet implemented. This feature will be available in a future update."
            )
            self.statusBar.showMessage("Format conversion not available", 3000)


def apply_palette_to_dialog(dialog, color=(200, 200, 200)):
    # Create a new palette for the dialog with lighter gray
    dialogPalette = QPalette()
    dialogPalette.setColor(QPalette.Window, QColor(*color))
    dialogPalette.setColor(QPalette.WindowText, Qt.black)  # Set text color if needed
    dialog.setPalette(dialogPalette)


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
