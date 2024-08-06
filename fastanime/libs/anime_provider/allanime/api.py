"""a module that handles the scraping of allanime

abstraction over allanime api
"""

import json
import logging
from typing import TYPE_CHECKING

from requests.exceptions import Timeout

from ...anime_provider.base_provider import AnimeProvider
from ..utils import decode_hex_string
from .constants import (
    ALLANIME_API_ENDPOINT,
    ALLANIME_BASE,
    ALLANIME_REFERER,
    USER_AGENT,
)
from .gql_queries import ALLANIME_EPISODES_GQL, ALLANIME_SEARCH_GQL, ALLANIME_SHOW_GQL
from .normalizer import normalize_anime, normalize_search_results

if TYPE_CHECKING:
    from typing import Iterator

    from ....libs.anime_provider.allanime.types import AllAnimeEpisode
    from ....libs.anime_provider.types import Anime, Server
logger = logging.getLogger(__name__)


# TODO: create tests for the api
#
# ** Based on ani-cli **
class AllAnimeAPI(AnimeProvider):
    """
    Provides a fast and effective interface to AllAnime site.
    """

    api_endpoint = ALLANIME_API_ENDPOINT

    def _fetch_gql(self, query: str, variables: dict):
        """main abstraction over all requests to the allanime api

        Args:
            query: [TODO:description]
            variables: [TODO:description]

        Returns:
            [TODO:return]
        """
        try:
            response = self.session.get(
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
                logger.error("allanime(ERROR): ", response.text)
                return {}
        except Timeout:
            logger.error(
                "allanime(Error):Timeout exceeded this could mean allanime is down or you have lost internet connection"
            )
            return {}
        except Exception as e:
            logger.error(f"allanime:Error: {e}")
            return {}

    def search_for_anime(
        self,
        user_query: str,
        translation_type: str = "sub",
        nsfw=True,
        unknown=True,
        **kwargs,
    ):
        """search for an anime title using allanime provider

        Args:
            nsfw ([TODO:parameter]): [TODO:description]
            unknown ([TODO:parameter]): [TODO:description]
            user_query: [TODO:description]
            translation_type: [TODO:description]
            **kwargs: [TODO:args]

        Returns:
            [TODO:return]
        """
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
            logger.error(f"FA(AllAnime): {e}")
            return {}

    def get_anime(self, allanime_show_id: str):
        """get an anime details given its id

        Args:
            allanime_show_id: [TODO:description]

        Returns:
            [TODO:return]
        """
        variables = {"showId": allanime_show_id}
        try:
            anime = self._fetch_gql(ALLANIME_SHOW_GQL, variables)
            return normalize_anime(anime["show"])
        except Exception as e:
            logger.error(f"FA(AllAnime): {e}")
            return None

    def _get_anime_episode(
        self, allanime_show_id: str, episode_string: str, translation_type: str = "sub"
    ) -> "AllAnimeEpisode | dict":
        """get the episode details and sources info

        Args:
            allanime_show_id: [TODO:description]
            episode_string: [TODO:description]
            translation_type: [TODO:description]

        Returns:
            [TODO:return]
        """
        variables = {
            "showId": allanime_show_id,
            "translationType": translation_type,
            "episodeString": episode_string,
        }
        try:
            episode = self._fetch_gql(ALLANIME_EPISODES_GQL, variables)
            return episode["episode"]
        except Exception as e:
            logger.error(f"FA(AllAnime): {e}")
            return {}

    def get_episode_streams(
        self, anime: "Anime", episode_number: str, translation_type="sub"
    ) -> "Iterator[Server] | None":
        """get the streams of an episode

        Args:
            translation_type ([TODO:parameter]): [TODO:description]
            anime: [TODO:description]
            episode_number: [TODO:description]

        Yields:
            [TODO:description]
        """
        anime_id = anime["id"]
        allanime_episode = self._get_anime_episode(
            anime_id, episode_number, translation_type
        )
        if not allanime_episode:
            return []

        embeds = allanime_episode["sourceUrls"]
        try:
            for embed in embeds:
                try:
                    # filter the working streams no need to get all since the others are mostly hsl
                    # TODO: should i just get all the servers and handle the hsl??
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
                    resp = self.session.get(
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
                                logger.debug("allanime:Found streams from gogoanime")
                                yield {
                                    "server": "gogoanime",
                                    "episode_title": (
                                        allanime_episode["notes"] or f'{anime["title"]}'
                                    )
                                    + f"; Episode {episode_number}",
                                    "links": resp.json()["links"],
                                }  # pyright:ignore
                            case "Kir":
                                logger.debug("allanime:Found streams from wetransfer")
                                yield {
                                    "server": "wetransfer",
                                    "episode_title": (
                                        allanime_episode["notes"] or f'{anime["title"]}'
                                    )
                                    + f"; Episode {episode_number}",
                                    "links": resp.json()["links"],
                                }  # pyright:ignore
                            case "S-mp4":
                                logger.debug("allanime:Found streams from sharepoint")
                                yield {
                                    "server": "sharepoint",
                                    "episode_title": (
                                        allanime_episode["notes"] or f'{anime["title"]}'
                                    )
                                    + f"; Episode {episode_number}",
                                    "links": resp.json()["links"],
                                }  # pyright:ignore
                            case "Sak":
                                logger.debug("allanime:Found streams from dropbox")
                                yield {
                                    "server": "dropbox",
                                    "episode_title": (
                                        allanime_episode["notes"] or f'{anime["title"]}'
                                    )
                                    + f"; Episode {episode_number}",
                                    "links": resp.json()["links"],
                                }  # pyright:ignore
                            case "Default":
                                logger.debug("allanime:Found streams from wixmp")
                                yield {
                                    "server": "wixmp",
                                    "episode_title": (
                                        allanime_episode["notes"] or f'{anime["title"]}'
                                    )
                                    + f"; Episode {episode_number}",
                                    "links": resp.json()["links"],
                                }  # pyright:ignore
                except Timeout:
                    logger.error(
                        "Timeout has been exceeded this could mean allanime is down or you have lost internet connection"
                    )
                    return []
                except Exception as e:
                    logger.error(f"FA(Allanime): {e}")
                    return []
        except Exception as e:
            logger.error(f"FA(Allanime): {e}")
            return []


if __name__ == "__main__":
    anime_provider = AllAnimeAPI()
    # lets see if it works :)
    import subprocess
    import sys

    from InquirerPy import inquirer, validator

    anime = input("Enter the anime name: ")
    translation = input("Enter the translation type: ")

    search_results = anime_provider.search_for_anime(
        anime, translation_type=translation.strip()
    )

    if not search_results:
        raise Exception("No results found")

    search_results = search_results["results"]
    options = {show["title"]: show for show in search_results}
    anime = inquirer.fuzzy(
        "Enter the anime title",
        list(options.keys()),
        validate=validator.EmptyInputValidator(),
    ).execute()
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
        episode = inquirer.fuzzy(
            "Choose an episode",
            availableEpisodesDetail[translation.strip()],
            validate=validator.EmptyInputValidator(),
        ).execute()
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
        stream_link = inquirer.fuzzy(
            "Choose a link to stream",
            stream_links,
            validate=validator.EmptyInputValidator(),
        ).execute()
        if stream_link == "quit":
            print("Have a nice day")
            sys.exit()
        if not stream_link:
            raise Exception("No stream was selected")

        title = episode_streams[0].get(
            "episode_title", "%s: Episode %s" % (anime_data["title"], episode)
        )
        subprocess.run(["mpv", f"--title={title}", stream_link])
