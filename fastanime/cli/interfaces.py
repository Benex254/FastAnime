from __future__ import annotations

from InquirerPy import inquirer
from rich import print

from ..libs.anilist.anilist import AniList
from ..libs.anilist.anilist_data_schema import AnilistDataSchema
from ..libs.anime_provider.allanime.api import anime_provider
from .config import Config
from .utils.mpv import mpv
from .utils.utils import clear, fuzzy_inquirer, get_selected_anime, get_selected_server


def fetch_episode(config: Config, anime, translation_type, selected_anime):
    # fetch episode
    episode_number = fuzzy_inquirer(
        "Select Episode:",
        [*anime["show"]["availableEpisodesDetail"][translation_type], "back"],
    )
    if episode_number == "back":
        anime_provider_(
            config,
            selected_anime[0]["name"],
        )
        return
    episode = anime_provider.get_anime_episode(
        selected_anime[0]["_id"], episode_number, config.translation_type
    )

    fetch_streams(config, episode, anime, translation_type, selected_anime)


def fetch_streams(config: Config, episode, *args):
    episode_streams = list(anime_provider.get_episode_streams(episode))

    server = fuzzy_inquirer(
        "Select Server:", [episode_stream[0] for episode_stream in episode_streams]
    )
    selected_server = get_selected_server(server, episode_streams)

    quality = config.quality
    links = selected_server[1]["links"]
    if quality > len(links) - 1:
        quality = config.quality = len(links) - 1
    elif quality < 0:
        quality = config.quality = 0
    stream_link = links[quality]["link"]
    print(
        "[bold magenta]Now playing:[/]",
        args[-1][0]["name"],
        "[bold magenta] Episode: [/]",
        episode["episode"]["episodeString"],
    )
    mpv(stream_link)
    clear()
    player_controls(config, episode, links, *args)


def player_controls(config: Config, episode, links: list, *args):
    anime = args[0]
    selected_anime = args[-1]
    episodes = [*anime["show"]["availableEpisodesDetail"][config.translation_type]]
    episodes = sorted(episodes, key=int)
    current_episode = episode["episode"]["episodeString"]

    def _back():
        fetch_streams(config, episode, *args)

    def _replay():
        stream_link = links[config.quality]["link"]
        print(
            "[bold magenta]Now playing:[/]",
            args[-1][0]["name"],
            "[bold magenta] Episode: [/]",
            episode["episode"]["episodeString"],
        )
        mpv(stream_link)
        clear()
        player_controls(config, episode, links, *args)

    def _next_episode():
        next_episode = episodes.index(current_episode) + 1
        if next_episode >= len(episodes):
            next_episode = len(episodes) - 1
        episode = anime_provider.get_anime_episode(
            selected_anime[0]["_id"], episodes[next_episode], config.translation_type
        )

        fetch_streams(config, episode, *args)

    def _episodes():
        fetch_episode(config, *args)

    def _previous_episode():
        prev_episode = episodes.index(current_episode) - 1
        if prev_episode <= 0:
            prev_episode = 0
        episode = anime_provider.get_anime_episode(
            selected_anime[0]["_id"], episodes[prev_episode], config.translation_type
        )

        fetch_streams(config, episode, *args)

    def _change_quality():
        options = [link["link"] for link in links]
        quality = fuzzy_inquirer("Select Quality:", options)
        config.quality = options.index(quality)  # set quality
        player_controls(config, episode, links, *args)

    def _change_translation_type():
        options = ["sub", "dub"]
        translation_type = fuzzy_inquirer("Select Translation Type:", options)
        config.translation_type = translation_type  # set trannslation type
        player_controls(config, episode, links, *args)

    options = {
        "Replay": _replay,
        "Next Episode": _next_episode,
        "Episodes": _episodes,
        "Previous Episode": _previous_episode,
        "Change Quality": _change_quality,
        "Change Translation Type": _change_translation_type,
        "Back": _back,
    }

    action = fuzzy_inquirer("Select Action:", options.keys())
    options[action]()


def anime_provider_(config: Config, anime_title, **kwargs):
    translation_type = config.translation_type
    search_results = anime_provider.search_for_anime(anime_title, translation_type)
    search_results_anime_titles = [
        anime["name"] for anime in search_results["shows"]["edges"]
    ]
    selected_anime_title = fuzzy_inquirer(
        "Select Search Result:",
        [*search_results_anime_titles, "back"],
        default=kwargs.get("default_anime_title", ""),
    )
    if selected_anime_title == "back":
        anilist(config)
        return
    fetch_anime_epiosode(
        config,
        selected_anime_title,
        search_results,
    )


def fetch_anime_epiosode(config, selected_anime_title, search_results):
    translation_type = config.translation_type
    selected_anime = get_selected_anime(selected_anime_title, search_results)
    anime = anime_provider.get_anime(selected_anime[0]["_id"])

    fetch_episode(config, anime, translation_type, selected_anime)


def _stream(config, anilist_data: AnilistDataSchema, preferred_lang="romaji"):
    anime_titles = [
        str(anime["title"][preferred_lang])
        for anime in anilist_data["data"]["Page"]["media"]
    ]
    selected_anime_title = fuzzy_inquirer("Select Anime:", anime_titles)
    anime_provider_(
        config, selected_anime_title, default_anime_title=selected_anime_title
    )


def anilist_options(config, anilist_data: AnilistDataSchema):
    def _watch_trailer():
        pass

    def _add_to_list():
        pass

    def _remove_from_list():
        pass

    def _view_info():
        pass

    options = {
        "stream": _stream,
        "watch trailer": _watch_trailer,
        "add to list": _add_to_list,
        "remove from list": _remove_from_list,
        "view info": _view_info,
        "back": anilist,
    }
    action = fuzzy_inquirer("Select Action:", options.keys())
    options[action](config, anilist_data)


def anilist(config, *args, **kwargs):
    def _anilist_search():
        search_term = inquirer.text(
            "Search:", instruction="Enter anime to search for"
        ).execute()

        return AniList.search(query=search_term)

    options = {
        "trending": AniList.get_trending,
        "search": _anilist_search,
        "most popular anime": AniList.get_most_popular,
        "most favourite anime": AniList.get_most_favourite,
        "most scored anime": AniList.get_most_scored,
        "upcoming anime": AniList.get_most_favourite,
        "recently updated anime": AniList.get_most_recently_updated,
    }
    action = fuzzy_inquirer("Select Action:", options.keys())
    anilist_data = options[action]()
    if anilist_data[0]:
        anilist_options(config, anilist_data[1])
