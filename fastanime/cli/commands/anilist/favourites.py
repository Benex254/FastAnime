import click


@click.command(
    help="Fetch the top 15 most favourited anime from anilist",
    short_help="View most favourited anime",
)
@click.pass_obj
def favourites(config):
    from ....anilist import AniList
    from ...interfaces.anilist_interfaces import anilist_results_menu
    from ...utils.tools import FastAnimeRuntimeState

    anime_data = AniList.get_most_favourite()
    if anime_data[0]:
        fastanime_runtime_state = FastAnimeRuntimeState()
        fastanime_runtime_state.anilist_data = anime_data[1]
        anilist_results_menu(config, fastanime_runtime_state)
