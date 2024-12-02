"""a module that handles the scraping of allanime

abstraction over allanime api
"""

import json
import logging
from typing import TYPE_CHECKING

from ...anime_provider.base_provider import AnimeProvider
from ..decorators import debug_provider
from ..utils import give_random_quality, one_digit_symmetric_xor
from .constants import ALLANIME_API_ENDPOINT, ALLANIME_BASE, ALLANIME_REFERER
from .gql_queries import ALLANIME_EPISODES_GQL, ALLANIME_SEARCH_GQL, ALLANIME_SHOW_GQL

if TYPE_CHECKING:
    from .types import AllAnimeEpisode
logger = logging.getLogger(__name__)


# TODO: create tests for the api
#
# ** Based on ani-cli **
class AllAnime(AnimeProvider):
    HEADERS = {
        "Referer": ALLANIME_REFERER,
    }

    def _execute_graphql_query(self, query: str, variables: dict):
        response = self.session.get(
            ALLANIME_API_ENDPOINT,
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

    @debug_provider
    def search_for_anime(
        self,
        search_keywords: str,
        translation_type: str = "sub",
        *,
        limit=40,
        page=1,
        country_of_origin="all",
        nsfw=True,
        unknown=True,
        **kwargs,
    ):
        search = {"allowAdult": nsfw, "allowUnknown": unknown, "query": search_keywords}
        variables = {
            "search": search,
            "limit": limit,
            "page": page,
            "translationtype": translation_type,
            "countryorigin": country_of_origin,
        }
        search_results = self._execute_graphql_query(ALLANIME_SEARCH_GQL, variables)
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

    @debug_provider
    def get_anime(self, show_id: str):
        variables = {"showId": show_id}
        anime = self._execute_graphql_query(ALLANIME_SHOW_GQL, variables)
        id: str = anime["show"]["_id"]
        title: str = anime["show"]["name"]
        availableEpisodesDetail = anime["show"]["availableEpisodesDetail"]
        self.store.set(show_id, "anime_info", {"title": title})
        type = anime.get("__typename")
        normalized_anime = {
            "id": id,
            "title": title,
            "availableEpisodesDetail": availableEpisodesDetail,
            "type": type,
        }
        return normalized_anime

    @debug_provider
    def _get_anime_episode(
        self, show_id: str, episode, translation_type: str = "sub"
    ) -> "AllAnimeEpisode | dict":
        variables = {
            "showId": show_id,
            "translationType": translation_type,
            "episodeString": episode,
        }
        episode = self._execute_graphql_query(ALLANIME_EPISODES_GQL, variables)
        return episode["episode"]

    @debug_provider
    def get_episode_streams(
        self, anime_id, episode_number: str, translation_type="sub"
    ):

        anime_title = (self.store.get(anime_id, "anime_info", "") or {"title": ""})[
            "title"
        ]
        allanime_episode = self._get_anime_episode(
            anime_id, episode_number, translation_type
        )
        if not allanime_episode:
            return []

        embeds = allanime_episode["sourceUrls"]

        @debug_provider
        def _get_server(embed):
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
                return
            url = embed.get("sourceUrl")
            #
            if not url:
                return
            if url.startswith("--"):
                url = url[2:]
                url = one_digit_symmetric_xor(56, url)

            if "tools.fast4speed.rsvp" in url:
                logger.debug("[ALLANIME]:Found streams from gogoanime")
                return {
                    "server": "Yt",
                    "episode_title": f"{anime_title}; Episode {episode_number}",
                    "headers": {"Referer": f"https://{ALLANIME_BASE}/"},
                    "subtitles": [],
                    "links": [
                        {
                            "link": url,
                            "quality": "1080",
                        }
                    ],
                }

            # get the stream url for an episode of the defined source names
            embed_url = f"https://{ALLANIME_BASE}{url.replace('clock', 'clock.json')}"
            resp = self.session.get(
                embed_url,
                timeout=10,
            )

            if resp.ok:
                match embed["sourceName"]:
                    case "Luf-mp4":
                        logger.debug("allanime:Found streams from gogoanime")
                        return {
                            "server": "gogoanime",
                            "headers": {"Referer": f"https://{ALLANIME_BASE}/"},
                            "subtitles": [],
                            "episode_title": (
                                allanime_episode["notes"] or f"{anime_title}"
                            )
                            + f"; Episode {episode_number}",
                            "links": give_random_quality(resp.json()["links"]),
                        }
                    case "Kir":
                        logger.debug("allanime:Found streams from wetransfer")
                        return {
                            "server": "wetransfer",
                            "headers": {"Referer": f"https://{ALLANIME_BASE}/"},
                            "subtitles": [],
                            "episode_title": (
                                allanime_episode["notes"] or f"{anime_title}"
                            )
                            + f"; Episode {episode_number}",
                            "links": give_random_quality(resp.json()["links"]),
                        }
                    case "S-mp4":
                        logger.debug("allanime:Found streams from sharepoint")
                        return {
                            "server": "sharepoint",
                            "headers": {"Referer": f"https://{ALLANIME_BASE}/"},
                            "subtitles": [],
                            "episode_title": (
                                allanime_episode["notes"] or f"{anime_title}"
                            )
                            + f"; Episode {episode_number}",
                            "links": give_random_quality(resp.json()["links"]),
                        }
                    case "Sak":
                        logger.debug("allanime:Found streams from dropbox")
                        return {
                            "server": "dropbox",
                            "headers": {"Referer": f"https://{ALLANIME_BASE}/"},
                            "subtitles": [],
                            "episode_title": (
                                allanime_episode["notes"] or f"{anime_title}"
                            )
                            + f"; Episode {episode_number}",
                            "links": give_random_quality(resp.json()["links"]),
                        }
                    case "Default":
                        logger.debug("allanime:Found streams from wixmp")
                        return {
                            "server": "wixmp",
                            "headers": {"Referer": f"https://{ALLANIME_BASE}/"},
                            "subtitles": [],
                            "episode_title": (
                                allanime_episode["notes"] or f"{anime_title}"
                            )
                            + f"; Episode {episode_number}",
                            "links": give_random_quality(resp.json()["links"]),
                        }

        for embed in embeds:
            if server := _get_server(embed):
                yield server
