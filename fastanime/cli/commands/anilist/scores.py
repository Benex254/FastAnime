import click

from ....libs.anilist.anilist import AniList
from ...interfaces.anilist_interfaces import select_anime
from ...utils.tools import QueryDict


@click.command(
    help="Fetch the 15 most scored anime", short_help="View most scored anime"
)
@click.pass_obj
def scores(config):
    anime_data = AniList.get_most_scored()
    if anime_data[0]:
        anilist_config = QueryDict()
        anilist_config.data = anime_data[1]
        select_anime(config, anilist_config)
