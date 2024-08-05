import json
import logging
from typing import Generator

import requests
from requests.exceptions import Timeout
from rich import print
from rich.progress import Progress

from ....libs.anime_provider.allanime.types import (
    AllAnimeEpisode,
    AllAnimeSearchResults,
    AllAnimeShow,
    AllAnimeStreams,
    Server,
)
from .constants import (
    ALLANIME_API_ENDPOINT,
    ALLANIME_BASE,
    ALLANIME_REFERER,
    USER_AGENT,
)
from .gql_queries import ALLANIME_EPISODES_GQL, ALLANIME_SEARCH_GQL, ALLANIME_SHOW_GQL
from .utils import decode_hex_string

Logger = logging.getLogger(__name__)


# TODO: create tests for the api
#
class AllAnimeAPI:
    """
    Provides a fast and effective interface to AllAnime site.
    """

    api_endpoint = ALLANIME_API_ENDPOINT

    def _fetch_gql(self, query: str, variables: dict):
        try:
            response = requests.get(
                self.api_endpoint,
                params={
                    "variables": json.dumps(variables),
                    "query": query,
                },
                headers={"Referer": ALLANIME_REFERER, "User-Agent": USER_AGENT},
                timeout=10,
            )
            return response.json()["data"]
        except Timeout as e:
            print(
                "Timeout has been exceeded :cry:. This could mean allanime is down or your internet is down"
            )
            Logger.error(f"allanime(Error): {e}")
            return {}
        except Exception as e:
            print("sth went wrong :confused:")
            Logger.error(f"allanime:Error: {e}")
            return {}

    def search_for_anime(
        self, user_query: str, translation_type: str = "sub", nsfw=True, unknown=True
    ) -> AllAnimeSearchResults:
        search = {"allowAdult": nsfw, "allowUnknown": unknown, "query": user_query}
        limit = 40
        translationtype = translation_type
        countryorigin = "all"
        page = 1
        variables = {
            "search": search,
            "limit": limit,
            "page": page,
            "translationtype": translationtype,
            "countryorigin": countryorigin,
        }
        with Progress() as progress:
            progress.add_task("[cyan]searching..", start=False, total=None)

            search_results = self._fetch_gql(ALLANIME_SEARCH_GQL, variables)
            return search_results  # pyright:ignore

    def get_anime(self, allanime_show_id: str) -> AllAnimeShow:
        variables = {"showId": allanime_show_id}
        with Progress() as progress:
            progress.add_task("[cyan]fetching anime..", start=False, total=None)
            anime = self._fetch_gql(ALLANIME_SHOW_GQL, variables)
            return anime["show"]  # pyright:ignore

    def get_anime_episode(
        self, allanime_show_id: str, episode_string: str, translation_type: str = "sub"
    ) -> AllAnimeEpisode:
        variables = {
            "showId": allanime_show_id,
            "translationType": translation_type,
            "episodeString": episode_string,
        }
        with Progress() as progress:
            progress.add_task("[cyan]fetching episode..", start=False, total=None)
            episode = self._fetch_gql(ALLANIME_EPISODES_GQL, variables)
            return episode  # pyright: ignore

    def get_episode_streams(self, allanime_episode_embeds_data) -> (
        Generator[
            tuple[Server, AllAnimeStreams],
            tuple[Server, AllAnimeStreams],
            tuple[Server, AllAnimeStreams],
        ]
        | dict
    ):
        if (
            not allanime_episode_embeds_data
            or allanime_episode_embeds_data.get("episode") is None
        ):
            return {}
        embeds = allanime_episode_embeds_data["episode"]["sourceUrls"]
        with Progress() as progress:
            progress.add_task("[cyan]fetching streams..", start=False, total=None)
            for embed in embeds:
                # filter the working streams
                if embed.get("sourceName", "") not in (
                    "Sak",
                    "Kir",
                    "S-mp4",
                    "Luf-mp4",
                ):
                    continue
                url = embed.get("sourceUrl")

                if not url:
                    continue
                if url.startswith("--"):
                    url = url[2:]

                # get the stream url for an episode of the defined source names
                parsed_url = decode_hex_string(url)
                embed_url = (
                    f"https://{ALLANIME_BASE}{parsed_url.replace('clock','clock.json')}"
                )
                resp = requests.get(
                    embed_url,
                    headers={
                        "Referer": ALLANIME_REFERER,
                        "User-Agent": USER_AGENT,
                    },
                    timeout=10,
                )
                if resp.status_code == 200:
                    match embed["sourceName"]:
                        case "Luf-mp4":
                            Logger.debug("allanime:Found streams from gogoanime")
                            print("[yellow]GogoAnime Fetched")
                            yield "gogoanime", resp.json()
                        case "Kir":
                            Logger.debug("allanime:Found streams from wetransfer")
                            print("[yellow]WeTransfer Fetched")
                            yield "wetransfer", resp.json()
                        case "S-mp4":
                            Logger.debug("allanime:Found streams from sharepoint")

                            print("[yellow]Sharepoint Fetched")
                            yield "sharepoint", resp.json()
                        case "Sak":
                            Logger.debug("allanime:Found streams from dropbox")
                            print("[yellow]Dropbox Fetched")
                            yield "dropbox", resp.json()
                else:
                    return {}


anime_provider = AllAnimeAPI()


if __name__ == "__main__":
    # lets see if it works :)
    import subprocess
    import sys

    from .utils import run_fzf

    anime = input("Enter the anime name: ")
    translation = input("Enter the translation type: ")

    search_results = anime_provider.search_for_anime(
        anime, translation_type=translation.strip()
    )

    if not search_results:
        raise Exception("No results found")

    search_results = search_results["shows"]["edges"]
    options = [show["name"] for show in search_results]
    anime = run_fzf(options)
    if anime is None:
        print("No anime was selected")
        sys.exit(1)

    anime_result = list(filter(lambda x: x["name"] == anime, search_results))[0]
    anime_data = anime_provider.get_anime(anime_result["_id"])
    if anime_data is None:
        raise Exception("Anime not found")
    availableEpisodesDetail = anime_data["availableEpisodesDetail"]
    if not availableEpisodesDetail.get(translation.strip()):
        raise Exception("No episodes found")

    print("select episode")
    stream_link = True
    while stream_link != "quit":
        episode = run_fzf(availableEpisodesDetail[translation.strip()])
        if episode is None:
            print("No episode was selected")
            sys.exit(1)

        episode_data = anime_provider.get_anime_episode(
            anime_result["_id"], episode, translation.strip()
        )
        if episode_data is None:
            raise Exception("Episode not found")

        episode_streams = anime_provider.get_episode_streams(episode_data)

        if not episode_streams:
            raise Exception("No streams found")
        episode_streams = list(episode_streams)
        stream_links = []
        for server in episode_streams:
            # FIXME:
            stream_links = [
                *stream_links,
                *[stream["link"] for stream in server[1]["links"]],
            ]
        stream_links = stream_link = run_fzf([*stream_links, "quit"])

        if stream_link == "quit":
            print("Have a nice day")
            sys.exit()
        if not stream_link:
            raise Exception("No stream was selected")

        subprocess.run(["mpv", stream_link])
