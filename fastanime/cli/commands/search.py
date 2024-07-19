import click
from fuzzywuzzy import fuzz
from rich import print

from ...cli.config import Config
from ...libs.anime_provider.allanime.api import anime_provider
from ...libs.anime_provider.types import Anime
from ...libs.fzf import fzf
from ..utils.mpv import mpv


@click.command(
    help="This subcommand directly interacts with the provider to enable basic streaming and perhaps automation if required",
    short_help="Directly stream anime with provider",
)
@click.argument("anime_title", required=True, type=str)
@click.pass_obj
def search(
    config: Config,
    anime_title: str,
):
    search_results = anime_provider.search_for_anime(
        anime_title, config.translation_type
    )
    search_results = search_results["results"]
    search_results_ = {
        search_result["title"]: search_result for search_result in search_results
    }
    if config.auto_select:
        search_result = max(
            search_results_.keys(), key=lambda title: fuzz.ratio(title, anime_title)
        )
        print("[cyan]Auto Selecting:[/] ", search_result)

    else:
        search_result = fzf.run(
            list(search_results_.keys()), "Please Select title: ", "FastAnime"
        )

    anime: Anime = anime_provider.get_anime(search_results_[search_result]["id"])

    def stream_anime():
        episodes = anime["availableEpisodesDetail"][config.translation_type]

        episode = fzf.run(episodes, "Select an episode: ", header=search_result)
        streams = anime_provider.get_episode_streams(
            anime, episode, config.translation_type
        )
        if not streams:
            print("Failed to get streams")
            return
        links = [link["link"] for server in streams for link in server["links"]]
        link = fzf.run(links, "Select stream", "Streams")

        mpv(link, search_result)
        stream_anime()

    stream_anime()
