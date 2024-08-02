import os
from configparser import ConfigParser

from rich import print

from ..AnimeProvider import AnimeProvider
from ..constants import USER_CONFIG_PATH, USER_VIDEOS_DIR
from ..libs.rofi import Rofi
from ..Utility.user_data_helper import user_data_helper


class Config(object):
    anime_list: list
    watch_history: dict
    fastanime_anilist_app_login_url = (
        "https://anilist.co/api/v2/oauth/authorize?client_id=20148&response_type=token"
    )

    def __init__(self) -> None:
        self.load_config()

    def load_config(self):
        self.configparser = ConfigParser(
            {
                "server": "top",
                "continue_from_history": "True",
                "quality": "0",
                "auto_next": "False",
                "auto_select": "True",
                "sort_by": "search match",
                "downloads_dir": USER_VIDEOS_DIR,
                "translation_type": "sub",
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
            }
        )
        self.configparser.add_section("stream")
        self.configparser.add_section("general")
        self.configparser.add_section("anilist")
        if not os.path.exists(USER_CONFIG_PATH):
            with open(USER_CONFIG_PATH, "w") as config:
                self.configparser.write(config)

        self.configparser.read(USER_CONFIG_PATH)

        # --- set defaults ---
        self.downloads_dir = self.get_downloads_dir()
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
        self.quality = self.get_quality()
        self.notification_duration = self.get_notification_duration()
        self.error = self.get_error()
        self.server = self.get_server()
        self.format = self.get_format()
        self.preferred_language = self.get_preferred_language()
        self.rofi_theme = self.get_rofi_theme()
        Rofi.rofi_theme = self.rofi_theme
        self.rofi_theme_input = self.get_rofi_theme_input()
        Rofi.rofi_theme_input = self.rofi_theme_input
        self.rofi_theme_confirm = self.get_rofi_theme_confirm()
        Rofi.rofi_theme_confirm = self.rofi_theme_confirm
        # ---- setup user data ------
        self.watch_history: dict = user_data_helper.user_data.get("watch_history", {})
        self.anime_list: list = user_data_helper.user_data.get("animelist", [])
        self.user: dict = user_data_helper.user_data.get("user", {})

        self.anime_provider = AnimeProvider(self.provider)

    def update_user(self, user):
        self.user = user
        user_data_helper.update_user_info(user)

    def update_watch_history(
        self, anime_id: int, episode: str | None, start_time="0", total_time="0"
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
        user_data_helper.update_watch_history(self.watch_history)

    def update_anime_list(self, anime_id: int, remove=False):
        if remove:
            try:
                self.anime_list.remove(anime_id)
                print("Succesfully removed :cry:")
            except Exception:
                print(anime_id, "Nothing to remove :confused:")
        else:
            self.anime_list.append(anime_id)
            user_data_helper.update_animelist(self.anime_list)
            print("Succesfully added :smile:")
        input("Enter to continue...")

    def get_provider(self):
        return self.configparser.get("general", "provider")

    def get_rofi_theme(self):
        return self.configparser.get("general", "rofi_theme")

    def get_rofi_theme_input(self):
        return self.configparser.get("general", "rofi_theme_input")

    def get_rofi_theme_confirm(self):
        return self.configparser.get("general", "rofi_theme_confirm")

    def get_downloads_dir(self):
        return self.configparser.get("general", "downloads_dir")

    def get_use_fzf(self):
        return self.configparser.getboolean("general", "use_fzf")

    def get_use_rofi(self):
        return self.configparser.getboolean("general", "use_rofi")

    def get_skip(self):
        return self.configparser.getboolean("stream", "skip")

    def get_icons(self):
        return self.configparser.getboolean("general", "icons")

    def get_preview(self):
        return self.configparser.getboolean("general", "preview")

    def get_preferred_language(self):
        return self.configparser.get("general", "preferred_language")

    def get_sort_by(self):
        return self.configparser.get("anilist", "sort_by")

    def get_continue_from_history(self):
        return self.configparser.getboolean("stream", "continue_from_history")

    def get_translation_type(self):
        return self.configparser.get("stream", "translation_type")

    def get_auto_next(self):
        return self.configparser.getboolean("stream", "auto_next")

    def get_auto_select(self):
        return self.configparser.getboolean("stream", "auto_select")

    def get_quality(self):
        return self.configparser.getint("stream", "quality")

    def get_notification_duration(self):
        return self.configparser.getint("general", "notification_duration")

    def get_error(self):
        return self.configparser.getint("stream", "error")

    def get_server(self):
        return self.configparser.get("stream", "server")

    def get_format(self):
        return self.configparser.get("stream", "format")

    def update_config(self, section: str, key: str, value: str):
        self.configparser.set(section, key, value)
        with open(USER_CONFIG_PATH, "w") as config:
            self.configparser.write(config)

    def __repr__(self):
        return f"Config(server:{self.get_server()},quality:{self.get_quality()},auto_next:{self.get_auto_next()},continue_from_history:{self.get_continue_from_history()},sort_by:{self.get_sort_by()},downloads_dir:{self.get_downloads_dir()})"

    def __str__(self):
        return self.__repr__()
