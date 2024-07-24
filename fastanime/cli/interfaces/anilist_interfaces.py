from __future__ import annotations

import os
import random

from rich import print
from rich.prompt import Prompt

from ... import USER_CONFIG_PATH
from ...libs.anilist.anilist import AniList
from ...libs.anilist.anilist_data_schema import AnilistBaseMediaDataSchema
from ...libs.anime_provider.allanime.api import anime_provider
from ...libs.anime_provider.types import Anime, SearchResult, Server
from ...libs.fzf import fzf
from ...Utility.data import anime_normalizer
from ...Utility.utils import anime_title_percentage_match, sanitize_filename
from ..config import Config
from ..utils.mpv import mpv
from ..utils.tools import QueryDict, exit_app
from ..utils.utils import clear, fuzzy_inquirer


def player_controls(config: Config, anilist_config: QueryDict):
    # user config
    translation_type: str = config.translation_type.lower()

    # internal config
    anime: Anime = anilist_config.anime
    current_episode: str = anilist_config.episode_number
    episodes: list = sorted(anilist_config.episodes, key=float)
    links: list = anilist_config.current_stream_links
    current_link: str = anilist_config.current_stream_link
    anime_title: str = anilist_config.anime_title
    anime_id: int = anilist_config.anime_id

    def _servers():
        config.server = ""

        fetch_streams(config, anilist_config)

    def _replay():
        selected_server: Server = anilist_config.current_server
        print(
            "[bold magenta]Now Replaying:[/]",
            anime_title,
            "[bold magenta] Episode: [/]",
            current_episode,
        )

        mpv(current_link, selected_server["episode_title"])
        clear()
        player_controls(config, anilist_config)

    def _next_episode():
        next_episode = episodes.index(current_episode) + 1
        if next_episode >= len(episodes):
            next_episode = len(episodes) - 1
        episode = anime_provider.get_anime_episode(
            anime["id"], episodes[next_episode], translation_type
        )
        if not episode:
            print(
                "Sth went wrong :cry: this could mean the provider is down or your internet"
            )
            input("Enter to continue...")
            _next_episode()
            return

        # update internal config
        anilist_config.episode = episode
        anilist_config.episode_number = episodes[next_episode]

        # update user config
        config.update_watch_history(anime_id, episodes[next_episode])

        # call interface
        fetch_streams(config, anilist_config)

    def _episodes():
        # reset watch_history
        config.update_watch_history(anime_id, None)

        # call interface
        fetch_episode(config, anilist_config)

    def _previous_episode():
        prev_episode = episodes.index(current_episode) - 1
        if prev_episode <= 0:
            prev_episode = 0
        episode = anime_provider.get_anime_episode(
            anime["id"], episodes[prev_episode], config.translation_type.lower()
        )
        if not episode:
            print(
                "Sth went wrong :cry: this could mean the provider is down or your internet"
            )
            input("Enter to continue...")
            _previous_episode()
            return

        # update internal config
        anilist_config.episode = episode
        # anilist_config.episode_title = episode["title"]
        anilist_config.episode_number = episodes[prev_episode]

        # update user config
        config.update_watch_history(anime_id, episodes[prev_episode])

        # call interface
        fetch_streams(config, anilist_config)

    def _change_quality():
        # extract the actual link urls
        options = [link["link"] for link in links]

        # prompt for new quality
        if config.use_fzf:
            quality = fzf.run(
                options, prompt="Select Quality:", header="Quality Options"
            )
        else:
            quality = fuzzy_inquirer("Select Quality", options)
        config.quality = options.index(quality)  # set quality
        player_controls(config, anilist_config)

    def _change_translation_type():
        # prompt for new translation type
        options = ["sub", "dub"]
        if config.use_fzf:
            translation_type = fzf.run(
                options, prompt="Select Translation Type: ", header="Lang Options"
            ).lower()
        else:
            translation_type = fuzzy_inquirer(
                "Select Translation Type", options
            ).lower()

        # update internal config
        config.translation_type = translation_type.lower()

        # reload to controls
        player_controls(config, anilist_config)

    options = {
        "Replay": _replay,
        "Next Episode": _next_episode,
        "Previous Episode": _previous_episode,
        "Episodes": _episodes,
        "Change Quality": _change_quality,
        "Change Translation Type": _change_translation_type,
        "Servers": _servers,
        "Main Menu": lambda: anilist(config, anilist_config),
        "Anime Options Menu": lambda: anilist_options(config, anilist_config),
        "Search Results": lambda: select_anime(config, anilist_config),
        "Exit": exit_app,
    }

    if config.auto_next:
        _next_episode()
        return
    if config.use_fzf:
        action = fzf.run(
            list(options.keys()), prompt="Select Action:", header="Player Controls"
        )
    else:
        action = fuzzy_inquirer("Select Action", options.keys())
    options[action]()


