import click

from ....libs.anilist.anilist import AniList
from ...interfaces.anilist_interfaces import select_anime
from ...utils.tools import QueryDict


@click.command(
    help="Fetch the top 15 anime that are currently trending",
    short_help="Trending anime 🔥🔥🔥",
)
@click.pass_obj
def trending(config):
    success, data = AniList.get_trending()
    if success:
        anilist_config = QueryDict()
        anilist_config.data = data
        select_anime(config, anilist_config)
