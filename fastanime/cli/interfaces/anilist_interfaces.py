from __future__ import annotations

import os
import random
from datetime import datetime
from typing import TYPE_CHECKING

from click import clear
from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator
from rich import print
from rich.progress import Progress
from rich.prompt import Confirm, Prompt
from yt_dlp.utils import sanitize_filename

from ...anilist import AniList
from ...constants import USER_CONFIG_PATH
from ...libs.fzf import fzf
from ...libs.rofi import Rofi
from ...Utility.data import anime_normalizer
from ...Utility.utils import anime_title_percentage_match
from ..utils.mpv import run_mpv
from ..utils.tools import FastAnimeRuntimeState, exit_app
from ..utils.utils import filter_by_quality, fuzzy_inquirer
from .utils import aniskip

if TYPE_CHECKING:
    from ...libs.anilist.types import AnilistBaseMediaDataSchema
    from ...libs.anime_provider.types import Anime, SearchResult, Server
    from ..config import Config


def calculate_time_delta(start_time, end_time):
    time_format = "%H:%M:%S"

    # Convert string times to datetime objects
    start = datetime.strptime(start_time, time_format)
    end = datetime.strptime(end_time, time_format)

    # Calculate the difference
    delta = end - start

    return delta


def player_controls(config: "Config", fastanime_runtime_state: FastAnimeRuntimeState):
    # user config
    config.translation_type.lower()

    # internal config
    current_episode: str = fastanime_runtime_state.episode_number
    episodes: list = sorted(fastanime_runtime_state.episodes, key=float)
    links: list = fastanime_runtime_state.current_stream_links
    current_link: str = fastanime_runtime_state.current_stream_link
    anime_title: str = fastanime_runtime_state.anime_title
    anime_id: int = fastanime_runtime_state.selected_anime_id_anilist

    def _servers():
        config.server = ""

        fetch_streams(config, fastanime_runtime_state)

    def _replay():
        selected_server: "Server" = fastanime_runtime_state.current_server
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
                fastanime_runtime_state.selected_anime_anilist["idMal"], current_episode
            ):
                custom_args.extend(args)
        if config.use_mpv_mod:
            from ..utils.player import player

            mpv = player.create_player(
                current_link,
                config.anime_provider,
                fastanime_runtime_state,
                config,
                selected_server["episode_title"],
            )

            if custom_args and None:
                chapters_file = custom_args[0].split("=", 1)
                script_opts = custom_args[1].split("=", 1)
                mpv._set_property("chapters-file", chapters_file[1])
                mpv._set_property("script-opts", script_opts[1])
            mpv.start = start_time
            mpv.wait_for_shutdown()
            mpv.terminate()
            stop_time = player.last_stop_time
            total_time = player.last_total_time
        else:
            stop_time, total_time = run_mpv(
                current_link,
                selected_server["episode_title"],
                start_time=start_time,
                custom_args=custom_args,
            )
        if stop_time == "0" or total_time == "0":
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
        player_controls(config, fastanime_runtime_state)

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
                        anilist_media_actions_menu(config, fastanime_runtime_state)
                        return
                else:
                    if not Confirm.ask(
                        "Are you sure you wish to continue to the next episode you haven't completed the current episode?",
                        default=False,
                    ):
                        anilist_media_actions_menu(config, fastanime_runtime_state)
                        return
            elif not config.use_rofi:
                if not Confirm.ask(
                    "Are you sure you wish to continue to the next episode, your progress for the current episodes will be erased?",
                    default=True,
                ):
                    player_controls(config, fastanime_runtime_state)
                    return

        # all checks have passed lets go to the next episode
        next_episode = episodes.index(current_episode) + 1
        if next_episode >= len(episodes):
            next_episode = len(episodes) - 1

        # updateinternal config
        fastanime_runtime_state.episode_number = episodes[next_episode]

        # update user config
        config.update_watch_history(anime_id, episodes[next_episode])

        # call interface
        fetch_streams(config, fastanime_runtime_state)

    def _episodes():
        # reset watch_history
        config.continue_from_history = False

        # call interface
        fetch_episode(config, fastanime_runtime_state)

    def _previous_episode():
        prev_episode = episodes.index(current_episode) - 1
        if prev_episode <= 0:
            prev_episode = 0
        # fastanime_runtime_state.episode_title = episode["title"]
        fastanime_runtime_state.episode_number = episodes[prev_episode]

        # update user config
        config.update_watch_history(anime_id, episodes[prev_episode])

        # call interface
        fetch_streams(config, fastanime_runtime_state)

    def _change_quality():
        # extract the actual link urls
        options = [link["quality"] for link in links]

        # prompt for new quality
        if config.use_fzf:
            quality = fzf.run(
                options, prompt="Select Quality:", header="Quality Options"
            )
        elif config.use_rofi:
            quality = Rofi.run(options, "Select Quality")
        else:
            quality = fuzzy_inquirer(
                options,
                "Select Quality",
            )
        config.quality = quality  # set quality
        player_controls(config, fastanime_runtime_state)

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
                options,
                "Select Translation Type",
            ).lower()

        # update internal config
        config.translation_type = translation_type.lower()

        # reload to controls
        player_controls(config, fastanime_runtime_state)

    icons = config.icons
    options = {
        f"{'🔂 ' if icons else ''}Replay": _replay,
        f"{'⏭  ' if icons else ''}Next Episode": _next_episode,
        f"{'⏮  ' if icons else ''}Previous Episode": _previous_episode,
        f"{'🗃️ ' if icons else ''}Episodes": _episodes,
        f"{'📀 ' if icons else ''}Change Quality": _change_quality,
        f"{'🎧 ' if icons else ''}Change Translation Type": _change_translation_type,
        f"{'💽 ' if icons else ''}Servers": _servers,
        f"{'📱 ' if icons else ''}Main Menu": lambda: fastanime_main_menu(
            config, fastanime_runtime_state
        ),
        f"{'📜 ' if icons else ''}Anime Options Menu": lambda: anilist_media_actions_menu(
            config, fastanime_runtime_state
        ),
        f"{'🔎 ' if icons else ''}Search Results": lambda: anilist_results_menu(
            config, fastanime_runtime_state
        ),
        f"{'❌ ' if icons else ''}Exit": exit_app,
    }

    if config.auto_next:
        print("Auto selecting next episode")
        _next_episode()
        return

    choices = list(options.keys())
    if config.use_fzf:
        action = fzf.run(choices, prompt="Select Action:", header="Player Controls")
    elif config.use_rofi:
        action = Rofi.run(choices, "Select Action")
    else:
        action = fuzzy_inquirer(choices, "Select Action")
    options[action]()


