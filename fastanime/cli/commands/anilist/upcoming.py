import click


@click.command(
    help="Fetch the 15 most anticipited anime", short_help="View upcoming anime"
)
@click.option(
    "--dump-json",
    "-d",
    is_flag=True,
    help="Only print out the results dont open anilist menu",
)
@click.pass_obj
def upcoming(config, dump_json):
    from ....anilist import AniList

    success, data = AniList.get_upcoming_anime()
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
