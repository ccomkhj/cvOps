from pycocotools.coco import COCO
import json


def remove_coco_category(input_file_path, output_file_path, category_to_remove):
    # Load COCO dataset
    coco = COCO(input_file_path)

    # Find the category id for the category to remove
    category_ids_to_remove = coco.getCatIds(catNms=[category_to_remove])

    if not category_ids_to_remove:
        print(f"Category '{category_to_remove}' not found in the input file.")
        return

    category_id_to_remove = category_ids_to_remove[0]

    # Load original JSON data to preserve structure
    with open(input_file_path, "r") as file:
        coco_data = json.load(file)

    # Remove specified category
    coco_data["categories"] = [
        category
        for category in coco_data["categories"]
        if category["id"] != category_id_to_remove
    ]

    # Remove annotations related to the category
    coco_data["annotations"] = [
        annotation
        for annotation in coco_data["annotations"]
        if annotation["category_id"] != category_id_to_remove
    ]

    # Find all remaining categories and reassign their IDs starting from 1
    new_category_id_map = {
        category["id"]: idx + 1 for idx, category in enumerate(coco_data["categories"])
    }

    # Update category IDs in the categories list
    for category in coco_data["categories"]:
        category["id"] = new_category_id_map[category["id"]]

    # Update category IDs in the annotations
    for annotation in coco_data["annotations"]:
        annotation["category_id"] = new_category_id_map[annotation["category_id"]]

    # Find all image ids that still have annotations
    remaining_annotation_image_ids = {
        annotation["image_id"] for annotation in coco_data["annotations"]
    }

    # Keep only those images which have at least one annotation left
    coco_data["images"] = [
        image
        for image in coco_data["images"]
        if image["id"] in remaining_annotation_image_ids
    ]

    # Write the modified data back to a new JSON file
    with open(output_file_path, "w") as file:
        json.dump(coco_data, file, indent=4)

    print(
        f"Category '{category_to_remove}' has been removed and categories renumbered. The new file is saved as '{output_file_path}'."
    )


# Example usage
remove_coco_category(
    "annotations.json",
    "annotations_nodes.json",
    "leaves",
)
