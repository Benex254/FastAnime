import click


@click.command(
    help="Fetch the 15 most scored anime", short_help="View most scored anime"
)
@click.option(
    "--dump-json",
    "-d",
    is_flag=True,
    help="Only print out the results dont open anilist menu",
)
@click.pass_obj
def scores(config, dump_json):
    from ....anilist import AniList

    anime_data = AniList.get_most_scored()
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
        from sys import exit

        exit(1)
