from coco_assistant import COCO_Assistant
import os
import glob
from PIL import Image
import numpy as np
import typer
import yaml
from tqdm import tqdm
from rich import print
from rich.panel import Panel

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


if __name__ == "__main__":
    app()
