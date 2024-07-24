import os

import click

from ...cli.utils.mpv import mpv
from ...libs.fzf import fzf
from ..config import Config
from ..utils.tools import exit_app
from ..utils.utils import fuzzy_inquirer


@click.command(
    help="View and watch your downloads using mpv", short_help="Watch downloads"
)
@click.option("--path", "-p", help="print the downloads folder and exit", is_flag=True)
@click.pass_obj
def downloads(config: Config, path: bool):
    USER_VIDEOS_DIR = config.downloads_dir
    if path:
        print(USER_VIDEOS_DIR)
        return
    if not os.path.exists(USER_VIDEOS_DIR):
        print("Downloads directory specified does not exist")
        return
    playlists = os.listdir(USER_VIDEOS_DIR)
    playlists.append("Exit")

    def stream():
        if config.use_fzf:
            playlist_name = fzf.run(playlists, "Enter Playlist Name", "Downloads")
        else:
            playlist_name = fuzzy_inquirer("Enter Playlist Name: ", playlists)
        if playlist_name == "Exit":
            exit_app()
            return
        playlist = os.path.join(USER_VIDEOS_DIR, playlist_name)
        mpv(playlist)
        stream()

    stream()
