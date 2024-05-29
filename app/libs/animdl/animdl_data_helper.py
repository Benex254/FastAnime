import re
import json

from fuzzywuzzy import fuzz

from .extras import Logger
from .animdl_types import AnimdlAnimeUrlAndTitle,AnimdlData,AnimdlAnimeEpisode,AnimdlEpisodeStream


# Currently this links don't work so we filter it out
broken_link_pattern = r"https://tools.fast4speed.rsvp/\w*"


def path_parser(path: str) -> str:
    """Parses a string and removes path unsafe characters

    Args:
        path (str): a path literal

    Returns:
        str: a parsed string that can be used as a valid path
    """
    return (
        path.replace(":", "")
        .replace("/", "")
        .replace("\\", "")
        .replace('"', "")
        .replace("'", "")
        .replace("<", "")
        .replace(">", "")
        .replace("|", "")
        .replace("?", "")
        .replace(".", "")
        .replace("*", "")
    )


def string_contains_only_spaces(input_string: str) -> bool:
    """Checks if the string is a string of spaces

    Args:
        input_string (str): any string

    Returns:
        bool: a boolean in indicating whether it does contain only spaces or not
    """
    return all(char.isspace() for char in input_string)


def anime_title_percentage_match(
    possible_user_requested_anime_title: str, title: str
) -> int:
    """Returns the percentage match between the possible title and user title

    Args:
        possible_user_requested_anime_title (str): an Animdl search result title
        title (str): the anime title the user wants

    Returns:
        int: the percentage match
    """

    percentage_ratio = fuzz.ratio(title, possible_user_requested_anime_title)
    Logger.info(
        f"Animdl Api Fuzzy: Percentage match of {possible_user_requested_anime_title} against {title}: {percentage_ratio}%"
    )
    return percentage_ratio


def filter_broken_streams(
    streams: list[AnimdlEpisodeStream],
) -> list[AnimdlEpisodeStream]:
    stream_filter = lambda stream: (
        True if not re.match(broken_link_pattern, stream["stream_url"]) else False
    )
    return list(filter(stream_filter, streams))


def filter_streams_by_quality(
    anime_episode_streams: list[AnimdlEpisodeStream], quality: str|int, strict=False
) -> AnimdlEpisodeStream:
    # filtered_streams = []
    # get the appropriate stream or default to best
    get_quality_func = lambda stream_: (
        stream_.get("quality") if stream_.get("quality") else 0
    )
    match quality:
        case "best":
            return max(anime_episode_streams, key=get_quality_func)
        case "worst":
            return min(anime_episode_streams, key=get_quality_func)
        case _:
            for episode_stream in anime_episode_streams:
                if str(episode_stream.get("quality")) == str(quality):
                    return episode_stream
            else:
                # if not strict:
                Logger.info(f"Animdl Api: Not strict so defaulting to best")
                return max(anime_episode_streams, key=get_quality_func)
                # else:
                #     Logger.warning(
                #         f"Animdl Api: No stream matching the given quality was found"
                #     )
                #     return AnimdlEpisodeStream({})


# TODO: add typing to return dict
def parse_stream_urls_data(raw_stream_urls_data: str) -> list[AnimdlAnimeEpisode]:
    try:
        return [
            AnimdlAnimeEpisode(json.loads(episode.strip()))
            for episode in raw_stream_urls_data.strip().split("\n")
        ]
    except Exception as e:
        Logger.error(f"Animdl Api Parser {e}")
        return []


def search_output_parser(raw_data: str) -> list[AnimdlAnimeUrlAndTitle]:
    """Parses the recieved raw search animdl data and makes it more easy to use

    Args:
        raw_data (str): valid animdl data

    Returns:
        dict: parsed animdl data containing an anime title
    """
    # get each line of dat and ignore those that contain unwanted data
    data = raw_data.split("\n")[3:]

    parsed_data = []
    pass_next = False

    # loop through all lines and return an appropriate AnimdlAimeUrlAndTitle
    for i, data_item in enumerate(data[:]):
        # continue if current was used in creating previous animdlanimeurlandtitle
        if pass_next:
            pass_next = False
            continue

        # there is no data or its just spaces so ignore and continue
        if not data_item or string_contains_only_spaces(data_item):
            continue

        # split title? from url?
        item = data_item.split(" / ")

        numbering_pattern = r"^\d*\.\s*"

        # attempt to parse
        try:
            # remove numbering from search results
            anime_title = re.sub(numbering_pattern, "", item[0]).lower()

            # special case for onepiece since allanime labels it as 1p instead of onepiece
            one_piece_regex = re.compile(r"1p", re.IGNORECASE)
            if one_piece_regex.match(anime_title):
                anime_title = "one piece"

            # checks if the data is already structure like anime title, animdl url if not makes it that way
            if item[1] == "" or string_contains_only_spaces(item[1]):
                pass_next = True
                parsed_data.append(AnimdlAnimeUrlAndTitle(anime_title, data[(i + 1)]))
            else:
                parsed_data.append(AnimdlAnimeUrlAndTitle(anime_title, item[1]))
        except:
            pass
    return parsed_data  # anime title,url
