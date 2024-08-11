import click


@click.command(
    help="Fetch the top 15 most popular anime", short_help="View most popular anime"
)
@click.pass_obj
def popular(config):
    from ....anilist import AniList
    from ...interfaces.anilist_interfaces import anilist_results_menu
    from ...utils.tools import FastAnimeRuntimeState

    anime_data = AniList.get_most_popular()
    if anime_data[0]:
        fastanime_runtime_state = FastAnimeRuntimeState()
        fastanime_runtime_state.anilist_data = anime_data[1]
        anilist_results_menu(config, fastanime_runtime_state)
