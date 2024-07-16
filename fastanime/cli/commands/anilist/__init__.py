import click

from ...interfaces.anilist_interfaces import anilist as anilist_interface
from ...utils.tools import QueryDict
from .favourites import favourites
from .popular import popular
from .recent import recent
from .scores import scores
from .search import search
from .trending import trending
from .upcoming import upcoming

commands = {
    "trending": trending,
    "recent": recent,
    "search": search,
    "upcoming": upcoming,
    "scores": scores,
    "popular": popular,
    "favourites": favourites,
}


@click.group(
    commands=commands,
    invoke_without_command=True,
    help="A beautiful interface that gives you access to a commplete streaming experience",
    short_help="Access all streaming options",
)
@click.pass_context
def anilist(ctx: click.Context):
    if ctx.invoked_subcommand is None:
        anilist_config = QueryDict()
        anilist_interface(ctx.obj, anilist_config)
