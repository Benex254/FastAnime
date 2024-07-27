import click

from ....anilist import AniList
from ...interfaces.anilist_interfaces import anilist as anilist_interface
from ...utils.tools import QueryDict
from .completed import completed
from .dropped import dropped
from .favourites import favourites
from .login import loggin
from .paused import paused
from .planning import planning
from .popular import popular
from .random_anime import random_anime
from .recent import recent
from .repeating import repeating
from .scores import scores
from .search import search
from .trending import trending
from .upcoming import upcoming
from .watchlist import watch_list

commands = {
    "trending": trending,
    "recent": recent,
    "search": search,
    "upcoming": upcoming,
    "scores": scores,
    "popular": popular,
    "favourites": favourites,
    "random": random_anime,
    "loggin": loggin,
    "watching": watch_list,
    "paused": paused,
    "repeating": repeating,
    "dropped": dropped,
    "completed": completed,
    "planning": planning,
}


@click.group(
    commands=commands,
    invoke_without_command=True,
    help="A beautiful interface that gives you access to a commplete streaming experience",
    short_help="Access all streaming options",
)
@click.pass_context
def anilist(ctx: click.Context):
    if user := ctx.obj.user:
        AniList.update_login_info(user, user["token"])
    if ctx.invoked_subcommand is None:
        anilist_config = QueryDict()
        anilist_interface(ctx.obj, anilist_config)
