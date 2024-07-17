import shutil
import subprocess


def mpv(link, title, *custom_args):
    MPV = shutil.which("mpv")
    if not MPV:
        print("mpv not found")
        return
    subprocess.run([MPV, *custom_args, f"--title={title}", link])
