import click

from ...completion_functions import anime_titles_shell_complete


@click.command(
    help="Search for anime using anilists api and get top ~50 results",
    short_help="Search for anime",
)
@click.argument("title", shell_complete=anime_titles_shell_complete)
@click.pass_obj
def search(config, title):
    from ....anilist import AniList
    from ...interfaces.anilist_interfaces import anilist_results_menu
    from ...utils.tools import FastAnimeRuntimeState

    success, search_results = AniList.search(title)
    if success:
        fastanime_runtime_state = FastAnimeRuntimeState()
        fastanime_runtime_state.anilist_data = search_results
        anilist_results_menu(config, fastanime_runtime_state)
