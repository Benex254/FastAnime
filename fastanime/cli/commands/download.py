import click
from rich import print
from thefuzz import fuzz

from ...libs.anime_provider.allanime.api import anime_provider
from ...libs.anime_provider.types import Anime
from ...libs.fzf import fzf
from ...Utility.downloader.downloader import downloader
from ..config import Config
from ..utils.tools import exit_app
from ..utils.utils import clear


@click.command(
    help="Download anime using the anime provider for a specified range",
    short_help="Download anime",
)
@click.argument(
    "anime-title",
    required=True,
)
@click.option(
    "--episode-range",
    "-r",
    help="A range of episodes to download",
)
@click.pass_obj
def download(config: Config, anime_title, episode_range):
    translation_type = config.translation_type
    download_dir = config.downloads_dir
    search_results = anime_provider.search_for_anime(
        anime_title, translation_type=translation_type
    )
    search_results = search_results["results"]
    search_results_ = {
        search_result["title"]: search_result for search_result in search_results
    }

    if config.auto_select:
        search_result = max(
            search_results_.keys(), key=lambda title: fuzz.ratio(title, anime_title)
        )
        print("[cyan]Auto selecting:[/] ", search_result)
    else:
        search_result = fzf.run(
            list(search_results_.keys()), "Please Select title: ", "FastAnime"
        )

    anime: Anime | None = anime_provider.get_anime(search_results_[search_result]["id"])
    if not anime:
        print("Sth went wring anime no found")
        input("Enter to continue...")
        download(config, anime_title, episode_range)
        return

    episodes = anime["availableEpisodesDetail"][config.translation_type]
    if episode_range:
        episodes_start, episodes_end = episode_range.split("-")

    else:
        episodes_start, episodes_end = 0, len(episodes)
    for episode in range(round(float(episodes_start)), round(float(episodes_end))):
        try:
            episode = str(episode)
            if episode not in episodes:
                print(f"[cyan]Warning[/]: Episode {episode} not found, skipping")
                continue
            streams = anime_provider.get_episode_streams(
                anime, episode, config.translation_type
            )
            if not streams:
                print("No streams skipping")
                continue

            streams = list(streams)
            links = [
                (link.get("priority", 0), link["link"])
                for server in streams
                for link in server["links"]
            ]
            link = max(links, key=lambda x: x[0])[1]
            downloader._download_file(
                link, download_dir, (anime["title"], streams[0]["episode_title"]), True
            )
        except Exception as e:
            print(e)
            print("Continuing")
            clear()
    print("Done")
    exit_app()
