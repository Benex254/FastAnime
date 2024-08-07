import click

from ...cli.config import Config


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
    from ..utils.utils import fuzzy_inquirer

    anime_provider = AnimeProvider(config.provider)

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
                "Please Select Title",
                choices,
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
            if config.use_fzf:
                episode = fzf.run(episodes, "Select an episode: ", header=search_result)
            elif config.use_rofi:
                episode = Rofi.run(episodes, "Select an episode")
            else:
                episode = fuzzy_inquirer("Select episode", episodes)

        # ---- fetch streams ----
        with Progress() as progress:
            progress.add_task("Fetching Episode Streams...", total=None)
            streams = anime_provider.get_episode_streams(
                anime, episode, config.translation_type
            )
            if not streams:
                print("Failed to get streams")
                return

        # ---- fetch servers ----
        with Progress() as progress:
            if config.server == "top":
                progress.add_task("Fetching top server...", total=None)
                server = next(streams)
                link = server["links"][config.quality]["link"]
            else:
                progress.add_task("Fetching servers", total=None)
                links = [link["link"] for server in streams for link in server["links"]]
                if config.use_fzf:
                    link = fzf.run(links, "Select an link: ", header=search_result)
                elif config.use_rofi:
                    link = Rofi.run(links, "Select an link")
                else:
                    link = fuzzy_inquirer("Select link", links)

        print(f"[purple]Now Playing:[/] {search_result} Episode {episode}")

        run_mpv(link, search_result)
        stream_anime()

    stream_anime()
