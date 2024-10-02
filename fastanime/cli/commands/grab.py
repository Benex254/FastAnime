from typing import TYPE_CHECKING

import click

from ..completion_functions import anime_titles_shell_complete

if TYPE_CHECKING:
    from ..config import Config


@click.command(
    help="Helper command to get streams for anime to use externally in a non-python application",
    short_help="Print anime streams to standard out",
    epilog="""
\b
\b\bExamples:
  # --- print anime info + episode streams ---
\b
  # multiple titles can be specified with the -t option
  fastanime grab -t <anime-title> -t <anime-title>
  # -- or --
  # print all available episodes
  fastanime grab -t <anime-title> -r ':'
\b
  # print the latest episode
  fastanime grab -t <anime-title> -r '-1'
\b
  # print a specific episode range
  # be sure to observe the range Syntax
  fastanime grab -t <anime-title> -r '<start>:<stop>'
\b
  fastanime grab -t <anime-title> -r '<start>:<stop>:<step>'
\b
  fastanime grab -t <anime-title> -r '<start>:'
\b
  fastanime grab -t <anime-title> -r ':<end>'
\b
  # --- grab options ---
\b
  # print search results only
  fastanime grab -t <anime-title> -r <range> --search-results-only
\b
  # print anime info only
  fastanime grab -t <anime-title> -r <range> --anime-info-only
\b
  # print episode streams only
  fastanime grab -t <anime-title> -r <range> --episode-streams-only
""",
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

    logger = getLogger(__name__)
    if config.manga:
        manga_title = anime_titles[0]
        from ...MangaProvider import MangaProvider

        manga_provider = MangaProvider()
        search_data = manga_provider.search_for_manga(manga_title)
        if not search_data:
            exit(1)
        if search_results_only:
            print(json.dumps(search_data))
            exit(0)
        search_results = search_data["results"]
        if not search_results:
            logger.error("no results for your search")
            exit(1)
        search_results_ = {
            search_result["title"]: search_result for search_result in search_results
        }

        search_result_anime_title = max(
            search_results_.keys(), key=lambda title: fuzz.ratio(title, anime_titles[0])
        )
        manga_info = manga_provider.get_manga(
            search_results_[search_result_anime_title]["id"]
        )
        if not manga_info:
            return
        if anime_info_only:
            print(json.dumps(manga_info))
            exit(0)

        chapter_info = manga_provider.get_chapter_thumbnails(
            manga_info["id"], str(episode_range)
        )
        if not chapter_info:
            exit(1)
        print(json.dumps(chapter_info))

    else:
        from ...AnimeProvider import AnimeProvider

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
                search_result["title"]: search_result
                for search_result in search_results
            }

            search_result_anime_title = max(
                search_results_.keys(), key=lambda title: fuzz.ratio(title, anime_title)
            )

            # ---- fetch anime ----
            anime = anime_provider.get_anime(
                search_results_[search_result_anime_title]["id"]
            )
            if not anime:
                exit(1)
            if anime_info_only:
                # grab only the anime data skipping all lines after this
                grabbed_animes.append(anime)
                continue
            episodes = sorted(
                anime["availableEpisodesDetail"][config.translation_type], key=float
            )

            # where the magic happens
            if episode_range:
                if ":" in episode_range:
                    ep_range_tuple = episode_range.split(":")
                    if len(ep_range_tuple) == 2 and all(ep_range_tuple):
                        episodes_start, episodes_end = ep_range_tuple
                        episodes_range = episodes[
                            int(episodes_start) : int(episodes_end)
                        ]
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
                        anime["id"], episode, config.translation_type
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
