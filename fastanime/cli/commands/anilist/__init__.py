import click

from ...utils.tools import FastAnimeRuntimeState
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
    "stats": "stats.stats",
}


@click.group(
    lazy_subcommands=commands,
    cls=LazyGroup,
    invoke_without_command=True,
    help="A beautiful interface that gives you access to a commplete streaming experience",
    short_help="Access all streaming options",
    epilog="""
\b
\b\bExamples:
  # ---- search ----  
\b
  # get anime with the tag of isekai
  fastanime anilist search -T isekai
\b
  # get anime of 2024 and sort by popularity
  # that has already finished airing or is releasing
  # and is not in your anime lists
  fastanime anilist search -y 2024 -s POPULARITY_DESC --status RELEASING --status FINISHED --not-on-list
\b
  # get anime of 2024 season WINTER
  fastanime anilist search -y 2024 --season WINTER
\b
  # get anime genre action and tag isekai,magic
  fastanime anilist search -g Action -T Isekai -T Magic
\b
  # get anime of 2024 thats finished airing
  fastanime anilist search -y 2024 -S FINISHED
\b
  # get the most favourite anime movies
  fastanime anilist search -f MOVIE -s FAVOURITES_DESC
\b
  # ---- login ----
\b
  # To sign in just run 
  fastanime anilist login
\b
  # To view your login status 
  fastanime anilist login --status
\b
  # To erase login data
  fastanime anilist login --erase
\b
  # ---- notifier ----  
\b
  # basic form
  fastanime anilist notifier
\b
  # with logging to stdout
  fastanime --log anilist notifier
\b
  # with logging to a file. stored in the same place as your config
  fastanime --log-file anilist notifier
""",
)
@click.pass_context
def anilist(ctx: click.Context):
    from typing import TYPE_CHECKING

    from ....anilist import AniList
    from ....AnimeProvider import AnimeProvider
    from ...interfaces.anilist_interfaces import (
        fastanime_main_menu as anilist_interface,
    )

    if TYPE_CHECKING:
        from ...config import Config
    config: Config = ctx.obj
    config.anime_provider = AnimeProvider(config.provider)
    if user := ctx.obj.user:
        AniList.update_login_info(user, user["token"])
    if ctx.invoked_subcommand is None:
        fastanime_runtime_state = FastAnimeRuntimeState()
        anilist_interface(ctx.obj, fastanime_runtime_state)
