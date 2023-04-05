import os

import cv2
import matplotlib.pyplot as plt
import numpy as np
import typer
import yaml
from PIL import Image

from tools.helpers import load, palette2mask

app = typer.Typer(help="Awesome cvOps Tool.", rich_markup_mode="rich")


@app.command()
def visualize(
    img_dir: str = typer.Argument(..., help="directory of images"),
    ann_dir: str = typer.Argument(..., help="directory of annotations"),
):
    """
    [bold green]Visualize mask sample[/bold green]
    """
    anns = load(ann_dir)
    imgs = load(img_dir)

    for ann, img in zip(anns, imgs):
        palette = cv2.cvtColor(cv2.imread(ann), cv2.COLOR_BGR2RGB)
        im = cv2.cvtColor(cv2.imread(img), cv2.COLOR_BGR2RGB)

        alpha = 0.5
        overlap = cv2.addWeighted(palette, alpha, im, 1 - alpha, 0.0)

        plt.imshow(overlap)
        plt.title(f"overlap image of {os.path.basename(img)}")
        plt.show()


@app.command()
def convert(
    ann_dir: str = typer.Argument(..., help="directory of annotations"),
    save_dir: str = typer.Argument(..., help="directory of saved masks"),
    config: str = typer.Argument(
        default="config/mask.yaml", help="location of config file"
    ),
):
    """
    [bold green]Convert 3 Channel mask to 1 Channel. [/bold green]
    """
    anns = load(ann_dir)

    # Load config file
    with open(config, "r") as stream:
        try:
            conv = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    for ann in anns:
        mask = palette2mask(ann, conv)
        name = os.path.basename(ann).split("__")[
            0
        ]  # It should be modifed for your use-case.

        print(f"Annotation of {name} is processed.")

        name = name.split(".")[0]  # get rid of jpg format
        Image.fromarray(mask).convert("P").save(os.path.join(save_dir, name + ".png"))

    print(f"Conversion is successfully done.")


@app.command()
def show(
    mask_dir: str = typer.Argument(..., help="directory of binary(-like) masks."),
):
    """
    [bold green]Visualize mask sample[/bold green]
    """
    anns = load(mask_dir)

    for ann in anns:
        mask = cv2.cvtColor(cv2.imread(ann), cv2.COLOR_BGR2GRAY)
        plt.imshow(mask, cmap="Paired")
        plt.title(f"Mask of {os.path.basename(ann)}")
        plt.show()

@app.command()
def checkcolor(
    mask_dir: str = typer.Argument(..., help="directory of binary(-like) masks."),
):
    """
    [bold green]Visualize mask sample[/bold green]
    """
    anns = load(mask_dir)

    for ann in anns:

        mask = cv2.cvtColor(cv2.imread(ann), cv2.COLOR_BGR2RGB)
        plt.imshow(mask)
        print(f"Mask of {os.path.basename(ann)}. Palletes are: {np.unique(mask.reshape(-1, mask.shape[2]), axis=0)}")
        plt.title(f"Mask of {os.path.basename(ann)}. Palletes are: {np.unique(mask.reshape(-1, mask.shape[2]), axis=0)}")
        plt.show()

if __name__ == "__main__":
    app()
