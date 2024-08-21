import logging
from typing import TYPE_CHECKING

from InquirerPy import inquirer

logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from ...libs.anime_provider.types import EpisodeStream

# Define ANSI escape codes as constants
RESET = "\033[0m"
BOLD = "\033[1m"
INVISIBLE_CURSOR = "\033[?25l"
VISIBLE_CURSOR = "\033[?25h"
UNDERLINE = "\033[4m"

# ESC[38;2;{r};{g};{b}m
BG_GREEN = "\033[48;2;120;233;12;m"
GREEN = "\033[38;2;45;24;45;m"


def get_requested_quality_or_default_to_first(url, quality):
    import yt_dlp

    with yt_dlp.YoutubeDL({"quiet": True, "silent": True, "no_warnings": True}) as ydl:
        m3u8_info = ydl.extract_info(url, False)
        if not m3u8_info:
            return

    m3u8_formats = m3u8_info["formats"]
    quality = int(quality)
    quality_u = quality - 80
    quality_l = quality + 80
    for m3u8_format in m3u8_formats:
        if m3u8_format["height"] == quality or (
            m3u8_format["height"] < quality_u and m3u8_format["height"] > quality_l
        ):
            return m3u8_format["url"]
    else:
        return m3u8_formats[0]["url"]


def move_preferred_subtitle_lang_to_top(sub_list, lang_str):
    """Moves the dictionary with the given ID to the front of the list.

    Args:
      sub_list: list of subs
      lang_str: the sub lang pref

    Returns:
      The modified list.
    """
    import re

    for i, d in enumerate(sub_list):
        if re.search(lang_str, d["language"], re.IGNORECASE):
            sub_list.insert(0, sub_list.pop(i))
            break
    return sub_list


def filter_by_quality(quality: str, stream_links: "list[EpisodeStream]", default=True):
    """Helper function used to filter a list of EpisodeStream objects to one that has a corresponding quality

    Args:
        quality: the quality to use
        stream_links: a list of EpisodeStream objects

    Returns:
        an EpisodeStream object or None incase the quality was not found
    """
    for stream_link in stream_links:
        q = float(quality)
        Q = float(stream_link["quality"])
        # some providers have inaccurate/weird/non-standard eg qualities 718 instead of 720
        if Q <= q + 80 and Q >= q - 80:
            return stream_link
    else:
        if stream_links and default:
            from rich import print

            try:
                print("[yellow bold]WARNING Qualities were:[/] ", stream_links)
                print(
                    "[cyan bold]Using default of quality:[/] ",
                    stream_links[0]["quality"],
                )
                return stream_links[0]
            except Exception as e:
                print(e)
                return


def format_bytes_to_human(num_of_bytes: float, suffix: str = "B"):
    """Helper function usedd to format bytes to human

    Args:
        num_of_bytes: the number of bytes to format
        suffix: the suffix to use

    Returns:
        formated bytes
    """
    for unit in ("", "K", "M", "G", "T", "P", "E", "Z"):
        if abs(num_of_bytes) < 1024.0:
            return f"{num_of_bytes:3.1f}{unit}{suffix}"
        num_of_bytes /= 1024.0
    return f"{num_of_bytes:.1f}Yi{suffix}"


def get_true_fg(string: str, r: int, g: int, b: int, bold: bool = True) -> str:
    """Custom helper function that enables colored text in the terminal

    Args:
        bold: whether to bolden the text
        string: string to color
        r: red
        g: green
        b: blue

    Returns:
        colored string
    """
    # NOTE: Currently only supports terminals that support true color
    if bold:
        return f"{BOLD}\033[38;2;{r};{g};{b};m{string}{RESET}"
    else:
        return f"\033[38;2;{r};{g};{b};m{string}{RESET}"


def get_true_bg(string, r: int, g: int, b: int) -> str:
    return f"\033[48;2;{r};{g};{b};m{string}{RESET}"


def fuzzy_inquirer(choices: list, prompt: str, **kwargs):
    """helper function that enables easier interaction with InquirerPy lib

    Args:
        choices: the choices to prompt
        prompt: the prompt string to use
        **kwargs: other options to pass to fuzzy_inquirer

    Returns:
        a choice
    """
    from click import clear

    clear()
    action = inquirer.fuzzy(  # pyright:ignore
        prompt,
        choices,
        height="100%",
        border=True,
        validate=lambda result: result in choices,
        **kwargs,
    ).execute()
    return action
