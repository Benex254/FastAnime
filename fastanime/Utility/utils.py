import logging
import os
import re
from functools import lru_cache

from thefuzz import fuzz

from fastanime.libs.anilist.anilist_data_schema import AnilistBaseMediaDataSchema

from .data import anime_normalizer

logger = logging.getLogger(__name__)


@lru_cache()
def remove_html_tags(text: str):
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


@lru_cache()
def sanitize_filename(filename: str):
    """
    Sanitize a string to be safe for use as a file name.

    :param filename: The original filename string.
    :return: A sanitized filename string.
    """
    # List of characters not allowed in filenames on various operating systems
    invalid_chars = r'[<>:"/\\|?*\0]'
    reserved_names = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    }

    # Replace invalid characters with an underscore
    sanitized = re.sub(invalid_chars, " ", filename)

    # Remove leading and trailing whitespace
    sanitized = sanitized.strip()

    # Check for reserved filenames
    name, ext = os.path.splitext(sanitized)
    if name.upper() in reserved_names:
        name += "_file"
        sanitized = name + ext

    # Ensure the filename is not empty
    if not sanitized:
        sanitized = "default_filename"

    return sanitized


def anime_title_percentage_match(
    possible_user_requested_anime_title: str, anime: AnilistBaseMediaDataSchema
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
    # compares both the romaji and english names and gets highest Score
    title_a = str(anime["title"]["romaji"])
    title_b = str(anime["title"]["english"])
    percentage_ratio = max(
        fuzz.ratio(title_a.lower(), possible_user_requested_anime_title.lower()),
        fuzz.ratio(title_b.lower(), possible_user_requested_anime_title.lower()),
    )
    logger.info(f"{locals()}")
    return percentage_ratio


if __name__ == "__main__":
    # Example usage
    unsafe_filename = "CON:example?file*name.txt"
    safe_filename = sanitize_filename(unsafe_filename)
    print(safe_filename)  # Output: 'CON_example_file_name.txt'
