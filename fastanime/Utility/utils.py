import logging
from typing import TYPE_CHECKING

from thefuzz import fuzz

from .data import anime_normalizer

if TYPE_CHECKING:
    from ..libs.anilist.types import AnilistBaseMediaDataSchema

logger = logging.getLogger(__name__)


def sort_by_episode_number(filename: str):
    import re

    match = re.search(r"\d+", filename)
    return int(match.group()) if match else 0


def anime_title_percentage_match(
    possible_user_requested_anime_title: str, anime: "AnilistBaseMediaDataSchema"
) -> float:
    """Returns the percentage match between the possible title and user title

    Args:
        possible_user_requested_anime_title (str): an Animdl search result title
        title (str): the anime title the user wants

    Returns:
        int: the percentage match
    """
    possible_user_requested_anime_title = anime_normalizer.get(
        possible_user_requested_anime_title, possible_user_requested_anime_title
    )
    # compares both the romaji and english names and gets highest Score
    title_a = str(anime["title"]["romaji"])
    title_b = str(anime["title"]["english"])
    percentage_ratio = max(
        *[
            fuzz.ratio(title.lower(), possible_user_requested_anime_title.lower())
            for title in anime["synonyms"]
        ],
        fuzz.ratio(title_a.lower(), possible_user_requested_anime_title.lower()),
        fuzz.ratio(title_b.lower(), possible_user_requested_anime_title.lower()),
    )
    logger.info(f"{locals()}")
    return percentage_ratio
