"""a module that handles the scraping of allanime

abstraction over allanime api
"""

import json
import logging
from typing import TYPE_CHECKING

from requests.exceptions import Timeout

from ...anime_provider.base_provider import AnimeProvider
from ..utils import give_random_quality, one_digit_symmetric_xor
from .constants import ALLANIME_API_ENDPOINT, ALLANIME_BASE, ALLANIME_REFERER
from .gql_queries import ALLANIME_EPISODES_GQL, ALLANIME_SEARCH_GQL, ALLANIME_SHOW_GQL

if TYPE_CHECKING:
    from .types import AllAnimeEpisode
logger = logging.getLogger(__name__)


# TODO: create tests for the api
#
# ** Based on ani-cli **
class AllAnimeAPI(AnimeProvider):
    """
    Provides a fast and effective interface to AllAnime site.
    """

    api_endpoint = ALLANIME_API_ENDPOINT
    HEADERS = {
        "Referer": ALLANIME_REFERER,
    }

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
                timeout=10,
            )
            if response.ok:
                return response.json()["data"]
            else:
                logger.error("[ALLANIME-ERROR]: ", response.text)
                return {}
        except Timeout:
            logger.error(
                "[ALLANIME-ERROR]: Timeout exceeded this could mean allanime is down or you have lost internet connection"
            )
            return {}
        except Exception as e:
            logger.error(f"[ALLANIME-ERROR]: {e}")
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
            page_info = search_results["shows"]["pageInfo"]
            results = []
            for result in search_results["shows"]["edges"]:
                normalized_result = {
                    "id": result["_id"],
                    "title": result["name"],
                    "type": result["__typename"],
                    "availableEpisodes": result["availableEpisodes"],
                }
                results.append(normalized_result)

            normalized_search_results = {
                "pageInfo": page_info,
                "results": results,
            }
            return normalized_search_results

        except Exception as e:
            logger.error(f"[ALLANIME-ERROR]: {e}")
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
            id: str = anime["show"]["_id"]
            title: str = anime["show"]["name"]
            availableEpisodesDetail = anime["show"]["availableEpisodesDetail"]
            type = anime.get("__typename")
            normalized_anime = {
                "id": id,
                "title": title,
                "availableEpisodesDetail": availableEpisodesDetail,
                "type": type,
            }
            return normalized_anime
        except Exception as e:
            logger.error(f"[ALLANIME-ERROR]: {e}")
            return {}

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
            logger.error(f"[ALLANIME-ERROR]: {e}")
            return {}

    def get_episode_streams(self, anime, episode_number: str, translation_type="sub"):
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
                        # priorities based on death note
                        "Sak",  #  7
                        "S-mp4",  # 7.9
                        "Luf-mp4",  # 7.7
                        "Default",  # 8.5
                        "Yt-mp4",  # 7.9
                        "Kir",  # NA
                        # "Vid-mp4"  # 4
                        # "Ok",  # 3.5
                        # "Ss-Hls",  #  5.5
                        # "Mp4",  # 4
                    ):
                        continue
                    url = embed.get("sourceUrl")
                    #
                    if not url:
                        continue
                    if url.startswith("--"):
                        url = url[2:]
                        url = one_digit_symmetric_xor(56, url)

                    if "tools.fast4speed.rsvp" in url:
                        yield {
                            "server": "Yt",
                            "episode_title": f'{anime["title"]}; Episode {episode_number}',
                            "headers": {"Referer": f"https://{ALLANIME_BASE}/"},
                            "subtitles": [],
                            "links": [
                                {
                                    "link": url,
                                    "quality": "1080",
                                }
                            ],
                        }
                        continue

                    # get the stream url for an episode of the defined source names
                    embed_url = (
                        f"https://{ALLANIME_BASE}{url.replace('clock', 'clock.json')}"
                    )
                    resp = self.session.get(
                        embed_url,
                        timeout=10,
                    )

                    if resp.ok:
                        match embed["sourceName"]:
                            case "Luf-mp4":
                                logger.debug("allanime:Found streams from gogoanime")
                                yield {
                                    "server": "gogoanime",
                                    "headers": {},
                                    "subtitles": [],
                                    "episode_title": (
                                        allanime_episode["notes"] or f'{anime["title"]}'
                                    )
                                    + f"; Episode {episode_number}",
                                    "links": give_random_quality(resp.json()["links"]),
                                }
                            case "Kir":
                                logger.debug("allanime:Found streams from wetransfer")
                                yield {
                                    "server": "wetransfer",
                                    "headers": {},
                                    "subtitles": [],
                                    "episode_title": (
                                        allanime_episode["notes"] or f'{anime["title"]}'
                                    )
                                    + f"; Episode {episode_number}",
                                    "links": give_random_quality(resp.json()["links"]),
                                }
                            case "S-mp4":
                                logger.debug("allanime:Found streams from sharepoint")
                                yield {
                                    "server": "sharepoint",
                                    "headers": {},
                                    "subtitles": [],
                                    "episode_title": (
                                        allanime_episode["notes"] or f'{anime["title"]}'
                                    )
                                    + f"; Episode {episode_number}",
                                    "links": give_random_quality(resp.json()["links"]),
                                }
                            case "Sak":
                                logger.debug("allanime:Found streams from dropbox")
                                yield {
                                    "server": "dropbox",
                                    "headers": {},
                                    "subtitles": [],
                                    "episode_title": (
                                        allanime_episode["notes"] or f'{anime["title"]}'
                                    )
                                    + f"; Episode {episode_number}",
                                    "links": give_random_quality(resp.json()["links"]),
                                }
                            case "Default":
                                logger.debug("allanime:Found streams from wixmp")
                                yield {
                                    "server": "wixmp",
                                    "headers": {},
                                    "subtitles": [],
                                    "episode_title": (
                                        allanime_episode["notes"] or f'{anime["title"]}'
                                    )
                                    + f"; Episode {episode_number}",
                                    "links": give_random_quality(resp.json()["links"]),
                                }
                except Timeout:
                    logger.error(
                        "[ALLANIME-ERROR]: Timeout has been exceeded this could mean allanime is down or you have lost internet connection"
                    )
                except Exception as e:
                    logger.error(f"[ALLANIME-ERROR]: {e}")
        except Exception as e:
            logger.error(f"[ALLANIME-ERROR]: {e}")
            return []
