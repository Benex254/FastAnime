from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from ..config import Config


@click.command(
    help="View and watch your downloads using mpv", short_help="Watch downloads"
)
@click.option("--path", "-p", help="print the downloads folder and exit", is_flag=True)
@click.pass_obj
def downloads(config: "Config", path: bool):
    import logging
    import os

    from ...cli.utils.mpv import run_mpv
    from ...libs.fzf import fzf
    from ...libs.rofi import Rofi
    from ..utils.tools import exit_app
    from ..utils.utils import fuzzy_inquirer

    logger = logging.getLogger(__name__)

    USER_VIDEOS_DIR = config.downloads_dir
    if path:
        print(USER_VIDEOS_DIR)
        return
    if not os.path.exists(USER_VIDEOS_DIR):
        print("Downloads directory specified does not exist")
        return
    anime_downloads = os.listdir(USER_VIDEOS_DIR)
    anime_downloads.append("Exit")

    def create_thumbnails(video_path, anime_title, downloads_thumbnail_cache_dir):
        import os
        import shutil
        import subprocess

        FFMPEG_THUMBNAILER = shutil.which("ffmpegthumbnailer")
        if not FFMPEG_THUMBNAILER:
            return

        out = os.path.join(downloads_thumbnail_cache_dir, anime_title)
        completed_process = subprocess.run(
            [FFMPEG_THUMBNAILER, "-i", video_path, "-o", out], stderr=subprocess.PIPE
        )
        if completed_process.returncode == 0:
            logger.info(f"Success in creating {anime_title} thumbnail")
        else:
            logger.warn(f"Failed in creating {anime_title} thumbnail")

    def get_previews(workers=None):
        import concurrent.futures
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
        # use concurrency to download the images as fast as possible
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            # load the jobs
            future_to_url = {}
            for anime_title in anime_downloads:
                anime_path = os.path.join(USER_VIDEOS_DIR, anime_title)
                if not os.path.isdir(anime_path):
                    continue
                playlist = os.listdir(anime_path)
                if playlist:
                    # actual link to download image from
                    video_path = os.path.join(anime_path, playlist[0])
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
        os.environ["SHELL"] = shutil.which("bash") or "bash"
        preview = """
            %s
            if [ -s %s/{} ]; then fzf-preview %s/{}
            else echo Loading...
            fi
        """ % (
            fzf_preview,
            downloads_thumbnail_cache_dir,
            downloads_thumbnail_cache_dir,
        )
        return preview

    def stream():
        if config.use_fzf:
            if not config.preview:
                playlist_name = fzf.run(
                    anime_downloads,
                    "Enter Playlist Name",
                )
            else:
                preview = get_previews()
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
                "Enter Playlist Name: ",
            )
        if playlist_name == "Exit":
            exit_app()
            return
        playlist = os.path.join(USER_VIDEOS_DIR, playlist_name)
        run_mpv(playlist)
        stream()

    stream()
