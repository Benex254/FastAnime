import click

from ...completion_functions import anime_titles_shell_complete
from .data import (
    genres_available,
    media_formats_available,
    media_statuses_available,
    seasons_available,
    sorts_available,
    tags_available_list,
    years_available,
)


@click.command(
    help="Search for anime using anilists api and get top ~50 results",
    short_help="Search for anime",
)
@click.option("--title", "-t", shell_complete=anime_titles_shell_complete)
@click.option(
    "--dump-json",
    "-d",
    is_flag=True,
    help="Only print out the results dont open anilist menu",
)
@click.option(
    "--season",
    help="The season the media was released",
    type=click.Choice(seasons_available),
)
@click.option(
    "--status",
    "-S",
    help="The media status of the anime",
    multiple=True,
    type=click.Choice(media_statuses_available),
)
@click.option(
    "--sort",
    "-s",
    help="What to sort the search results on",
    type=click.Choice(sorts_available),
)
@click.option(
    "--genres",
    "-g",
    multiple=True,
    help="the genres to filter by",
    type=click.Choice(genres_available),
)
@click.option(
    "--tags",
    "-T",
    multiple=True,
    help="the tags to filter by",
    type=click.Choice(tags_available_list),
)
@click.option(
    "--media-format",
    "-f",
    multiple=True,
    help="Media format",
    type=click.Choice(media_formats_available),
)
@click.option(
    "--year",
    "-y",
    type=click.Choice(years_available),
    help="the year the media was released",
)
@click.option(
    "--on-list/--not-on-list",
    "-L/-no-L",
    help="Whether the anime should be in your list or not",
    type=bool,
)
@click.pass_obj
def search(
    config,
    title,
    dump_json,
    season,
    status,
    sort,
    genres,
    tags,
    media_format,
    year,
    on_list,
):
    from ....anilist import AniList

    success, search_results = AniList.search(
        query=title,
        sort=sort,
        status_in=list(status),
        genre_in=list(genres),
        season=season,
        tag_in=list(tags),
        seasonYear=year,
        format_in=list(media_format),
        on_list=on_list,
    )
    if success:
        if dump_json:
            import json

            print(json.dumps(search_results))
        else:
            from ...interfaces.anilist_interfaces import anilist_results_menu
            from ...utils.tools import FastAnimeRuntimeState

            fastanime_runtime_state = FastAnimeRuntimeState()

            fastanime_runtime_state.current_page = 1
            fastanime_runtime_state.current_data_loader = (
                lambda page=1, **kwargs: AniList.search(
                    query=title,
                    sort=sort,
                    status_in=list(status),
                    genre_in=list(genres),
                    season=season,
                    tag_in=list(tags),
                    seasonYear=year,
                    format_in=list(media_format),
                    on_list=on_list,
                    page=page,
                )
            )
            fastanime_runtime_state.anilist_results_data = search_results
            anilist_results_menu(config, fastanime_runtime_state)
    else:
        from sys import exit

        exit(1)
