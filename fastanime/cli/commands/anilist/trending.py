import click

from ....libs.anilist.anilist import AniList
from .utils import get_search_result


@click.command()
def trending():
    success, trending = AniList.get_trending()
    if trending and success:
        get_search_result(trending)
