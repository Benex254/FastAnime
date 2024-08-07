from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from ..config import Config


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
@click.option(
    "--highest_priority",
    "-h",
    help="Choose stream indicated as highest priority",
    is_flag=True,
)
@click.pass_obj
def download(config: "Config", anime_title, episode_range, highest_priority):
    from click import clear
    from rich import print
    from rich.progress import Progress
    from thefuzz import fuzz

    from ...AnimeProvider import AnimeProvider
    from ...libs.anime_provider.types import Anime
    from ...libs.fzf import fzf
    from ...Utility.downloader.downloader import downloader
    from ..utils.tools import exit_app
    from ..utils.utils import fuzzy_inquirer

    anime_provider = AnimeProvider(config.provider)

    translation_type = config.translation_type
    download_dir = config.downloads_dir

    # ---- search for anime ----
    with Progress() as progress:
        progress.add_task("Fetching Search Results...", total=None)
        search_results = anime_provider.search_for_anime(
            anime_title, translation_type=translation_type
        )
    if not search_results:
        print("Search results failed")
        input("Enter to retry")
        download(config, anime_title, episode_range, highest_priority)
        return
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
        choices = list(search_results_.keys())
        if config.use_fzf:
            search_result = fzf.run(choices, "Please Select title: ", "FastAnime")
        else:
            search_result = fuzzy_inquirer("Please Select title", choices)

    # ---- fetch anime ----
    with Progress() as progress:
        progress.add_task("Fetching Anime...", total=None)
        anime: Anime | None = anime_provider.get_anime(
            search_results_[search_result]["id"]
        )
    if not anime:
        print("Sth went wring anime no found")
        input("Enter to continue...")
        download(config, anime_title, episode_range, highest_priority)
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
            with Progress() as progress:
                progress.add_task("Fetching Episode Streams...", total=None)
                streams = anime_provider.get_episode_streams(
                    anime, episode, config.translation_type
                )
                if not streams:
                    print("No streams skipping")
                    continue

            with Progress() as progress:
                if highest_priority:
                    progress.add_task("Fetching highest priority stream", total=None)
                    streams = list(streams)
                    links = [
                        (link.get("priority", 0), link["link"])
                        for server in streams
                        for link in server["links"]
                    ]
                    link = max(links, key=lambda x: x[0])[1]
                    episode_title = streams[0]["episode_title"]
                elif config.server == "top":
                    progress.add_task("Fetching Top Server", total=None)
                    server = next(streams)
                    link = server["links"][config.quality]["link"]
                    episode_title = server["episode_title"]
                else:
                    # TODO: Make this better but no rush whats the point of manual selection
                    progress.add_task("Fetching links", total=None)
                    streams = list(streams)
                    links = [
                        link["link"] for server in streams for link in server["links"]
                    ]
                    episode_title = streams[0]["episode_title"]
                    if config.use_fzf:
                        link = fzf.run(links, "Select link", "Links")
                    else:
                        link = fuzzy_inquirer("Select link", links)

            print(f"[purple]Now Downloading:[/] {search_result} Episode {episode}")

            downloader._download_file(
                link,
                download_dir,
                (anime["title"], episode_title),
                True,
                config.format,
            )
        except Exception as e:
            print(e)
            print("Continuing")
            clear()
    print("Done")
    exit_app()
