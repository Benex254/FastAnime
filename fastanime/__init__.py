import os
import sys

from rich import print
from rich.traceback import install

import plyer

install()

# TODO:confirm data integrity

# ----- some useful paths -----
app_dir = os.path.abspath(os.path.dirname(__file__))
data_folder = os.path.join(app_dir, "data")
configs_folder = os.path.join(app_dir, "configs")
if not os.path.exists(data_folder):
    os.mkdir(data_folder)

if vid_path := plyer.storagepath.get_videos_dir():  # type: ignore
    downloads_dir = os.path.join(vid_path, "FastAnime")
    if not os.path.exists(downloads_dir):
        os.mkdir(downloads_dir)
else:
    # fallback
    downloads_dir = os.path.join(app_dir, "videos")
    if not os.path.exists(downloads_dir):
        os.mkdir(downloads_dir)

user_data_path = os.path.join(data_folder, "user_data.json")
assets_folder = os.path.join(app_dir, "assets")


def FastAnime(gui=False):
    if "--gui" in sys.argv:
        gui = True
        sys.argv.remove("--gui")
    print(f"Hello {os.environ.get("USERNAME")} from the fastanime team")
    if gui:
        print(__name__)
        from .gui.gui import run_gui

        print("Run GUI")
        run_gui()
    else:
        from .cli import run_cli

        run_cli()
