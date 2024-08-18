from typing import TYPE_CHECKING

import click

from ..completion_functions import anime_titles_shell_complete

if TYPE_CHECKING:
    from ..config import Config


@click.command(
    help="Helper command to get streams for anime to use externally in a non-python application",
    short_help="Print anime streams to standard out",
)
@click.option(
    "--anime-titles",
    "--anime_title",
    "-t",
    required=True,
    shell_complete=anime_titles_shell_complete,
    multiple=True,
    help="Specify which anime to download",
)
@click.option(
    "--episode-range",
    "-r",
    help="A range of episodes to download (start-end)",
)
@click.option(
    "--search-results-only",
    "-s",
    help="print only the search results to stdout",
    is_flag=True,
)
@click.option(
    "--anime-info-only", "-i", help="print only selected anime title info", is_flag=True
)
@click.option(
    "--episode-streams-only",
    "-e",
    help="print only selected anime episodes streams of given range",
    is_flag=True,
)
@click.pass_obj
def grab(
    config: "Config",
    anime_titles: tuple,
    episode_range,
    search_results_only,
    anime_info_only,
    episode_streams_only,
):
    import json
    from logging import getLogger
    from sys import exit

    from thefuzz import fuzz

    from ...AnimeProvider import AnimeProvider

    logger = getLogger(__name__)

    anime_provider = AnimeProvider(config.provider)

    grabbed_animes = []
    for anime_title in anime_titles:
        # ---- search for anime ----
        search_results = anime_provider.search_for_anime(
            anime_title, translation_type=config.translation_type
        )
        if not search_results:
            exit(1)
        if search_results_only:
            # grab only search results skipping all lines after this
            grabbed_animes.append(search_results)
            continue

        search_results = search_results["results"]
        if not search_results:
            logger.error("no results for your search")
            exit(1)
        search_results_ = {
            search_result["title"]: search_result for search_result in search_results
        }

        search_result = max(
            search_results_.keys(), key=lambda title: fuzz.ratio(title, anime_title)
        )

        # ---- fetch anime ----
        anime = anime_provider.get_anime(search_results_[search_result]["id"])
        if not anime:
            exit(1)
        episodes = sorted(
            anime["availableEpisodesDetail"][config.translation_type], key=float
        )
        if anime_info_only:
            # grab only the anime data skipping all lines after this
            grabbed_animes.append(anime)
            continue

        # where the magic happens
        if episode_range:
            if ":" in episode_range:
                ep_range_tuple = episode_range.split(":")
                if len(ep_range_tuple) == 2 and all(ep_range_tuple):
                    episodes_start, episodes_end = ep_range_tuple
                    episodes_range = episodes[int(episodes_start) : int(episodes_end)]
                elif len(ep_range_tuple) == 3 and all(ep_range_tuple):
                    episodes_start, episodes_end, step = ep_range_tuple
                    episodes_range = episodes[
                        int(episodes_start) : int(episodes_end) : int(step)
                    ]
                else:
                    episodes_start, episodes_end = ep_range_tuple
                    if episodes_start.strip():
                        episodes_range = episodes[int(episodes_start) :]
                    elif episodes_end.strip():
                        episodes_range = episodes[: int(episodes_end)]
                    else:
                        episodes_range = episodes
            else:
                episodes_range = episodes[int(episode_range) :]

        else:
            episodes_range = sorted(episodes, key=float)

        if not episode_streams_only:
            grabbed_anime = dict(anime)
            grabbed_anime["requested_episodes"] = episodes_range
            grabbed_anime["translation_type"] = config.translation_type
            grabbed_anime["episodes_streams"] = {}
        else:
            grabbed_anime = {}

        # lets download em
        for episode in episodes_range:
            try:
                if episode not in episodes:
                    continue
                streams = anime_provider.get_episode_streams(
                    anime, episode, config.translation_type
                )
                if not streams:
                    continue
                episode_streams = {server["server"]: server for server in streams}

                if episode_streams_only:
                    grabbed_anime[episode] = episode_streams
                else:
                    grabbed_anime["episodes_streams"][  # pyright:ignore
                        episode
                    ] = episode_streams

            except Exception as e:
                logger.error(e)

        # grab the full data for single title and appen to final result or episode streams
        grabbed_animes.append(grabbed_anime)

    # print out the final result either {} or [] depending if more than one title os requested
    if len(grabbed_animes) == 1:
        print(json.dumps(grabbed_animes[0]))
    else:
        print(json.dumps(grabbed_animes))