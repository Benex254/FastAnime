import logging
import random
import re
import time
from typing import TYPE_CHECKING

from yt_dlp.utils import (
    extract_attributes,
    get_element_by_id,
    get_elements_html_by_class,
)

from ..base_provider import AnimeProvider
from ..decorators import debug_provider
from .constants import (
    ANIMEPAHE_BASE,
    ANIMEPAHE_ENDPOINT,
    REQUEST_HEADERS,
    SERVER_HEADERS,
)
from .utils import process_animepahe_embed_page

if TYPE_CHECKING:
    from .types import AnimePaheAnimePage, AnimePaheSearchPage, AnimePaheSearchResult
JUICY_STREAM_REGEX = re.compile(r"source='(.*)';")
logger = logging.getLogger(__name__)

KWIK_RE = re.compile(r"Player\|(.+?)'")


class AnimePahe(AnimeProvider):
    search_page: "AnimePaheSearchPage"
    anime: "AnimePaheAnimePage"
    HEADERS = REQUEST_HEADERS

    @debug_provider
    def search_for_anime(self, user_query: str, *args):
        url = f"{ANIMEPAHE_ENDPOINT}m=search&q={user_query}"
        response = self.session.get(
            url,
        )
        if not response.ok:
            return
        data: "AnimePaheSearchPage" = response.json()
        results = []
        for result in data["data"]:
            results.append(
                {
                    "availableEpisodes": list(range(result["episodes"])),
                    "id": result["session"],
                    "title": result["title"],
                    "type": result["type"],
                    "year": result["year"],
                    "score": result["score"],
                    "status": result["status"],
                    "season": result["season"],
                    "poster": result["poster"],
                }
            )
            self.store.set(
                str(result["session"]),
                "search_result",
                result,
            )

        return {
            "pageInfo": {
                "total": data["total"],
                "perPage": data["per_page"],
                "currentPage": data["current_page"],
            },
            "results": results,
        }

    @debug_provider
    def _pages_loader(
        self,
        data,
        session_id,
        url,
        page,
    ):
        response = self.session.get(
            url,
        )
        response.raise_for_status()
        if not data:
            data.update(response.json())
        else:
            if ep_data := response.json().get("data"):
                data["data"].extend(ep_data)
        if response.json()["next_page_url"]:
            # TODO: Refine this
            time.sleep(
                random.choice(
                    [
                        0.25,
                        0.1,
                        0.5,
                        0.75,
                        1,
                    ]
                )
            )
            page += 1
            url = f"{ANIMEPAHE_ENDPOINT}m=release&id={session_id}&sort=episode_asc&page={page}"
            self._pages_loader(
                data,
                session_id,
                url,
                page,
            )
        return data

    @debug_provider
    def get_anime(self, session_id: str, *args):
        page = 1
        if d := self.store.get(str(session_id), "search_result"):
            anime_result: "AnimePaheSearchResult" = d
            data: "AnimePaheAnimePage" = {}  # pyright:ignore

            url = f"{ANIMEPAHE_ENDPOINT}m=release&id={session_id}&sort=episode_asc&page={page}"

            data = self._pages_loader(
                data,
                session_id,
                url,
                page,
            )

            if not data:
                return {}
            data["title"] = anime_result["title"]  # pyright:ignore
            self.store.set(str(session_id), "anime_info", data)
            episodes = list(map(str, [episode["episode"] for episode in data["data"]]))
            title = ""
            return {
                "id": session_id,
                "title": anime_result["title"],
                "year": anime_result["year"],
                "season": anime_result["season"],
                "poster": anime_result["poster"],
                "score": anime_result["score"],
                "availableEpisodesDetail": {
                    "sub": episodes,
                    "dub": episodes,
                    "raw": episodes,
                },
                "episodesInfo": [
                    {
                        "title": f"{episode['title'] or title};{episode['episode']}",
                        "episode": episode["episode"],
                        "id": episode["session"],
                        "translation_type": episode["audio"],
                        "duration": episode["duration"],
                        "poster": episode["snapshot"],
                    }
                    for episode in data["data"]
                ],
            }

    @debug_provider
    def _get_streams(self, res_dict, streams, translation_type):
        embed_url = res_dict["data-src"]
        data_audio = "dub" if res_dict["data-audio"] == "eng" else "sub"
        # filter streams by translation_type
        if data_audio != translation_type:
            return

        if not embed_url:
            logger.warning(
                "[ANIMEPAHE-WARN]: embed url not found please report to the developers"
            )
            return []
        # get embed page
        embed_response = self.session.get(
            embed_url, headers={"User-Agent": self.USER_AGENT, **SERVER_HEADERS}
        )
        embed_response.raise_for_status()
        embed_page = embed_response.text

        decoded_js = process_animepahe_embed_page(embed_page)
        if not decoded_js:
            logger.error("[ANIMEPAHE-ERROR]: failed to decode embed page")
            return
        juicy_stream = JUICY_STREAM_REGEX.search(decoded_js)
        if not juicy_stream:
            logger.error("[ANIMEPAHE-ERROR]: failed to find juicy stream")
            return
        juicy_stream = juicy_stream.group(1)
        # add the link
        streams["links"].append(
            {
                "quality": res_dict["data-resolution"],
                "translation_type": data_audio,
                "link": juicy_stream,
            }
        )

    @debug_provider
    def get_episode_streams(
        self, anime_id, episode_number: str, translation_type, *args
    ):
        anime_title = ""
        # extract episode details from memory
        anime_info = self.store.get(str(anime_id), "anime_info")
        if not anime_info:
            logger.error(
                f"[ANIMEPAHE-ERROR]: Anime with ID {anime_id} not found in store"
            )
            return []

        anime_title = anime_info["title"]
        episode = next(
            (
                ep
                for ep in anime_info["data"]
                if float(ep["episode"]) == float(episode_number)
            ),
            None,
        )

        if not episode:
            logger.error(
                f"[ANIMEPAHE-ERROR]: Episode {episode_number} doesn't exist for anime {anime_title}"
            )
            return []

        # fetch the episode page
        url = f"{ANIMEPAHE_BASE}/play/{anime_id}/{episode['session']}"
        response = self.session.get(url)

        response.raise_for_status()
        # get the element containing links to juicy streams
        c = get_element_by_id("resolutionMenu", response.text)
        resolutionMenuItems = get_elements_html_by_class("dropdown-item", c)
        # convert the elements containing embed links to a neat dict containing:
        # data-src
        # data-audio
        # data-resolution
        res_dicts = [extract_attributes(item) for item in resolutionMenuItems]

        # get all links
        streams = {
            "server": "kwik",
            "links": [],
            "episode_title": f"{episode['title'] or anime_title}; Episode {episode['episode']}",
            "subtitles": [],
            "headers": {},
        }
        for res_dict in res_dicts:
            # get embed url
            if _streams := self._get_streams(res_dict, streams, translation_type):
                yield _streams
