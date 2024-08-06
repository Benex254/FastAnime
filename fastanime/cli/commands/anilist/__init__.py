import click

from ...utils.tools import QueryDict
from .__lazyloader__ import LazyGroup

commands = {
    "trending": "trending.trending",
    "recent": "recent.recent",
    "search": "search.search",
    "upcoming": "upcoming.upcoming",
    "scores": "scores.scores",
    "popular": "popular.popular",
    "favourites": "favourites.favourites",
    "random": "random_anime.random_anime",
    "login": "login.login",
    "watching": "watching.watching",
    "paused": "paused.paused",
    "rewatching": "rewatching.rewatching",
    "dropped": "dropped.dropped",
    "completed": "completed.completed",
    "planning": "planning.planning",
    "notifier": "notifier.notifier",
}


@click.group(
    lazy_subcommands=commands,
    cls=LazyGroup,
    invoke_without_command=True,
    help="A beautiful interface that gives you access to a commplete streaming experience",
    short_help="Access all streaming options",
)
@click.pass_context
def anilist(ctx: click.Context):
    from typing import TYPE_CHECKING

    from ....anilist import AniList
    from ....AnimeProvider import AnimeProvider
    from ...interfaces.anilist_interfaces import anilist as anilist_interface

    if TYPE_CHECKING:
        from ...config import Config
    config: Config = ctx.obj
    config.anime_provider = AnimeProvider(config.provider)
    if user := ctx.obj.user:
        AniList.update_login_info(user, user["token"])
    if ctx.invoked_subcommand is None:
        anilist_config = QueryDict()
        anilist_interface(ctx.obj, anilist_config)
