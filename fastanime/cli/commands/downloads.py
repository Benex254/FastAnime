import logging
from typing import TYPE_CHECKING

import click

from ..completion_functions import downloaded_anime_titles

logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from ..config import Config


@click.command(
    help="View and watch your downloads using mpv",
    short_help="Watch downloads",
    epilog="""
\b
\b\bExamples:
    fastanime downloads
\b
    # view individual episodes
    fastanime downloads --view-episodes
    # --- or ---
    fastanime downloads -v
\b
    # to set seek time when using ffmpegthumbnailer for local previews
    # -1 means random and is the default
    fastanime downloads --time-to-seek <intRange(-1,100)>
    # --- or ---
    fastanime downloads -t <intRange(-1,100)>
\b
    # to watch a specific title
    # be sure to get the completions for the best experience
    fastanime downloads --title <title>
\b
    # to get the path to the downloads folder set
    fastanime downloads --path
    # useful when you want to use the value for other programs
""",
)
@click.option("--path", "-p", help="print the downloads folder and exit", is_flag=True)
@click.option(
    "--title",
    "-T",
    shell_complete=downloaded_anime_titles,
    help="watch a specific title",
)
@click.option("--view-episodes", "-v", help="View individual episodes", is_flag=True)
@click.option(
    "--ffmpegthumbnailer-seek-time",
    "--time-to-seek",
    "-t",
    type=click.IntRange(-1, 100),
    help="ffmpegthumbnailer seek time",
)
@click.pass_obj
def downloads(
    config: "Config", path: bool, title, view_episodes, ffmpegthumbnailer_seek_time
):
    import os

    from ...cli.utils.mpv import run_mpv
    from ...libs.fzf import fzf
    from ...libs.rofi import Rofi
    from ...Utility.utils import sort_by_episode_number
    from ..utils.tools import exit_app
    from ..utils.utils import fuzzy_inquirer

    if not ffmpegthumbnailer_seek_time:
        ffmpegthumbnailer_seek_time = config.ffmpegthumbnailer_seek_time
    USER_VIDEOS_DIR = config.downloads_dir
    if path:
        print(USER_VIDEOS_DIR)
        return
    if not os.path.exists(USER_VIDEOS_DIR):
        print("Downloads directory specified does not exist")
        return
    anime_downloads = sorted(
        os.listdir(USER_VIDEOS_DIR),
    )
    anime_downloads.append("Exit")

    def create_thumbnails(video_path, anime_title, downloads_thumbnail_cache_dir):
        import os
        import shutil
        import subprocess

        FFMPEG_THUMBNAILER = shutil.which("ffmpegthumbnailer")
        if not FFMPEG_THUMBNAILER:
            return

        out = os.path.join(downloads_thumbnail_cache_dir, anime_title)
        if ffmpegthumbnailer_seek_time == -1:
            import random

            seektime = str(random.randrange(0, 100))
        else:
            seektime = str(ffmpegthumbnailer_seek_time)
        _ = subprocess.run(
            [
                FFMPEG_THUMBNAILER,
                "-i",
                video_path,
                "-o",
                out,
                "-s",
                "0",
                "-t",
                seektime,
            ],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )

    def get_previews_anime(workers=None, bg=True):
        import concurrent.futures
        import random
        import shutil
        from pathlib import Path

        if not shutil.which("ffmpegthumbnailer"):
            print("ffmpegthumbnailer not found")
            logger.error("ffmpegthumbnailer not found")
            return

        from ...constants import APP_CACHE_DIR
        from ..utils.scripts import fzf_preview

        downloads_thumbnail_cache_dir = os.path.join(APP_CACHE_DIR, "video_thumbnails")
        Path(downloads_thumbnail_cache_dir).mkdir(parents=True, exist_ok=True)

        def _worker():
            # use concurrency to download the images as fast as possible
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                # load the jobs
                future_to_url = {}
                for anime_title in anime_downloads:
                    anime_path = os.path.join(USER_VIDEOS_DIR, anime_title)
                    if not os.path.isdir(anime_path):
                        continue
                    playlist = [
                        anime
                        for anime in sorted(
                            os.listdir(anime_path),
                        )
                        if "mp4" in anime
                    ]
                    if playlist:
                        # actual link to download image from
                        video_path = os.path.join(anime_path, random.choice(playlist))
                        future_to_url[
                            executor.submit(
                                create_thumbnails,
                                video_path,
                                anime_title,
                                downloads_thumbnail_cache_dir,
                            )
                        ] = anime_title

                # execute the jobs
                for future in concurrent.futures.as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        future.result()
                    except Exception as e:
                        logger.error("%r generated an exception: %s" % (url, e))

        if bg:
            from threading import Thread

            worker = Thread(target=_worker)
            worker.daemon = True
            worker.start()
        else:
            _worker()
        os.environ["SHELL"] = shutil.which("bash") or "bash"
        preview = """
            %s
            if [ -s %s/{} ]; then 
                if ! fzf-preview %s/{} 2>/dev/null; then
                    echo Loading...
                fi
            else echo Loading...
            fi
        """ % (
            fzf_preview,
            downloads_thumbnail_cache_dir,
            downloads_thumbnail_cache_dir,
        )
        return preview

    def get_previews_episodes(anime_playlist_path, workers=None, bg=True):
        import shutil
        from pathlib import Path

        from ...constants import APP_CACHE_DIR
        from ..utils.scripts import fzf_preview

        if not shutil.which("ffmpegthumbnailer"):
            print("ffmpegthumbnailer not found")
            logger.error("ffmpegthumbnailer not found")
            return

        downloads_thumbnail_cache_dir = os.path.join(APP_CACHE_DIR, "video_thumbnails")
        Path(downloads_thumbnail_cache_dir).mkdir(parents=True, exist_ok=True)

        def _worker():
            import concurrent.futures

            # use concurrency to download the images as fast as possible
            # anime_playlist_path = os.path.join(USER_VIDEOS_DIR, anime_playlist_path)
            if not os.path.isdir(anime_playlist_path):
                return
            anime_episodes = sorted(
                os.listdir(anime_playlist_path), key=sort_by_episode_number
            )
            with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
                # load the jobs
                future_to_url = {}
                for episode_title in anime_episodes:
                    episode_path = os.path.join(anime_playlist_path, episode_title)

                    # actual link to download image from
                    future_to_url[
                        executor.submit(
                            create_thumbnails,
                            episode_path,
                            episode_title,
                            downloads_thumbnail_cache_dir,
                        )
                    ] = episode_title

                # execute the jobs
                for future in concurrent.futures.as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        future.result()
                    except Exception as e:
                        logger.error("%r generated an exception: %s" % (url, e))

        if bg:
            from threading import Thread

            worker = Thread(target=_worker)
            worker.daemon = True
            worker.start()
        else:
            _worker()
        os.environ["SHELL"] = shutil.which("bash") or "bash"
        preview = """
            %s
            if [ -s %s/{} ]; then 
                if ! fzf-preview %s/{} 2>/dev/null; then
                    echo Loading...
                fi
            else echo Loading...
            fi
        """ % (
            fzf_preview,
            downloads_thumbnail_cache_dir,
            downloads_thumbnail_cache_dir,
        )
        return preview

    def stream_episode(
        anime_playlist_path,
    ):
        if view_episodes:
            if not os.path.isdir(anime_playlist_path):
                print(anime_playlist_path, "is not dir")
                exit_app(1)
                return
            episodes = sorted(
                os.listdir(anime_playlist_path), key=sort_by_episode_number
            )
            downloaded_episodes = [*episodes, "Back"]

            if config.use_fzf:
                if not config.preview:
                    episode_title = fzf.run(
                        downloaded_episodes,
                        "Enter Episode ",
                    )
                else:
                    preview = get_previews_episodes(anime_playlist_path)
                    episode_title = fzf.run(
                        downloaded_episodes,
                        "Enter Episode ",
                        preview=preview,
                    )
            elif config.use_rofi:
                episode_title = Rofi.run(downloaded_episodes, "Enter Episode")
            else:
                episode_title = fuzzy_inquirer(
                    downloaded_episodes,
                    "Enter Playlist Name",
                )
            if episode_title == "Back":
                stream_anime()
                return
            episode_path = os.path.join(anime_playlist_path, episode_title)
            if config.sync_play:
                from ..utils.syncplay import SyncPlayer

                SyncPlayer(episode_path)
            else:
                run_mpv(
                    episode_path,
                    player=config.player,
                )
            stream_episode(anime_playlist_path)

    def stream_anime(title=None):
        if title:
            from thefuzz import fuzz

            playlist_name = max(anime_downloads, key=lambda t: fuzz.ratio(title, t))
        elif config.use_fzf:
            if not config.preview:
                playlist_name = fzf.run(
                    anime_downloads,
                    "Enter Playlist Name",
                )
            else:
                preview = get_previews_anime()
                playlist_name = fzf.run(
                    anime_downloads,
                    "Enter Playlist Name",
                    preview=preview,
                )
        elif config.use_rofi:
            playlist_name = Rofi.run(anime_downloads, "Enter Playlist Name")
        else:
            playlist_name = fuzzy_inquirer(
                anime_downloads,
                "Enter Playlist Name",
            )
        if playlist_name == "Exit":
            exit_app()
            return
        playlist = os.path.join(USER_VIDEOS_DIR, playlist_name)
        if view_episodes:
            stream_episode(
                playlist,
            )
        else:
            if config.sync_play:
                from ..utils.syncplay import SyncPlayer

                SyncPlayer(playlist)
            else:
                run_mpv(
                    playlist,
                    player=config.player,
                )
        stream_anime()

    stream_anime(title)
