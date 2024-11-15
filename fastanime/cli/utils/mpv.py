import re
import os
import shutil
import subprocess
import logging
import time

from ...constants import S_PLATFORM

logger = logging.getLogger(__name__)


def stream_video(MPV, url, mpv_args, custom_args):
    last_time = "0"
    total_time = "0"
    if os.environ.get("FASTANIME_DISABLE_MPV_POPEN", "0") == "0":
        process = subprocess.Popen(
            [
                MPV,
                url,
                *mpv_args,
                *custom_args,
                "--no-terminal",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            encoding="utf-8",
        )

        av_time_pattern = re.compile(r"AV: ([0-9:]*) / ([0-9:]*) \(([0-9]*)%\)")

        try:
            while True:
                if not process.stderr:
                    time.sleep(0.1)
                    continue
                output = process.stderr.readline()

                if output:
                    # Match the timestamp in the output
                    match = av_time_pattern.search(output.strip())
                    if match:
                        current_time = match.group(1)
                        total_time = match.group(2)
                        match.group(3)
                        last_time = current_time

                # Check if the process has terminated
                retcode = process.poll()
                if retcode is not None:
                    break

        except Exception as e:
            print(f"An error occurred: {e}")
            logger.error(f"An error occurred: {e}")
        finally:
            process.terminate()
            process.wait()
    else:
        subprocess.run([MPV, url, *mpv_args, *custom_args])
    return last_time, total_time


def run_mpv(
    link: str,
    title: str = "",
    start_time: str = "0",
    ytdl_format="",
    custom_args=[],
    headers={},
    subtitles=[],
    player="",
):
    # If title is None, set a default value

    # Regex to check if the link is a YouTube URL
    youtube_regex = r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+"

    if link.endswith(".torrent"):
        WEBTORRENT_CLI = shutil.which("webtorrent")
        if not WEBTORRENT_CLI:
            import time

            print(
                "webtorrent cli is not installed which is required for downloading and streaming from nyaa\nplease install it or use another provider"
            )
            time.sleep(120)
            return "0", "0"
        cmd = [WEBTORRENT_CLI, link, f"--{player}"]
        subprocess.run(cmd)
        return "0", "0"
    if player == "vlc":
        VLC = shutil.which("vlc")
        if not VLC and not S_PLATFORM == "win32":
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
                return "0", "0"
            else:
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
                    "org.videolan.vlc/org.videolan.vlc.gui.video.VideoPlayerActivity",
                    "-e",
                    "title",
                    title,
                ]

            subprocess.run(args)
            return "0", "0"
        else:
            args = ["vlc", link]
            for subtitle in subtitles:
                args.append("--sub-file")
                args.append(subtitle["url"])
                break
            if title:
                args.append("--video-title")
                args.append(title)
            subprocess.run(args)
            return "0", "0"
    else:
        # Determine if mpv is available
        MPV = shutil.which("mpv")
        if not MPV and not S_PLATFORM == "win32":
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
                return "0", "0"
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
            return "0", "0"
        else:
            # General mpv command with custom arguments
            mpv_args = []
            if headers:
                mpv_headers = "--http-header-fields="
                for header_name, header_value in headers.items():
                    mpv_headers += f"{header_name}:{header_value},"
                mpv_args.append(mpv_headers)
            for subtitle in subtitles:
                mpv_args.append(f"--sub-file={subtitle['url']}")
            if start_time != "0":
                mpv_args.append(f"--start={start_time}")
            if title:
                mpv_args.append(f"--title={title}")
            if ytdl_format:
                mpv_args.append(f"--ytdl-format={ytdl_format}")
            stop_time, total_time = stream_video(MPV, link, mpv_args, custom_args)
            return stop_time, total_time
