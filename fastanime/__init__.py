import logging
import os
import sys
from platform import platform

import plyer
from rich.traceback import install

install(show_locals=True)
# Create a logger instance
logger = logging.getLogger(__name__)

# initiate constants
__version__ = "0.3.0"

PLATFORM = platform()
APP_NAME = "FastAnime"

# ---- app deps ----
APP_DIR = os.path.abspath(os.path.dirname(__file__))
CONFIGS_DIR = os.path.join(APP_DIR, "configs")
ASSETS_DIR = os.path.join(APP_DIR, "assets")

# ----- user configs and data -----
if PLATFORM == "windows":
    APP_DATA_DIR_ = os.environ.get("LOCALAPPDATA", APP_DIR)
else:
    APP_DATA_DIR_ = os.environ.get("XDG_DATA_HOME", APP_DIR)

if not APP_DATA_DIR_:
    APP_DATA_DIR = os.path.join(APP_DIR, "data")
else:
    APP_DATA_DIR = os.path.join(APP_DATA_DIR_, APP_NAME)

if not os.path.exists(APP_DATA_DIR):
    os.mkdir(APP_DATA_DIR)

USER_DATA_PATH = os.path.join(APP_DATA_DIR, "user_data.json")
USER_CONFIG_PATH = os.path.join(APP_DATA_DIR, "config.ini")


# video dir
if vid_path := plyer.storagepath.get_videos_dir():  # type: ignore
    USER_DOWNLOADS_DIR = os.path.join(vid_path, "FastAnime")
else:
    USER_DOWNLOADS_DIR = os.path.join(APP_DIR, "videos")

if not os.path.exists(USER_DOWNLOADS_DIR):
    os.mkdir(USER_DOWNLOADS_DIR)


def FastAnime(gui=False):
    if "--gui" in sys.argv:
        gui = True
        sys.argv.remove("--gui")
        # Configure logging
        from rich.logging import RichHandler

        logging.basicConfig(
            level=logging.DEBUG,  # Set the logging level to DEBUG
            format="%(message)s",  # Use a simple message format
            datefmt="[%X]",  # Use a custom date format
            handlers=[RichHandler()],  # Use RichHandler to format the logs
        )
    if gui:
        from .gui import run_gui

        run_gui()
    else:
        from .cli import run_cli

        run_cli()
