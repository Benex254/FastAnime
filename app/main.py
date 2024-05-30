import os

os.environ["KIVY_VIDEO"] = "ffpyplayer"

from queue import Queue
from threading import Thread
from subprocess import Popen
import webbrowser

import plyer

from kivy.config import Config

# Config.set('kivy', 'window_icon', "logo.ico")
# Config.write()

from kivy.loader import Loader

Loader.num_workers = 5
Loader.max_upload_per_frame = 10

from kivy.clock import Clock
from kivy.logger import Logger
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.uix.settings import SettingsWithSidebar, Settings

from kivymd.icon_definitions import md_icons
from kivymd.app import MDApp

from View.screens import screens
from libs.animdl import AnimdlApi
from Utility import (
    themes_available,
    show_notification,
    user_data_helper,
    animdl_config_manager,
)


# Ensure the user data fields exist
if not (user_data_helper.user_data.exists("user_anime_list")):
    user_data_helper.update_user_anime_list([])

if not (user_data_helper.yt_cache.exists("yt_stream_links")):
    user_data_helper.update_anime_trailer_cache([])

# TODO: Confirm data integrity from user_data and yt_cache


class AniXStreamApp(MDApp):
    queue = Queue()
    downloads_queue = Queue()
    animdl_streaming_subprocess: Popen | None = None

    def worker(self, queue: Queue):
        while True:
            task = queue.get()  # task should be a function
            try:
                task()
            except Exception as e:
                show_notification("An error occured while streaming", f"{e}")
            self.queue.task_done()

    def downloads_worker(self, queue: Queue):
        while True:
            download_task = queue.get()  # task should be a function
            try:
                download_task()
            except Exception as e:
                show_notification("An error occured while downloading", f"{e}")
            self.downloads_queue.task_done()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_all_kv_files(self.directory)
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Lightcoral"
        self.manager_screens = ScreenManager()
        self.manager_screens.transition = FadeTransition()

        # initialize worker
        self.worker_thread = Thread(target=self.worker, args=(self.queue,))
        self.worker_thread.daemon = True
        self.worker_thread.start()
        Logger.info("AniXStream:Successfully started background tasks worker")

        # initialize  downloads worker
        self.downloads_worker_thread = Thread(
            target=self.downloads_worker, args=(self.downloads_queue,)
        )
        self.downloads_worker_thread.daemon = True
        self.downloads_worker_thread.start()
        Logger.info("AniXStream:Successfully started download worker")

    def build(self) -> ScreenManager:
        self.settings_cls = SettingsWithSidebar

        self.generate_application_screens()

        if config := self.config:
            if theme_color := config.get("Preferences", "theme_color"):
                self.theme_cls.primary_palette = theme_color
            if theme_style := config.get("Preferences", "theme_style"):
                self.theme_cls.theme_style = theme_style

        self.anime_screen = self.manager_screens.get_screen("anime screen")
        self.search_screen = self.manager_screens.get_screen("search screen")
        self.download_screen = self.manager_screens.get_screen("downloads screen")
        return self.manager_screens

    def on_start(self, *args):
        pass

    def generate_application_screens(self) -> None:
        for i, name_screen in enumerate(screens.keys()):
            model = screens[name_screen]["model"]()
            controller = screens[name_screen]["controller"](model)
            view = controller.get_view()
            view.manager_screens = self.manager_screens
            view.name = name_screen
            self.manager_screens.add_widget(view)

    def build_config(self, config):

        # General settings setup
        if vid_path := plyer.storagepath.get_videos_dir():  # type: ignore
            downloads_dir = os.path.join(vid_path, "anixstream")
            if not os.path.exists(downloads_dir):
                os.mkdir(downloads_dir)
        else:
            downloads_dir = os.path.join(".", "videos")
            if not os.path.exists(downloads_dir):
                os.mkdir(downloads_dir)
        config.setdefaults(
            "Preferences",
            {
                "theme_color": "Cyan",
                "theme_style": "Dark",
                "downloads_dir": downloads_dir,
                "is_startup_anime_enable": False,
            },
        )

        # animdl config settings setup
        animdl_config = animdl_config_manager.get_animdl_config()
        config.setdefaults(
            "Providers",
            {
                "default_provider": animdl_config["default_provider"],
            },
        )
        config.setdefaults(
            "Quality",
            {
                "quality_string": animdl_config["quality_string"],
            },
        )
        config.setdefaults(
            "PlayerSelection",
            {
                "default_player": animdl_config["default_player"],
            },
        )

    def build_settings(self, settings: Settings):
        settings.add_json_panel(
            "Settings", self.config, "./general_settings_panel.json"
        )
        settings.add_json_panel(
            "Animdl Config", self.config, "./animdl_config_panel.json"
        )

    def on_config_change(self, config, section, key, value):
        # TODO: Change to match case
        if section == "Preferences":
            match key:
                case "theme_color":
                    if value in themes_available:
                        self.theme_cls.primary_palette = value
                    else:
                        Logger.warning(
                            "AniXStream Settings: An invalid theme has been entered and will be ignored"
                        )
                        config.set("Preferences", "theme_color", "Cyan")
                        config.write()
                case "theme_style":
                    self.theme_cls.theme_style = value
        elif section == "Providers":
            animdl_config_manager.update_animdl_config("default_provider", value)
        elif section == "Quality":
            animdl_config_manager.update_animdl_config("quality_string", value)
        elif section == "PlayerSelection":
            animdl_config_manager.update_animdl_config("default_player", value)

    def on_stop(self):
        del self.downloads_worker_thread
        if self.animdl_streaming_subprocess:
            self.stop_streaming = True
            self.animdl_streaming_subprocess.terminate()
            del self.worker_thread

            Logger.info("Animdl:Successfully terminated existing animdl subprocess")

    # custom methods
    def search_for_anime(self, search_field, **kwargs):
        if self.manager_screens.current != "search screen":
            self.manager_screens.current = "search screen"
        self.search_screen.handle_search_for_anime(search_field, **kwargs)

    def add_anime_to_user_anime_list(self, id: int):
        updated_list = user_data_helper.get_user_anime_list()
        updated_list.append(id)
        user_data_helper.update_user_anime_list(updated_list)

    def remove_anime_from_user_anime_list(self, id: int):
        updated_list = user_data_helper.get_user_anime_list()
        if updated_list.count(id):
            updated_list.remove(id)
        user_data_helper.update_user_anime_list(updated_list)

    def add_anime_to_user_downloads_list(self, id: int):
        updated_list = user_data_helper.get_user_downloads()
        updated_list.append(id)
        user_data_helper.get_user_downloads()

    def show_anime_screen(self, id: int, caller_screen_name: str):
        self.manager_screens.current = "anime screen"
        self.anime_screen.controller.update_anime_view(id, caller_screen_name)

    def download_anime_complete(
        self, successful_downloads: list, failed_downloads: list, anime_title: str
    ):
        show_notification(
            f"Finished Dowloading {anime_title}",
            f"There were {len(successful_downloads)} successful downloads and {len(failed_downloads)} failed downloads",
        )
        Logger.info(
            f"Downloader:Finished Downloading {anime_title} and there were {len(failed_downloads)} failed downloads"
        )

    def download_anime(self, anime_id: int, default_cmds: dict):
        show_notification(
            "New Download Task Queued",
            f"{default_cmds.get('title')} has been queued for downloading",
        )
        self.add_anime_to_user_downloads_list(anime_id)

        # TODO:Add custom download cmds functionality
        on_progress = lambda *args: self.download_screen.on_episode_download_progress(
            *args
        )
        output_path = self.config.get("Preferences", "downloads_dir")  # type: ignore
        self.download_screen.on_new_download_task(
            default_cmds["title"], default_cmds.get("episodes_range")
        )
        if episodes_range := default_cmds.get("episodes_range"):
            download_task = lambda: AnimdlApi.download_anime_by_title(
                default_cmds["title"],
                on_progress,
                lambda anime_title, episode: show_notification(
                    "Finished installing an episode", f"{anime_title}-{episode}"
                ),
                self.download_anime_complete,
                output_path,
                episodes_range,
            )  # ,default_cmds["quality"]
            self.downloads_queue.put(download_task)
            Logger.info(
                f"Downloader:Successfully Queued {default_cmds['title']} for downloading"
            )
        else:
            download_task = lambda: AnimdlApi.download_anime_by_title(
                default_cmds["title"],
                on_progress,
                lambda anime_title, episode: show_notification(
                    "Finished installing an episode", f"{anime_title}-{episode}"
                ),
                self.download_anime_complete,
                output_path,
            )  # ,default_cmds.get("quality")
            self.downloads_queue.put(download_task)
            Logger.info(
                f"Downloader:Successfully Queued {default_cmds['title']} for downloading"
            )

    def watch_on_allanime(self, title_):
        """
        Opens the given anime in your default browser on allanimes site
        Parameters:
        ----------
        title_: The anime title requested to be opened
        """
        if anime := AnimdlApi.get_anime_url_by_title(title_):
            title, link = anime
            parsed_link = f"https://allmanga.to/bangumi/{link.split('/')[-1]}"
        else:
            Logger.error(
                f"AniXStream:Failed to open {title_} in browser on allanime site"
            )
            show_notification(
                "Failure", f"Failed to open {title_} in browser on allanime site"
            )
        if webbrowser.open(parsed_link):
            Logger.info(
                f"AniXStream:Successfully opened {title} in browser allanime site"
            )
            show_notification(
                "Success", f"Successfully opened {title} in browser allanime site"
            )
        else:
            Logger.error(
                f"AniXStream:Failed to open {title} in browser on allanime site"
            )
            show_notification(
                "Failure", f"Failed to open {title} in browser on allanime site"
            )

    def stream_anime_with_custom_input_cmds(self, *cmds):
        self.animdl_streaming_subprocess = (
            AnimdlApi._run_animdl_command_and_get_subprocess(["stream", *cmds])
        )

    def stream_anime_by_title_with_animdl(
        self, title, episodes_range: str | None = None
    ):
        self.stop_streaming = False
        self.animdl_streaming_subprocess = AnimdlApi.stream_anime_by_title_on_animdl(
            title, episodes_range
        )

    def stream_anime_with_mpv(
        self, title, episodes_range: str | None = None, quality: str = "best"
    ):
        self.stop_streaming = False
        streams = AnimdlApi.stream_anime_with_mpv(title, episodes_range, quality)
        # TODO: End mpv child process properly
        for stream in streams:
            self.animdl_streaming_subprocess = stream
            for line in self.animdl_streaming_subprocess.stderr:  # type: ignore
                if self.stop_streaming:
                    if stream:
                        stream.terminate()
                        stream.kill()
                    del stream
                    return

    def watch_on_animdl(
        self,
        stream_with_mpv_options: dict | None = None,
        episodes_range: str | None = None,
        custom_options: tuple[str] | None = None,
    ):
        """
        Enables you to stream an anime using animdl either by parsing a title or custom animdl options

        parameters:
        -----------
        title_dict:dict["japanese","kanji"]
        a dictionary containing the titles of the anime
        custom_options:tuple[str]
        a tuple containing valid animdl stream commands
        """
        if self.animdl_streaming_subprocess:
            self.animdl_streaming_subprocess.kill()
            self.stop_streaming = True

        if stream_with_mpv_options:
            stream_func = lambda: self.stream_anime_with_mpv(
                stream_with_mpv_options["title"],
                stream_with_mpv_options.get("episodes_range"),
                stream_with_mpv_options["quality"],
            )
            self.queue.put(stream_func)

            Logger.info(
                f"Animdl:Successfully started to stream {stream_with_mpv_options['title']}"
            )
        else:
            stream_func = lambda: self.stream_anime_with_custom_input_cmds(
                *custom_options
            )
            self.queue.put(stream_func)
        show_notification("Streamer", "Started streaming")


if __name__ == "__main__":
    AniXStreamApp().run()
