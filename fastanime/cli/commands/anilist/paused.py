from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from ...config import Config


@click.command(help="View anime you paused on watching")
@click.pass_obj
def paused(config: "Config"):
    from ....anilist import AniList
    from ...interfaces import anilist_interfaces
    from ...utils.tools import FastAnimeRuntimeState, exit_app

    if not config.user:
        print("Not authenticated")
        print("Please run: fastanime anilist loggin")
        exit_app()
    anime_list = AniList.get_anime_list("PAUSED")
    if not anime_list:
        return
    if not anime_list[0] or not anime_list[1]:
        return
    media = [
        mediaListItem["media"]
        for mediaListItem in anime_list[1]["data"]["Page"]["mediaList"]
    ]  # pyright:ignore
    anime_list[1]["data"]["Page"]["media"] = media  # pyright:ignore
    anilist_config = FastAnimeRuntimeState()
    anilist_config.data = anime_list[1]
    anilist_interfaces.anilist_results_menu(config, anilist_config)
