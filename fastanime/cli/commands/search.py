import click
from rich import print
from thefuzz import fuzz

from ...cli.config import Config
from ...libs.anime_provider.allanime.api import anime_provider
from ...libs.anime_provider.types import Anime
from ...libs.fzf import fzf
from ..utils.mpv import mpv
from ..utils.tools import exit_app
from ..utils.utils import clear


@click.command(
    help="This subcommand directly interacts with the provider to enable basic streaming. Useful for binging anime.",
    short_help="Binge anime",
)
@click.option(
    "--episode-range",
    "-r",
    help="A range of episodes to binge",
)
@click.argument("anime_title", required=True, type=str)
@click.pass_obj
def search(config: Config, anime_title: str, episode_range: str):
    search_results = anime_provider.search_for_anime(
        anime_title, config.translation_type
    )
    search_results = search_results["results"]
    if not search_results:
        print("Anime not found :cry:")
        exit_app()
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

    anime: Anime | None = anime_provider.get_anime(search_results_[search_result]["id"])
    if not anime:
        print("Sth went wring anime no found")
        input("Enter to continue...")
        search(config, anime_title, episode_range)
        return
    episode_range_ = None
    episodes = anime["availableEpisodesDetail"][config.translation_type]
    if episode_range:
        episodes_start, episodes_end = episode_range.split("-")
        if episodes_start and episodes_end:
            episode_range_ = iter(
                range(round(float(episodes_start)), round(float(episodes_end)) + 1)
            )
        else:
            episode_range_ = iter(sorted(episodes, key=float))

    def stream_anime():
        clear()
        episode = None

        if episode_range_:
            try:
                episode = str(next(episode_range_))
                print(
                    f"[cyan]Auto selecting:[/] {search_result} [cyan]Episode:[/] {episode}"
                )
            except StopIteration:
                print("[green]Completed binge sequence[/]:smile:")

        if not episode or episode not in episodes:
            episode = fzf.run(episodes, "Select an episode: ", header=search_result)
        streams = anime_provider.get_episode_streams(
            anime, episode, config.translation_type
        )
        if not streams:
            print("Failed to get streams")
            return
        links = [link["link"] for server in streams for link in server["links"]]

        # TODO: Come up with way to know quality and better server interface
        link = links[config.quality]
        # link = fzf.run(links, "Select stream", "Streams")

        mpv(link, search_result)
        stream_anime()

    stream_anime()
