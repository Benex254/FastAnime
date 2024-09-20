import os
import sys
from pathlib import Path
from platform import system

import click

from . import APP_NAME, __version__

PLATFORM = system()

# ---- app deps ----
APP_DIR = os.path.abspath(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(APP_DIR, "assets")


# --- icon stuff ---
if PLATFORM == "Windows":
    ICON_PATH = os.path.join(ASSETS_DIR, "logo.ico")
else:
    ICON_PATH = os.path.join(ASSETS_DIR, "logo.png")
# PREVIEW_IMAGE = os.path.join(ASSETS_DIR, "preview")


# ----- user configs and data -----

S_PLATFORM = sys.platform
APP_DATA_DIR = click.get_app_dir(APP_NAME, roaming=False)
if S_PLATFORM == "win32":
    # app data
    # app_data_dir_base = os.getenv("LOCALAPPDATA")
    # if not app_data_dir_base:
    #     raise RuntimeError("Could not determine app data dir please report to devs")
    # APP_DATA_DIR = os.path.join(app_data_dir_base, AUTHOR, APP_NAME)
    #
    # cache dir
    APP_CACHE_DIR = os.path.join(APP_DATA_DIR, "cache")

    # videos dir
    video_dir_base = os.path.join(Path().home(), "Videos")
    USER_VIDEOS_DIR = os.path.join(video_dir_base, APP_NAME)

elif S_PLATFORM == "darwin":
    # app data
    # app_data_dir_base = os.path.expanduser("~/Library/Application Support")
    # APP_DATA_DIR = os.path.join(app_data_dir_base, APP_NAME, __version__)
    #
    # cache dir
    cache_dir_base = os.path.expanduser("~/Library/Caches")
    APP_CACHE_DIR = os.path.join(cache_dir_base, APP_NAME, __version__)

    # videos dir
    video_dir_base = os.path.expanduser("~/Movies")
    USER_VIDEOS_DIR = os.path.join(video_dir_base, APP_NAME)
else:
    # # app data
    # app_data_dir_base = os.environ.get("XDG_CONFIG_HOME", "")
    # if not app_data_dir_base.strip():
    #     app_data_dir_base = os.path.expanduser("~/.config")
    # APP_DATA_DIR = os.path.join(app_data_dir_base, APP_NAME)
    #
    # cache dir
    cache_dir_base = os.environ.get("XDG_CACHE_HOME", "")
    if not cache_dir_base.strip():
        cache_dir_base = os.path.expanduser("~/.cache")
    APP_CACHE_DIR = os.path.join(cache_dir_base, APP_NAME)

    # videos dir
    video_dir_base = os.environ.get("XDG_VIDEOS_DIR", "")
    if not video_dir_base.strip():
        video_dir_base = os.path.expanduser("~/Videos")
    USER_VIDEOS_DIR = os.path.join(video_dir_base, APP_NAME)

# ensure paths exist
Path(APP_DATA_DIR).mkdir(parents=True, exist_ok=True)
Path(APP_CACHE_DIR).mkdir(parents=True, exist_ok=True)
Path(USER_VIDEOS_DIR).mkdir(parents=True, exist_ok=True)

# useful paths
USER_DATA_PATH = os.path.join(APP_DATA_DIR, "user_data.json")
USER_WATCH_HISTORY_PATH = os.path.join(APP_DATA_DIR, "watch_history.json")
USER_CONFIG_PATH = os.path.join(APP_DATA_DIR, "config.ini")
LOG_FILE_PATH = os.path.join(APP_DATA_DIR, "fastanime.log")


USER_NAME = os.environ.get("USERNAME", "Anime fun")
