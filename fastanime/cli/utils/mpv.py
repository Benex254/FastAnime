import re
import shutil
import subprocess
from typing import Optional


# legacy
# def mpv(link, title: None | str = "anime", *custom_args):
#     MPV = shutil.which("mpv")
#     if not MPV:
#         args = [
#             "nohup",
#             "am",
#             "start",
#             "--user",
#             "0",
#             "-a",
#             "android.intent.action.VIEW",
#             "-d",
#             link,
#             "-n",
#             "is.xyz.mpv/.MPVActivity",
#         ]
#         subprocess.run(args)
#     else:
#         subprocess.run([MPV, *custom_args, f"--title={title}", link])
#
#
def mpv(link: str, title: Optional[str] = "anime", *custom_args):
    # Determine if mpv is available
    MPV = shutil.which("mpv")

    # If title is None, set a default value
    if title is None:
        title = "anime"

    # Regex to check if the link is a YouTube URL
    youtube_regex = r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+"

    if not MPV:
        # Determine if the link is a YouTube URL
        if re.match(youtube_regex, link):
            # Android specific commands to launch mpv with a YouTube URL
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
                "com.google.android.youtube/.UrlActivity",
            ]
        else:
            # Android specific commands to launch mpv with a regular URL
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
        # General mpv command with custom arguments
        mpv_args = [MPV, *custom_args, f"--title={title}", link]
        subprocess.run(mpv_args)


# Example usage
if __name__ == "__main__":
    mpv(
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "Example Video",
        "--fullscreen",
        "--volume=50",
    )
