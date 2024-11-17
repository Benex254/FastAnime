import json
import logging
import os
from configparser import ConfigParser
from typing import TYPE_CHECKING

from ..constants import (
    USER_CONFIG_PATH,
    USER_DATA_PATH,
    USER_VIDEOS_DIR,
    ASSETS_DIR,
    USER_WATCH_HISTORY_PATH,
    S_PLATFORM,
)
from ..libs.rofi import Rofi

logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from ..AnimeProvider import AnimeProvider


class Config(object):
    manga = False
    sync_play = False
    anime_list: list
    watch_history: dict = {}
    fastanime_anilist_app_login_url = (
        "https://anilist.co/api/v2/oauth/authorize?client_id=20148&response_type=token"
    )
    anime_provider: "AnimeProvider"
    user_data = {"recent_anime": [], "animelist": [], "user": {}}
    default_config = {
        "auto_next": "False",
        "auto_select": "True",
        "cache_requests": "true",
        "check_for_updates": "True",
        "continue_from_history": "True",
        "default_media_list_tracking": "None",
        "downloads_dir": USER_VIDEOS_DIR,
        "disable_mpv_popen": "True",
        "episode_complete_at": "80",
        "ffmpegthumbnailer_seek_time": "-1",
        "force_forward_tracking": "true",
        "force_window": "immediate",
        "format": "best[height<=1080]/bestvideo[height<=1080]+bestaudio/best",
        "icons": "false",
        "image_previews": "True" if S_PLATFORM != "win32" else "False",
        "normalize_titles": "True",
        "notification_duration": "2",
        "player": "mpv",
        "preferred_history": "local",
        "preferred_language": "english",
        "preview": "False",
        "provider": "allanime",
        "quality": "1080",
        "recent": "50",
        "rofi_theme": os.path.join(ASSETS_DIR, "rofi_theme.rasi"),
        "rofi_theme_preview": os.path.join(ASSETS_DIR, "rofi_theme_preview.rasi"),
        "rofi_theme_confirm": os.path.join(ASSETS_DIR, "rofi_theme_confirm.rasi"),
        "rofi_theme_input": os.path.join(ASSETS_DIR, "rofi_theme_input.rasi"),
        "server": "top",
        "skip": "false",
        "sort_by": "search match",
        "sub_lang": "eng",
        "translation_type": "sub",
        "use_fzf": "False",
        "use_persistent_provider_store": "false",
        "use_python_mpv": "false",
        "use_rofi": "false",
    }

    def __init__(self) -> None:
        self.initialize_user_data_and_watch_history_recent_anime()
        self.load_config()

    def load_config(self):
        self.configparser = ConfigParser(self.default_config)
        self.configparser.add_section("stream")
        self.configparser.add_section("general")
        self.configparser.add_section("anilist")

        # --- set config values from file or using defaults ---
        if os.path.exists(USER_CONFIG_PATH):
            self.configparser.read(USER_CONFIG_PATH, encoding="utf-8")

        # TODO: rewrite all this removing the useless functions
        # hate technical debt
        # why did i do this lol
        self.auto_next = self.get_auto_next()
        self.auto_select = self.get_auto_select()
        self.cache_requests = self.get_cache_requests()
        self.check_for_updates = self.configparser.get("general", "check_for_updates")
        self.continue_from_history = self.get_continue_from_history()
        self.default_media_list_tracking = self.get_default_media_list_tracking()
        self.disable_mpv_popen = self.configparser.getboolean(
            "stream", "disable_mpv_popen"
        )
        self.downloads_dir = self.get_downloads_dir()
        self.episode_complete_at = self.get_episode_complete_at()
        self.ffmpegthumbnailer_seek_time = self.get_ffmpegthumnailer_seek_time()
        self.force_forward_tracking = self.get_force_forward_tracking()
        self.force_window = self.get_force_window()
        self.format = self.get_format()
        self.icons = self.get_icons()
        self.image_previews = self.get_image_previews()
        self.normalize_titles = self.get_normalize_titles()
        self.notification_duration = self.get_notification_duration()
        self.player = self.get_player()
        self.preferred_history = self.get_preferred_history()
        self.preferred_language = self.get_preferred_language()
        self.preview = self.get_preview()
        self.provider = self.get_provider()
        self.quality = self.get_quality()

        self.recent = self.get_recent()
        self.rofi_theme_confirm = self.get_rofi_theme_confirm()
        self.rofi_theme_input = self.get_rofi_theme_input()
        self.rofi_theme = self.get_rofi_theme()
        self.rofi_theme_preview = self.get_rofi_theme_preview()

        Rofi.rofi_theme_confirm = self.rofi_theme_confirm
        Rofi.rofi_theme_input = self.rofi_theme_input
        Rofi.rofi_theme = self.rofi_theme
        Rofi.rofi_theme_preview = self.rofi_theme_preview

        self.server = self.get_server()
        self.skip = self.get_skip()
        self.sort_by = self.get_sort_by()
        self.sub_lang = self.get_sub_lang()
        self.translation_type = self.get_translation_type()
        self.use_fzf = self.get_use_fzf()
        self.use_python_mpv = self.get_use_mpv_mod()
        self.use_rofi = self.get_use_rofi()
        self.use_persistent_provider_store = self.get_use_persistent_provider_store()

        # ---- setup user data ------
        self.anime_list: list = self.user_data.get("animelist", [])
        self.user: dict = self.user_data.get("user", {})

        if not os.path.exists(USER_CONFIG_PATH):
            with open(USER_CONFIG_PATH, "w", encoding="utf-8") as config:
                config.write(self.__repr__())

    def set_fastanime_config_environs(self):
        current_config = []
        for key in self.default_config:
            current_config.append((f"FASTANIME_{key.upper()}", str(getattr(self, key))))
        os.environ.update(current_config)

    def update_user(self, user):
        self.user = user
        self.user_data["user"] = user
        self._update_user_data()

    def update_recent(self, recent_anime: list):
        recent_anime_ids = []
        _recent_anime = []
        for anime in recent_anime:
            if (
                anime["id"] not in recent_anime_ids
                and len(recent_anime_ids) <= self.recent
            ):
                _recent_anime.append(anime)
                recent_anime_ids.append(anime["id"])

        self.user_data["recent_anime"] = _recent_anime
        self._update_user_data()

    def media_list_track(
        self,
        anime_id: int,
        episode_no: str,
        episode_stopped_at="0",
        episode_total_length="0",
        progress_tracking="prompt",
    ):
        self.watch_history.update(
            {
                str(anime_id): {
                    "episode_no": episode_no,
                    "episode_stopped_at": episode_stopped_at,
                    "episode_total_length": episode_total_length,
                    "progress_tracking": progress_tracking,
                }
            }
        )
        with open(USER_WATCH_HISTORY_PATH, "w") as f:
            json.dump(self.watch_history, f)

    def initialize_user_data_and_watch_history_recent_anime(self):
        try:
            if os.path.isfile(USER_DATA_PATH):
                with open(USER_DATA_PATH, "r") as f:
                    user_data = json.load(f)
                    self.user_data.update(user_data)
        except Exception as e:
            logger.error(e)
        try:
            if os.path.isfile(USER_WATCH_HISTORY_PATH):
                with open(USER_WATCH_HISTORY_PATH, "r") as f:
                    watch_history = json.load(f)
                    self.watch_history.update(watch_history)
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
        return self.configparser.getint("general", "ffmpegthumbnailer_seek_time")

    def get_preferred_language(self):
        return self.configparser.get("general", "preferred_language")

    def get_sub_lang(self):
        return self.configparser.get("general", "sub_lang")

    def get_downloads_dir(self):
        return self.configparser.get("general", "downloads_dir")

    def get_icons(self):
        return self.configparser.getboolean("general", "icons")

    def get_image_previews(self):
        return self.configparser.getboolean("general", "image_previews")

    def get_preview(self):
        return self.configparser.getboolean("general", "preview")

    def get_use_fzf(self):
        return self.configparser.getboolean("general", "use_fzf")

    def get_use_persistent_provider_store(self):
        return self.configparser.getboolean("general", "use_persistent_provider_store")

    # rofi conifiguration
    def get_use_rofi(self):
        return self.configparser.getboolean("general", "use_rofi")

    def get_rofi_theme(self):
        return self.configparser.get("general", "rofi_theme")

    def get_rofi_theme_preview(self):
        return self.configparser.get("general", "rofi_theme_preview")

    def get_rofi_theme_input(self):
        return self.configparser.get("general", "rofi_theme_input")

    def get_rofi_theme_confirm(self):
        return self.configparser.get("general", "rofi_theme_confirm")

    def get_force_forward_tracking(self):
        return self.configparser.getboolean("general", "force_forward_tracking")

    def get_cache_requests(self):
        return self.configparser.getboolean("general", "cache_requests")

    def get_default_media_list_tracking(self):
        return self.configparser.get("general", "default_media_list_tracking")

    def get_normalize_titles(self):
        return self.configparser.getboolean("general", "normalize_titles")

    def get_recent(self):
        return self.configparser.getint("general", "recent")

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
        return self.configparser.getboolean("stream", "use_python_mpv")

    def get_notification_duration(self):
        return self.configparser.getint("general", "notification_duration")

    def get_episode_complete_at(self):
        return self.configparser.getint("stream", "episode_complete_at")

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

    def get_player(self):
        return self.configparser.get("stream", "player")

    def get_sort_by(self):
        return self.configparser.get("anilist", "sort_by")

    def update_config(self, section: str, key: str, value: str):
        self.configparser.set(section, key, value)
        with open(USER_CONFIG_PATH, "w") as config:
            self.configparser.write(config)

    def __repr__(self):
        current_config_state = f"""\
#
#    ███████╗░█████╗░░██████╗████████╗░█████╗░███╗░░██╗██╗███╗░░░███╗███████╗  ░█████╗░░█████╗░███╗░░██╗███████╗██╗░██████╗░
#    ██╔════╝██╔══██╗██╔════╝╚══██╔══╝██╔══██╗████╗░██║██║████╗░████║██╔════╝  ██╔══██╗██╔══██╗████╗░██║██╔════╝██║██╔════╝░
#    █████╗░░███████║╚█████╗░░░░██║░░░███████║██╔██╗██║██║██╔████╔██║█████╗░░  ██║░░╚═╝██║░░██║██╔██╗██║█████╗░░██║██║░░██╗░
#    ██╔══╝░░██╔══██║░╚═══██╗░░░██║░░░██╔══██║██║╚████║██║██║╚██╔╝██║██╔══╝░░  ██║░░██╗██║░░██║██║╚████║██╔══╝░░██║██║░░╚██╗
#    ██║░░░░░██║░░██║██████╔╝░░░██║░░░██║░░██║██║░╚███║██║██║░╚═╝░██║███████╗  ╚█████╔╝╚█████╔╝██║░╚███║██║░░░░░██║╚██████╔╝
#    ╚═╝░░░░░╚═╝░░╚═╝╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚══╝╚═╝╚═╝░░░░░╚═╝╚══════╝  ░╚════╝░░╚════╝░╚═╝░░╚══╝╚═╝░░░░░╚═╝░╚═════╝░
#
[general]
# whether to show the icons in the tui [True/False]
# more like emojis
# by the way if you have any recommendations to which should be used where please
# don't hesitate to share your opinion
# cause it's a lot of work to look for the right one for each menu option
# be sure to also give the replacement emoji
icons = {self.icons}

# whether to normalize provider titles [True/False]
# basically takes the provider titles and finds the corresponding anilist title then changes the title to that
# useful for uniformity especially when downloading from different providers
# this also applies to episode titles
normalize_titles = {self.normalize_titles}

# whether to check for updates every time you run the script [True/False]
# this is useful for keeping your script up to date
# cause there are always new features being added 😄
check_for_updates = {self.check_for_updates}

# can be [allanime, animepahe, hianime]
# allanime is the most realible
# animepahe provides different links to streams of different quality so a quality can be selected reliably with --quality option
# hianime which is now hianime usually provides subs in different languuages and its servers are generally faster
provider = {self.provider}

# Display language [english, romaji]
# this is passed to anilist directly and is used to set the language which the anime titles will be in
# when using the anilist interface
preferred_language = {self.preferred_language}

# Download directory
# where you will find your videos after downloading them with 'fastanime download' command
downloads_dir = {self.downloads_dir}

# whether to show a preview window when using fzf or rofi [True/False]
# the preview requires you have a commandline image viewer as documented in the README
# this is only when usinf fzf
# if you dont care about image previews it doesnt matter
# though its awesome
# try it and you will see
preview = {self.preview} 

# whether to show images in the preview [true/false]
image_previews = {self.image_previews}

# the time to seek when using ffmpegthumbnailer [-1 to 100]
# -1 means random and is the default
# ffmpegthumbnailer is used to generate previews and you can select at what time in the video to extract an image
# random makes things quite exciting cause you never no at what time it will extract the image from
ffmpegthumbnailer_seek_time = {self.ffmpegthumbnailer_seek_time}

# whether to use fzf as the interface for the anilist command and others. [True/False]
use_fzf = {self.use_fzf} 

# whether to use rofi for the ui [True/False]
# it's more useful if you want to create a desktop entry 
# which can be setup with 'fastanime config --desktop-entry'
# though if you want it to be your sole interface even when fastanime is run directly from the terminal
use_rofi = {self.use_rofi}

# rofi themes to use 
# the values of this option is the path to the rofi config files to use
# i choose to split it into three since it gives the best look and feel
# you can refer to the rofi demo on github to see for your self
# by the way i recommend getting the rofi themes from this project;  
rofi_theme = {self.rofi_theme}

rofi_theme_preview = {self.rofi_theme_preview}

rofi_theme_input = {self.rofi_theme_input}

rofi_theme_confirm = {self.rofi_theme_confirm}

# the duration in minutes a notification will stay in the screen
# used by notifier command
notification_duration = {self.notification_duration}

# used when the provider gives subs of different languages
# currently its the case for:
# hianime
# the values for this option are the short names for countries
# regex is used to determine what you selected
sub_lang = {self.sub_lang}

# what is your default media list tracking [track/disabled/prompt]
# only affects your anilist anime list
# track - means your progress will always be reflected in your anilist anime list
# disabled - means progress tracking will no longer be reflected in your anime list
# prompt - means for every anime you will be prompted whether you want your progress to be tracked or not
default_media_list_tracking = {self.default_media_list_tracking}

# whether media list tracking should only be updated when the next episode is greater than the previous
# this affects only your anilist anime list
force_forward_tracking = {self.force_forward_tracking}

# whether to cache requests [true/false]
# this makes the experience better and more faster
# as data need not always be fetched from web server
# and instead can be gotten  locally
# from the cached_requests_db
cache_requests = {self.cache_requests}

# whether to use a persistent store (basically a sqlitedb) for storing some data the provider requires
# to enable a seamless experience [true/false]
# this option exists primarily because i think it may help in the optimization
# of fastanime as a library in a website project
# for now i don't recommend changing it
# leave it as is
use_persistent_provider_store = {self.use_persistent_provider_store}

# no of recent anime to keep [0-50]
# 0 will disable recent anime tracking
recent = {self.recent}


[stream]
# the quality of the stream [1080,720,480,360]
# this option is usually only reliable when:
# provider=animepahe
# since it provides links that actually point to streams of different qualities
# while the rest just point to another link that can provide the anime from the same server
quality = {self.quality}

# Auto continue from watch history [True/False]
# this will make fastanime to choose the episode that you last watched to completion
# and increment it by one
# and use that to auto select the episode you want to watch
continue_from_history = {self.continue_from_history}  

# which history to use [local/remote]
# local history means it will just use the watch history stored locally in your device 
# the file that stores it is called watch_history.json and is stored next to your config file
# remote means it ignores the last episode stored locally and instead uses the one in your anilist anime list
# this config option is useful if you want to overwrite your local history or import history covered from another device or platform
# since remote history will take precendence over whats available locally
preferred_history = {self.preferred_history}

# Preferred language for anime [dub/sub]
translation_type = {self.translation_type}

# what server to use for a particular provider
# allanime: [dropbox, sharepoint, wetransfer, gogoanime, wixmp]
# animepahe: [kwik]
# hianime: [HD1, HD2, StreamSB, StreamTape]
# 'top' can also be used as a value for this option
# 'top' will cause fastanime to auto select the first server it sees
# this saves on resources and is faster since not all servers are being fetched
server = {self.server}

# Auto select next episode [True/False]
# this makes fastanime increment the current episode number 
# then after using that value to fetch the next episode instead of prompting
# this option is useful for binging
auto_next = {self.auto_next}

# Auto select the anime provider results with fuzzy find. [True/False]
# Note this won't always be correct
# this is because the providers sometime use non-standard names
# that are there own preference rather than the official names
# But 99% of the time will be accurate
# if this happens just turn of auto_select in the menus or from the commandline and manually select the correct anime title
# and then please open an issue at <> highlighting the normalized title and the title given by the provider for the anime you wished to watch  
# or even better edit this file <> and open a pull request
auto_select = {self.auto_select}

# whether to skip the opening and ending theme songs [True/False]
# NOTE: requires ani-skip to be in path
# for python-mpv users am planning to create this functionality n python without the use of an external script
# so its disabled for now
skip = {self.skip}

# at what percentage progress should the episode be considered as completed [0-100]
# this value is used to determine whether to increment the current episode number and save it to your local list
# so you can continue immediately to the next episode without select it the next time you decide to watch the anime
# it is also used to determine whether your anilist anime list should be updated or not
episode_complete_at = {self.episode_complete_at}

# whether to use python-mpv [True/False]
# to enable superior control over the player 
# adding more options to it
# Enable this one and you will be wonder why you did not discover fastanime sooner 
# Since you basically don't have to close the player window 
# to go to the next or previous episode, switch servers, 
# change translation type or change to a given episode x
# so try it if you haven't already
# if you have any issues setting it up 
# don't be afraid to ask
# especially on windows
# honestly it can be a pain to set it up there
# personally it took me quite sometime to figure it out
# this is because of how windows handles shared libraries
# so just ask when you find yourself stuck
# or just switch to arch linux
use_python_mpv = {self.use_python_mpv}


# whether to use popen to get the timestamps for continue_from_history
# implemented because popen does not work for some reason in nixos
# if you are on nixos and you have a solution to this problem please share
# i will be glad to hear it 😄
# So for now ignore this option
# and anyways the new method of getting timestamps is better
disable_mpv_popen = {self.disable_mpv_popen}

# force mpv window
# the default 'immediate' just makes mpv to open the window even if the video has not yet loaded
# done for asthetics
# passed directly to mpv so values are same
force_window = immediate

# the format of downloaded anime and trailer
# based on yt-dlp format and passed directly to it
# learn more by looking it up on their site
# only works for downloaded anime if: 
# provider=allanime, server=gogoanime
# provider=allanime, server=wixmp
# provider=hianime
# this is because they provider a m3u8 file that contans multiple quality streams
format = {self.format}

# set the player to use for streaming [mpv/vlc]
# while this option exists i will still recommend that you use mpv
# since you will miss out on some features if you use the others
player = {self.player}

# NOTE:
# if you have any trouble setting up your config
# please don't be afraid to ask in our discord
# plus if there are any errors, improvements or suggestions please tell us in the discord
# or help us by contributing
# we appreciate all the help we can get
# since we may not always have the time to immediately implement the changes
#
# HOPE YOU ENJOY FASTANIME AND BE SURE TO STAR THE PROJECT ON GITHUB
#
"""
        return current_config_state

    def __str__(self):
        return self.__repr__()
