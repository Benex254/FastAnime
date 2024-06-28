import os
import shutil

from pyshortcuts import make_shortcut

from .. import ASSETS_DIR, PLATFORM


def create_desktop_shortcut():
    app = "_ -m fastanime --gui"

    logo = os.path.join(ASSETS_DIR, "logo.png")
    if PLATFORM == "Windows":
        logo = os.path.join(ASSETS_DIR, "logo.ico")
    if fastanime := shutil.which("fastanime"):
        app = f"{fastanime} --gui"
        make_shortcut(
            app,
            name="FastAnime",
            description="Download and watch anime",
            terminal=False,
            icon=logo,
            executable=fastanime,
        )
    else:
        make_shortcut(
            app,
            name="FastAnime",
            description="Download and watch anime",
            terminal=False,
            icon=logo,
        )