def fetch_streams(config: Config, anilist_config: QueryDict):
    # user config
    quality: int = config.quality

    # internal config
    episode_number: str = anilist_config.episode_number
    anime_title: str = anilist_config.anime_title
    anime_id: int = anilist_config.anime_id
    anime: Anime = anilist_config.anime
    translation_type = config.translation_type

    # get streams for episode from provider
    episode_streams = anime_provider.get_episode_streams(
        anime, episode_number, translation_type
    )
    if not episode_streams:
        print("Failed to fetch :cry:")
        input("Enter to retry...")
        return fetch_streams(config, anilist_config)

    episode_streams = {
        episode_stream["server"]: episode_stream for episode_stream in episode_streams
    }

    # prompt for preferred server
    server = None
    if config.server and config.server in episode_streams.keys():
        server = config.server
    if config.server == "top":
        server = list(episode_streams.keys())[0]
    if not server:
        choices = [*episode_streams.keys(), "Back"]
        if config.use_fzf:
            server = fzf.run(
                choices,
                prompt="Select Server: ",
                header="Servers",
            )
        else:
            server = fuzzy_inquirer("Select Server", choices)
    if server == "Back":
        # reset watch_history
        config.update_watch_history(anime_id, None)

        fetch_episode(config, anilist_config)
        return
    selected_server = episode_streams[server]

    links = selected_server["links"]
    if quality > len(links) - 1:
        quality = config.quality = len(links) - 1
    elif quality < 0:
        quality = config.quality = 0
    stream_link = links[quality]["link"]

    # update internal config
    anilist_config.current_stream_links = links
    anilist_config.current_stream_link = stream_link
    anilist_config.current_server = selected_server
    anilist_config.current_server_name = server

    # play video
    print(
        "[bold magenta]Now playing:[/]",
        anime_title,
        "[bold magenta] Episode: [/]",
        episode_number,
    )

    mpv(stream_link, selected_server["episode_title"])

    # update_watch_history
    config.update_watch_history(anime_id, str(int(episode_number) + 1))

    # switch to controls
    clear()

    player_controls(config, anilist_config)


def fetch_episode(config: Config, anilist_config: QueryDict):
    # user config
    translation_type: str = config.translation_type.lower()
    continue_from_history: bool = config.continue_from_history
    user_watch_history: dict = config.watch_history
    anime_id: int = anilist_config.anime_id
    anime_title: str = anilist_config.anime_title

    # internal config
    anime: Anime = anilist_config.anime
    _anime: SearchResult = anilist_config._anime

    # prompt for episode number
    episodes = anime["availableEpisodesDetail"][translation_type]
    if continue_from_history and user_watch_history.get(str(anime_id)) in episodes:
        episode_number = user_watch_history[str(anime_id)]
        print(f"[bold cyan]Continuing from Episode:[/] [bold]{episode_number}[/]")
    else:
        choices = [*episodes, "Back"]
        if config.use_fzf:
            episode_number = fzf.run(
                choices,
                prompt="Select Episode:",
                header=anime_title,
            )
        else:
            episode_number = fuzzy_inquirer("Select Episode", choices)

    if episode_number == "Back":
        anilist_options(config, anilist_config)
        return
    config.update_watch_history(anime_id, episode_number)

    # get the episode info from provider
    episode = anime_provider.get_anime_episode(
        _anime["id"], episode_number, translation_type
    )

    if not episode:

        print(
            "Sth went wrong :cry: this could mean the provider is down or your internet"
        )
        input("Enter to continue...")
        fetch_episode(config, anilist_config)
        return
    # update internal config
    anilist_config.episodes = episodes
    anilist_config.episode = episode
    # anilist_config.episode_title = episode["title"]
    anilist_config.episode_number = episode_number

    # next interface
    fetch_streams(config, anilist_config)


def fetch_anime_episode(config, anilist_config: QueryDict):
    selected_anime: SearchResult = anilist_config._anime
    anilist_config.anime = anime_provider.get_anime(selected_anime["id"])
    if not anilist_config.anime:

        print(
            "Sth went wrong :cry: this could mean the provider is down or your internet"
        )
        input("Enter to continue...")
        fetch_anime_episode(config, anilist_config)
        return

    fetch_episode(config, anilist_config)


