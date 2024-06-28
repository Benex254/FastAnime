import click

from ....libs.anilist.anilist import AniList
from .utils import get_search_result


@click.command()
@click.option("--title", prompt="Enter anime title")
def search(title):
    success, search_results = AniList.search(title)
    if search_results and success:
        get_search_result(search_results)