def fetch_streams(config: "Config", fastanime_runtime_state: FastAnimeRuntimeState):
    # user config
    quality: str = config.quality

    # internal config
    episode_number: str = fastanime_runtime_state.episode_number
    anime_title: str = fastanime_runtime_state.anime_title
    anime_id: int = fastanime_runtime_state.selected_anime_id_anilist
    anime: "Anime" = fastanime_runtime_state.anime
    translation_type = config.translation_type
    anime_provider = config.anime_provider

    server = None
    # get streams for episode from provider
    with Progress() as progress:
        progress.add_task("Fetching Episode Streams...", total=None)
        episode_streams = anime_provider.get_episode_streams(
            anime,
            episode_number,
            translation_type,
            fastanime_runtime_state.selected_anime_anilist,
        )
    if not episode_streams:
        if not config.use_rofi:
            print("Failed to fetch :cry:")
            input("Enter to retry...")
        else:
            if not Rofi.confirm("Sth went wrong!!Enter to continue..."):
                exit(1)
        return fetch_streams(config, fastanime_runtime_state)

    if config.server == "top":
        # no need to get all servers if top just works
        with Progress() as progress:
            progress.add_task("Fetching top server...", total=None)
            selected_server = next(episode_streams)
            server = "top"
    else:
        with Progress() as progress:
            progress.add_task("Fetching servers...", total=None)
            episode_streams_dict = {
                episode_stream["server"]: episode_stream
                for episode_stream in episode_streams
            }

        # prompt for preferred server
        if config.server and config.server in episode_streams_dict.keys():
            server = config.server
        if not server:
            choices = [*episode_streams_dict.keys(), "top", "Back"]
            if config.use_fzf:
                server = fzf.run(
                    choices,
                    prompt="Select Server: ",
                    header="Servers",
                )
            elif config.use_rofi:
                server = Rofi.run(choices, "Select Server")
            else:
                server = fuzzy_inquirer(
                    choices,
                    "Select Server",
                )
        if server == "Back":
            # reset watch_history
            config.update_watch_history(anime_id, None)

            fetch_episode(config, fastanime_runtime_state)
            return
        elif server == "top":
            selected_server = episode_streams_dict[list(episode_streams_dict.keys())[0]]
        else:
            selected_server = episode_streams_dict[server]

    links = selected_server["links"]

    stream_link_ = filter_by_quality(quality, links)
    if not stream_link_:
        print("Quality not found")
        input("Enter to continue...")
        anilist_media_actions_menu(config, fastanime_runtime_state)
        return
    stream_link = stream_link_["link"]
    # update internal config
    fastanime_runtime_state.current_stream_links = links
    fastanime_runtime_state.current_stream_link = stream_link
    fastanime_runtime_state.current_server = selected_server
    fastanime_runtime_state.current_server_name = server

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
            fastanime_runtime_state.selected_anime_anilist["idMal"], episode_number
        ):
            custom_args.extend(args)
    if config.use_mpv_mod:
        from ..utils.player import player

        mpv = player.create_player(
            stream_link,
            anime_provider,
            fastanime_runtime_state,
            config,
            selected_server["episode_title"],
        )

        if custom_args and None:
            chapters_file = custom_args[0].split("=", 1)
            script_opts = custom_args[1].split("=", 1)
            mpv._set_property("chapters-file", chapters_file[1])
            mpv._set_property("script-opts", script_opts[1])
        mpv.start = start_time
        mpv.wait_for_shutdown()
        mpv.terminate()
        stop_time = player.last_stop_time
        total_time = player.last_total_time

    else:
        stop_time, total_time = run_mpv(
            stream_link,
            selected_server["episode_title"],
            start_time=start_time,
            custom_args=custom_args,
        )
    print("Finished at: ", stop_time)

    # update_watch_history
    if stop_time == "0" or total_time == "0":
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

    player_controls(config, fastanime_runtime_state)