def provide_anime(config: Config, anilist_config: QueryDict):
    # user config
    translation_type = config.translation_type.lower()

    # internal config
    selected_anime_title = anilist_config.selected_anime_title

    anime_data: AnilistBaseMediaDataSchema = anilist_config.selected_anime_anilist

    # search and get the requested title from provider
    search_results = anime_provider.search_for_anime(
        selected_anime_title, translation_type
    )
    if not search_results:
        print(
            "Sth went wrong :cry: while fetching this could mean you have poor internet connection or the provider is down"
        )
        input("Enter to continue...")
        provide_anime(config, anilist_config)
        return

    search_results = {anime["title"]: anime for anime in search_results["results"]}
    _title = None
    if _title := next(
        (
            original
            for original, normalized in anime_normalizer.items()
            if normalized.lower() == selected_anime_title.lower()
        ),
        None,
    ):
        _title = _title

    if config.auto_select:
        anime_title = max(
            search_results.keys(),
            key=lambda title: anime_title_percentage_match(title, anime_data),
        )
        print(f"[cyan]Auto selecting[/]: {anime_title}")
    else:
        choices = [*search_results.keys(), "Back"]
        if config.use_fzf:
            anime_title = fzf.run(
                choices,
                prompt="Select Search Result:",
                header="Anime Search Results",
            )

        else:
            anime_title = fuzzy_inquirer("Select Search Result", choices)
        if anime_title == "Back":
            anilist_options(config, anilist_config)
            return
    anilist_config.anime_title = anime_normalizer.get(anime_title) or anime_title
    anilist_config._anime = search_results[anime_title]
    fetch_anime_episode(config, anilist_config)


def anilist_options(config, anilist_config: QueryDict):
    selected_anime: AnilistBaseMediaDataSchema = anilist_config.selected_anime_anilist
    selected_anime_title: str = anilist_config.selected_anime_title

    def _watch_trailer(config: Config, anilist_config: QueryDict):
        if trailer := selected_anime.get("trailer"):
            trailer_url = "https://youtube.com/watch?v=" + trailer["id"]
            print("[bold magenta]Watching Trailer of:[/]", selected_anime_title)
            mpv(trailer_url, selected_anime_title)
            anilist_options(config, anilist_config)

    def _add_to_list(config: Config, anilist_config: QueryDict):
        config.update_anime_list(anilist_config.anime_id)
        anilist_options(config, anilist_config)

    def _remove_from_list(config: Config, anilist_config: QueryDict):
        config.update_anime_list(anilist_config.anime_id, True)
        anilist_options(config, anilist_config)

    def _change_translation_type(config: Config, anilist_config: QueryDict):
        # prompt for new translation type
        options = ["Sub", "Dub"]
        if config.use_fzf:
            translation_type = fzf.run(
                options, prompt="Select Translation Type:", header="Language Options"
            )
        else:
            translation_type = fuzzy_inquirer("Select translation type", options)

        # update internal config
        config.translation_type = translation_type.lower()

        anilist_options(config, anilist_config)

    def _view_info(config, anilist_config):
        from rich.console import Console
        from rich.prompt import Confirm

        from ...Utility import anilist_data_helper
        from ...Utility.utils import remove_html_tags
        from ..utils.print_img import print_img

        clear()
        console = Console()

        print_img(selected_anime["coverImage"]["large"])
        console.print("[bold cyan]Title(jp): ", selected_anime["title"]["romaji"])
        console.print("[bold cyan]Title(eng): ", selected_anime["title"]["english"])
        console.print("[bold cyan]Popularity: ", selected_anime["popularity"])
        console.print("[bold cyan]Favourites: ", selected_anime["favourites"])
        console.print("[bold cyan]Status: ", selected_anime["status"])
        console.print(
            "[bold cyan]Start Date: ",
            anilist_data_helper.format_anilist_date_object(selected_anime["startDate"]),
        )
        console.print(
            "[bold cyan]End Date: ",
            anilist_data_helper.format_anilist_date_object(selected_anime["endDate"]),
        )
        # console.print("[bold cyan]Season: ", selected_anime["season"])
        console.print("[bold cyan]Episodes: ", selected_anime["episodes"])
        console.print(
            "[bold cyan]Tags: ",
            anilist_data_helper.format_list_data_with_comma(
                [tag["name"] for tag in selected_anime["tags"]]
            ),
        )
        console.print(
            "[bold cyan]Genres: ",
            anilist_data_helper.format_list_data_with_comma(selected_anime["genres"]),
        )
        # console.print("[bold cyan]Type: ", selected_anime["st"])
        if selected_anime["nextAiringEpisode"]:
            console.print(
                "[bold cyan]Next Episode: ",
                anilist_data_helper.extract_next_airing_episode(
                    selected_anime["nextAiringEpisode"]
                ),
            )
        console.print(
            "[bold underline cyan]Description\n[/]",
            remove_html_tags(str(selected_anime["description"])),
        )
        if Confirm.ask("Enter to continue...", default=True):
            anilist_options(config, anilist_config)
        return

    options = {
        "Stream": provide_anime,
        "Watch Trailer": _watch_trailer,
        "Add to List": _add_to_list,
        "Remove from List": _remove_from_list,
        "View Info": _view_info,
        "Change Translation Type": _change_translation_type,
        "Back": select_anime,
        "Exit": exit_app,
    }
    if config.use_fzf:
        action = fzf.run(
            list(options.keys()), prompt="Select Action:", header="Anime Menu"
        )
    else:
        action = fuzzy_inquirer("Select Action", options.keys())
    options[action](config, anilist_config)


