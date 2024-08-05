import logging
import os

from InquirerPy import inquirer
from thefuzz import fuzz

from ...constants import PLATFORM
from ...Utility.data import anime_normalizer

logger = logging.getLogger(__name__)


# Define ANSI escape codes as constants
RESET = "\033[0m"
BOLD = "\033[1m"
INVISIBLE_CURSOR = "\033[?25l"
VISIBLE_CURSOR = "\033[?25h"
UNDERLINE = "\033[4m"

# ESC[38;2;{r};{g};{b}m
BG_GREEN = "\033[48;2;120;233;12;m"
GREEN = "\033[38;2;45;24;45;m"


def get_true_fg(string: str, r: int, g: int, b: int, bold=True) -> str:
    if bold:
        return f"{BOLD}\033[38;2;{r};{g};{b};m{string}{RESET}"
    else:
        return f"\033[38;2;{r};{g};{b};m{string}{RESET}"


def get_true_bg(string, r: int, g: int, b: int) -> str:
    return f"\033[48;2;{r};{g};{b};m{string}{RESET}"


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