def fetch_episode(config: "Config", fastanime_runtime_state: FastAnimeRuntimeState):
    # user config
    translation_type: str = config.translation_type.lower()
    continue_from_history: bool = config.continue_from_history
    user_watch_history: dict = config.watch_history
    anime_id: int = fastanime_runtime_state.selected_anime_id_anilist
    anime_title: str = fastanime_runtime_state.anime_title

    # internal config
    anime: "Anime" = fastanime_runtime_state.anime
    _anime: "SearchResult" = fastanime_runtime_state._anime
    selected_anime_anilist: "AnilistBaseMediaDataSchema" = (
        fastanime_runtime_state.selected_anime_anilist
    )
    # prompt for episode number
    episodes = anime["availableEpisodesDetail"][translation_type]
    episode_number = ""
    if continue_from_history:
        if user_watch_history.get(str(anime_id), {}).get("episode") in episodes:
            episode_number = user_watch_history[str(anime_id)]["episode"]
            print(f"[bold cyan]Continuing from Episode:[/] [bold]{episode_number}[/]")
        elif selected_anime_anilist["mediaListEntry"]:
            episode_number = str(
                (selected_anime_anilist["mediaListEntry"] or {"progress": ""}).get(
                    "progress"
                )
            )
            if episode_number not in episodes:
                episode_number = ""
            print(f"[bold cyan]Continuing from Episode:[/] [bold]{episode_number}[/]")
        else:
            episode_number = ""

    if not episode_number:
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
            episode_number = fuzzy_inquirer(
                choices,
                "Select Episode",
            )

    if episode_number == "Back":
        anilist_media_actions_menu(config, fastanime_runtime_state)
        return
    start_time = user_watch_history.get(str(anime_id), {}).get("start_time", "0")
    config.update_watch_history(anime_id, episode_number, start_time=start_time)

    # update internal config
    fastanime_runtime_state.episodes = episodes
    # fastanime_runtime_state.episode_title = episode["title"]
    fastanime_runtime_state.episode_number = episode_number

    # next interface
    fetch_streams(config, fastanime_runtime_state)


def fetch_anime_episode(config, fastanime_runtime_state: FastAnimeRuntimeState):
    selected_anime: "SearchResult" = fastanime_runtime_state._anime
    anime_provider = config.anime_provider
    with Progress() as progress:
        progress.add_task("Fetching Anime Info...", total=None)
        fastanime_runtime_state.anime = anime_provider.get_anime(
            selected_anime["id"], fastanime_runtime_state.selected_anime_anilist
        )
    if not fastanime_runtime_state.anime:
        print(
            "Sth went wrong :cry: this could mean the provider is down or your internet"
        )
        if not config.use_rofi:
            input("Enter to continue...")
        else:
            if not Rofi.confirm("Sth went wrong!!Enter to continue..."):
                exit(1)
        fetch_anime_episode(config, fastanime_runtime_state)
        return

    fetch_episode(config, fastanime_runtime_state)


