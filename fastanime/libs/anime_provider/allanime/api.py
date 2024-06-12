import json
import logging

import requests

from .gql_queries import ALLANIME_SHOW_GQL, ALLANIME_SEARCH_GQL, ALLANIME_EPISODES_GQL
from .constants import (
    ALLANIME_BASE,
    ALLANIME_REFERER,
    ALLANIME_API_ENDPOINT,
    USER_AGENT,
)
from .utils import decode_hex_string
from .data_types import (
    AllAnimeEpisode,
    AllAnimeSearchResults,
)

Logger = logging.getLogger(__name__)


# TODO: create tests for the api
#
class AllAnimeAPI:
    """
    Provides a fast and effective interface to AllAnime site.
    """

    api_endpoint = ALLANIME_API_ENDPOINT

    def _fetch_gql(self, query: str, variables: dict) -> dict:
        try:
            response = requests.get(
                self.api_endpoint,
                params={
                    "variables": json.dumps(variables),
                    "query": query,
                },
                headers={"Referer": ALLANIME_REFERER, "User-Agent": USER_AGENT},
            )
            if response.status_code != 200:
                return {}
            return response.json().get("data", {})
        except Exception as e:
            Logger.error(f"allanime:Error: {e}")
            return {}

    def search_for_anime(
        self, user_query: str, translation_type: str = "sub"
    ) -> AllAnimeSearchResults | dict:
        search = {"allowAdult": False, "allowUnknown": False, "query": user_query}
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
        return self._fetch_gql(ALLANIME_SEARCH_GQL, variables)

    def get_anime(self, allanime_show_id: str):
        variables = {"showId": allanime_show_id}
        return anime_provider._fetch_gql(ALLANIME_SHOW_GQL, variables)

    def get_anime_episode(
        self, allanime_show_id: str, episode_string: str, translation_type: str = "sub"
    ) -> AllAnimeEpisode | dict:
        variables = {
            "showId": allanime_show_id,
            "translationType": translation_type,
            "episodeString": episode_string,
        }
        return anime_provider._fetch_gql(ALLANIME_EPISODES_GQL, variables)

    def get_episode_streams(self, allanime_episode_embeds_data):
        if (
            not allanime_episode_embeds_data
            or allanime_episode_embeds_data.get("episode") is None
        ):
            return {}
        embeds = allanime_episode_embeds_data["episode"]["sourceUrls"]
        for embed in embeds:
            # filter the working streams
            if embed.get("sourceName", "") not in ("Sak", "Kir", "S-mp4", "Luf-mp4"):
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
            )
            if resp.status_code == 200:
                match embed["sourceName"]:
                    case "Luf-mp4":
                        Logger.debug("allanime:Found streams from gogoanime")
                        yield "gogoanime", resp.json()
                    case "Kir":
                        Logger.debug("allanime:Found streams from wetransfer")
                        yield "wetransfer", resp.json()
                    case "S-mp4":
                        Logger.debug("allanime:Found streams from sharepoint")
                        yield "sharepoint", resp.json()
                    case "Sak":
                        Logger.debug("allanime:Found streams from dropbox")
                        yield "dropbox", resp.json()
                    case _:
                        yield "Unknown", resp.json()
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
    availableEpisodesDetail = anime_data["show"]["availableEpisodesDetail"]
    if not availableEpisodesDetail.get(translation.strip()):
        raise Exception("No episodes found")

    print("select episode")
    stream_link = True
    while stream_link != "quit":
        episode = run_fzf(availableEpisodesDetail[translation.strip()])
        if episode is None:
            print("No episode was selected")
            sys.exit(1)

        episode_data = anime_provider.get_anime_episode(anime_result["_id"], episode)
        if episode_data is None:
            raise Exception("Episode not found")

        episode_streams = anime_provider.get_episode_streams(episode_data)

        if not episode_streams:
            raise Exception("No streams found")
        episode_streams = list(episode_streams)
        stream_links = []
        for server in episode_streams:
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
