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
    import os

    from ...cli.utils.mpv import run_mpv
    from ...libs.fzf import fzf
    from ...libs.rofi import Rofi
    from ..utils.tools import exit_app
    from ..utils.utils import fuzzy_inquirer

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
        elif config.use_rofi:
            playlist_name = Rofi.run(playlists, "Enter Playlist Name")
        else:
            playlist_name = fuzzy_inquirer("Enter Playlist Name: ", playlists)
        if playlist_name == "Exit":
            exit_app()
            return
        playlist = os.path.join(USER_VIDEOS_DIR, playlist_name)
        run_mpv(playlist)
        stream()

    stream()
