import click


@click.command(
    help="Fetch the top 15 anime that are currently trending",
    short_help="Trending anime 🔥🔥🔥",
)
@click.pass_obj
def trending(config):
    from ....anilist import AniList
    from ...interfaces.anilist_interfaces import anilist_results_menu
    from ...utils.tools import FastAnimeRuntimeState

    success, data = AniList.get_trending()
    if success:
        fastanime_runtime_state = FastAnimeRuntimeState()
        fastanime_runtime_state.anilist_data = data
        anilist_results_menu(config, fastanime_runtime_state)
