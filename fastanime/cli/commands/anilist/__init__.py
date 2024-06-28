import click

from ...interfaces import anilist as anilist_interface
from .favourites import favourites
from .popular import popular
from .recent import recent
from .search import search
from .trending import trending
from .upcoming import upcoming

commands = {
    "favourites": favourites,
    "recent": recent,
    "search": search,
    "popular": popular,
    "trending": trending,
    "upcoming": upcoming,
}


@click.group(commands=commands, invoke_without_command=True)
@click.pass_obj
def anilist(config):
    anilist_interface(config=config)
