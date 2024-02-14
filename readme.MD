# cvOps

cvOps offers a Graphical User Interface (GUI) for managing COCO datasets with ease. It utilizes PyQt5 to provide a straightforward and user-friendly experience for visualizing annotations, merging datasets, splitting datasets, and updating annotations. This utility is especially useful for researchers and developers working with machine learning and computer vision tasks that involve COCO datasets.

## Features

- **Visualize Annotations**: Supports the visualization of bounding boxes and segmentation masks directly from the COCO annotations.
- **Merge Datasets**: Combine multiple COCO datasets into a single dataset, merging both the image sets and annotation files.
- **Split Dataset**: Partition a COCO dataset into training and validation sets based on a specified split ratio.
- **Update Dataset**: Integrate new annotations with existing training and validation sets, allowing for continuous dataset expansion and improvement.

## Getting Started

1. **Launch**: Run the script to open the COCO Tools GUI.

    ```bash
    python3 cvops/gui_coco_operation.py
    ```

2. **Usage**:
    - Upon launching, the main window presents options for Visualization, Merging, Splitting, and Updating datasets.
    - **Visualize**: Click on the "Visualize" button and select an image directory along with the corresponding annotation file. Choose to visualize bounding boxes or segmentation masks.
    - **Merge**: To merge datasets, select the image and annotation directories for each dataset you wish to merge. Specify if images should be merged.
    - **Split**: Choose an annotation file and an image directory for splitting. Specify the split ratio to determine the size of the training set.
    - **Update**: For updating a dataset, select new annotations, existing training and validation annotation files, and an image location. Specify the split ratio for new data.

## Contributing

Feel free to fork the repository and submit pull requests to add new features or improvements to the existing GUI tool.