import logging
from queue import Queue
from threading import Thread

import yt_dlp

from ..utils import sanitize_filename

logger = logging.getLogger(__name__)


class MyLogger:
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


def main_progress_hook(data):
    match data["status"]:
        case "error":
            logger.error("sth went wrong")
        case "finished":
            logger.info("download complete")


# Options for yt-dlp


class YtDLPDownloader:
    downloads_queue = Queue()

    def _worker(self):
        while True:
            task, args = self.downloads_queue.get()
            try:
                task(*args)
            except Exception as e:
                logger.error(f"Something went wrong {e}")
            self.downloads_queue.task_done()

    def __init__(self):
        self._thread = Thread(target=self._worker)
        self._thread.daemon = True
        self._thread.start()

    # Function to download the file
    def _download_file(self, url: str, download_dir, title, silent):
        anime_title = sanitize_filename(title[0])
        episode_title = sanitize_filename(title[1])
        ydl_opts = {
            "outtmpl": f"{download_dir}/{anime_title}/{episode_title}.%(ext)s",  # Specify the output path and template
            "progress_hooks": [
                main_progress_hook,
            ],  # Progress hook
            "silent": silent,
            "verbose": False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    def download_file(self, url: str, title, silent=True):
        self.downloads_queue.put((self._download_file, (url, title, silent)))


downloader = YtDLPDownloader()
