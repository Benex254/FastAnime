import shutil
import subprocess

from .tools import exit_app


def SyncPlayer(url: str, anime_title=None, *args):
    # TODO: handle m3u8 multi quality streams
    #
    # check for SyncPlay
    SYNCPLAY_EXECUTABLE = shutil.which("syncplay")
    if not SYNCPLAY_EXECUTABLE:
        print("Syncplay not found")
        exit_app(1)
        return "0", "0"
    # start SyncPlayer
    if not anime_title:
        subprocess.run(
            [
                SYNCPLAY_EXECUTABLE,
                url,
            ]
        )
    else:
        subprocess.run(
            [SYNCPLAY_EXECUTABLE, url, "--", f"--force-media-title={anime_title}"]
        )

    # for compatability
    return "0", "0"
