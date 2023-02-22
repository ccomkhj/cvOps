from coco_assistant import COCO_Assistant
from sklearn.model_selection import train_test_split
from skmultilearn.model_selection import iterative_train_test_split
import typer
import json
import funcy
import numpy as np
from typing import Optional
from tools.helpers import filter_annotations, filter_images, save_coco

app = typer.Typer(help="Awesome cvOps Tool.", rich_markup_mode="rich")


@app.command()
def visualize(
    img_dir: str = typer.Argument(..., help="directory of images"),
    ann_dir: str = typer.Argument(..., help="directory of annotations"),
):
    """
    [bold green]Visualize coco sample[/bold green]

    [blue]
    Example:
    .
    ├── images_dir
    │   ├── sample1
    │   ├── sample2
    |   ├── sample3
    |
    ├── anns_dir
    │   ├── sample1.json
    │   ├── sample2.json
    │   ├── sample3.json
    [/blue]
    """

    # Create COCO_Assistant object
    cas = COCO_Assistant(img_dir, ann_dir)
    cas.visualise()


@app.command()
def merge(
    img_dir: str = typer.Argument(..., help="directory of images"),
    ann_dir: str = typer.Argument(..., help="directory of annotations"),
):
    """
    [bold green]Merge coco sample[/bold green]

    [blue]
    Example:
    .
    ├── images_dir
    │   ├── sample1
    │   ├── sample2
    |   ├── sample3
    |
    ├── anns_dir
    │   ├── sample1.json
    │   ├── sample2.json
    │   ├── sample3.json
    [/blue]
    """

    # Create COCO_Assistant object
    cas = COCO_Assistant(img_dir, ann_dir)
    cas.merge()


@app.command()
def split(
    ann_path: str = typer.Argument(..., help="Path to COCO annotations file."),
    train_path: str = typer.Argument(
        ..., help="Where to store COCO training annotations"
    ),
    test_path: str = typer.Argument(..., help="Where to store COCO test annotations"),
    split: float = typer.Argument(
        default=0.8, help="A ratio of a split; a number in (0, 1)"
    ),
    multi: Optional[bool] = typer.Argument(
        default=False,
        help="Split a multi-class dataset while preserving class distributions in train and test sets",
    ),
):

    with open(ann_path, "rt", encoding="UTF-8") as annotations:
        coco = json.load(annotations)
        info = coco["info"]
        licenses = coco["licenses"]
        images = coco["images"]
        annotations = coco["annotations"]
        categories = coco["categories"]

        images_with_annotations = funcy.lmap(lambda a: int(a["image_id"]), annotations)

        images = funcy.lremove(lambda i: i["id"] not in images_with_annotations, images)

        if multi:

            annotation_categories = funcy.lmap(
                lambda a: int(a["category_id"]), annotations
            )

            # bottle neck 1
            # remove classes that has only one sample, because it can't be split into the training and testing sets
            annotation_categories = funcy.lremove(
                lambda i: annotation_categories.count(i) <= 1, annotation_categories
            )

            annotations = funcy.lremove(
                lambda i: i["category_id"] not in annotation_categories, annotations
            )

            X_train, y_train, X_test, y_test = iterative_train_test_split(
                np.array([annotations]).T,
                np.array([annotation_categories]).T,
                test_size=1 - split,
            )

            save_coco(
                train_path,
                info,
                licenses,
                filter_images(images, X_train.reshape(-1)),
                X_train.reshape(-1).tolist(),
                categories,
            )
            save_coco(
                test_path,
                info,
                licenses,
                filter_images(images, X_test.reshape(-1)),
                X_test.reshape(-1).tolist(),
                categories,
            )

            print(
                "Saved {} entries in {} and {} in {}".format(
                    len(X_train), train_path, len(X_test), test_path
                )
            )

        else:

            X_train, X_test = train_test_split(images, train_size=split)

            anns_train = filter_annotations(annotations, X_train)
            anns_test = filter_annotations(annotations, X_test)

            save_coco(train_path, info, licenses, X_train, anns_train, categories)
            save_coco(test_path, info, licenses, X_test, anns_test, categories)

            print(
                "Saved {} entries in {} and {} in {}".format(
                    len(anns_train), train_path, len(anns_test), test_path
                )
            )


if __name__ == "__main__":
    app()
