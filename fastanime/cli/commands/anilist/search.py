import click

from ....libs.anilist.anilist import AniList
from ...interfaces.anime_interface import anime_interface
from .utils import get_search_result


@click.command()
@click.option("--title", prompt="Enter anime title")
def search(title):
    success, search_results = AniList.search(title)
    if search_results and success:
        result = get_search_result(search_results)
        if result:
            anime_interface(result)
