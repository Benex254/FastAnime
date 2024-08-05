from __future__ import annotations

import os
import shutil
import sys

from rich import print
from rich.prompt import Prompt

from ... import APP_CACHE_DIR, USER_CONFIG_PATH, USER_NAME
from ...libs.anilist.anilist import AniList
from ...libs.anilist.anilist_data_schema import AnilistBaseMediaDataSchema
from ...libs.anime_provider.allanime.api import anime_provider
from ...libs.anime_provider.allanime.types import AllAnimeEpisode, AllAnimeShow
from ...libs.fzf import fzf
from ...Utility import anilist_data_helper
from ...Utility.data import anime_normalizer
from ...Utility.utils import remove_html_tags, sanitize_filename
from ..config import Config
from ..utils.mpv import mpv
from ..utils.tools import QueryDict
from ..utils.utils import clear

SEARCH_RESULTS_CACHE = os.path.join(APP_CACHE_DIR, "search_results")


def write_search_results(
    search_results: list[AnilistBaseMediaDataSchema], config: Config
):
    import textwrap

    import requests

    for anime in search_results:
        if not os.path.exists(SEARCH_RESULTS_CACHE):
            os.mkdir(SEARCH_RESULTS_CACHE)
        anime_title = (
            anime["title"][config.preferred_language] or anime["title"]["romaji"]
        )
        anime_title = sanitize_filename(anime_title)
        ANIME_CACHE = os.path.join(SEARCH_RESULTS_CACHE, anime_title)
        if not os.path.exists(ANIME_CACHE):
            os.mkdir(ANIME_CACHE)
        with open(
            f"{ANIME_CACHE}/image",
            "wb",
        ) as f:
            image = requests.get(anime["coverImage"]["large"])
            f.write(image.content)

        with open(f"{ANIME_CACHE}/data", "w") as f:
            # data = json.dumps(anime, sort_keys=True, indent=2, separators=(',', ': '))
            template = f"""
            {"-"*40}
            Anime Title(jp): {anime['title']['romaji']}
            Anime Title(eng): {anime['title']['english']}
            {"-"*40}
            Popularity: {anime['popularity']}
            Favourites: {anime['favourites']}
            Status: {anime['status']}
            Episodes: {anime['episodes']}
            Genres: {anilist_data_helper.format_list_data_with_comma(anime['genres'])}
            Next Episode: {anilist_data_helper.extract_next_airing_episode(anime['nextAiringEpisode'])}
            Start Date: {anilist_data_helper.format_anilist_date_object(anime['startDate'])}
            End Date: {anilist_data_helper.format_anilist_date_object(anime['endDate'])}
            {"-"*40}
            Description:
            """
            template = textwrap.dedent(template)
            template = f"""
            {template}
            {textwrap.fill(remove_html_tags(str(anime['description'])),width=45)}
            """
            f.write(template)


def get_preview(search_results: list[AnilistBaseMediaDataSchema], config: Config):
    from threading import Thread

    background_worker = Thread(
        target=write_search_results, args=(search_results, config)
    )
    background_worker.daemon = True
    background_worker.start()

    os.environ["SHELL"] = shutil.which("bash") or "bash"
    preview = """
        if [ -s %s/{}/image ]; then fzf-preview %s/{}/image
        else echo Loading...
        fi
        if [ -s %s/{}/data ]; then cat %s/{}/data
        else echo Loading...
        fi
    """ % (
        SEARCH_RESULTS_CACHE,
        SEARCH_RESULTS_CACHE,
        SEARCH_RESULTS_CACHE,
        SEARCH_RESULTS_CACHE,
    )
    # preview.replace("\n", ";")
    return preview


def exit_app(*args):
    print("Have a good day :smile:", USER_NAME)
    sys.exit(0)


def player_controls(config: Config, anilist_config: QueryDict):
    # user config
    translation_type: str = config.translation_type.lower()

    # internal config
    _anime: AllAnimeShow = anilist_config._anime
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
        print(
            "[bold magenta]Now Replaying:[/]",
            anime_title,
            "[bold magenta] Episode: [/]",
            current_episode,
        )

        mpv(current_link)
        clear()
        player_controls(config, anilist_config)

    def _next_episode():
        next_episode = episodes.index(current_episode) + 1
        if next_episode >= len(episodes):
            next_episode = len(episodes) - 1
        episode = anime_provider.get_anime_episode(
            _anime["_id"], episodes[next_episode], translation_type
        )

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
            _anime["_id"], episodes[prev_episode], config.translation_type.lower()
        )

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
        quality = fzf.run(options, prompt="Select Quality:", header="Quality Options")
        config.quality = options.index(quality)  # set quality
        player_controls(config, anilist_config)

    def _change_translation_type():
        # prompt for new translation type
        options = ["sub", "dub"]
        translation_type = fzf.run(
            options, prompt="Select Translation Type: ", header="Lang Options"
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
        "Exit": sys.exit,
    }

    if config.auto_next:
        _next_episode()
        return
    action = fzf.run(
        list(options.keys()), prompt="Select Action:", header="Player Controls"
    )

    options[action]()


