import click


@click.command(
    help="Get random anime from anilist based on a range of anilist anime ids that are seected at random",
    short_help="View random anime",
)
@click.option(
    "--dump-json",
    "-d",
    is_flag=True,
    help="Only print out the results dont open anilist menu",
)
@click.pass_obj
def random_anime(config, dump_json):
    import random

    from ....anilist import AniList

    random_anime = range(1, 100000)

    random_anime = random.sample(random_anime, k=50)

    anime_data = AniList.search(id_in=list(random_anime))

    if anime_data[0]:
        if dump_json:
            import json

            print(json.dumps(anime_data[1]))
        else:
            from ...interfaces.anilist_interfaces import anilist_results_menu
            from ...utils.tools import FastAnimeRuntimeState

            fastanime_runtime_state = FastAnimeRuntimeState()
            fastanime_runtime_state.anilist_results_data = anime_data[1]
            anilist_results_menu(config, fastanime_runtime_state)
    else:
        exit(1)
