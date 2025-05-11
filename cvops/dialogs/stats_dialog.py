import os
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTabWidget,
    QWidget,
    QTextEdit,
    QGroupBox,
    QGridLayout,
    QComboBox,
    QCheckBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from pycocotools.coco import COCO


class MplCanvas(FigureCanvas):
    """Matplotlib canvas for embedding plots in PyQt"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)


class StatsDialog(QDialog):
    """
    A dialog for visualizing statistics about COCO datasets.
    
    Provides various statistical visualizations and analyses of COCO datasets,
    including category distributions, image sizes, annotation counts, etc.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dataset Statistics")
        self.setMinimumSize(900, 700)
        self.coco = None
        self.setupUI()
    
    def setupUI(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # File selection section
        file_group = QGroupBox("Dataset Selection")
        file_layout = QVBoxLayout()
        
        self.annPathLabel = QLabel("Annotation File: Not Selected")
        file_layout.addWidget(self.annPathLabel)
        
        button_layout = QHBoxLayout()
        
        annPathButton = QPushButton("Select Annotation File")
        annPathButton.clicked.connect(self.selectAnnPath)
        button_layout.addWidget(annPathButton)
        
        analyzeButton = QPushButton("Analyze Dataset")
        analyzeButton.clicked.connect(self.analyzeDataset)
        button_layout.addWidget(analyzeButton)
        
        file_layout.addLayout(button_layout)
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        # Tabs for different statistics views
        self.tabWidget = QTabWidget()
        
        # Summary tab
        self.summaryTab = QWidget()
        summary_layout = QVBoxLayout(self.summaryTab)
        self.summaryText = QTextEdit()
        self.summaryText.setReadOnly(True)
        summary_layout.addWidget(self.summaryText)
        self.tabWidget.addTab(self.summaryTab, "Summary")
        
        # Categories tab
        self.categoriesTab = QWidget()
        categories_layout = QVBoxLayout(self.categoriesTab)
        
        # Add a canvas for the category distribution chart
        self.categoryCanvas = MplCanvas(self, width=5, height=4, dpi=100)
        categories_layout.addWidget(self.categoryCanvas)
        
        # Add a table for detailed category information
        self.categoryTable = QTableWidget()
        self.categoryTable.setColumnCount(4)
        self.categoryTable.setHorizontalHeaderLabels(["ID", "Name", "Supercategory", "Count"])
        self.categoryTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        categories_layout.addWidget(self.categoryTable)
        
        self.tabWidget.addTab(self.categoriesTab, "Categories")
        
        # Images tab
        self.imagesTab = QWidget()
        images_layout = QVBoxLayout(self.imagesTab)
        
        # Add a canvas for image size distribution
        self.imageCanvas = MplCanvas(self, width=5, height=4, dpi=100)
        images_layout.addWidget(self.imageCanvas)
        
        # Add image statistics text
        self.imageStatsText = QTextEdit()
        self.imageStatsText.setReadOnly(True)
        self.imageStatsText.setMaximumHeight(150)
        images_layout.addWidget(self.imageStatsText)
        
        self.tabWidget.addTab(self.imagesTab, "Images")
        
        # Annotations tab
        self.annotationsTab = QWidget()
        annotations_layout = QVBoxLayout(self.annotationsTab)
        
        # Add a canvas for annotations per image distribution
        self.annotationsCanvas = MplCanvas(self, width=5, height=4, dpi=100)
        annotations_layout.addWidget(self.annotationsCanvas)
        
        # Add annotation statistics text
        self.annotationStatsText = QTextEdit()
        self.annotationStatsText.setReadOnly(True)
        self.annotationStatsText.setMaximumHeight(150)
        annotations_layout.addWidget(self.annotationStatsText)
        
        self.tabWidget.addTab(self.annotationsTab, "Annotations")
        
        main_layout.addWidget(self.tabWidget)
        
        # Close button
        closeButton = QPushButton("Close")
        closeButton.clicked.connect(self.close)
        main_layout.addWidget(closeButton)
    
    def selectAnnPath(self):
        annPath, _ = QFileDialog.getOpenFileName(
            self, "Select Annotation File", filter="JSON files (*.json)"
        )
        if annPath:
            self.annPathLabel.setText(f"Annotation File: {annPath}")
    
    def analyzeDataset(self):
        ann_path = self.annPathLabel.text().replace("Annotation File: ", "")
        
        if not ann_path or not os.path.exists(ann_path):
            QMessageBox.critical(self, "Error", "Please select a valid annotation file.")
            return
        
        try:
            # Load COCO dataset
            self.coco = COCO(ann_path)
            
            # Update all tabs with the dataset information
            self.updateSummaryTab()
            self.updateCategoriesTab()
            self.updateImagesTab()
            self.updateAnnotationsTab()
            
            QMessageBox.information(self, "Analysis Complete", "Dataset analysis completed successfully.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Analysis failed: {str(e)}")
    
    def updateSummaryTab(self):
        if not self.coco:
            return
        
        # Get basic statistics
        num_images = len(self.coco.imgs)
        num_annotations = len(self.coco.anns)
        num_categories = len(self.coco.cats)
        
        # Calculate annotations per image
        anns_per_img = {}
        for img_id in self.coco.imgs:
            ann_ids = self.coco.getAnnIds(imgIds=img_id)
            anns_per_img[img_id] = len(ann_ids)
        
        avg_anns_per_img = sum(anns_per_img.values()) / len(anns_per_img) if anns_per_img else 0
        max_anns_per_img = max(anns_per_img.values()) if anns_per_img else 0
        min_anns_per_img = min(anns_per_img.values()) if anns_per_img else 0
        
        # Get image size information
        img_widths = [img['width'] for img in self.coco.imgs.values()]
        img_heights = [img['height'] for img in self.coco.imgs.values()]
        
        avg_width = sum(img_widths) / len(img_widths) if img_widths else 0
        avg_height = sum(img_heights) / len(img_heights) if img_heights else 0
        
        # Format summary text
        summary_text = f"<h2>Dataset Summary</h2>"
        summary_text += f"<p><b>Total Images:</b> {num_images}</p>"
        summary_text += f"<p><b>Total Annotations:</b> {num_annotations}</p>"
        summary_text += f"<p><b>Total Categories:</b> {num_categories}</p>"
        
        summary_text += f"<h3>Annotation Statistics</h3>"
        summary_text += f"<p><b>Average Annotations per Image:</b> {avg_anns_per_img:.2f}</p>"
        summary_text += f"<p><b>Maximum Annotations in an Image:</b> {max_anns_per_img}</p>"
        summary_text += f"<p><b>Minimum Annotations in an Image:</b> {min_anns_per_img}</p>"
        
        summary_text += f"<h3>Image Size Statistics</h3>"
        summary_text += f"<p><b>Average Image Width:</b> {avg_width:.2f} pixels</p>"
        summary_text += f"<p><b>Average Image Height:</b> {avg_height:.2f} pixels</p>"
        summary_text += f"<p><b>Width Range:</b> {min(img_widths)} to {max(img_widths)} pixels</p>"
        summary_text += f"<p><b>Height Range:</b> {min(img_heights)} to {max(img_heights)} pixels</p>"
        
        self.summaryText.setHtml(summary_text)
    
    def updateCategoriesTab(self):
        if not self.coco:
            return
        
        # Get category distribution
        category_counts = {}
        for cat_id in self.coco.cats:
            category_counts[cat_id] = 0
        
        for ann in self.coco.anns.values():
            cat_id = ann['category_id']
            if cat_id in category_counts:
                category_counts[cat_id] += 1
        
        # Create bar chart of category distribution
        self.categoryCanvas.axes.clear()
        
        # Sort categories by count
        sorted_cats = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        cat_ids = [cat_id for cat_id, _ in sorted_cats]
        counts = [count for _, count in sorted_cats]
        cat_names = [self.coco.cats[cat_id]['name'] for cat_id in cat_ids]
        
        # Create bar chart
        bars = self.categoryCanvas.axes.bar(range(len(cat_ids)), counts, color='skyblue')
        self.categoryCanvas.axes.set_xticks(range(len(cat_ids)))
        self.categoryCanvas.axes.set_xticklabels(cat_names, rotation=45, ha='right')
        self.categoryCanvas.axes.set_title('Category Distribution')
        self.categoryCanvas.axes.set_ylabel('Number of Annotations')
        
        # Add count labels on top of bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            self.categoryCanvas.axes.text(
                bar.get_x() + bar.get_width()/2., height + 0.1,
                str(count), ha='center', va='bottom', rotation=0
            )
        
        self.categoryCanvas.fig.tight_layout()
        self.categoryCanvas.draw()
        
        # Update category table
        self.categoryTable.setRowCount(len(self.coco.cats))
        
        for i, (cat_id, cat) in enumerate(self.coco.cats.items()):
            self.categoryTable.setItem(i, 0, QTableWidgetItem(str(cat_id)))
            self.categoryTable.setItem(i, 1, QTableWidgetItem(cat['name']))
            self.categoryTable.setItem(i, 2, QTableWidgetItem(cat.get('supercategory', 'N/A')))
            self.categoryTable.setItem(i, 3, QTableWidgetItem(str(category_counts.get(cat_id, 0))))
    
    def updateImagesTab(self):
        if not self.coco:
            return
        
        # Get image size information
        img_widths = [img['width'] for img in self.coco.imgs.values()]
        img_heights = [img['height'] for img in self.coco.imgs.values()]
        img_areas = [w * h for w, h in zip(img_widths, img_heights)]
        aspect_ratios = [w / h for w, h in zip(img_widths, img_heights)]
        
        # Create scatter plot of image dimensions
        self.imageCanvas.axes.clear()
        self.imageCanvas.axes.scatter(img_widths, img_heights, alpha=0.5)
        self.imageCanvas.axes.set_xlabel('Width (pixels)')
        self.imageCanvas.axes.set_ylabel('Height (pixels)')
        self.imageCanvas.axes.set_title('Image Dimensions')
        self.imageCanvas.fig.tight_layout()
        self.imageCanvas.draw()
        
        # Calculate image statistics
        avg_width = sum(img_widths) / len(img_widths) if img_widths else 0
        avg_height = sum(img_heights) / len(img_heights) if img_heights else 0
        avg_area = sum(img_areas) / len(img_areas) if img_areas else 0
        avg_aspect = sum(aspect_ratios) / len(aspect_ratios) if aspect_ratios else 0
        
        # Count common resolutions
        resolution_counts = {}
        for w, h in zip(img_widths, img_heights):
            resolution = f"{w}x{h}"
            resolution_counts[resolution] = resolution_counts.get(resolution, 0) + 1
        
        # Sort resolutions by count
        sorted_resolutions = sorted(resolution_counts.items(), key=lambda x: x[1], reverse=True)
        top_resolutions = sorted_resolutions[:5]  # Top 5 resolutions
        
        # Format image statistics text
        stats_text = f"<h3>Image Size Statistics</h3>"
        stats_text += f"<p><b>Average Dimensions:</b> {avg_width:.2f} x {avg_height:.2f} pixels</p>"
        stats_text += f"<p><b>Average Area:</b> {avg_area:.2f} pixels²</p>"
        stats_text += f"<p><b>Average Aspect Ratio (W/H):</b> {avg_aspect:.2f}</p>"
        
        stats_text += f"<h3>Common Resolutions</h3>"
        stats_text += "<ul>"
        for resolution, count in top_resolutions:
            stats_text += f"<li>{resolution}: {count} images ({count/len(img_widths)*100:.1f}%)</li>"
        stats_text += "</ul>"
        
        self.imageStatsText.setHtml(stats_text)
    
    def updateAnnotationsTab(self):
        if not self.coco:
            return
        
        # Calculate annotations per image
        anns_per_img = {}
        for img_id in self.coco.imgs:
            ann_ids = self.coco.getAnnIds(imgIds=img_id)
            anns_per_img[img_id] = len(ann_ids)
        
        # Create histogram of annotations per image
        self.annotationsCanvas.axes.clear()
        self.annotationsCanvas.axes.hist(list(anns_per_img.values()), bins=20, alpha=0.7, color='skyblue')
        self.annotationsCanvas.axes.set_xlabel('Annotations per Image')
        self.annotationsCanvas.axes.set_ylabel('Number of Images')
        self.annotationsCanvas.axes.set_title('Distribution of Annotations per Image')
        self.annotationsCanvas.fig.tight_layout()
        self.annotationsCanvas.draw()
        
        # Calculate annotation statistics
        ann_counts = list(anns_per_img.values())
        avg_anns = sum(ann_counts) / len(ann_counts) if ann_counts else 0
        median_anns = sorted(ann_counts)[len(ann_counts)//2] if ann_counts else 0
        max_anns = max(ann_counts) if ann_counts else 0
        min_anns = min(ann_counts) if ann_counts else 0
        
        # Count images with zero annotations
        zero_anns = sum(1 for count in ann_counts if count == 0)
        
        # Check for segmentation vs bbox annotations
        has_segmentation = 0
        has_bbox = 0
        for ann in self.coco.anns.values():
            if 'segmentation' in ann and ann['segmentation']:
                has_segmentation += 1
            if 'bbox' in ann and ann['bbox']:
                has_bbox += 1
        
        # Format annotation statistics text
        stats_text = f"<h3>Annotation Distribution</h3>"
        stats_text += f"<p><b>Average Annotations per Image:</b> {avg_anns:.2f}</p>"
        stats_text += f"<p><b>Median Annotations per Image:</b> {median_anns}</p>"
        stats_text += f"<p><b>Maximum Annotations in an Image:</b> {max_anns}</p>"
        stats_text += f"<p><b>Minimum Annotations in an Image:</b> {min_anns}</p>"
        stats_text += f"<p><b>Images with No Annotations:</b> {zero_anns} ({zero_anns/len(ann_counts)*100:.1f}% of images)</p>"
        
        stats_text += f"<h3>Annotation Types</h3>"
        stats_text += f"<p><b>Annotations with Segmentation:</b> {has_segmentation} ({has_segmentation/len(self.coco.anns)*100:.1f}% of annotations)</p>"
        stats_text += f"<p><b>Annotations with Bounding Boxes:</b> {has_bbox} ({has_bbox/len(self.coco.anns)*100:.1f}% of annotations)</p>"
        
        self.annotationStatsText.setHtml(stats_text)
