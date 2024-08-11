import click


@click.command(
    help="Fetch the 15 most scored anime", short_help="View most scored anime"
)
@click.pass_obj
def scores(config):
    from ....anilist import AniList
    from ...interfaces.anilist_interfaces import anilist_results_menu
    from ...utils.tools import FastAnimeRuntimeState

    anime_data = AniList.get_most_scored()
    if anime_data[0]:
        fastanime_runtime_state = FastAnimeRuntimeState()
        fastanime_runtime_state.data = anime_data[1]
        anilist_results_menu(config, fastanime_runtime_state)
