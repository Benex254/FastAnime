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
    "download": "download.download",
    "downloads": "downloads.downloads",
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
@click.option("--resume", is_flag=True, help="Resume from the last session")
@click.pass_context
def anilist(ctx: click.Context, resume: bool):
    from typing import TYPE_CHECKING

    from ....anilist import AniList
    from ....AnimeProvider import AnimeProvider

    if TYPE_CHECKING:
        from ...config import Config
    config: Config = ctx.obj
    config.anime_provider = AnimeProvider(config.provider)
    if user := ctx.obj.user:
        AniList.update_login_info(user, user["token"])
    if ctx.invoked_subcommand is None:
        fastanime_runtime_state = FastAnimeRuntimeState()
        if resume:
            from ...interfaces.anilist_interfaces import (
                anime_provider_search_results_menu,
            )

            if not config.user_data["recent_anime"]:
                click.echo("No recent anime found", err=True, color=True)
                return
            fastanime_runtime_state.anilist_results_data = {
                "data": {"Page": {"media": config.user_data["recent_anime"]}}
            }

            fastanime_runtime_state.selected_anime_anilist = config.user_data[
                "recent_anime"
            ][0]
            fastanime_runtime_state.selected_anime_id_anilist = config.user_data[
                "recent_anime"
            ][0]["id"]
            fastanime_runtime_state.selected_anime_title_anilist = (
                config.user_data["recent_anime"][0]["title"]["romaji"]
                or config.user_data["recent_anime"][0]["title"]["english"]
            )
            anime_provider_search_results_menu(config, fastanime_runtime_state)

        else:
            from ...interfaces.anilist_interfaces import (
                fastanime_main_menu as anilist_interface,
            )

            anilist_interface(ctx.obj, fastanime_runtime_state)
