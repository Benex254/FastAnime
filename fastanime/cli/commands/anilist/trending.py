import click
from ....libs.anilist.anilist import AniList
from .utils import get_search_result
from ...interfaces.anime_interface import anime_interface


@click.command()
def trending():
    success, trending = AniList.get_trending()
    if trending and success:
        result = get_search_result(trending)
        if result:
            anime_interface(result)
