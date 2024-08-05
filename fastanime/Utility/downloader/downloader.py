from queue import Queue
from threading import Thread

import yt_dlp

from ... import USER_DOWNLOADS_DIR
from ..show_notification import show_notification
from ..utils import sanitize_filename


class MyLogger:
    def debug(self, msg):
        print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)


def main_progress_hook(data):
    match data["status"]:
        case "error":
            show_notification(
                "Something went wrong while downloading the video", data["filename"]
            )
        case "finished":
            show_notification("Downloaded", data["filename"])


# Options for yt-dlp


class YtDLPDownloader:
    downloads_queue = Queue()

    def _worker(self):
        while True:
            task, args = self.downloads_queue.get()
            try:
                task(*args)
            except Exception as e:
                show_notification("Something went wrong", f"Reason: {e}")
            self.downloads_queue.task_done()

    def __init__(self):
        self._thread = Thread(target=self._worker)
        self._thread.daemon = True
        self._thread.start()

    # Function to download the file
    def _download_file(self, url: str, title, custom_progress_hook, silent):
        anime_title = sanitize_filename(title[0])
        ydl_opts = {
            "outtmpl": f"{USER_DOWNLOADS_DIR}/{anime_title}/{anime_title}-episode {title[1]}.%(ext)s",  # Specify the output path and template
            "progress_hooks": [
                main_progress_hook,
                custom_progress_hook,
            ],  # Progress hook
            "silent": silent,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    def download_file(self, url: str, title, custom_progress_hook, silent=True):
        self.downloads_queue.put(
            (self._download_file, (url, title, custom_progress_hook, silent))
        )


downloader = YtDLPDownloader()
