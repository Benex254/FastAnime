import click


@click.command(
    help="Fetch the 15 most anticipited anime", short_help="View upcoming anime"
)
@click.pass_obj
def upcoming(config):
    from ....anilist import AniList
    from ...interfaces.anilist_interfaces import anilist_results_menu
    from ...utils.tools import FastAnimeRuntimeState

    success, data = AniList.get_upcoming_anime()
    if success:
        fastanime_runtime_state = FastAnimeRuntimeState()
        fastanime_runtime_state.anilist_data = data
        anilist_results_menu(config, fastanime_runtime_state)
