import click

from ....libs.anilist.anilist import AniList
from ...interfaces.anilist_interfaces import select_anime
from ...utils.tools import QueryDict


@click.command(
    help="Search for anime using anilists api and get top ~50 results",
    short_help="Search for anime",
)
@click.argument(
    "title",
)
@click.pass_obj
def search(config, title):
    success, search_results = AniList.search(title)
    if success:
        anilist_config = QueryDict()
        anilist_config.data = search_results
        select_anime(config, anilist_config)
