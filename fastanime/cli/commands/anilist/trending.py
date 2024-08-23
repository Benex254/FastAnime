import click


@click.command(
    help="Fetch the top 15 anime that are currently trending",
    short_help="Trending anime 🔥🔥🔥",
)
@click.option(
    "--dump-json",
    "-d",
    is_flag=True,
    help="Only print out the results dont open anilist menu",
)
@click.pass_obj
def trending(config, dump_json):
    from ....anilist import AniList

    success, data = AniList.get_trending()
    if success:
        if dump_json:
            import json

            print(json.dumps(data))
        else:
            from ...interfaces.anilist_interfaces import anilist_results_menu
            from ...utils.tools import FastAnimeRuntimeState

            fastanime_runtime_state = FastAnimeRuntimeState()
            fastanime_runtime_state.anilist_results_data = data
            anilist_results_menu(config, fastanime_runtime_state)
    else:
        from sys import exit

        exit(1)
