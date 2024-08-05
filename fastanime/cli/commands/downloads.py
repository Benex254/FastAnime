import os

import click

from ... import USER_VIDEOS_DIR
from ...cli.utils.mpv import mpv
from ...libs.fzf import fzf
from ..utils.tools import exit_app


@click.command(
    help="View and watch your downloads using mpv", short_help="Watch downloads"
)
def downloads():
    playlists = os.listdir(USER_VIDEOS_DIR)
    playlists.append("Exit")

    def stream():
        playlist_name = fzf.run(playlists, "Enter Playlist Name", "Downloads")
        if playlist_name == "Exit":
            exit_app()
            return
        playlist = os.path.join(USER_VIDEOS_DIR, playlist_name)
        mpv(playlist)
        stream()

    stream()
