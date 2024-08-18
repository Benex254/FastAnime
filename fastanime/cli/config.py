import json
import logging
import os
from configparser import ConfigParser
from typing import TYPE_CHECKING

from rich import print

from ..constants import USER_CONFIG_PATH, USER_DATA_PATH, USER_VIDEOS_DIR
from ..libs.rofi import Rofi

logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from ..AnimeProvider import AnimeProvider


class Config(object):
    """class that handles and manages configuration and user data throughout the clis lifespan

    Attributes:
        anime_list: [TODO:attribute]
        watch_history: [TODO:attribute]
        fastanime_anilist_app_login_url: [TODO:attribute]
        anime_provider: [TODO:attribute]
        user_data: [TODO:attribute]
        configparser: [TODO:attribute]
        downloads_dir: [TODO:attribute]
        provider: [TODO:attribute]
        use_fzf: [TODO:attribute]
        use_rofi: [TODO:attribute]
        skip: [TODO:attribute]
        icons: [TODO:attribute]
        preview: [TODO:attribute]
        translation_type: [TODO:attribute]
        sort_by: [TODO:attribute]
        continue_from_history: [TODO:attribute]
        auto_next: [TODO:attribute]
        auto_select: [TODO:attribute]
        use_mpv_mod: [TODO:attribute]
        quality: [TODO:attribute]
        notification_duration: [TODO:attribute]
        error: [TODO:attribute]
        server: [TODO:attribute]
        format: [TODO:attribute]
        force_window: [TODO:attribute]
        preferred_language: [TODO:attribute]
        rofi_theme: [TODO:attribute]
        rofi_theme: [TODO:attribute]
        rofi_theme_input: [TODO:attribute]
        rofi_theme_input: [TODO:attribute]
        rofi_theme_confirm: [TODO:attribute]
        rofi_theme_confirm: [TODO:attribute]
        watch_history: [TODO:attribute]
        anime_list: [TODO:attribute]
        user: [TODO:attribute]
    """

    sync_play = False
    anime_list: list
    watch_history: dict
    fastanime_anilist_app_login_url = (
        "https://anilist.co/api/v2/oauth/authorize?client_id=20148&response_type=token"
    )
    anime_provider: "AnimeProvider"
    user_data = {"watch_history": {}, "animelist": [], "user": {}}

    def __init__(self) -> None:
        self.initialize_user_data()
        self.load_config()

    def load_config(self):
        self.configparser = ConfigParser(
            {
                "quality": "1080",
                "auto_next": "False",
                "auto_select": "True",
                "sort_by": "search match",
                "downloads_dir": USER_VIDEOS_DIR,
                "translation_type": "sub",
                "server": "top",
                "continue_from_history": "True",
                "preferred_history": "local",
                "use_mpv_mod": "false",
                "force_window": "immediate",
                "preferred_language": "english",
                "use_fzf": "False",
                "preview": "False",
                "format": "best[height<=1080]/bestvideo[height<=1080]+bestaudio/best",
                "provider": "allanime",
                "error": "3",
                "icons": "false",
                "notification_duration": "2",
                "skip": "false",
                "use_rofi": "false",
                "rofi_theme": "",
                "rofi_theme_input": "",
                "rofi_theme_confirm": "",
                "ffmpegthumnailer_seek_time": "-1",
                "sub_lang": "eng",
            }
        )
        self.configparser.add_section("stream")
        self.configparser.add_section("general")
        self.configparser.add_section("anilist")
        if not os.path.exists(USER_CONFIG_PATH):
            with open(USER_CONFIG_PATH, "w") as config:
                self.configparser.write(config)

        self.configparser.read(USER_CONFIG_PATH)

        # --- set config values from file or using defaults ---
        self.downloads_dir = self.get_downloads_dir()
        self.sub_lang = self.get_sub_lang()
        self.provider = self.get_provider()
        self.use_fzf = self.get_use_fzf()
        self.use_rofi = self.get_use_rofi()
        self.skip = self.get_skip()
        self.icons = self.get_icons()
        self.preview = self.get_preview()
        self.translation_type = self.get_translation_type()
        self.sort_by = self.get_sort_by()
        self.continue_from_history = self.get_continue_from_history()
        self.auto_next = self.get_auto_next()
        self.auto_select = self.get_auto_select()
        self.use_mpv_mod = self.get_use_mpv_mod()
        self.quality = self.get_quality()
        self.notification_duration = self.get_notification_duration()
        self.error = self.get_error()
        self.server = self.get_server()
        self.format = self.get_format()
        self.force_window = self.get_force_window()
        self.preferred_language = self.get_preferred_language()
        self.preferred_history = self.get_preferred_history()
        self.rofi_theme = self.get_rofi_theme()
        Rofi.rofi_theme = self.rofi_theme
        self.rofi_theme_input = self.get_rofi_theme_input()
        Rofi.rofi_theme_input = self.rofi_theme_input
        self.rofi_theme_confirm = self.get_rofi_theme_confirm()
        Rofi.rofi_theme_confirm = self.rofi_theme_confirm
        self.ffmpegthumbnailer_seek_time = self.get_ffmpegthumnailer_seek_time()
        # ---- setup user data ------
        self.watch_history: dict = self.user_data.get("watch_history", {})
        self.anime_list: list = self.user_data.get("animelist", [])
        self.user: dict = self.user_data.get("user", {})

    def update_user(self, user):
        self.user = user
        self.user_data["user"] = user
        self._update_user_data()

    def update_watch_history(
        self, anime_id: int, episode: str, start_time="0", total_time="0"
    ):
        self.watch_history.update(
            {
                str(anime_id): {
                    "episode": episode,
                    "start_time": start_time,
                    "total_time": total_time,
                }
            }
        )
        self.user_data["watch_history"] = self.watch_history
        self._update_user_data()

    def initialize_user_data(self):
        try:
            if os.path.isfile(USER_DATA_PATH):
                with open(USER_DATA_PATH, "r") as f:
                    user_data = json.load(f)
                    self.user_data.update(user_data)
        except Exception as e:
            logger.error(e)

    def _update_user_data(self):
        """method that updates the actual user data file"""
        with open(USER_DATA_PATH, "w") as f:
            json.dump(self.user_data, f)

    # getters for user configuration

    # --- general section ---
    def get_provider(self):
        return self.configparser.get("general", "provider")

    def get_ffmpegthumnailer_seek_time(self):
        return self.configparser.getint("general", "ffmpegthumnailer_seek_time")

    def get_preferred_language(self):
        return self.configparser.get("general", "preferred_language")

    def get_sub_lang(self):
        return self.configparser.get("general", "sub_lang")

    def get_downloads_dir(self):
        return self.configparser.get("general", "downloads_dir")

    def get_icons(self):
        return self.configparser.getboolean("general", "icons")

    def get_preview(self):
        return self.configparser.getboolean("general", "preview")

    def get_use_fzf(self):
        return self.configparser.getboolean("general", "use_fzf")

    # rofi conifiguration
    def get_use_rofi(self):
        return self.configparser.getboolean("general", "use_rofi")

    def get_rofi_theme(self):
        return self.configparser.get("general", "rofi_theme")

    def get_rofi_theme_input(self):
        return self.configparser.get("general", "rofi_theme_input")

    def get_rofi_theme_confirm(self):
        return self.configparser.get("general", "rofi_theme_confirm")

    # --- stream section ---
    def get_skip(self):
        return self.configparser.getboolean("stream", "skip")

    def get_auto_next(self):
        return self.configparser.getboolean("stream", "auto_next")

    def get_auto_select(self):
        return self.configparser.getboolean("stream", "auto_select")

    def get_continue_from_history(self):
        return self.configparser.getboolean("stream", "continue_from_history")

    def get_use_mpv_mod(self):
        return self.configparser.getboolean("stream", "use_mpv_mod")

    def get_notification_duration(self):
        return self.configparser.getint("general", "notification_duration")

    def get_error(self):
        return self.configparser.getint("stream", "error")

    def get_force_window(self):
        return self.configparser.get("stream", "force_window")

    def get_translation_type(self):
        return self.configparser.get("stream", "translation_type")

    def get_preferred_history(self):
        return self.configparser.get("stream", "preferred_history")

    def get_quality(self):
        return self.configparser.get("stream", "quality")

    def get_server(self):
        return self.configparser.get("stream", "server")

    def get_format(self):
        return self.configparser.get("stream", "format")

    def get_sort_by(self):
        return self.configparser.get("anilist", "sort_by")

    def update_config(self, section: str, key: str, value: str):
        self.configparser.set(section, key, value)
        with open(USER_CONFIG_PATH, "w") as config:
            self.configparser.write(config)

    def __repr__(self):
        current_config_state = f"""
[stream]
# Auto continue from watch history
continue_from_history = {self.continue_from_history}  

# which hostory to use [local/remote]
preferred_history = {self.preferred_history}


# Preferred language for anime (options: dub, sub)
translation_type = {self.translation_type}

# Default server (options: dropbox, sharepoint, wetransfer.gogoanime, top, wixmp)
server = {self.server}

# Auto-select next episode
auto_next = {self.auto_next}

# Auto select the anime provider results with fuzzy find.
# Note this wont always be correct.But 99% of the time will be.
auto_select = {self.auto_select}

# whether to skip the opening and ending theme songs
# NOTE: requires ani-skip to be in path
skip = {self.skip}

# the maximum delta time in minutes after which the episode should be considered as completed
# used in the continue from time stamp
error = {self.error}

# whether to use python-mpv
# to enable superior control over the player 
# adding more options to it
use_mpv_mod = {self.use_mpv_mod}

# force mpv window
# passed directly to mpv so values are same
force_window = immediate

# the format of downloaded anime and trailer
# based on yt-dlp format and passed directly to it
# learn more by looking it up on their site
# only works for downloaded anime if server=gogoanime
# since its the only one that offers different formats
# the others tend not to
format = {self.format}

[general]

# can be [allanime,animepahe]
provider = {self.provider}

# Display language (options: english, romaji)
preferred_language = {self.preferred_language}

# Download directory
downloads_dir = {self.downloads_dir}

# whether to show a preview window when using fzf or rofi
preview = {self.preview} 

# the time to seek when using ffmpegthumbnailer [-1 to 100]
# -1 means random and is the default
ffmpegthumbnailer_seek_time = {self.ffmpegthumbnailer_seek_time}

# whether to use fzf as the interface for the anilist command and others.
use_fzf = {self.use_fzf} 

# whether to use rofi for the ui
use_rofi = {self.use_rofi}

# rofi theme to use
rofi_theme = {self.rofi_theme}

rofi_theme_input = {self.rofi_theme_input}

rofi_theme_confirm = {self.rofi_theme_confirm}


# whether to show the icons
icons = {self.icons}

# the duration in minutes a notification will stay in the screen
# used by notifier command
notification_duration = {self.notification_duration}
        """
        return current_config_state

    def __str__(self):
        return self.__repr__()

    # WARNING: depracated and will probably be removed
    def update_anime_list(self, anime_id: int, remove=False):
        if remove:
            try:
                self.anime_list.remove(anime_id)
                print("Succesfully removed :cry:")
            except Exception:
                print(anime_id, "Nothing to remove :confused:")
        else:
            self.anime_list.append(anime_id)
            self.user_data["animelist"] = list(set(self.anime_list))
            self._update_user_data()
            print("Succesfully added :smile:")
            input("Enter to continue...")
