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
from .constants import (
    ANIMEPAHE_BASE,
    ANIMEPAHE_ENDPOINT,
    REQUEST_HEADERS,
    SERVER_HEADERS,
)
from .utils import process_animepahe_embed_page

if TYPE_CHECKING:
    from .types import AnimePaheAnimePage, AnimePaheSearchPage, AnimeSearchResult
JUICY_STREAM_REGEX = re.compile(r"source='(.*)';")
logger = logging.getLogger(__name__)

KWIK_RE = re.compile(r"Player\|(.+?)'")


# TODO: hack this to completion
class AnimePaheApi(AnimeProvider):
    search_page: "AnimePaheSearchPage"
    anime: "AnimePaheAnimePage"
    HEADERS = REQUEST_HEADERS

    def search_for_anime(self, user_query: str, *args):
        try:
            url = f"{ANIMEPAHE_ENDPOINT}m=search&q={user_query}"
            response = self.session.get(
                url,
            )
            if not response.ok:
                return
            data: "AnimePaheSearchPage" = response.json()
            self.search_page = data

            return {
                "pageInfo": {
                    "total": data["total"],
                    "perPage": data["per_page"],
                    "currentPage": data["current_page"],
                },
                "results": [
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
                    for result in data["data"]
                ],
            }

        except Exception as e:
            logger.error(f"[ANIMEPAHE-ERROR]: {e}")
            return {}

    def get_anime(self, session_id: str, *args):
        page = 1
        try:
            anime_result: "AnimeSearchResult" = [
                anime
                for anime in self.search_page["data"]
                if anime["session"] == session_id
            ][0]
            data: "AnimePaheAnimePage" = {}  # pyright:ignore

            url = f"{ANIMEPAHE_ENDPOINT}m=release&id={session_id}&sort=episode_asc&page={page}"

            def _pages_loader(
                url,
                page,
            ):
                response = self.session.get(
                    url,
                )
                if response.ok:
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
                        _pages_loader(
                            url,
                            page,
                        )

            _pages_loader(
                url,
                page,
            )

            if not data:
                return {}
            self.anime = data  # pyright:ignore
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
        except Exception as e:
            logger.error(f"[ANIMEPAHE-ERROR]: {e}")
            return {}

    def get_episode_streams(self, anime, episode_number: str, translation_type, *args):
        try:
            # extract episode details from memory
            episode = [
                episode
                for episode in self.anime["data"]
                if float(episode["episode"]) == float(episode_number)
            ]

            if not episode:
                logger.error(
                    f"[ANIMEPAHE-ERROR]: episode {episode_number} doesn't exist"
                )
                return []
            episode = episode[0]

            anime_id = anime["id"]
            # fetch the episode page
            url = f"{ANIMEPAHE_BASE}/play/{anime_id}/{episode['session']}"
            response = self.session.get(url)
            # get the element containing links to juicy streams
            c = get_element_by_id("resolutionMenu", response.text)
            resolutionMenuItems = get_elements_html_by_class("dropdown-item", c)
            # convert the elements containing embed links to a neat dict containing:
            # data-src
            # data-audio
            # data-resolution
            res_dicts = [extract_attributes(item) for item in resolutionMenuItems]

            # get the episode title
            episode_title = (
                f"{episode['title'] or anime['title']}; Episode {episode['episode']}"
            )
            # get all links
            streams = {
                "server": "kwik",
                "links": [],
                "episode_title": episode_title,
                "subtitles": [],
                "headers": {},
            }
            for res_dict in res_dicts:
                # get embed url
                embed_url = res_dict["data-src"]
                data_audio = "dub" if res_dict["data-audio"] == "eng" else "sub"
                # filter streams by translation_type
                if data_audio != translation_type:
                    continue

                if not embed_url:
                    logger.warn(
                        "[ANIMEPAHE-WARN]: embed url not found please report to the developers"
                    )
                    return []
                # get embed page
                embed_response = self.session.get(
                    embed_url, headers={"User-Agent": self.USER_AGENT, **SERVER_HEADERS}
                )
                if not response.ok:
                    continue
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
            yield streams
        except Exception as e:
            logger.error(f"[ANIMEPAHE-ERROR]: {e}")
