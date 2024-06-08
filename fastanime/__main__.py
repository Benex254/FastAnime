import os
import random
import webbrowser
from queue import Queue
from subprocess import Popen
from threading import Thread

import plyer
from kivy.clock import Clock
from kivy.config import Config
from kivy.loader import Loader
from kivy.logger import Logger
from kivy.resources import resource_add_path, resource_find, resource_remove_path
from kivy.uix.screenmanager import FadeTransition, ScreenManager
from kivy.uix.settings import Settings, SettingsWithSidebar
from kivymd.app import MDApp
from dotenv import load_dotenv

from .libs.animdl import AnimdlApi
from .Utility import (
    animdl_config_manager,
    show_notification,
    themes_available,
    user_data_helper,
)
from .Utility.utils import write_crash
from .View.components.media_card.components.media_popup import MediaPopup
from .View.screens import screens

load_dotenv()
os.environ["KIVY_VIDEO"] = "ffpyplayer"  # noqa: E402

Config.set("graphics", "width", "1000")  # noqa: E402
Config.set("graphics", "minimum_width", "1000")  # noqa: E402
Config.set("kivy", "window_icon", resource_find("logo.ico"))  # noqa: E402
Config.write()  # noqa: E402
# resource_add_path("_internal")

app_dir = os.path.dirname(__file__)

# make sure we aint searching dist folder
dist_folder = os.path.join(app_dir, "dist")
resource_remove_path(dist_folder)

assets_folder = os.path.join(app_dir, "assets")
resource_add_path(assets_folder)
conigs_folder = os.path.join(app_dir, "configs")
resource_add_path(conigs_folder)
# from kivy.core.window import Window
Loader.num_workers = 5
Loader.max_upload_per_frame = 10


# Ensure the user data fields exist
if not (user_data_helper.user_data.exists("user_anime_list")):
    user_data_helper.update_user_anime_list([])


# TODO: Confirm data integrity from user_data and yt_cache
class AniXStreamApp(MDApp):
    # some initialize

    queue = Queue()
    downloads_queue = Queue()
    animdl_streaming_subprocess: Popen | None = None
    default_anime_image = resource_find(random.choice(["default_1.jpg", "default.jpg"]))
    default_banner_image = resource_find(random.choice(["banner_1.jpg", "banner.jpg"]))
    # default_video = resource_find("Billyhan_When you cant afford Crunchyroll to watch anime.mp4")

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
        self.icon = resource_find("logo.png")

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
        self.home_screen = self.manager_screens.get_screen("home screen")
        return self.manager_screens

    def on_start(self, *args):
        self.media_card_popup = MediaPopup()
        if self.config.get("Preferences", "is_startup_anime_enable") == "1":  # type: ignore
            Clock.schedule_once(
                lambda _: self.home_screen.controller.populate_home_screen(), 1
            )

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
            "Settings", self.config, resource_find("general_settings_panel.json")
        )
        settings.add_json_panel(
            "Animdl Config", self.config, resource_find("animdl_config_panel.json")
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
        def on_progress(*args):
            return self.download_screen.on_episode_download_progress(*args)

        output_path = self.config.get("Preferences", "downloads_dir")  # type: ignore
        self.download_screen.on_new_download_task(
            default_cmds["title"], default_cmds.get("episodes_range")
        )
        if episodes_range := default_cmds.get("episodes_range"):

            def download_task():
                return AnimdlApi.download_anime_by_title(
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

            def download_task():
                return AnimdlApi.download_anime_by_title(
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
        try:
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
                return
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
        except Exception as e:
            show_notification("Something went wrong", f"{e}")

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
            try:
                if isinstance(stream, str):
                    show_notification("Failed to stream current episode", f"{stream}")
                    continue
                self.animdl_streaming_subprocess = stream

                for line in self.animdl_streaming_subprocess.stderr:  # type: ignore
                    if self.stop_streaming:
                        if stream:
                            stream.terminate()
                            stream.kill()
                        del stream
                        return
            except Exception as e:
                show_notification("Something went wrong while streaming", f"{e}")

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

            def stream_func():
                return self.stream_anime_with_mpv(
                    stream_with_mpv_options["title"],
                    stream_with_mpv_options.get("episodes_range"),
                    stream_with_mpv_options["quality"],
                )

            self.queue.put(stream_func)

            Logger.info(
                f"Animdl:Successfully started to stream {stream_with_mpv_options['title']}"
            )
        else:

            def stream_func():
                return self.stream_anime_with_custom_input_cmds(*custom_options)

            self.queue.put(stream_func)
        show_notification("Streamer", "Started streaming")


def run_app():
    AniXStreamApp().run()


if __name__ == "__main__":
    in_development = bool(os.environ.get("IN_DEVELOPMENT", False))
    print("In Development {}".format(in_development))
    if in_development:
        run_app()
    else:
        try:
            run_app()
        except Exception as e:
            write_crash(e)
