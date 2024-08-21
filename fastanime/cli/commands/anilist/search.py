import click

from ...completion_functions import anime_titles_shell_complete


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
    type=click.Choice(["WINTER", "SPRING", "SUMMER", "FALL"]),
)
@click.option(
    "--status",
    "-S",
    help="The media status of the anime",
    type=click.Choice(
        ["FINISHED", "RELEASING", "NOT_YET_RELEASED", "CANCELLED", "HIATUS"]
    ),
)
@click.option(
    "--sort",
    "-s",
    help="What to sort the search results on",
    type=click.Choice(
        [
            "ID",
            "ID_DESC",
            "TITLE_ROMAJI",
            "TITLE_ROMAJI_DESC",
            "TITLE_ENGLISH",
            "TITLE_ENGLISH_DESC",
            "TITLE_NATIVE",
            "TITLE_NATIVE_DESC",
            "TYPE",
            "TYPE_DESC",
            "FORMAT",
            "FORMAT_DESC",
            "START_DATE",
            "START_DATE_DESC",
            "END_DATE",
            "END_DATE_DESC",
            "SCORE",
            "SCORE_DESC",
            "POPULARITY",
            "POPULARITY_DESC",
            "TRENDING",
            "TRENDING_DESC",
            "EPISODES",
            "EPISODES_DESC",
            "DURATION",
            "DURATION_DESC",
            "STATUS",
            "STATUS_DESC",
            "CHAPTERS",
            "CHAPTERS_DESC",
            "VOLUMES",
            "VOLUMES_DESC",
            "UPDATED_AT",
            "UPDATED_AT_DESC",
            "SEARCH_MATCH",
            "FAVOURITES",
            "FAVOURITES_DESC",
        ]
    ),
)
@click.option("--genres", "-g", multiple=True, help="the genres to filter by")
@click.option("--tags", "-t", multiple=True, help="the tags to filter by")
@click.option(
    "--media-format",
    "-f",
    multiple=True,
    help="Media format",
    type=click.Choice(
        ["TV", "TV_SHORT", "MOVIE", "SPECIAL", "OVA", "MUSIC", "NOVEL", "ONE_SHOT"]
    ),
)
@click.option(
    "--year",
    "-y",
    type=click.Choice(
        [
            "2024",
            "2023",
            "2022",
            "2021",
            "2020",
            "2019",
            "2018",
            "2017",
            "2016",
            "2015",
            "2014",
            "2013",
            "2012",
            "2011",
            "2010",
            "2009",
            "2008",
            "2007",
            "2006",
            "2005",
            "2004",
            "2000",
            "1990",
            "1980",
            "1970",
            "1960",
            "1950",
            "1940",
            "1930",
            "1920",
            "1910",
            "1900",
        ]
    ),
    help="the year the media was released",
)
@click.pass_obj
def search(
    config, title, dump_json, season, status, sort, genres, tags, media_format, year
):
    from ....anilist import AniList

    success, search_results = AniList.search(
        query=title,
        sort=sort,
        status=status,
        genre_in=list(genres),
        season=season,
        tag_in=list(tags),
        seasonYear=year,
        format_in=list(media_format),
    )
    if success:
        if dump_json:
            import json

            print(json.dumps(search_results))
        else:
            from ...interfaces.anilist_interfaces import anilist_results_menu
            from ...utils.tools import FastAnimeRuntimeState

            fastanime_runtime_state = FastAnimeRuntimeState()
            fastanime_runtime_state.anilist_data = search_results
            anilist_results_menu(config, fastanime_runtime_state)
    else:
        from sys import exit

        exit(1)