def provide_anime(config: "Config", fastanime_runtime_state: FastAnimeRuntimeState):
    # user config
    translation_type = config.translation_type.lower()

    # internal config
    selected_anime_title = fastanime_runtime_state.selected_anime_title_anilist

    anime_data: "AnilistBaseMediaDataSchema" = (
        fastanime_runtime_state.selected_anime_anilist
    )
    anime_provider = config.anime_provider

    # search and get the requested title from provider
    with Progress() as progress:
        progress.add_task("Fetching Search Results...", total=None)
        search_results = anime_provider.search_for_anime(
            selected_anime_title,
            translation_type,
            fastanime_runtime_state.selected_anime_anilist,
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
        provide_anime(config, fastanime_runtime_state)
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
            anime_title = fuzzy_inquirer(
                choices,
                "Select Search Result",
            )
        if anime_title == "Back":
            anilist_media_actions_menu(config, fastanime_runtime_state)
            return
    fastanime_runtime_state.anime_title = (
        anime_normalizer.get(anime_title) or anime_title
    )
    fastanime_runtime_state._anime = search_results[anime_title]
    fetch_anime_episode(config, fastanime_runtime_state)


#
#  ---- ANILIST MEDIA ACTIONS MENU ----
#
def anilist_media_actions_menu(
    config: "Config", fastanime_runtime_state: FastAnimeRuntimeState
):
    """The menu responsible for handling all media actions such as watching a trailer or streaming it

    Args:
        config: [TODO:description]
        fastanime_runtime_state: [TODO:description]
    """
    selected_anime_anilist: "AnilistBaseMediaDataSchema" = (
        fastanime_runtime_state.selected_anime_anilist
    )
    selected_anime_title_anilist: str = (
        fastanime_runtime_state.selected_anime_title_anilist
    )

    # the progress of the episode based on what  anilist has not locally
    progress = (selected_anime_anilist["mediaListEntry"] or {"progress": 0}).get(
        "progress", 0
    )
    episodes_total = selected_anime_anilist["episodes"] or "Inf"

    def _watch_trailer(
        config: "Config", fastanime_runtime_state: FastAnimeRuntimeState
    ):
        """Helper function to watch trailers with

        Args:
            config: [TODO:description]
            fastanime_runtime_state: [TODO:description]
        """
        if trailer := selected_anime_anilist.get("trailer"):
            trailer_url = "https://youtube.com/watch?v=" + trailer["id"]
            print("[bold magenta]Watching Trailer of:[/]", selected_anime_title_anilist)
            run_mpv(
                trailer_url,
                ytdl_format=config.format,
            )
            anilist_media_actions_menu(config, fastanime_runtime_state)
        else:
            if not config.use_rofi:
                print("no trailer available :confused:")
                input("Enter to continue...")
            else:
                if not Rofi.confirm("No trailler found!!Enter to continue"):
                    exit(0)
            anilist_media_actions_menu(config, fastanime_runtime_state)

    def _add_to_list(config: "Config", fastanime_runtime_state: FastAnimeRuntimeState):
        """Helper function to update an anime's media_list_type

        Args:
            config: [TODO:description]
            fastanime_runtime_state: [TODO:description]
        """
        anime_lists = {
            "Watching": "CURRENT",
            "Paused": "PAUSED",
            "Planning": "PLANNING",
            "Dropped": "DROPPED",
            "Rewatching": "REPEATING",
            "Completed": "COMPLETED",
        }
        choices = list(anime_lists.keys())
        if config.use_fzf:
            anime_list = fzf.run(
                choices,
                "Choose the list you want to add to",
                "Add your animelist",
            )
        elif config.use_rofi:
            anime_list = Rofi.run(choices, "Choose list you want to add to")
        else:
            anime_list = fuzzy_inquirer(
                choices,
                "Choose the list you want to add to",
            )
        result = AniList.update_anime_list(
            {"status": anime_lists[anime_list], "mediaId": selected_anime_anilist["id"]}
        )
        if not result[0]:
            print("Failed to update", result)
        else:
            print(
                f"Successfully added {selected_anime_title_anilist} to your {anime_list} list :smile:"
            )
        if not config.use_rofi:
            input("Enter to continue...")
        anilist_media_actions_menu(config, fastanime_runtime_state)

    def _score_anime(config: "Config", fastanime_runtime_state: FastAnimeRuntimeState):
        """Helper function to score anime on anilist from terminal or rofi

        Args:
            config: [TODO:description]
            fastanime_runtime_state: [TODO:description]
        """
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
            {"scoreRaw": score, "mediaId": selected_anime_anilist["id"]}
        )
        if not result[0]:
            print("Failed to update", result)
        else:
            print(f"Successfully scored {selected_anime_title_anilist}; score: {score}")
        if not config.use_rofi:
            input("Enter to continue...")
        anilist_media_actions_menu(config, fastanime_runtime_state)

    # FIX: For some reason this fails to delete
    def _remove_from_list(
        config: "Config", fastanime_runtime_state: FastAnimeRuntimeState
    ):
        """Remove an anime from  your media list

        Args:
            config: [TODO:description]
            fastanime_runtime_state: [TODO:description]
        """
        if Confirm.ask(
            f"Are you sure you want to procede, the folowing action will permanently remove {selected_anime_title_anilist} from your list and your progress will be erased",
            default=False,
        ):
            success, data = AniList.delete_medialist_entry(selected_anime_anilist["id"])
            if not success or not data:
                print("Failed to delete", data)
            elif not data.get("deleted"):
                print("Failed to delete", data)
            else:
                print("Successfully deleted :cry:", selected_anime_title_anilist)
        else:
            print(selected_anime_title_anilist, ":relieved:")
        if not config.use_rofi:
            input("Enter to continue...")
        anilist_media_actions_menu(config, fastanime_runtime_state)

    def _change_translation_type(
        config: "Config", fastanime_runtime_state: "FastAnimeRuntimeState"
    ):
        """Change the translation type to use

        Args:
            config: [TODO:description]
            fastanime_runtime_state: [TODO:description]
        """
        # prompt for new translation type
        options = ["Sub", "Dub"]
        if config.use_fzf:
            translation_type = fzf.run(
                options, prompt="Select Translation Type:", header="Language Options"
            )
        elif config.use_rofi:
            translation_type = Rofi.run(options, "Select Translation Type")
        else:
            translation_type = fuzzy_inquirer(
                options,
                "Select translation type",
            )

        # update internal config
        config.translation_type = translation_type.lower()

        anilist_media_actions_menu(config, fastanime_runtime_state)

    def _view_info(config: "Config", fastanime_runtime_state: "FastAnimeRuntimeState"):
        """helper function to view info of an anime from terminal

        Args:
            config ([TODO:parameter]): [TODO:description]
            fastanime_runtime_state ([TODO:parameter]): [TODO:description]
        """
        from rich.console import Console
        from rich.prompt import Confirm

        from ...Utility import anilist_data_helper
        from ...Utility.utils import remove_html_tags
        from ..utils.print_img import print_img

        clear()
        console = Console()

        print_img(selected_anime_anilist["coverImage"]["large"])
        console.print(
            "[bold cyan]Title(jp): ", selected_anime_anilist["title"]["romaji"]
        )
        console.print(
            "[bold cyan]Title(eng): ", selected_anime_anilist["title"]["english"]
        )
        console.print("[bold cyan]Popularity: ", selected_anime_anilist["popularity"])
        console.print("[bold cyan]Favourites: ", selected_anime_anilist["favourites"])
        console.print("[bold cyan]Status: ", selected_anime_anilist["status"])
        console.print(
            "[bold cyan]Start Date: ",
            anilist_data_helper.format_anilist_date_object(
                selected_anime_anilist["startDate"]
            ),
        )
        console.print(
            "[bold cyan]End Date: ",
            anilist_data_helper.format_anilist_date_object(
                selected_anime_anilist["endDate"]
            ),
        )
        # console.print("[bold cyan]Season: ", selected_anime["season"])
        console.print("[bold cyan]Episodes: ", selected_anime_anilist["episodes"])
        console.print(
            "[bold cyan]Tags: ",
            anilist_data_helper.format_list_data_with_comma(
                [tag["name"] for tag in selected_anime_anilist["tags"]]
            ),
        )
        console.print(
            "[bold cyan]Genres: ",
            anilist_data_helper.format_list_data_with_comma(
                selected_anime_anilist["genres"]
            ),
        )
        if selected_anime_anilist["nextAiringEpisode"]:
            console.print(
                "[bold cyan]Next Episode: ",
                anilist_data_helper.extract_next_airing_episode(
                    selected_anime_anilist["nextAiringEpisode"]
                ),
            )
        console.print(
            "[bold underline cyan]Description\n[/]",
            remove_html_tags(str(selected_anime_anilist["description"])),
        )
        if Confirm.ask("Enter to continue...", default=True):
            anilist_media_actions_menu(config, fastanime_runtime_state)
        return

    def _toggle_auto_select(
        config: "Config", fastanime_runtime_state: "FastAnimeRuntimeState"
    ):
        """helper function to toggle auto select anime title using fuzzy matching

        Args:
            config: [TODO:description]
            fastanime_runtime_state: [TODO:description]
        """
        config.auto_select = not config.auto_select
        anilist_media_actions_menu(config, fastanime_runtime_state)

    def _toggle_continue_from_history(
        config: "Config", fastanime_runtime_state: "FastAnimeRuntimeState"
    ):
        """helper function to toggle continue from history

        Args:
            config: [TODO:description]
            fastanime_runtime_state: [TODO:description]
        """
        config.continue_from_history = not config.continue_from_history
        anilist_media_actions_menu(config, fastanime_runtime_state)

    def _toggle_auto_next(
        config: "Config", fastanime_runtime_state: "FastAnimeRuntimeState"
    ):
        """helper function to toggle auto next

        Args:
            config: [TODO:description]
            fastanime_runtime_state: [TODO:description]
        """
        config.auto_next = not config.auto_next
        anilist_media_actions_menu(config, fastanime_runtime_state)

    def _change_provider(
        config: "Config", fastanime_runtime_state: "FastAnimeRuntimeState"
    ):
        """Helper function to change provider to use

        Args:
            config: [TODO:description]
            fastanime_runtime_state: [TODO:description]
        """
        options = ["allanime", "animepahe"]
        if config.use_fzf:
            provider = fzf.run(
                options, prompt="Select Translation Type:", header="Language Options"
            )
        elif config.use_rofi:
            provider = Rofi.run(options, "Select Translation Type")
        else:
            provider = fuzzy_inquirer(
                options,
                "Select translation type",
            )

        config.provider = provider
        config.anime_provider.provider = provider
        config.anime_provider.lazyload_provider()

        anilist_media_actions_menu(config, fastanime_runtime_state)

    def _stream_anime(
        config: "Config", fastanime_runtime_state: "FastAnimeRuntimeState"
    ):
        """helper function to go to the next menu respecting your config

        Args:
            config: [TODO:description]
            fastanime_runtime_state: [TODO:description]
        """
        provide_anime(config, fastanime_runtime_state)

    def _select_episode_to_stream(
        config: "Config", fastanime_runtime_state: "FastAnimeRuntimeState"
    ):
        """Convinience function to disable continue from history and show the episodes menu

        Args:
            config: [TODO:description]
            fastanime_runtime_state: [TODO:description]
        """
        config.continue_from_history = False
        provide_anime(config, fastanime_runtime_state)

    icons = config.icons
    options = {
        f"{'📽️ ' if icons else ''}Stream ({progress}/{episodes_total})": _stream_anime,
        f"{'📽️ ' if icons else ''}Episodes": _select_episode_to_stream,
        f"{'📼 ' if icons else ''}Watch Trailer": _watch_trailer,
        f"{'✨ ' if icons else ''}Score Anime": _score_anime,
        f"{'📥 ' if icons else ''}Add to List": _add_to_list,
        f"{'📤 ' if icons else ''}Remove from List": _remove_from_list,
        f"{'📖 ' if icons else ''}View Info": _view_info,
        f"{'🎧 ' if icons else ''}Change Translation Type": _change_translation_type,
        f"{'💽 ' if icons else ''}Change Provider": _change_provider,
        f"{'🔘 ' if icons else ''}Toggle auto select anime": _toggle_auto_select,  #  WARN: problematic if you choose an anime that doesnt match id
        f"{'💠 ' if icons else ''}Toggle auto next episode": _toggle_auto_next,
        f"{'🔘 ' if icons else ''}Toggle continue from history": _toggle_continue_from_history,
        f"{'🔙 ' if icons else ''}Back": anilist_results_menu,
        f"{'❌ ' if icons else ''}Exit": exit_app,
    }
    choices = list(options.keys())
    if config.use_fzf:
        action = fzf.run(choices, prompt="Select Action:", header="Anime Menu")
    elif config.use_rofi:
        action = Rofi.run(choices, "Select Action")
    else:
        action = fuzzy_inquirer(
            choices,
            "Select Action",
        )
    options[action](config, fastanime_runtime_state)


