import os
import re
import shutil
from subprocess import PIPE, CompletedProcess, Popen, run
from typing import Callable

from .animdl_data_helper import (
    anime_title_percentage_match,
    filter_broken_streams,
    filter_streams_by_quality,
    parse_stream_urls_data,
    path_parser,
    search_output_parser,
)
from .animdl_exceptions import (
    AnimdlAnimeUrlNotFoundException,
    MPVNotFoundException,
    NoValidAnimeStreamsException,
    Python310NotFoundException,
)
from .animdl_types import AnimdlAnimeEpisode, AnimdlAnimeUrlAndTitle, AnimdlData
from .extras import Logger

broken_link_pattern = r"https://tools.fast4speed.rsvp/\w*"


def run_mpv_command(*cmds) -> Popen:
    if mpv := shutil.which("mpv"):
        Logger.debug({"Animdl Api: Started mpv command"})
        child_process = Popen(
            [mpv, *cmds],
            stderr=PIPE,
            text=True,
            stdout=PIPE,
        )
        return child_process
    else:
        raise MPVNotFoundException("MPV is required to be on path for this to work")


# TODO: WRITE Docs for each method
class AnimdlApi:
    @classmethod
    def _run_animdl_command(cls, cmds: list[str], capture=True) -> CompletedProcess:
        """The core abstraction over the animdl cli that executes valid animdl commands

        Args:
            cmds (list): a list of valid animdl commands and options
            capture (bool, optional): whether to capture the command output or not. Defaults to True.

        Raises:
            Python310NotFoundException: An exception raised when the machine doesn't have python 3.10 in path which is required by animdls dependencies

        Returns:
            CompletedProcess: the completed animdl process
        """
        if py_path := shutil.which("python"):
            Logger.debug("Animdl Api: Started Animdl command")
            if capture:
                return run(
                    [py_path, "-m", "animdl", *cmds],
                    capture_output=True,
                    stdin=PIPE,
                    text=True,
                )
            else:
                return run([py_path, "-m", "animdl", *cmds])
        else:
            raise Python310NotFoundException(
                "Python 3.10 is required to be in path for this to work"
            )

    @classmethod
    def _run_animdl_command_and_get_subprocess(cls, cmds: list[str]) -> Popen:
        """An abstraction over animdl cli but offers more control as compered to  _run_animdl_command

        Args:
            cmds (list[str]): valid animdl commands and options

        Raises:
            Python310NotFoundException: An exception raised when the machine doesn't have python 3.10 in path which is required by animdls dependencies

        Returns:
            Popen: returns a subprocess in order to offer more control
        """

        # TODO: parse the commands
        parsed_cmds = list(cmds)

        if py_path := shutil.which("python"):
            Logger.debug("Animdl Api: Started Animdl command")
            base_cmds = [py_path, "-m", "animdl"]
            cmds_ = [*base_cmds, *parsed_cmds]
            child_process = Popen(cmds_)
            return child_process
        else:
            raise Python310NotFoundException(
                "Python 3.10 is required to be in path for this to work"
            )

    @classmethod
    def get_anime_url_by_title(
        cls, actual_user_requested_title: str
    ) -> AnimdlAnimeUrlAndTitle:
        """Searches for the title using animdl and gets the animdl anime url associated with a particular title which is used by animdl for scraping

        Args:
            actual_user_requested_title (str): any anime title the user wants

        Raises:
            AnimdlAnimeUrlNotFoundException: raised if no anime title is found

        Returns:
            AnimdlAnimeTitleAndUrl: The animdl anime url and title for the most likely one the user wants.NOTE: not always correct
        """
        result = cls._run_animdl_command(["search", actual_user_requested_title])
        possible_animes = search_output_parser(result.stderr)
        if possible_animes:
            most_likely_anime_url_and_title = max(
                possible_animes,
                key=lambda possible_data: anime_title_percentage_match(
                    possible_data.anime_title, actual_user_requested_title
                ),
            )
            return most_likely_anime_url_and_title  # ("title","anime url")
        else:
            raise AnimdlAnimeUrlNotFoundException(
                "The anime your searching for doesnt exist or animdl provider is broken or animdl not in your system path\nTry changing the default provider"
            )

    @classmethod
    def stream_anime_by_title_on_animdl(
        cls, title: str, episodes_range: str | None = None, quality: str = "best"
    ) -> Popen:
        """Streams the anime title on animdl

        Args:
            title (str): the anime title you want to stream
            episodes_range (str, optional): the episodes you want to stream; should be a valid animdl range. Defaults to None.
            quality (str, optional): the quality of the stream. Defaults to "best".

        Returns:
            Popen: the stream child subprocess for mor control
        """

        anime = cls.get_anime_url_by_title(title)

        base_cmds = ["stream", anime[1], "-q", quality]
        cmd = [*base_cmds, "-r", episodes_range] if episodes_range else base_cmds
        return cls._run_animdl_command_and_get_subprocess(cmd)

    @classmethod
    def stream_anime_with_mpv(
        cls, title: str, episodes_range: str | None = None, quality: str = "best"
    ):
        """Stream an anime directly with mpv without having to interact with animdl cli

        Args:
            title (str): the anime title you want to stream
            episodes_range (str | None, optional): a valid animdl episodes range you want ito watch. Defaults to None.
            quality (str, optional): the quality of the stream. Defaults to "best".

        Yields:
            Popen: the child subprocess you currently are watching
        """

        anime_data = cls.get_all_stream_urls_by_anime_title(title, episodes_range)
        stream = []
        for episode in anime_data.episodes:
            if streams := filter_broken_streams(episode["streams"]):
                stream = filter_streams_by_quality(streams, quality)

                episode_title = str(episode["episode"])
                if e_title := stream.get("title"):
                    episode_title = f"{episode_title}-{e_title}"

                window_title = (
                    f"{anime_data.anime_title} episode {episode_title}".title()
                )

                cmds = [stream["stream_url"], f"--title={window_title}"]
                if audio_tracks := stream.get("audio_tracks"):
                    tracks = ";".join(audio_tracks)
                    cmds = [*cmds, f"--audio-files={tracks}"]

                if subtitles := stream.get("subtitle"):
                    subs = ";".join(subtitles)
                    cmds = [*cmds, f"--sub-files={subs}"]

                Logger.debug(
                    f"Animdl Api Mpv Streamer: Starting to stream on mpv with commands: {cmds}"
                )
                yield run_mpv_command(*cmds)
                Logger.debug(
                    f"Animdl Api Mpv Streamer: Finished to stream episode {episode['episode']} on mpv"
                )
            else:
                Logger.debug(
                    f"Animdl Api Mpv Streamer: Failed to stream episode {episode['episode']} no valid streams"
                )
                yield f"Epiosde {episode['episode']} doesnt have any valid stream links"

    @classmethod
    def get_all_anime_stream_urls_by_anime_url(
        cls, anime_url: str, episodes_range: str | None = None
    ) -> list[AnimdlAnimeEpisode]:
        """gets all the streams for the animdl url

        Args:
            anime_url (str): an animdl url used in scraping
            episodes_range (str | None, optional): a valid animdl episodes range. Defaults to None.

        Returns:
            list[AnimdlAnimeEpisode]: A list of anime episodes gotten from animdl
        """

        cmd = (
            ["grab", anime_url, "-r", episodes_range]
            if episodes_range
            else ["grab", anime_url]
        )
        result = cls._run_animdl_command(cmd)
        return parse_stream_urls_data(result.stdout)  # type: ignore

    @classmethod
    def get_all_stream_urls_by_anime_title(
        cls, title: str, episodes_range: str | None = None
    ) -> AnimdlData:
        """retrieves all anime stream urls of the given episode range from animdl

        Args:
            title (str): the anime title
            episodes_range (str, optional): an animdl episodes range. Defaults to None.

        Returns:
            AnimdlData: The parsed data from animdl grab
        """

        possible_anime = cls.get_anime_url_by_title(title)
        return AnimdlData(
            possible_anime.anime_title,
            cls.get_all_anime_stream_urls_by_anime_url(
                possible_anime.animdl_anime_url, episodes_range
            ),
        )

    # TODO: Should i finish??
    @classmethod
    def get_stream_urls_by_anime_title_and_quality(
        cls, title: str, quality="best", episodes_range=None
    ):
        (cls.get_all_stream_urls_by_anime_title(title))

    @classmethod
    def download_anime_by_title(
        cls,
        _anime_title: str,
        on_episode_download_progress: Callable,
        on_episode_download_complete: Callable,
        on_complete: Callable,
        output_path: str,
        episodes_range: str | None = None,
        quality: str = "best",
    ) -> tuple[list[int], list[int]]:
        """Downloads anime either adaptive, progressive, or .m3u streams and uses mpv to achieve this

        Args:
            _anime_title (str): the anime title you want to download
            on_episode_download_progress (Callable): the callback when a chunk of an episode is downloaded
            on_episode_download_complete (Callable): the callback when an episode has been successfully downloaded
            on_complete (Callable): callback when the downloading process is complete
            output_path (str): the directory | folder to download the anime
            episodes_range (str | None, optional): a valid animdl episode range. Defaults to None.
            quality (str, optional): the anime quality. Defaults to "best".

        Raises:
            NoValidAnimeStreamsException: raised when no valid streams were found for a particular episode

        Returns:
            tuple[list[int], list[int]]: a tuple containing successful, and failed downloads list
        """

        anime_streams_data = cls.get_all_stream_urls_by_anime_title(
            _anime_title, episodes_range
        )

        failed_downloads = []
        successful_downloads = []

        anime_title = anime_streams_data.anime_title.capitalize()

        # determine and parse download location
        parsed_anime_title = path_parser(anime_title)
        download_location = os.path.join(output_path, parsed_anime_title)

        if not os.path.exists(download_location):
            os.mkdir(download_location)

        Logger.debug(f"Animdl Api Downloader: Started downloading: {anime_title}")
        for episode in anime_streams_data.episodes:
            episode_number = episode["episode"]
            episode_title = f"Episode {episode_number}"
            try:
                streams = filter_broken_streams(episode["streams"])

                # raises an exception if no streams for current episodes
                if not streams:
                    raise NoValidAnimeStreamsException(
                        f"No valid streams were found for episode {episode_number}"
                    )

                episode_stream = filter_streams_by_quality(streams, quality)

                # determine episode_title
                if _episode_title := episode_stream.get("title"):
                    episode_title = f"{episode_title} - {path_parser(_episode_title)}"

                # determine episode download location
                parsed_episode_title = path_parser(episode_title)
                episode_download_location = os.path.join(
                    download_location, parsed_episode_title
                )
                if not os.path.exists(episode_download_location):
                    os.mkdir(episode_download_location)

                # init download process
                stream_url = episode_stream["stream_url"]
                audio_tracks = episode_stream.get("audio_tracks")
                subtitles = episode_stream.get("subtitle")

                episode_info = {
                    "episode": episode_title,
                    "anime_title": anime_title,
                }

                # check if its adaptive or progressive and call the appropriate downloader
                if stream_url and subtitles and audio_tracks:
                    Logger.debug(
                        f"Animdl api Downloader: Downloading adaptive episode {anime_title}-{episode_title}"
                    )
                    cls.download_adaptive(
                        stream_url,
                        audio_tracks[0],
                        subtitles[0],
                        episode_download_location,
                        on_episode_download_progress,
                        episode_info,
                    )
                elif stream_url and subtitles:
                    # probably wont occur
                    Logger.debug(
                        f"Animdl api Downloader: downloading !? episode {anime_title}-{episode_title}"
                    )
                    cls.download_video_and_subtitles(
                        stream_url,
                        subtitles[0],
                        episode_download_location,
                        on_episode_download_progress,
                        episode_info,
                    )
                else:
                    Logger.debug(
                        f"Animdl api Downloader: Downloading progressive episode {anime_title}-{episode_title}"
                    )
                    cls.download_progressive(
                        stream_url,
                        episode_download_location,
                        episode_info,
                        on_episode_download_progress,
                    )

                # epiosode download complete
                on_episode_download_complete(anime_title, episode_title)
                successful_downloads.append(episode_number)
                Logger.debug(
                    f"Animdl api Downloader: Success in dowloading {anime_title}-{episode_title}"
                )
            except Exception as e:
                Logger.debug(
                    f"Animdl api Downloader: Failed in dowloading {anime_title}-{episode_title}; reason {e}"
                )
                failed_downloads.append(episode_number)

        Logger.debug(
            f"Animdl api Downloader: Completed in dowloading {anime_title}-{episodes_range}; Successful:{len(successful_downloads)}, Failed:{len(failed_downloads)}"
        )
        on_complete(successful_downloads, failed_downloads, anime_title)
        return (successful_downloads, failed_downloads)

    @classmethod
    def download_with_mpv(cls, url: str, output_path: str, on_progress: Callable):
        """The method used to download a remote resource with mpv

        Args:
            url (str): the url of the remote resource to download
            output_path (str): the location to download the resource to
            on_progress (Callable): the callback when a chunk of the resource is downloaded

        Returns:
            subprocess return code: the return code of the mpv subprocess
        """

        mpv_child_process = run_mpv_command(url, f"--stream-dump={output_path}")
        progress_regex = re.compile(r"\d+/\d+")  # eg Dumping 2044776/125359745

        # extract progress info from mpv
        for stream in mpv_child_process.stderr:  # type: ignore
            # Logger.info(f"Animdl Api Downloader: {stream}")
            if progress_matches := progress_regex.findall(stream):
                current_bytes, total_bytes = [
                    float(val) for val in progress_matches[0].split("/")
                ]
                on_progress(current_bytes, total_bytes)
        return mpv_child_process.returncode

    @classmethod
    def download_progressive(
        cls,
        video_url: str,
        output_path: str,
        episode_info: dict[str, str],
        on_progress: Callable,
    ):
        """the progressive downloader of mpv

        Args:
            video_url (str): a video url
            output_path (str): download location
            episode_info (dict[str, str]): the details of the episode we downloading
            on_progress (Callable): the callback when a chunk is downloaded

        Raises:
            Exception: exception raised when anything goes wrong
        """

        episode = (
            path_parser(episode_info["anime_title"])
            + " - "
            + path_parser(episode_info["episode"])
        )
        file_name = episode + ".mp4"
        download_location = os.path.join(output_path, file_name)

        def on_progress_(current_bytes, total_bytes):
            return on_progress(current_bytes, total_bytes, episode_info)

        isfailure = cls.download_with_mpv(video_url, download_location, on_progress_)
        if isfailure:
            raise Exception

    @classmethod
    def download_adaptive(
        cls,
        video_url: str,
        audio_url: str,
        sub_url: str,
        output_path: str,
        on_progress: Callable,
        episode_info: dict[str, str],
    ):
        """the adaptive downloader

        Args:
            video_url (str): url of video you want ot download
            audio_url (str): url of audio file you want ot download
            sub_url (str): url of sub file you want ot download
            output_path (str): download location
            on_progress (Callable): the callback when a chunk is downloaded
            episode_info (dict[str, str]): episode details

        Raises:
            Exception: incase anything goes wrong
        """

        def on_progress_(current_bytes, total_bytes):
            return on_progress(current_bytes, total_bytes, episode_info)

        episode = (
            path_parser(episode_info["anime_title"])
            + " - "
            + path_parser(episode_info["episode"])
        )
        sub_filename = episode + ".ass"
        sub_filepath = os.path.join(output_path, sub_filename)
        cls.download_with_mpv(sub_url, sub_filepath, on_progress_)

        audio_filename = episode + ".mp3"
        audio_filepath = os.path.join(output_path, audio_filename)
        cls.download_with_mpv(audio_url, audio_filepath, on_progress_)

        video_filename = episode + ".mp4"
        video_filepath = os.path.join(output_path, video_filename)
        is_video_failure = cls.download_with_mpv(
            video_url, video_filepath, on_progress_
        )

        if is_video_failure:
            raise Exception

    @classmethod
    def download_video_and_subtitles(
        cls,
        video_url: str,
        sub_url: str,
        output_path: str,
        on_progress: Callable,
        episode_info: dict[str, str],
    ):
        """only downloads video and subs

        Args:
            video_url (str): url of video you want ot download
            sub_url (str): url of sub you want ot download
            output_path (str): the download location
            on_progress (Callable): the callback for when a chunk is downloaded
            episode_info (dict[str, str]): episode details

        Raises:
            Exception: when anything goes wrong
        """

        def on_progress_(current_bytes, total_bytes):
            return on_progress(current_bytes, total_bytes, episode_info)

        episode = (
            path_parser(episode_info["anime_title"])
            + " - "
            + path_parser(episode_info["episode"])
        )
        sub_filename = episode + ".ass"
        sub_filepath = os.path.join(output_path, sub_filename)
        cls.download_with_mpv(sub_url, sub_filepath, on_progress_)

        video_filename = episode + ".mp4"
        video_filepath = os.path.join(output_path, video_filename)
        is_video_failure = cls.download_with_mpv(
            video_url, video_filepath, on_progress_
        )

        if is_video_failure:
            raise Exception
