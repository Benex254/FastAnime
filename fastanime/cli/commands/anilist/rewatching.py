from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from ...config import Config


@click.command(help="View anime you are rewatching")
@click.pass_obj
def rewatching(config: "Config"):
    from ....anilist import AniList
    from ...interfaces import anilist_interfaces
    from ...utils.tools import QueryDict, exit_app

    if not config.user:
        print("Not authenticated")
        print("Please run: fastanime anilist loggin")
        exit_app()
    anime_list = AniList.get_anime_list("REPEATING")
    if not anime_list:
        return
    if not anime_list[0] or not anime_list[1]:
        return
    media = [
        mediaListItem["media"]
        for mediaListItem in anime_list[1]["data"]["Page"]["mediaList"]
    ]  # pyright:ignore
    anime_list[1]["data"]["Page"]["media"] = media  # pyright:ignore
    anilist_config = QueryDict()
    anilist_config.data = anime_list[1]
    anilist_interfaces.select_anime(config, anilist_config)
