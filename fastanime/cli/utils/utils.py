import logging
import os

from InquirerPy import inquirer
from thefuzz import fuzz

from ... import PLATFORM
from ...Utility.data import anime_normalizer

logger = logging.getLogger(__name__)


def clear():
    if PLATFORM == "Windows":
        os.system("cls")
    else:
        os.system("clear")


def fuzzy_inquirer(prompt: str, choices, **kwargs):
    clear()
    action = inquirer.fuzzy(
        prompt,
        choices,
        height="100%",
        border=True,
        validate=lambda result: result in choices,
        **kwargs,
    ).execute()
    return action


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


def get_selected_anime(anime_title, results):
    def _get_result(result, compare):
        return result["name"] == compare

    return list(
        filter(lambda x: _get_result(x, anime_title), results["shows"]["edges"])
    )


def get_selected_server(_server, servers):
    def _get_server(server, server_name):
        return server[0] == server_name

    server = list(filter(lambda x: _get_server(x, _server), servers)).pop()
    return server
