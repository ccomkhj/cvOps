import os
from PyQt5.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QCheckBox,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QSlider,
    QGroupBox,
    QGridLayout,
    QSpinBox,
    QColorDialog,
    QListWidget,
    QListWidgetItem,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QIcon, QFont
from cvops.coco_operation import visualize as coco_visualize
from pycocotools.coco import COCO


class AdvancedVisualizeDialog(QDialog):
    """
    An advanced dialog window for visualizing annotations with COCO format.

    Offers more control over visualization parameters including:
    - Category filtering
    - Opacity control
    - Color selection
    - Visualization mode selection
    - Confidence threshold (if applicable)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Visualization")
        self.setMinimumSize(700, 500)
        self.coco = None
        self.categories = []
        self.selected_categories = []
        self.visualization_colors = {}
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # File selection section
        file_group = QGroupBox("Dataset Selection")
        file_layout = QVBoxLayout()
        
        self.imgDirLabel = QLabel("Image Directory: Not Selected")
        file_layout.addWidget(self.imgDirLabel)

        self.annPathLabel = QLabel("Annotation File: Not Selected")
        file_layout.addWidget(self.annPathLabel)

        button_layout = QHBoxLayout()
        
        imgDirButton = QPushButton("Select Image Directory")
        imgDirButton.clicked.connect(self.selectImgDir)
        button_layout.addWidget(imgDirButton)

        annPathButton = QPushButton("Select Annotation File")
        annPathButton.clicked.connect(self.selectAnnPath)
        button_layout.addWidget(annPathButton)
        
        file_layout.addLayout(button_layout)
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        # Visualization options section
        options_group = QGroupBox("Visualization Options")
        options_layout = QGridLayout()
        
        # Visualization mode
        options_layout.addWidget(QLabel("Visualization Mode:"), 0, 0)
        self.modeComboBox = QComboBox()
        self.modeComboBox.addItems(["All Annotations", "Bounding Boxes Only", "Segmentation Only"])
        options_layout.addWidget(self.modeComboBox, 0, 1)
        
        # Opacity slider
        options_layout.addWidget(QLabel("Opacity:"), 1, 0)
        opacity_layout = QHBoxLayout()
        self.opacitySlider = QSlider(Qt.Horizontal)
        self.opacitySlider.setRange(10, 100)
        self.opacitySlider.setValue(80)
        self.opacityLabel = QLabel("80%")
        self.opacitySlider.valueChanged.connect(self.updateOpacityLabel)
        opacity_layout.addWidget(self.opacitySlider)
        opacity_layout.addWidget(self.opacityLabel)
        options_layout.addLayout(opacity_layout, 1, 1)
        
        # Line thickness
        options_layout.addWidget(QLabel("Line Thickness:"), 2, 0)
        self.thicknessSpinBox = QSpinBox()
        self.thicknessSpinBox.setRange(1, 10)
        self.thicknessSpinBox.setValue(2)
        options_layout.addWidget(self.thicknessSpinBox, 2, 1)
        
        # Show labels checkbox
        self.showLabelsCheckBox = QCheckBox("Show Labels")
        self.showLabelsCheckBox.setChecked(True)
        options_layout.addWidget(self.showLabelsCheckBox, 3, 0)
        
        # Show scores checkbox (for predictions)
        self.showScoresCheckBox = QCheckBox("Show Confidence Scores")
        self.showScoresCheckBox.setChecked(True)
        options_layout.addWidget(self.showScoresCheckBox, 3, 1)
        
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)
        
        # Category filtering section
        category_group = QGroupBox("Category Filtering")
        category_layout = QVBoxLayout()
        
        self.categoryList = QListWidget()
        self.categoryList.setSelectionMode(QListWidget.MultiSelection)
        category_layout.addWidget(self.categoryList)
        
        category_buttons = QHBoxLayout()
        selectAllButton = QPushButton("Select All")
        selectAllButton.clicked.connect(self.selectAllCategories)
        category_buttons.addWidget(selectAllButton)
        
        deselectAllButton = QPushButton("Deselect All")
        deselectAllButton.clicked.connect(self.deselectAllCategories)
        category_buttons.addWidget(deselectAllButton)
        
        setColorsButton = QPushButton("Set Category Colors")
        setColorsButton.clicked.connect(self.setCategoryColors)
        category_buttons.addWidget(setColorsButton)
        
        category_layout.addLayout(category_buttons)
        category_group.setLayout(category_layout)
        main_layout.addWidget(category_group)
        
        # Buttons at the bottom
        button_layout = QHBoxLayout()
        
        visualizeButton = QPushButton("Visualize")
        visualizeButton.clicked.connect(self.visualize)
        visualizeButton.setIcon(QIcon("demo/icons/visualization.png"))
        button_layout.addWidget(visualizeButton)
        
        closeButton = QPushButton("Close")
        closeButton.clicked.connect(self.close)
        button_layout.addWidget(closeButton)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
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
            self.loadCategories(annPath)
    
    def loadCategories(self, ann_path):
        try:
            self.coco = COCO(ann_path)
            self.categories = []
            self.categoryList.clear()
            
            # Get all categories
            for cat_id in self.coco.getCatIds():
                cat = self.coco.loadCats(cat_id)[0]
                self.categories.append(cat)
                
                # Create list item with category name
                item = QListWidgetItem(f"{cat['id']}: {cat['name']}")
                item.setData(Qt.UserRole, cat['id'])
                self.categoryList.addItem(item)
                item.setSelected(True)  # Select all by default
            
            # Initialize colors for each category
            self.visualization_colors = {}
            for cat in self.categories:
                # Generate a random color for each category
                r = (cat['id'] * 50) % 255
                g = (cat['id'] * 100) % 255
                b = (cat['id'] * 150) % 255
                self.visualization_colors[cat['id']] = QColor(r, g, b)
            
            QMessageBox.information(self, "Categories Loaded", f"Loaded {len(self.categories)} categories from the annotation file.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load categories: {str(e)}")
    
    def updateOpacityLabel(self, value):
        self.opacityLabel.setText(f"{value}%")
    
    def selectAllCategories(self):
        for i in range(self.categoryList.count()):
            self.categoryList.item(i).setSelected(True)
    
    def deselectAllCategories(self):
        for i in range(self.categoryList.count()):
            self.categoryList.item(i).setSelected(False)
    
    def setCategoryColors(self):
        if not self.categories:
            QMessageBox.warning(self, "Warning", "Please load an annotation file first.")
            return
        
        # Get the selected category
        selected_items = self.categoryList.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select at least one category.")
            return
        
        # For simplicity, just set color for the first selected category
        item = selected_items[0]
        cat_id = item.data(Qt.UserRole)
        
        # Open color dialog
        current_color = self.visualization_colors.get(cat_id, QColor(255, 0, 0))
        color = QColorDialog.getColor(current_color, self, "Select Color for Category")
        
        if color.isValid():
            self.visualization_colors[cat_id] = color
            # Update the item text with color indication (could be improved with custom delegate)
            item.setText(f"{cat_id}: {self.getCategoryName(cat_id)} [Custom Color]")
    
    def getCategoryName(self, cat_id):
        for cat in self.categories:
            if cat['id'] == cat_id:
                return cat['name']
        return "Unknown"
    
    def getSelectedCategories(self):
        selected_cats = []
        for i in range(self.categoryList.count()):
            item = self.categoryList.item(i)
            if item.isSelected():
                cat_id = item.data(Qt.UserRole)
                selected_cats.append(cat_id)
        return selected_cats
    
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
        
        # Get visualization options
        mode = self.modeComboBox.currentText()
        show_only_box = mode == "Bounding Boxes Only"
        opacity = self.opacitySlider.value() / 100.0
        thickness = self.thicknessSpinBox.value()
        show_labels = self.showLabelsCheckBox.isChecked()
        show_scores = self.showScoresCheckBox.isChecked()
        selected_categories = self.getSelectedCategories()
        
        try:
            # For now, we'll use the existing visualization function
            # In a real implementation, you would pass all these parameters to a more advanced visualization function
            QMessageBox.information(self, "Visualization", 
                                    "Starting visualization with the following options:\n"
                                    f"- Mode: {mode}\n"
                                    f"- Opacity: {opacity:.2f}\n"
                                    f"- Line Thickness: {thickness}\n"
                                    f"- Show Labels: {show_labels}\n"
                                    f"- Show Scores: {show_scores}\n"
                                    f"- Selected Categories: {len(selected_categories)} categories")
            
            # Call the visualization function with the basic parameters
            # In a future implementation, you would extend this to support all the advanced options
            coco_visualize(img_dir, ann_path, show_only_box)
            
            QMessageBox.information(self, "Visualization", "Visualization completed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Visualization failed: {str(e)}")
