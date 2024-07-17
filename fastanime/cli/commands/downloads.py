import os
import shutil
import subprocess

import click

from ... import USER_VIDEOS_DIR
from ...libs.fzf import fzf
from ..utils.tools import exit_app


@click.command(
    help="View and watch your downloads using mpv", short_help="Watch downloads"
)
def downloads():
    MPV = shutil.which("mpv")
    if not MPV:
        print("mpv not found")
        exit_app()
        return
    playlists = os.listdir(USER_VIDEOS_DIR)
    playlists.append("Exit")

    def stream():
        playlist_name = fzf.run(playlists, "Enter Playlist Name", "Downloads")
        if playlist_name == "Exit":
            exit_app()
        playlist = os.path.join(USER_VIDEOS_DIR, playlist_name)
        subprocess.run([MPV, playlist])
        stream()

    stream()
