from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from ...config import Config


@click.command(help="View anime you paused on watching")
@click.option(
    "--dump-json",
    "-d",
    is_flag=True,
    help="Only print out the results dont open anilist menu",
)
@click.pass_obj
def paused(config: "Config", dump_json):
    from sys import exit

    from ....anilist import AniList

    if not config.user:
        print("Not authenticated")
        print("Please run: fastanime anilist loggin")
        exit(1)
    anime_list = AniList.get_anime_list("PAUSED")
    if not anime_list:
        exit(1)
    if not anime_list[0] or not anime_list[1]:
        exit(1)
    media = [
        mediaListItem["media"]
        for mediaListItem in anime_list[1]["data"]["Page"]["mediaList"]
    ]  # pyright:ignore
    anime_list[1]["data"]["Page"]["media"] = media  # pyright:ignore
    if dump_json:
        import json

        print(json.dumps(anime_list[1]))
    else:
        from ...interfaces import anilist_interfaces
        from ...utils.tools import FastAnimeRuntimeState

        anilist_config = FastAnimeRuntimeState()
        anilist_config.anilist_results_data = anime_list[1]
        anilist_interfaces.anilist_results_menu(config, anilist_config)
