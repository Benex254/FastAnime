import logging
from queue import Queue
from threading import Thread

import yt_dlp
from yt_dlp.utils import sanitize_filename

logger = logging.getLogger(__name__)


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
    # TODO: untpack the title to its actual values episode_title and anime_title
    def _download_file(
        self,
        url: str,
        anime_title: str,
        episode_title: str,
        download_dir: str,
        silent: bool,
        vid_format: str = "best",
        force_unknown_ext=False,
        verbose=False,
        headers={},
    ):
        """Helper function that downloads anime given url and path details

        Args:
            url: [TODO:description]
            anime_title: [TODO:description]
            episode_title: [TODO:description]
            download_dir: [TODO:description]
            silent: [TODO:description]
            vid_format: [TODO:description]
        """
        anime_title = sanitize_filename(anime_title)
        episode_title = sanitize_filename(episode_title)
        ydl_opts = {
            # Specify the output path and template
            "http_headers": headers,
            "outtmpl": f"{download_dir}/{anime_title}/{episode_title}.%(ext)s",
            "silent": silent,
            "verbose": verbose,
            "format": vid_format,
            "compat_opts": ("allow-unsafe-ext",) if force_unknown_ext else tuple(),
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    # WARN: May remove this legacy functionality
    def download_file(self, url: str, title, silent=True):
        """A helper that just does things in the background

        Args:
            title ([TODO:parameter]): [TODO:description]
            silent ([TODO:parameter]): [TODO:description]
            url: [TODO:description]
        """
        self.downloads_queue.put((self._download_file, (url, title, silent)))


downloader = YtDLPDownloader()
