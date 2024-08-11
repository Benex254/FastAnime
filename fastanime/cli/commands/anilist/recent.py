import click


@click.command(
    help="Fetch the 15 most recently updated anime from anilist that are currently releasing",
    short_help="View recently updated anime",
)
@click.pass_obj
def recent(config):
    from ....anilist import AniList
    from ...interfaces.anilist_interfaces import anilist_results_menu
    from ...utils.tools import FastAnimeRuntimeState

    anime_data = AniList.get_most_recently_updated()
    if anime_data[0]:
        fastanime_runtime_state = FastAnimeRuntimeState()
        fastanime_runtime_state.anilist_data = anime_data[1]
        anilist_results_menu(config, fastanime_runtime_state)
