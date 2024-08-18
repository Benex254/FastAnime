import time
from typing import TYPE_CHECKING

import click

from ..completion_functions import anime_titles_shell_complete

if TYPE_CHECKING:
    from ..config import Config


@click.command(
    help="Download anime using the anime provider for a specified range",
    short_help="Download anime",
)
@click.option(
    "--anime-titles",
    "--anime_title",
    "-t",
    required=True,
    shell_complete=anime_titles_shell_complete,
    multiple=True,
    help="Specify which anime to download",
)
@click.option(
    "--episode-range",
    "-r",
    help="A range of episodes to download (start-end)",
)
@click.option(
    "--force-unknown-ext",
    "-f",
    help="This option forces yt-dlp to download extensions its not aware of",
    is_flag=True,
)
@click.option(
    "--silent/--no-silent",
    "-q/-V",
    type=bool,
    help="Download silently (during download)",
    default=True,
)
@click.option("--verbose", "-v", is_flag=True, help="Download verbosely (everywhere)")
@click.pass_obj
def download(
    config: "Config",
    anime_titles: list,
    episode_range,
    force_unknown_ext,
    silent,
    verbose,
):
    from rich import print
    from rich.progress import Progress
    from thefuzz import fuzz

    from ...AnimeProvider import AnimeProvider
    from ...libs.anime_provider.types import Anime
    from ...libs.fzf import fzf
    from ...Utility.downloader.downloader import downloader
    from ..utils.tools import exit_app
    from ..utils.utils import filter_by_quality, fuzzy_inquirer

    anime_provider = AnimeProvider(config.provider)

    translation_type = config.translation_type
    download_dir = config.downloads_dir

    print(f"[green bold]Queued:[/] {anime_titles}")
    for anime_title in anime_titles:
        print(f"[green bold]Now Downloading: [/] {anime_title}")
        # ---- search for anime ----
        with Progress() as progress:
            progress.add_task("Fetching Search Results...", total=None)
            search_results = anime_provider.search_for_anime(
                anime_title, translation_type=translation_type
            )
        if not search_results:
            print("Search results failed")
            input("Enter to retry")
            download(
                config, anime_title, episode_range, force_unknown_ext, silent, verbose
            )
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
                search_result = fuzzy_inquirer(
                    choices,
                    "Please Select title",
                )

        # ---- fetch anime ----
        with Progress() as progress:
            progress.add_task("Fetching Anime...", total=None)
            anime: Anime | None = anime_provider.get_anime(
                search_results_[search_result]["id"]
            )
        if not anime:
            print("Sth went wring anime no found")
            input("Enter to continue...")
            download(
                config, anime_title, episode_range, force_unknown_ext, silent, verbose
            )
            return

        episodes = sorted(
            anime["availableEpisodesDetail"][config.translation_type], key=float
        )
        # where the magic happens
        if episode_range:
            if ":" in episode_range:
                ep_range_tuple = episode_range.split(":")
                if len(ep_range_tuple) == 2 and all(ep_range_tuple):
                    episodes_start, episodes_end = ep_range_tuple
                    episodes_range = episodes[int(episodes_start) : int(episodes_end)]
                elif len(ep_range_tuple) == 3 and all(ep_range_tuple):
                    episodes_start, episodes_end, step = ep_range_tuple
                    episodes_range = episodes[
                        int(episodes_start) : int(episodes_end) : int(step)
                    ]
                else:
                    episodes_start, episodes_end = ep_range_tuple
                    if episodes_start.strip():
                        episodes_range = episodes[int(episodes_start) :]
                    elif episodes_end.strip():
                        episodes_range = episodes[: int(episodes_end)]
                    else:
                        episodes_range = episodes
            else:
                episodes_range = episodes[int(episode_range) :]
            print(f"[green bold]Downloading: [/] {episodes_range}")

        else:
            episodes_range = sorted(episodes, key=float)

        # lets download em
        for episode in episodes_range:
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
                # ---- fetch servers ----
                if config.server == "top":
                    with Progress() as progress:
                        progress.add_task("Fetching top server...", total=None)
                        server = next(streams, None)
                        if not server:
                            print("Sth went wrong when fetching the server")
                            continue
                    stream_link = filter_by_quality(config.quality, server["links"])
                    if not stream_link:
                        print("[yellow bold]WARNING:[/] No streams found")
                        time.sleep(1)
                        print("Continuing...")
                        continue
                    link = stream_link["link"]
                    provider_headers = server["headers"]
                    episode_title = server["episode_title"]
                else:
                    with Progress() as progress:
                        progress.add_task("Fetching servers", total=None)
                        # prompt for server selection
                        servers = {server["server"]: server for server in streams}
                    servers_names = list(servers.keys())
                    if config.server in servers_names:
                        server = config.server
                    else:
                        if config.use_fzf:
                            server = fzf.run(servers_names, "Select an link: ")
                        else:
                            server = fuzzy_inquirer(
                                servers_names,
                                "Select link",
                            )
                    stream_link = filter_by_quality(
                        config.quality, servers[server]["links"]
                    )
                    if not stream_link:
                        print("[yellow bold]WARNING:[/] No streams found")
                        time.sleep(1)
                        print("Continuing...")
                        continue
                    link = stream_link["link"]
                    provider_headers = servers[server]["headers"]

                    episode_title = servers[server]["episode_title"]
                print(f"[purple]Now Downloading:[/] {search_result} Episode {episode}")

                downloader._download_file(
                    link,
                    anime["title"],
                    episode_title,
                    download_dir,
                    silent,
                    config.format,
                    force_unknown_ext,
                    verbose,
                    headers=provider_headers,
                )
            except Exception as e:
                print(e)
                time.sleep(1)
                print("Continuing...")
    print("Done Downloading")
    exit_app()
