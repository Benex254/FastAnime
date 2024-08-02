import os
from platform import system

from platformdirs import PlatformDirs

from . import APP_NAME, AUTHOR

PLATFORM = system()
dirs = PlatformDirs(appname=APP_NAME, appauthor=AUTHOR, ensure_exists=True)


# ---- app deps ----
APP_DIR = os.path.abspath(os.path.dirname(__file__))
CONFIGS_DIR = os.path.join(APP_DIR, "configs")
ASSETS_DIR = os.path.join(APP_DIR, "assets")

# --- notification bell ---
NOTIFICATION_BELL = os.path.join(ASSETS_DIR, "tut_turu.mp3")

# --- icon stuff ---
if PLATFORM == "Windows":
    ICON_PATH = os.path.join(ASSETS_DIR, "logo.ico")
else:
    ICON_PATH = os.path.join(ASSETS_DIR, "logo.png")

# ----- user configs and data -----
APP_DATA_DIR = dirs.user_config_dir
if not APP_DATA_DIR:
    APP_DATA_DIR = dirs.user_data_dir

USER_DATA_PATH = os.path.join(APP_DATA_DIR, "user_data.json")
USER_CONFIG_PATH = os.path.join(APP_DATA_DIR, "config.ini")
NOTIFIER_LOG_FILE_PATH = os.path.join(APP_DATA_DIR, "notifier.log")

# cache dir
APP_CACHE_DIR = dirs.user_cache_dir

# video dir
USER_VIDEOS_DIR = os.path.join(dirs.user_videos_dir, APP_NAME)


USER_NAME = os.environ.get("USERNAME", "Anime fun")