#
#   ---- ANILIST RESULTS MENU ----
#
def anilist_results_menu(
    config: "Config", fastanime_runtime_state: FastAnimeRuntimeState
):
    """The menu that handles and displays the results of an anilist action enabling using to select anime of choice

    Args:
        config: [TODO:description]
        fastanime_runtime_state: [TODO:description]
    """
    search_results = fastanime_runtime_state.anilist_data["data"]["Page"]["media"]

    anime_data = {}
    for anime in search_results:
        anime: "AnilistBaseMediaDataSchema"

        # determine the progress of watching the anime based on whats in anilist data !! NOT LOCALLY
        progress = (anime["mediaListEntry"] or {"progress": 0}).get("progress", 0)

        # if the max episodes is none set it to inf meaning currently not determinable or infinity
        episodes_total = anime["episodes"] or "Inf"

        # set the actual title and ensure its a string since even after this it may be none
        title = str(
            anime["title"][config.preferred_language] or anime["title"]["romaji"]
        )
        # this process is mostly need inoder for the preview to work correctly
        title = sanitize_filename(f"{title} ({progress} of {episodes_total})")

        # Check if the anime is currently airing and has new/unwatched episodes
        if (
            anime["status"] == "RELEASING"
            and anime["nextAiringEpisode"]
            and progress > 0
        ):
            last_aired_episode = anime["nextAiringEpisode"]["episode"] - 1
            if last_aired_episode - progress > 0:
                title += f" 🔹{last_aired_episode - progress} new episode(s)🔹"

        # add the anime to the anime data dict setting the key to the title
        # this dict is used for promting the title and maps directly to the anime object of interest containing the actual data
        anime_data[title] = anime

    # prompt for the anime of choice
    choices = [*anime_data.keys(), "Back"]
    if config.use_fzf:
        if config.preview:
            from .utils import get_fzf_preview

            preview = get_fzf_preview(search_results, anime_data.keys())
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
        if config.preview:
            from .utils import IMAGES_CACHE_DIR, get_rofi_icons

            get_rofi_icons(search_results, anime_data.keys())
            choices = []
            for title in anime_data.keys():
                icon_path = os.path.join(IMAGES_CACHE_DIR, title)
                choices.append(f"{title}\0icon\x1f{icon_path}")
            choices.append("Back")
            selected_anime_title = Rofi.run_with_icons(choices, "Select Anime")
        else:
            selected_anime_title = Rofi.run(choices, "Select Anime")
    else:
        selected_anime_title = fuzzy_inquirer(
            choices,
            "Select Anime",
        )
    if selected_anime_title == "Back":
        fastanime_main_menu(config, fastanime_runtime_state)
        return

    selected_anime: "AnilistBaseMediaDataSchema" = anime_data[selected_anime_title]
    fastanime_runtime_state.selected_anime_anilist = selected_anime
    fastanime_runtime_state.selected_anime_title_anilist = (
        selected_anime["title"]["romaji"] or selected_anime["title"]["english"]
    )
    fastanime_runtime_state.selected_anime_id_anilist = selected_anime["id"]

    anilist_media_actions_menu(config, fastanime_runtime_state)


