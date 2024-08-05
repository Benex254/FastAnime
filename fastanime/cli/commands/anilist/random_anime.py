import random

import click

from ....anilist import AniList
from ...interfaces.anilist_interfaces import select_anime
from ...utils.tools import QueryDict


@click.command(
    help="Get random anime from anilist based on a range of anilist anime ids that are seected at random",
    short_help="View random anime",
)
@click.pass_obj
def random_anime(config):
    random_anime = range(1, 15000)

    random_anime = random.sample(random_anime, k=50)

    anime_data = AniList.search(id_in=list(random_anime))

    if anime_data[0]:
        anilist_config = QueryDict()
        anilist_config.data = anime_data[1]
        select_anime(config, anilist_config)
    else:
        print(anime_data[1])
