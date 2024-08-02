from __future__ import annotations

import os
import random
from datetime import datetime

from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator
from rich import print
from rich.progress import Progress
from rich.prompt import Confirm, Prompt

from ...anilist import AniList
from ...constants import USER_CONFIG_PATH
from ...libs.anilist.anilist_data_schema import AnilistBaseMediaDataSchema
from ...libs.anime_provider.types import Anime, SearchResult, Server
from ...libs.fzf import fzf
from ...libs.rofi import Rofi
from ...Utility.data import anime_normalizer
from ...Utility.utils import anime_title_percentage_match, sanitize_filename
from ..config import Config
from ..utils.mpv import mpv
from ..utils.tools import QueryDict, exit_app
from ..utils.utils import clear, fuzzy_inquirer
from .utils import aniskip


def calculate_time_delta(start_time, end_time):
    time_format = "%H:%M:%S"

    # Convert string times to datetime objects
    start = datetime.strptime(start_time, time_format)
    end = datetime.strptime(end_time, time_format)

    # Calculate the difference
    delta = end - start

    return delta


def player_controls(config: Config, anilist_config: QueryDict):
    # user config
    config.translation_type.lower()

    # internal config
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

        start_time = config.watch_history[str(anime_id)]["start_time"]
        print("[green]Continuing from:[/] ", start_time)
        custom_args = []
        if config.skip:
            if args := aniskip(
                anilist_config.selected_anime_anilist["idMal"], current_episode
            ):
                custom_args = args
        stop_time, total_time = mpv(
            current_link,
            selected_server["episode_title"],
            start_time=start_time,
            custom_args=custom_args,
        )
        if stop_time == "0":
            episode = str(int(current_episode) + 1)
        else:
            error = 5 * 60
            delta = calculate_time_delta(stop_time, total_time)
            if delta.total_seconds() > error:
                episode = current_episode
            else:
                episode = str(int(current_episode) + 1)
                stop_time = "0"
                total_time = "0"

        clear()
        config.update_watch_history(anime_id, episode, stop_time, total_time)
        player_controls(config, anilist_config)

    def _next_episode():
        # ensures you dont accidentally erase your progress for an in complete episode
        stop_time = config.watch_history.get(str(anime_id), {}).get("start_time", "0")

        total_time = config.watch_history.get(str(anime_id), {}).get("total_time", "0")

        error = config.error * 60
        if stop_time == "0" or total_time == "0":
            dt = 0
        else:
            delta = calculate_time_delta(stop_time, total_time)
            dt = delta.total_seconds()
        if dt > error:
            if config.auto_next:
                if config.use_rofi:
                    if not Rofi.confirm(
                        "Are you sure you wish to continue to the next episode you haven't completed the current episode?"
                    ):
                        anilist_options(config, anilist_config)
                        return
                else:
                    if not Confirm.ask(
                        "Are you sure you wish to continue to the next episode you haven't completed the current episode?",
                        default=False,
                    ):
                        anilist_options(config, anilist_config)
                        return
            elif not config.use_rofi:
                if not Confirm.ask(
                    "Are you sure you wish to continue to the next episode, your progress for the current episodes will be erased?",
                    default=True,
                ):
                    player_controls(config, anilist_config)
                    return

        # all checks have passed lets go to the next episode
        next_episode = episodes.index(current_episode) + 1
        if next_episode >= len(episodes):
            next_episode = len(episodes) - 1

        # updateinternal config
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
        elif config.use_rofi:
            quality = Rofi.run(options, "Select Quality")
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
        elif config.use_rofi:
            translation_type = Rofi.run(options, "Select Translation Type")
        else:
            translation_type = fuzzy_inquirer(
                "Select Translation Type", options
            ).lower()

        # update internal config
        config.translation_type = translation_type.lower()

        # reload to controls
        player_controls(config, anilist_config)

    icons = config.icons
    options = {
        f"{'🔂 ' if icons else ''}Replay": _replay,
        f"{'⏭  ' if icons else ''}Next Episode": _next_episode,
        f"{'⏮  ' if icons else ''}Previous Episode": _previous_episode,
        f"{'🗃️ ' if icons else ''}Episodes": _episodes,
        f"{'📀 ' if icons else ''}Change Quality": _change_quality,
        f"{'🎧 ' if icons else ''}Change Translation Type": _change_translation_type,
        f"{'💽 ' if icons else ''}Servers": _servers,
        f"{'📱 ' if icons else ''}Main Menu": lambda: anilist(config, anilist_config),
        f"{'📜 ' if icons else ''}Anime Options Menu": lambda: anilist_options(
            config, anilist_config
        ),
        f"{'🔎 ' if icons else ''}Search Results": lambda: select_anime(
            config, anilist_config
        ),
        f"{'❌ ' if icons else ''}Exit": exit_app,
    }

    if config.auto_next:
        print("Auto selecting next episode")
        _next_episode()
        return
    if config.use_fzf:
        action = fzf.run(
            list(options.keys()), prompt="Select Action:", header="Player Controls"
        )
    elif config.use_rofi:
        action = Rofi.run(list(options.keys()), "Select Action")
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
    anime_provider = config.anime_provider

    # get streams for episode from provider
    with Progress() as progress:
        progress.add_task("Fetching Episode Streams...", total=None)
        episode_streams = anime_provider.get_episode_streams(
            anime, episode_number, translation_type
        )
        if not episode_streams:
            if not config.use_rofi:
                print("Failed to fetch :cry:")
                input("Enter to retry...")
            else:
                if not Rofi.confirm("Sth went wrong!!Enter to continue..."):
                    exit(1)
            return fetch_streams(config, anilist_config)

        episode_streams = {
            episode_stream["server"]: episode_stream
            for episode_stream in episode_streams
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
        elif config.use_rofi:
            server = Rofi.run(choices, "Select Server")
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
    # -- update anilist info if user --
    if config.user and episode_number:
        AniList.update_anime_list(
            {
                "mediaId": anime_id,
                # "status": "CURRENT",
                "progress": episode_number,
            }
        )

    start_time = config.watch_history.get(str(anime_id), {}).get("start_time", "0")
    if start_time != "0":
        print("[green]Continuing from:[/] ", start_time)
    custom_args = []
    if config.skip:
        if args := aniskip(
            anilist_config.selected_anime_anilist["idMal"], episode_number
        ):
            custom_args = args

    stop_time, total_time = mpv(
        stream_link,
        selected_server["episode_title"],
        start_time=start_time,
        custom_args=custom_args,
    )
    print("Finished at: ", stop_time)

    # update_watch_history
    if stop_time == "0":
        episode = str(int(episode_number) + 1)
    else:
        error = config.error * 60
        delta = calculate_time_delta(stop_time, total_time)
        if delta.total_seconds() > error:
            episode = episode_number
        else:
            episode = str(int(episode_number) + 1)
            stop_time = "0"
            total_time = "0"

    config.update_watch_history(
        anime_id, episode, start_time=stop_time, total_time=total_time
    )

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
    if (
        continue_from_history
        and user_watch_history.get(str(anime_id), {}).get("episode") in episodes
    ):
        episode_number = user_watch_history[str(anime_id)]["episode"]
        print(f"[bold cyan]Continuing from Episode:[/] [bold]{episode_number}[/]")
    else:
        choices = [*episodes, "Back"]
        if config.use_fzf:
            episode_number = fzf.run(
                choices,
                prompt="Select Episode:",
                header=anime_title,
            )
        elif config.use_rofi:
            episode_number = Rofi.run(choices, "Select Episode")
        else:
            episode_number = fuzzy_inquirer("Select Episode", choices)

    if episode_number == "Back":
        anilist_options(config, anilist_config)
        return
    start_time = user_watch_history.get(str(anime_id), {}).get("start_time", "0")
    config.update_watch_history(anime_id, episode_number, start_time=start_time)

    # update internal config
    anilist_config.episodes = episodes
    # anilist_config.episode_title = episode["title"]
    anilist_config.episode_number = episode_number

    # next interface
    fetch_streams(config, anilist_config)


def fetch_anime_episode(config, anilist_config: QueryDict):
    selected_anime: SearchResult = anilist_config._anime
    anime_provider = config.anime_provider
    with Progress() as progress:
        progress.add_task("Fetching Anime Info...", total=None)
        anilist_config.anime = anime_provider.get_anime(selected_anime["id"])
    if not anilist_config.anime:
        print(
            "Sth went wrong :cry: this could mean the provider is down or your internet"
        )
        if not config.use_rofi:
            input("Enter to continue...")
        else:
            if not Rofi.confirm("Sth went wrong!!Enter to continue..."):
                exit(1)
        fetch_anime_episode(config, anilist_config)
        return

    fetch_episode(config, anilist_config)


def provide_anime(config: Config, anilist_config: QueryDict):
    # user config
    translation_type = config.translation_type.lower()

    # internal config
    selected_anime_title = anilist_config.selected_anime_title

    anime_data: AnilistBaseMediaDataSchema = anilist_config.selected_anime_anilist
    anime_provider = config.anime_provider

    # search and get the requested title from provider
    with Progress() as progress:
        progress.add_task("Fetching Search Results...", total=None)
        search_results = anime_provider.search_for_anime(
            selected_anime_title, translation_type
        )
    if not search_results:
        print(
            "Sth went wrong :cry: while fetching this could mean you have poor internet connection or the provider is down"
        )
        if not config.use_rofi:
            input("Enter to continue...")
        else:
            if not Rofi.confirm("Sth went wrong!!Enter to continue..."):
                exit(1)
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

        elif config.use_rofi:
            anime_title = Rofi.run(choices, "Select Search Result")
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
            mpv(
                trailer_url,
                ytdl_format=config.format,
            )
            anilist_options(config, anilist_config)
        else:
            if not config.use_rofi:
                print("no trailer available :confused:")
                input("Enter to continue...")
            else:
                if not Rofi.confirm("No trailler found!!Enter to continue"):
                    exit(0)
            anilist_options(config, anilist_config)

    def _add_to_list(config: Config, anilist_config: QueryDict):
        # config.update_anime_list(anilist_config.anime_id)
        anime_lists = {
            "Watching": "CURRENT",
            "Paused": "PAUSED",
            "Planning": "PLANNING",
            "Dropped": "DROPPED",
            "Rewatching": "REPEATING",
            "Completed": "COMPLETED",
        }
        if config.use_fzf:
            anime_list = fzf.run(
                list(anime_lists.keys()),
                "Choose the list you want to add to",
                "Add your animelist",
            )
        elif config.use_rofi:
            anime_list = Rofi.run(
                list(anime_lists.keys()), "Choose list you want to add to"
            )
        else:
            anime_list = fuzzy_inquirer(
                "Choose the list you want to add to", list(anime_lists.keys())
            )
        result = AniList.update_anime_list(
            {"status": anime_lists[anime_list], "mediaId": selected_anime["id"]}
        )
        if not result[0]:
            print("Failed to update", result)
        else:
            print(
                f"Successfully added {selected_anime_title} to your {anime_list} list :smile:"
            )
        if not config.use_rofi:
            input("Enter to continue...")
        anilist_options(config, anilist_config)

    def _score_anime(config: Config, anilist_config: QueryDict):
        if config.use_rofi:
            score = Rofi.ask("Enter Score", is_int=True)
            score = max(100, min(0, score))
        else:
            score = inquirer.number(
                message="Enter the score:",
                min_allowed=0,
                max_allowed=100,
                validate=EmptyInputValidator(),
            ).execute()

        result = AniList.update_anime_list(
            {"scoreRaw": score, "mediaId": selected_anime["id"]}
        )
        if not result[0]:
            print("Failed to update", result)
        else:
            print(f"Successfully scored {selected_anime_title}; score: {score}")
        if not config.use_rofi:
            input("Enter to continue...")
        anilist_options(config, anilist_config)

    def _remove_from_list(config: Config, anilist_config: QueryDict):
        if Confirm.ask(
            f"Are you sure you want to procede, the folowing action will permanently remove {selected_anime_title} from your list and your progress will be erased",
            default=False,
        ):
            success, data = AniList.delete_medialist_entry(selected_anime["id"])
            if not success or not data:
                print("Failed to delete", data)
            elif not data.get("deleted"):
                print("Failed to delete", data)
            else:
                print("Successfully deleted :cry:", selected_anime_title)
        else:
            print(selected_anime_title, ":relieved:")
        if not config.use_rofi:
            input("Enter to continue...")
        anilist_options(config, anilist_config)

    def _change_translation_type(config: Config, anilist_config: QueryDict):
        # prompt for new translation type
        options = ["Sub", "Dub"]
        if config.use_fzf:
            translation_type = fzf.run(
                options, prompt="Select Translation Type:", header="Language Options"
            )
        elif config.use_rofi:
            translation_type = Rofi.run(options, "Select Translation Type")
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

    def _toggle_auto_select(config, anilist_config):
        config.auto_select = not config.auto_select
        anilist_options(config, anilist_config)

    def _toggle_auto_next(config, anilist_config):
        config.auto_select = not config.auto_select
        anilist_options(config, anilist_config)

    icons = config.icons
    options = {
        f"{'📽️ ' if icons else ''}Stream": provide_anime,
        f"{'📼 ' if icons else ''}Watch Trailer": _watch_trailer,
        f"{'✨ ' if icons else ''}Score Anime": _score_anime,
        f"{'📥 ' if icons else ''}Add to List": _add_to_list,
        f"{'📤 ' if icons else ''}Remove from List": _remove_from_list,
        f"{'📖 ' if icons else ''}View Info": _view_info,
        f"{'🎧 ' if icons else ''}Change Translation Type": _change_translation_type,
        f"{'🔘 ' if icons else ''}Toggle auto select anime": _toggle_auto_select,  # problematic if you choose an anime that doesnt match id
        f"{'💠 ' if icons else ''}Toggle auto next episode": _toggle_auto_next,
        f"{'🔙 ' if icons else ''}Back": select_anime,
        f"{'❌ ' if icons else ''}Exit": exit_app,
    }
    if config.use_fzf:
        action = fzf.run(
            list(options.keys()), prompt="Select Action:", header="Anime Menu"
        )
    elif config.use_rofi:
        action = Rofi.run(list(options.keys()), "Select Action")
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
    elif config.use_rofi:
        # TODO: Make this faster
        if config.preview:
            from .utils import IMAGES_DIR, get_icons

            get_icons(search_results, config)
            choices = []
            for anime in search_results:
                title = sanitize_filename(
                    str(
                        anime["title"][config.preferred_language]
                        or anime["title"]["romaji"]
                    )
                )
                icon_path = os.path.join(IMAGES_DIR, title)
                choices.append(f"{title}\0icon\x1f{icon_path}")
            choices.append("Back")
            selected_anime_title = Rofi.run_with_icons(choices, "Select Anime")
        else:
            selected_anime_title = Rofi.run(choices, "Select Anime")
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


def handle_animelist(anilist_config, config: Config, list_type: str):
    if not config.user:
        if not config.use_rofi:
            print("You haven't logged in please run: fastanime anilist login")
            input("Enter to continue...")
        else:
            if not Rofi.confirm("You haven't logged in!!Enter to continue"):
                exit(1)
        anilist(config, anilist_config)
        return
    match list_type:
        case "Watching":
            status = "CURRENT"
        case "Planned":
            status = "PLANNING"
        case "Completed":
            status = "COMPLETED"
        case "Dropped":
            status = "DROPPED"
        case "Paused":
            status = "PAUSED"
        case "Repeating":
            status = "REPEATING"
        case _:
            return
    anime_list = AniList.get_anime_list(status)
    if not anime_list:
        print("Sth went wrong", anime_list)
        if not config.use_rofi:
            input("Enter to continue")
        else:
            if not Rofi.confirm("Sth went wrong!!Enter to continue..."):
                exit(1)
        anilist(config, anilist_config)
        return
    if not anime_list[0] or not anime_list[1]:
        print("Sth went wrong", anime_list)
        if not config.use_rofi:
            input("Enter to continue")
        else:
            if not Rofi.confirm("Sth went wrong!!Enter to continue..."):
                exit(1)

        anilist(config, anilist_config)
        return
    media = [
        mediaListItem["media"]
        for mediaListItem in anime_list[1]["data"]["Page"]["mediaList"]
    ]  # pyright:ignore
    anime_list[1]["data"]["Page"]["media"] = media  # pyright:ignore
    return anime_list


def anilist(config: Config, anilist_config: QueryDict):
    def _anilist_search():
        if config.use_rofi:
            search_term = str(Rofi.ask("Search for"))
        else:
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
        if config.use_rofi:
            config.load_config()
            config.use_rofi = True
            config.use_fzf = False
        else:
            config.load_config()

        anilist(config, anilist_config)

    icons = config.icons
    options = {
        f"{'🔥 ' if icons else ''}Trending": AniList.get_trending,
        f"{'📺 ' if icons else ''}Watching": lambda x="Watching": handle_animelist(
            anilist_config, config, x
        ),
        f"{'⏸  ' if icons else ''}Paused": lambda x="Paused": handle_animelist(
            anilist_config, config, x
        ),
        f"{'🚮 ' if icons else ''}Dropped": lambda x="Dropped": handle_animelist(
            anilist_config, config, x
        ),
        f"{'📑 ' if icons else ''}Planned": lambda x="Planned": handle_animelist(
            anilist_config, config, x
        ),
        f"{'✅ ' if icons else ''}Completed": lambda x="Completed": handle_animelist(
            anilist_config, config, x
        ),
        f"{'🔁 ' if icons else ''}Rewatching": lambda x="Repeating": handle_animelist(
            anilist_config, config, x
        ),
        f"{'🔔 ' if icons else ''}Recently Updated Anime": AniList.get_most_recently_updated,
        f"{'🔎 ' if icons else ''}Search": _anilist_search,
        f"{'🎞️ ' if icons else ''}Watch History": _watch_history,
        # "AnimeList": _anime_list💯,
        f"{'🎲 ' if icons else ''}Random Anime": _anilist_random,
        f"{'🌟 ' if icons else ''}Most Popular Anime": AniList.get_most_popular,
        f"{'💖 ' if icons else ''}Most Favourite Anime": AniList.get_most_favourite,
        f"{'✨ ' if icons else ''}Most Scored Anime": AniList.get_most_scored,
        f"{'🎬 ' if icons else ''}Upcoming Anime": AniList.get_upcoming_anime,
        f"{'📝 ' if icons else ''}Edit Config": edit_config,
        f"{'❌ ' if icons else ''}Exit": exit_app,
    }
    if config.use_fzf:
        action = fzf.run(
            list(options.keys()),
            prompt="Select Action: ",
            header="Anilist Menu",
        )
    elif config.use_rofi:
        action = Rofi.run(list(options.keys()), "Select Action")
    else:
        action = fuzzy_inquirer("Select Action", options.keys())
    anilist_data = options[action]()
    if anilist_data[0]:
        anilist_config.data = anilist_data[1]
        select_anime(config, anilist_config)

    else:
        print(anilist_data[1])
        if not config.use_rofi:
            input("Enter to continue...")
        else:
            if not Rofi.confirm("Sth went wrong!!Enter to continue..."):
                exit(1)
        anilist(config, anilist_config)