#
# ---- FASTANIME MAIN MENU ----
#
def handle_animelist(
    config: "Config", fastanime_runtime_state: "FastAnimeRuntimeState", list_type: str
):
    """A helper function that handles user media lists

    Args:
        fastanime_runtime_state ([TODO:parameter]): [TODO:description]
        config: [TODO:description]
        list_type: [TODO:description]

    Returns:
        [TODO:return]
    """
    if not config.user:
        if not config.use_rofi:
            print("You haven't logged in please run: fastanime anilist login")
            input("Enter to continue...")
        else:
            if not Rofi.confirm("You haven't logged in!!Enter to continue"):
                exit(1)
        fastanime_main_menu(config, fastanime_runtime_state)
        return
    # determine the watch list to get
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

    # get the media list
    anime_list = AniList.get_anime_list(status)
    # handle null
    if not anime_list:
        print("Sth went wrong", anime_list)
        if not config.use_rofi:
            input("Enter to continue")
        else:
            if not Rofi.confirm("Sth went wrong!!Enter to continue..."):
                exit(1)
        fastanime_main_menu(config, fastanime_runtime_state)
        return
    # handle failure
    if not anime_list[0] or not anime_list[1]:
        print("Sth went wrong", anime_list)
        if not config.use_rofi:
            input("Enter to continue")
        else:
            if not Rofi.confirm("Sth went wrong!!Enter to continue..."):
                exit(1)
        # recall anilist menu
        fastanime_main_menu(config, fastanime_runtime_state)
        return
    # injecting the data is the simplest way since the ui expects a field called media that should have media type
    media = [
        mediaListItem["media"]
        for mediaListItem in anime_list[1]["data"]["Page"]["mediaList"]
    ]
    anime_list[1]["data"]["Page"]["media"] = media  # pyright:ignore
    return anime_list


