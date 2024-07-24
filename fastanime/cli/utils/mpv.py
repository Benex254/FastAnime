import shutil
import subprocess


def mpv(link, title="anime", *custom_args):
    MPV = shutil.which("mpv")
    if not MPV:
        args = [
            "nohup",
            "am",
            "start",
            "--user",
            "0",
            "-a",
            "android.intent.action.VIEW",
            "-d",
            link,
            "-n",
            "is.xyz.mpv/.MPVActivity",
        ]
        subprocess.run(args)
    else:
        subprocess.run([MPV, *custom_args, f"--title={title}", link])
