import shutil
import subprocess
import sys


def mpv(link, *custom_args):
    MPV = shutil.which("mpv")
    if not MPV:
        return
    subprocess.run([MPV, *custom_args, link])
    sys.stdout.flush()
