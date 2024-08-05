import logging
import os
import sys
from platform import platform

from dotenv import load_dotenv
from platformdirs import PlatformDirs

load_dotenv()

if os.environ.get("FA_RICH_TRACEBACK", False):
    from rich.traceback import install

    install(show_locals=True)


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

# cache dir
APP_CACHE_DIR = dirs.user_cache_dir

# video dir
USER_VIDEOS_DIR = os.path.join(dirs.user_videos_dir, APP_NAME)

# web dirs

WEB_DIR = os.path.join(APP_DIR, "web")
FRONTEND_DIR = os.path.join(WEB_DIR, "frontend")
BACKEND_DIR = os.path.join(WEB_DIR, "backend")


def FastAnime():
    if "--update" in sys.argv:
        from .Utility.app_updater import update_app

        update_app()
        sys.argv.remove("--update")
    if "--log" in sys.argv:
        # Configure logging
        from rich.logging import RichHandler

        logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.DEBUG,  # Set the logging level to DEBUG
            format="%(message)s",  # Use a simple message format
            datefmt="[%X]",  # Use a custom date format
            handlers=[RichHandler()],  # Use RichHandler to format the logs
        )
        sys.argv.remove("--log")

    from .cli import run_cli

    run_cli()