def fetch_streams(config: Config, anilist_config: QueryDict):
    # user config
    quality: int = config.quality

    # internal config
    episode: AllAnimeEpisode = anilist_config.episode
    episode_number: str = anilist_config.episode_number
    anime_title: str = anilist_config.anime_title
    anime_id: int = anilist_config.anime_id

    # get streams for episode from provider
    episode_streams = anime_provider.get_episode_streams(episode)
    episode_streams = {
        episode_stream[0]: episode_stream[1] for episode_stream in episode_streams
    }

    # prompt for preferred server
    server = None
    if config.server and config.server in episode_streams.keys():
        server = config.server
    if config.server == "top":
        server = list(episode_streams.keys())[0]
    if not server:
        server = fzf.run(
            [*episode_streams.keys(), "Back"],
            prompt="Select Server: ",
            header="Servers",
        )
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

    mpv(stream_link)

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

    # internal config
    anime = anilist_config.anime
    _anime: AllAnimeShow = anilist_config._anime

    # prompt for episode number
    episodes = anime["availableEpisodesDetail"][translation_type]
    if continue_from_history and user_watch_history.get(str(anime_id)) in episodes:
        episode_number = user_watch_history[str(anime_id)]
        print(f"[bold cyan]Continuing from Episode:[/] [bold]{episode_number}[/]")
    else:
        episode_number = fzf.run(
            [*episodes, "Back"],
            prompt="Select Episode:",
            header="Episodes",
        )

    if episode_number == "Back":
        provide_anime(config, anilist_config)
        return
    config.update_watch_history(anime_id, episode_number)

    # get the episode info from provider
    episode = anime_provider.get_anime_episode(
        _anime["_id"], episode_number, translation_type
    )

    # update internal config
    anilist_config.episodes = episodes
    anilist_config.episode = episode
    # anilist_config.episode_title = episode["title"]
    anilist_config.episode_number = episode_number

    # next interface
    fetch_streams(config, anilist_config)


def fetch_anime_episode(config, anilist_config: QueryDict):
    selected_anime: AllAnimeShow = anilist_config._anime
    anilist_config.anime = anime_provider.get_anime(selected_anime["_id"])

    fetch_episode(config, anilist_config)


def provide_anime(config: Config, anilist_config: QueryDict):
    # user config
    translation_type = config.translation_type.lower()

    # internal config
    selected_anime_title = anilist_config.selected_anime_title

    # search and get the requested title from provider
    search_results = anime_provider.search_for_anime(
        selected_anime_title, translation_type
    )

    search_results = {
        anime["name"]: anime for anime in search_results["shows"]["edges"]
    }
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

    anime_title = fzf.run(
        [*search_results.keys(), "Back"],
        prompt="Select Search Result:",
        header="Anime Search Results",
    )

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
            mpv(trailer_url)
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
        translation_type = fzf.run(
            options, prompt="Select Translation Type:", header="Language Options"
        )

        # update internal config
        config.translation_type = translation_type.lower()

        anilist_options(config, anilist_config)

    def _view_info(config, anilist_config):
        from rich.prompt import Confirm
        from rich.console import Console

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
    action = fzf.run(list(options.keys()), prompt="Select Action:", header="Anime Menu")
    options[action](config, anilist_config)


def select_anime(config: Config, anilist_config: QueryDict):
    search_results = anilist_config.data["data"]["Page"]["media"]
    anime_data = {
        sanitize_filename(
            str(anime["title"][config.preferred_language] or anime["title"]["romaji"])
        ): anime
        for anime in search_results
    }

    preview = get_preview(search_results, config)

    selected_anime_title = fzf.run(
        [
            *anime_data.keys(),
            "Back",
        ],
        prompt="Select Anime: ",
        header="Search Results",
        preview=preview,
    )
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

    def _watch_history():
        watch_history = list(map(int, config.watch_history.keys()))
        return AniList.search(id_in=watch_history, sort="TRENDING_DESC")

    def _anime_list():
        anime_list = config.anime_list
        return AniList.search(id_in=anime_list)

    def edit_config():
        import subprocess

        process = subprocess.run([os.environ.get("EDITOR", "open"), USER_CONFIG_PATH])
        config.load_config()

        anilist(config, anilist_config)

    options = {
        "Trending": AniList.get_trending,
        "Recently Updated Anime": AniList.get_most_recently_updated,
        "Search": _anilist_search,
        "Watch History": _watch_history,
        "AnimeList": _anime_list,
        "Most Popular Anime": AniList.get_most_popular,
        "Most Favourite Anime": AniList.get_most_favourite,
        "Most Scored Anime": AniList.get_most_scored,
        "Upcoming Anime": AniList.get_upcoming_anime,
        "Edit Config": edit_config,
        "Exit": sys.exit,
    }
    action = fzf.run(
        list(options.keys()),
        prompt="Select Action: ",
        header="Anilist Menu",
    )
    anilist_data = options[action]()
    if anilist_data[0]:
        anilist_config.data = anilist_data[1]
        select_anime(config, anilist_config)

    else:
        print(anilist_data[1])
        input("Enter to continue...")
        anilist(config, anilist_config)
