import shutil
import subprocess


def mpv(link, *custom_args):
    MPV = shutil.which("mpv")
    if not MPV:
        print("mpv not found")
        return
    subprocess.run([MPV, *custom_args, link])