def fastanime_main_menu(
    config: "Config", fastanime_runtime_state: FastAnimeRuntimeState
):
    """The main entry point to the anilist command

    Args:
        config: An object containing cconfiguration data
        fastanime_runtime_state: A query dict used to store data during navigation of the ui # initially this was very messy
    """

    def _anilist_search():
        """A function that enables seaching of an anime

        Returns:
            [TODO:return]
        """
        # TODO: Add filters and other search features
        if config.use_rofi:
            search_term = str(Rofi.ask("Search for"))
        else:
            search_term = Prompt.ask("[cyan]Search for[/]")

        return AniList.search(query=search_term)

    def _anilist_random():
        """A function that generates random anilist ids enabling random discovery of anime

        Returns:
            [TODO:return]
        """
        random_anime = range(1, 15000)
        random_anime = random.sample(random_anime, k=50)

        return AniList.search(id_in=list(random_anime))

    def _watch_history():
        """Function that lets you see all the anime that has locally been saved to your watch history

        Returns:
            [TODO:return]
        """
        watch_history = list(map(int, config.watch_history.keys()))
        return AniList.search(id_in=watch_history, sort="TRENDING_DESC")

    # WARNING: Will probably be depracated
    def _anime_list():
        anime_list = config.anime_list
        return AniList.search(id_in=anime_list)

    def _edit_config():
        """Helper function to edit your config when the ui is still running"""

        from click import edit

        edit(filename=USER_CONFIG_PATH)
        if config.use_rofi:
            config.load_config()
            config.use_rofi = True
            config.use_fzf = False
        else:
            config.load_config()

        fastanime_main_menu(config, fastanime_runtime_state)

    icons = config.icons
    # each option maps to anilist data that is described by the option name
    options = {
        f"{'🔥 ' if icons else ''}Trending": AniList.get_trending,
        f"{'📺 ' if icons else ''}Watching": lambda media_list_type="Watching": handle_animelist(
            config, fastanime_runtime_state, media_list_type
        ),
        f"{'⏸  ' if icons else ''}Paused": lambda media_list_type="Paused": handle_animelist(
            config, fastanime_runtime_state, media_list_type
        ),
        f"{'🚮 ' if icons else ''}Dropped": lambda media_list_type="Dropped": handle_animelist(
            config, fastanime_runtime_state, media_list_type
        ),
        f"{'📑 ' if icons else ''}Planned": lambda media_list_type="Planned": handle_animelist(
            config, fastanime_runtime_state, media_list_type
        ),
        f"{'✅ ' if icons else ''}Completed": lambda media_list_type="Completed": handle_animelist(
            config, fastanime_runtime_state, media_list_type
        ),
        f"{'🔁 ' if icons else ''}Rewatching": lambda media_list_type="Repeating": handle_animelist(
            config, fastanime_runtime_state, media_list_type
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
        f"{'📝 ' if icons else ''}Edit Config": _edit_config,
        f"{'❌ ' if icons else ''}Exit": exit_app,
    }
    # prompt user to select an action
    choices = list(options.keys())
    if config.use_fzf:
        action = fzf.run(
            choices,
            prompt="Select Action: ",
            header="Anilist Menu",
        )
    elif config.use_rofi:
        action = Rofi.run(choices, "Select Action")
    else:
        action = fuzzy_inquirer(
            choices,
            "Select Action",
        )
    anilist_data = options[action]()
    # anilist data is a (bool,data)
    # the bool indicated success
    if anilist_data[0]:
        fastanime_runtime_state.anilist_data = anilist_data[1]
        anilist_results_menu(config, fastanime_runtime_state)

    else:
        print(anilist_data[1])
        if not config.use_rofi:
            input("Enter to continue...")
        else:
            if not Rofi.confirm("Sth went wrong!!Enter to continue..."):
                exit(1)
        # recall the anilist function for the user to reattempt their choice
        fastanime_main_menu(config, fastanime_runtime_state)
