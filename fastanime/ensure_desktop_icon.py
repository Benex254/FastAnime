import os
import shutil

from kivy.utils import platform
from pyshortcuts import make_shortcut

from . import assets_folder

app = "_ -m fastanime"

if fastanime := shutil.which("fastanime"):
    app = fastanime


logo = os.path.join(assets_folder, "logo.png")

if platform == "win":
    logo = os.path.join(assets_folder, "logo.ico")

make_shortcut(
    app,
    name="FastAnime",
    description="Download and watch anime",
    terminal=False,
    icon=logo,
)
