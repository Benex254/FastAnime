import click

from ...completion_functions import anime_titles_shell_complete


@click.command(
    help="Search for anime using anilists api and get top ~50 results",
    short_help="Search for anime",
)
@click.option("--title", "-t", shell_complete=anime_titles_shell_complete)
@click.option(
    "--dump-json",
    "-d",
    is_flag=True,
    help="Only print out the results dont open anilist menu",
)
@click.pass_obj
def search(config, title, dump_json):
    from ....anilist import AniList

    success, search_results = AniList.search(title)
    if success:
        if dump_json:
            import json

            print(json.dumps(search_results))
        else:
            from ...interfaces.anilist_interfaces import anilist_results_menu
            from ...utils.tools import FastAnimeRuntimeState

            fastanime_runtime_state = FastAnimeRuntimeState()
            fastanime_runtime_state.anilist_data = search_results
            anilist_results_menu(config, fastanime_runtime_state)
    else:
        from sys import exit

        exit(1)
