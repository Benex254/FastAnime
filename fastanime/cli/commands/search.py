import click

from ...cli.config import Config
from ..completion_functions import anime_titles_shell_complete


@click.command(
    help="This subcommand directly interacts with the provider to enable basic streaming. Useful for binging anime.",
    short_help="Binge anime",
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
    help="A range of episodes to binge (start-end)",
)
@click.pass_obj
def search(config: Config, anime_titles: str, episode_range: str):
    from click import clear
    from rich import print
    from rich.progress import Progress
    from thefuzz import fuzz

    from ...AnimeProvider import AnimeProvider
    from ...libs.anime_provider.types import Anime
    from ...libs.fzf import fzf
    from ...libs.rofi import Rofi
    from ..utils.mpv import run_mpv
    from ..utils.tools import exit_app
    from ..utils.utils import filter_by_quality, fuzzy_inquirer

    anime_provider = AnimeProvider(config.provider)

    print(f"[green bold]Streaming:[/] {anime_titles}")
    for anime_title in anime_titles:
        # ---- search for anime ----
        with Progress() as progress:
            progress.add_task("Fetching Search Results...", total=None)
            search_results = anime_provider.search_for_anime(
                anime_title, config.translation_type
            )
        if not search_results:
            print("Search results not found")
            input("Enter to retry")
            search(config, anime_title, episode_range)
            return
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
            choices = list(search_results_.keys())
            if config.use_fzf:
                search_result = fzf.run(choices, "Please Select title: ", "FastAnime")
            elif config.use_rofi:
                search_result = Rofi.run(choices, "Please Select Title")
            else:
                search_result = fuzzy_inquirer(
                    choices,
                    "Please Select Title",
                )

        # ---- fetch selected anime ----
        with Progress() as progress:
            progress.add_task("Fetching Anime...", total=None)
            anime: Anime | None = anime_provider.get_anime(
                search_results_[search_result]["id"]
            )

        if not anime:
            print("Sth went wring anime no found")
            input("Enter to continue...")
            search(config, anime_title, episode_range)
            return
        episodes_range = []
        episodes: list[str] = sorted(
            anime["availableEpisodesDetail"][config.translation_type], key=float
        )
        if episode_range:
            if ":" in episode_range:
                ep_range_tuple = episode_range.split(":")
                if len(ep_range_tuple) == 3 and all(ep_range_tuple):
                    episodes_start, episodes_end, step = ep_range_tuple
                    episodes_range = episodes[
                        int(episodes_start) : int(episodes_end) : int(step)
                    ]

                elif len(ep_range_tuple) == 2 and all(ep_range_tuple):
                    episodes_start, episodes_end = ep_range_tuple
                    episodes_range = episodes[int(episodes_start) : int(episodes_end)]
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

            episodes_range = iter(episodes_range)

        def stream_anime():
            clear()
            episode = None

            if episodes_range:
                try:
                    episode = next(episodes_range)  # pyright:ignore
                    print(
                        f"[cyan]Auto selecting:[/] {search_result} [cyan]Episode:[/] {episode}"
                    )
                except StopIteration:
                    print("[green]Completed binge sequence[/]:smile:")
                    return

            if not episode or episode not in episodes:
                choices = [*episodes, "end"]
                if config.use_fzf:
                    episode = fzf.run(
                        choices, "Select an episode: ", header=search_result
                    )
                elif config.use_rofi:
                    episode = Rofi.run(choices, "Select an episode")
                else:
                    episode = fuzzy_inquirer(
                        choices,
                        "Select episode",
                    )
            if episode == "end":
                return

            # ---- fetch streams ----
            with Progress() as progress:
                progress.add_task("Fetching Episode Streams...", total=None)
                streams = anime_provider.get_episode_streams(
                    anime, episode, config.translation_type
                )
                if not streams:
                    print("Failed to get streams")
                    return

            try:
                # ---- fetch servers ----
                if config.server == "top":
                    with Progress() as progress:
                        progress.add_task("Fetching top server...", total=None)
                        server = next(streams, None)
                        if not server:
                            print("Sth went wrong when fetching the episode")
                            input("Enter to continue")
                            stream_anime()
                            return
                    stream_link = filter_by_quality(config.quality, server["links"])
                    if not stream_link:
                        print("Quality not found")
                        input("Enter to continue")
                        stream_anime()
                        return
                    link = stream_link["link"]
                    stream_headers = server["headers"]
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
                        elif config.use_rofi:
                            server = Rofi.run(servers_names, "Select an link")
                        else:
                            server = fuzzy_inquirer(
                                servers_names,
                                "Select link",
                            )
                    stream_link = filter_by_quality(
                        config.quality, servers[server]["links"]
                    )
                    if not stream_link:
                        print("Quality not found")
                        input("Enter to continue")
                        stream_anime()
                        return
                    link = stream_link["link"]
                    stream_headers = servers[server]["headers"]
                    episode_title = servers[server]["episode_title"]
                print(f"[purple]Now Playing:[/] {search_result} Episode {episode}")

                if config.sync_play:
                    from ..utils.syncplay import SyncPlayer

                    SyncPlayer(link, episode_title, headers=stream_headers)
                else:
                    run_mpv(link, episode_title, headers=stream_headers)
            except IndexError as e:
                print(e)
                input("Enter to continue")
            stream_anime()

        stream_anime()
