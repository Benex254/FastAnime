import json
import logging
from typing import Iterator

import requests
from requests.exceptions import Timeout

from ....libs.anime_provider.allanime.types import AllAnimeEpisode
from ....libs.anime_provider.types import Anime, Server
from .constants import (
    ALLANIME_API_ENDPOINT,
    ALLANIME_BASE,
    ALLANIME_REFERER,
    USER_AGENT,
)
from .gql_queries import ALLANIME_EPISODES_GQL, ALLANIME_SEARCH_GQL, ALLANIME_SHOW_GQL
from .normalizer import normalize_anime, normalize_search_results
from .utils import decode_hex_string

Logger = logging.getLogger(__name__)


# TODO: create tests for the api
#
# ** Based on ani-cli **
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
            if response.status_code == 200:
                return response.json()["data"]
            else:
                Logger.error("allanime(ERROR): ", response.text)
                return {}
        except Timeout:
            Logger.error(
                "allanime(Error):Timeout exceeded this could mean allanime is down or you have lost internet connection"
            )
            return {}
        except Exception as e:
            Logger.error(f"allanime:Error: {e}")
            return {}

    def search_for_anime(
        self,
        user_query: str,
        translation_type: str = "sub",
        nsfw=True,
        unknown=True,
        **kwargs,
    ):
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
        try:

            search_results = self._fetch_gql(ALLANIME_SEARCH_GQL, variables)
            return normalize_search_results(search_results)  # pyright:ignore
        except Exception as e:
            Logger.error(f"FA(AllAnime): {e}")
            return {}

    def get_anime(self, allanime_show_id: str):
        variables = {"showId": allanime_show_id}
        try:
            anime = self._fetch_gql(ALLANIME_SHOW_GQL, variables)
            return normalize_anime(anime["show"])
        except Exception as e:
            Logger.error(f"FA(AllAnime): {e}")
            return None

    def get_anime_episode(
        self, allanime_show_id: str, episode_string: str, translation_type: str = "sub"
    ) -> AllAnimeEpisode | dict:
        variables = {
            "showId": allanime_show_id,
            "translationType": translation_type,
            "episodeString": episode_string,
        }
        try:
            episode = self._fetch_gql(ALLANIME_EPISODES_GQL, variables)
            return episode["episode"]  # pyright: ignore
        except Exception as e:
            Logger.error(f"FA(AllAnime): {e}")
            return {}

    def get_episode_streams(
        self, anime: Anime, episode_number: str, translation_type="sub"
    ) -> Iterator[Server] | None:
        anime_id = anime["id"]
        allanime_episode = self.get_anime_episode(
            anime_id, episode_number, translation_type
        )
        if not allanime_episode:
            return {}

        embeds = allanime_episode["sourceUrls"]
        try:
            for embed in embeds:
                try:
                    # filter the working streams
                    if embed.get("sourceName", "") not in (
                        "Sak",
                        "Kir",
                        "S-mp4",
                        "Luf-mp4",
                        "Default",
                    ):
                        continue
                    url = embed.get("sourceUrl")

                    if not url:
                        continue
                    if url.startswith("--"):
                        url = url[2:]

                    # get the stream url for an episode of the defined source names
                    parsed_url = decode_hex_string(url)
                    embed_url = f"https://{ALLANIME_BASE}{parsed_url.replace('clock', 'clock.json')}"
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
                                yield {
                                    "server": "gogoanime",
                                    "episode_title": (
                                        allanime_episode["notes"] or f'{anime["title"]}'
                                    )
                                    + f"; Episode {episode_number}",
                                    "links": resp.json()["links"],
                                }  # pyright:ignore
                            case "Kir":
                                Logger.debug("allanime:Found streams from wetransfer")
                                yield {
                                    "server": "wetransfer",
                                    "episode_title": (
                                        allanime_episode["notes"] or f'{anime["title"]}'
                                    )
                                    + f"; Episode {episode_number}",
                                    "links": resp.json()["links"],
                                }  # pyright:ignore
                            case "S-mp4":
                                Logger.debug("allanime:Found streams from sharepoint")
                                yield {
                                    "server": "sharepoint",
                                    "episode_title": (
                                        allanime_episode["notes"] or f'{anime["title"]}'
                                    )
                                    + f"; Episode {episode_number}",
                                    "links": resp.json()["links"],
                                }  # pyright:ignore
                            case "Sak":
                                Logger.debug("allanime:Found streams from dropbox")
                                yield {
                                    "server": "dropbox",
                                    "episode_title": (
                                        allanime_episode["notes"] or f'{anime["title"]}'
                                    )
                                    + f"; Episode {episode_number}",
                                    "links": resp.json()["links"],
                                }  # pyright:ignore
                            case "Default":
                                Logger.debug("allanime:Found streams from wixmp")
                                yield {
                                    "server": "wixmp",
                                    "episode_title": (
                                        allanime_episode["notes"] or f'{anime["title"]}'
                                    )
                                    + f"; Episode {episode_number}",
                                    "links": resp.json()["links"],
                                }  # pyright:ignore
                except Timeout:
                    Logger.error(
                        "Timeout has been exceeded this could mean allanime is down or you have lost internet connection"
                    )
                    return []
                except Exception as e:
                    Logger.error(f"FA(Allanime): {e}")
                    return []
        except Exception as e:
            Logger.error(f"FA(Allanime): {e}")
            return []


if __name__ == "__main__":
    anime_provider = AllAnimeAPI()
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

    search_results = search_results["results"]
    options = {show["title"]: show for show in search_results}
    anime = run_fzf(options.keys())
    if anime is None:
        print("No anime was selected")
        sys.exit(1)

    anime_result = options[anime]
    anime_data = anime_provider.get_anime(anime_result["id"])
    if not anime_data:
        raise Exception("Anime not found")
    availableEpisodesDetail = anime_data["availableEpisodesDetail"]
    if not availableEpisodesDetail.get(translation.strip()):
        raise Exception("No episodes found")

    stream_link = True
    while stream_link != "quit":
        print("select episode")
        episode = run_fzf(availableEpisodesDetail[translation.strip()])
        if episode is None:
            print("No episode was selected")
            sys.exit(1)

        if not anime_data:
            print("Sth went wrong")
            break
        episode_streams_ = anime_provider.get_episode_streams(
            anime_data, episode, translation.strip()
        )
        if episode_streams_ is None:
            raise Exception("Episode not found")

        episode_streams = list(episode_streams_)
        stream_links = []
        for server in episode_streams:
            stream_links.extend([link["link"] for link in server["links"]])
        stream_links.append("back")
        stream_link = run_fzf(stream_links)
        if stream_link == "quit":
            print("Have a nice day")
            sys.exit()
        if not stream_link:
            raise Exception("No stream was selected")

        title = episode_streams[0].get(
            "episode_title", "%s: Episode %s" % (anime_data["title"], episode)
        )
        subprocess.run(["mpv", f"--title={title}", stream_link])
