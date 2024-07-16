import click

from ....libs.anilist.anilist import AniList
from ...interfaces.anilist_interfaces import select_anime
from ...utils.tools import QueryDict


@click.command(
    help="Fetch the top 15 most favourited anime from anilist",
    short_help="View most favourited anime",
)
@click.pass_obj
def favourites(config):
    anime_data = AniList.get_most_favourite()
    if anime_data[0]:
        anilist_config = QueryDict()
        anilist_config.data = anime_data[1]
        select_anime(config, anilist_config)
