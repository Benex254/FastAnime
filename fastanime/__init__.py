import logging
import os
import sys
from platform import platform

from platformdirs import PlatformDirs
from rich.traceback import install

install(show_locals=True)
# Create a logger instance
logger = logging.getLogger(__name__)

# initiate constants
__version__ = "v0.30.0"

PLATFORM = platform()
APP_NAME = "FastAnime"
AUTHOR = "Benex254"
GIT_REPO = "github.com"
REPO = f"{GIT_REPO}/{AUTHOR}/{APP_NAME}"
USER_NAME = os.environ.get("USERNAME", f"{APP_NAME} user")


dirs = PlatformDirs(appname=APP_NAME, appauthor=AUTHOR, ensure_exists=True)


# ---- app deps ----
APP_DIR = os.path.abspath(os.path.dirname(__file__))
CONFIGS_DIR = os.path.join(APP_DIR, "configs")
ASSETS_DIR = os.path.join(APP_DIR, "assets")

# ----- user configs and data -----
APP_DATA_DIR = dirs.user_config_dir
if not APP_DATA_DIR:
    APP_DATA_DIR = dirs.user_data_dir

USER_DATA_PATH = os.path.join(APP_DATA_DIR, "user_data.json")
USER_CONFIG_PATH = os.path.join(APP_DATA_DIR, "config.ini")


# video dir
USER_DOWNLOADS_DIR = dirs.user_downloads_dir


def FastAnime(gui=False):
    if "--update" in sys.argv:
        from .Utility.app_updater import update_app

        update_app()
        sys.argv.remove("--update")
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