def select_anime(config: Config, anilist_config: QueryDict):
    search_results = anilist_config.data["data"]["Page"]["media"]
    anime_data = {
        sanitize_filename(
            str(anime["title"][config.preferred_language] or anime["title"]["romaji"])
        ): anime
        for anime in search_results
    }

    choices = [*anime_data.keys(), "Back"]
    if config.use_fzf:
        if config.preview:
            from .utils import get_preview

            preview = get_preview(search_results, config)
            selected_anime_title = fzf.run(
                choices,
                prompt="Select Anime: ",
                header="Search Results",
                preview=preview,
            )
        else:
            selected_anime_title = fzf.run(
                choices,
                prompt="Select Anime: ",
                header="Search Results",
            )
    else:
        selected_anime_title = fuzzy_inquirer("Select Anime", choices)
    # "bat %s/{}" % SEARCH_RESULTS_CACHE
    if selected_anime_title == "Back":
        anilist(config, anilist_config)
        return

    selected_anime: AnilistBaseMediaDataSchema = anime_data[selected_anime_title]
    anilist_config.selected_anime_anilist = selected_anime
    anilist_config.selected_anime_title = (
        selected_anime["title"]["romaji"] or selected_anime["title"]["english"]
    )
    anilist_config.anime_id = selected_anime["id"]

    anilist_options(config, anilist_config)


def anilist(config: Config, anilist_config: QueryDict):
    def _anilist_search():
        search_term = Prompt.ask("[cyan]Search for[/]")

        return AniList.search(query=search_term)

    def _anilist_random():
        random_anime = range(1, 15000)
        random_anime = random.sample(random_anime, k=50)

        return AniList.search(id_in=list(random_anime))

    def _watch_history():
        watch_history = list(map(int, config.watch_history.keys()))
        return AniList.search(id_in=watch_history, sort="TRENDING_DESC")

    def _anime_list():
        anime_list = config.anime_list
        return AniList.search(id_in=anime_list)

    def edit_config():
        import subprocess

        subprocess.run([os.environ.get("EDITOR", "open"), USER_CONFIG_PATH])
        config.load_config()

        anilist(config, anilist_config)

    options = {
        "Trending": AniList.get_trending,
        "Recently Updated Anime": AniList.get_most_recently_updated,
        "Search": _anilist_search,
        "Watch History": _watch_history,
        "AnimeList": _anime_list,
        "Random Anime": _anilist_random,
        "Most Popular Anime": AniList.get_most_popular,
        "Most Favourite Anime": AniList.get_most_favourite,
        "Most Scored Anime": AniList.get_most_scored,
        "Upcoming Anime": AniList.get_upcoming_anime,
        "Edit Config": edit_config,
        "Exit": exit_app,
    }
    if config.use_fzf:

        action = fzf.run(
            list(options.keys()),
            prompt="Select Action: ",
            header="Anilist Menu",
        )
    else:
        action = fuzzy_inquirer("Select Action", options.keys())
    anilist_data = options[action]()
    if anilist_data[0]:
        anilist_config.data = anilist_data[1]
        select_anime(config, anilist_config)

    else:
        print(anilist_data[1])
        input("Enter to continue...")
        anilist(config, anilist_config)
