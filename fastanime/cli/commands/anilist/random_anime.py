import click


@click.command(
    help="Get random anime from anilist based on a range of anilist anime ids that are seected at random",
    short_help="View random anime",
)
@click.pass_obj
def random_anime(config):
    import random

    from ....anilist import AniList
    from ...interfaces.anilist_interfaces import anilist_results_menu
    from ...utils.tools import FastAnimeRuntimeState

    random_anime = range(1, 15000)

    random_anime = random.sample(random_anime, k=50)

    anime_data = AniList.search(id_in=list(random_anime))

    if anime_data[0]:
        fastanime_runtime_state = FastAnimeRuntimeState()
        fastanime_runtime_state.anilist_data = anime_data[1]
        anilist_results_menu(config, fastanime_runtime_state)
    else:
        print(anime_data[1])
