import logging

from fuzzywuzzy import fuzz

from ...libs.anime_provider.allanime.api import anime_provider
from ...Utility.data import anime_normalizer
from ..utils.fzf import fzf
from ..utils.mpv import mpv

logger = logging.getLogger(__name__)


def back_(anime, options):
    command = fzf(options.keys())
    if command:
        options[command](anime, options)


def anime_title_percentage_match(
    possible_user_requested_anime_title: str, title: tuple
) -> float:
    """Returns the percentage match between the possible title and user title

    Args:
        possible_user_requested_anime_title (str): an Animdl search result title
        title (str): the anime title the user wants

    Returns:
        int: the percentage match
    """
    if normalized_anime_title := anime_normalizer.get(
        possible_user_requested_anime_title
    ):
        possible_user_requested_anime_title = normalized_anime_title
    for key, value in locals().items():
        logger.info(f"{key}: {value}")
    # compares both the romaji and english names and gets highest Score
    percentage_ratio = max(
        fuzz.ratio(title[0].lower(), possible_user_requested_anime_title.lower()),
        fuzz.ratio(title[1].lower(), possible_user_requested_anime_title.lower()),
    )
    return percentage_ratio


def get_matched_result(anime_title, _search_results):
    result = max(
        _search_results,
        key=lambda x: anime_title_percentage_match(x, anime_title),
    )

    return result


def _get_result(result, compare):
    return result["name"] == compare


def _get_server(server, server_name):
    return server[0] == server_name


def stream_interface(_anime, back, prefered_translation="sub"):
    results = anime_provider.search_for_anime(_anime["title"]["romaji"])
    if results:
        _search_results = [result["name"] for result in results["shows"]["edges"]]

        anime_title = get_matched_result(
            (_anime["title"]["romaji"], _anime["title"]["english"]), _search_results
        )
        result = list(
            filter(lambda x: _get_result(x, anime_title), results["shows"]["edges"])
        )
        if not result:
            return

        anime = anime_provider.get_anime(result[0]["_id"])
        episode = fzf(anime["show"]["availableEpisodesDetail"][prefered_translation])

        if not episode:
            return
        if t_type := fzf(["sub", "dub"]):
            prefered_translation = t_type
        _episode_streams = anime_provider.get_anime_episode(
            result[0]["_id"], episode, prefered_translation
        )
        if _episode_streams:
            episode_streams = anime_provider.get_episode_streams(_episode_streams)
            if not episode_streams:
                return
            servers = list(episode_streams)

            _sever = fzf([server[0] for server in servers])
            if not _sever:
                return

            server = list(filter(lambda x: _get_server(x, _sever), servers)).pop()

            if not server:
                return
            #
            stream_link = server[1]["links"][0]["link"]
            mpv(stream_link)
            #
            # mpv_player.run_mpv(stream_link)
            stream_interface(_anime, back, prefered_translation)
