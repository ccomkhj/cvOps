# cvOps

cvOps provides an intuitive Graphical User Interface (GUI) for the streamlined management of COCO datasets. Utilizing the versatility of PyQt5, it stands as an essential toolkit for researchers and developers focused on machine learning and computer vision, simplifying critical tasks such as visualizing, merging, splitting, updating, and post-updating COCO datasets.


## Getting Started

0. **Install**: 
  ```bash
  pip install -e .
  pip install git+https://github.com/ccomkhj/COCO-Assistant.git@master
  ```

  Check if all test is successful using below.
  ```bash
  pytest
  ```

1. **Launch**: Activate the COCO Tools GUI by executing the accompanying script.

    ```bash
    python3 cvops/main_window.py
    ```

### 2. **Usage**:
The main interface presents options for Visualization, Merging, Splitting, Updating, and Post Updating of datasets.
- **Visualize**: To visualize COCO datasets.
- **Remap Categories**: Remap the sequence of categories.
- **Merge**: For merging datasets, indicate the image and annotation directories of the datasets to be combined. Specify if the image sets
 should also be merged. Note that directory name (i.e. sample1) and COCO file (i.e. sample1.json) should match.
 ```
 - .
 ├── images_dir
 │ ├── sample1
 │ ├── sample2
 │ ├── sample3
 │
 ├── anns_dir
 │ ├── sample1.json
 │ ├── sample2.json
 │ ├── sample3.json
 ```
- **Separate by Name**: Separate a dataset into multiple subsets based on parts of the image file names. This requires providing the path to the image files, the path to the COCO annotations file, and a list of name keys. The dataset will be split such that images matching each name key are grouped together, and new COCO annotation files will be created for each subset.
- **Split**: Splitting a dataset requires providing an annotation file and image directory, along with specifying the split ratio for training set allocation.
- **Update (Local)** : To run through Merge and Split in one-shot, select new annotations, and specify existing training and validation annotation files along with a new image location.
 : **Split (New Sample)** -> **Merge (Between New and Existing Samples for Train and Val Each)**
- **Update (S3)**: Same feature with `Update (Local)` but files are in AWS S3. Tip: Directly click the `Copy S3 URI` from the web interface. Configure `config/s3_credentials.yaml`
- **Post Update**: Execute post-update operations by choosing directories for new and existing samples. This ensures the dataset is optimized and organized according to the standard structure post-update. After checking the quality, you have an option to directly upload your updated project into S3.
 [Note] Even if you run S3 Update, still need to take Post Update.


1. **Data Structure**: After using cvOps, all data is structured as below. It supports other computer vision projects accordingly. ([SAHI](https://github.com/obss/sahi), [MMDET](https://github.com/open-mmlab/mmdetection))

  After performing the post-update process, the dataset will adhere to a standardized directory structure:

  ```
  /
  |-train_images/
  |-val_images/
  |-train.json
  |-val.json
  ```

  This structure organizes training and validation images into separate folders (`train_images`, `val_images`), with corresponding annotation files (`train.json`, `val.json`) located in the root dataset directory. This clear and efficient organization facilitates easy access and dataset management, crucial for training machine learning models effectively.

  Only then, you can use Update (S3). (Directly update project on AWS S3 bucket.)
  For this, `config/s3_credentials.yaml` is required.

  ```yaml
  aws_secret_access_key: {aws_secret_access_key}
  aws_access_key_id: {aws_access_key_id} 
  ```

![COCO Tools](demo/COCO_Tools.png)



## Contributing

We welcome and encourage contributions! Fork the repository and submit pull requests to propose new features or enhancements to the cvOps GUI tool, aiming to improve its utility in managing COCO datasets more efficiently and effectively.