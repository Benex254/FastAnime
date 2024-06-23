import click

from ....libs.anilist.anilist import AniList
from ...interfaces.anime_interface import anime_interface
from .utils import get_search_result


@click.command()
def trending():
    success, trending = AniList.get_trending()
    if trending and success:
        result = get_search_result(trending)
        if result:
            anime_interface(result)
