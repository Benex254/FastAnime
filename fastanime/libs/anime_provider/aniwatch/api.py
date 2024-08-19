import logging
import re
from itertools import cycle

from yt_dlp.utils import (
    extract_attributes,
    get_element_html_by_class,
    get_elements_html_by_class,
)

from ..base_provider import AnimeProvider
from ..common import fetch_anime_info_from_bal
from ..mini_anilist import search_for_anime_with_anilist
from ..utils import give_random_quality
from . import SERVERS_AVAILABLE
from .types import AniWatchStream

logger = logging.getLogger(__name__)

LINK_TO_STREAMS_REGEX = re.compile(r".*://(.*)/embed-(2|4|6)/e-([0-9])/(.*)\?.*")


class AniWatchApi(AnimeProvider):
    def search_for_anime(self, anime_title: str, *args):
        try:
            return search_for_anime_with_anilist(anime_title)
        except Exception as e:
            logger.error(e)

    def get_anime(self, anilist_id, *args):
        try:
            bal_results = fetch_anime_info_from_bal(anilist_id)
            if not bal_results:
                return
            ZORO = bal_results["Sites"]["Zoro"]
            aniwatch_id = list(ZORO.keys())[0]
            anime_url = f"https://hianime.to/ajax/v2/episode/list/{aniwatch_id}"
            response = self.session.get(anime_url, timeout=10)
            if response.status_code == 200:
                response_json = response.json()
                aniwatch_anime_page = response_json["html"]
                episodes_info_container_html = get_element_html_by_class(
                    "ss-list", aniwatch_anime_page
                )
                episodes_info_html_list = get_elements_html_by_class(
                    "ep-item", episodes_info_container_html
                )
                # keys: [ data-number: episode_number, data-id: episode_id, title: episode_title , href:episode_page_url]
                episodes_info_dicts = [
                    extract_attributes(episode_dict)
                    for episode_dict in episodes_info_html_list
                ]
                episodes = [episode["data-number"] for episode in episodes_info_dicts]
                self.episodes_info = [
                    {
                        "id": episode["data-id"],
                        "title": (
                            (episode["title"] or "").replace(
                                f"Episode {episode['data-number']}", ""
                            )
                            or ZORO[aniwatch_id]["title"]
                        )
                        + f"; Episode {episode['data-number']}",
                        "episode": episode["data-number"],
                    }
                    for episode in episodes_info_dicts
                ]
                return {
                    "id": aniwatch_id,
                    "availableEpisodesDetail": {
                        "dub": episodes,
                        "sub": episodes,
                        "raw": episodes,
                    },
                    "poster": ZORO[aniwatch_id]["image"],
                    "title": ZORO[aniwatch_id]["title"],
                    "episodes_info": self.episodes_info,
                }
        except Exception as e:
            logger.error(e)

    def get_episode_streams(self, anime, episode, translation_type, *args):
        try:
            episode_details = [
                episode_details
                for episode_details in self.episodes_info
                if episode_details["episode"] == episode
            ]
            if not episode_details:
                return
            episode_details = episode_details[0]
            episode_url = f"https://hianime.to/ajax/v2/episode/servers?episodeId={episode_details['id']}"
            response = self.session.get(episode_url)
            if response.status_code == 200:
                response_json = response.json()
                episode_page_html = response_json["html"]
                servers_containers_html = get_elements_html_by_class(
                    "ps__-list", episode_page_html
                )
                if not servers_containers_html:
                    return
                # sub servers
                try:
                    servers_html_sub = get_elements_html_by_class(
                        "server-item", servers_containers_html[0]
                    )
                except Exception:
                    logger.warn("AniWatch: sub not found")
                    servers_html_sub = None

                # dub servers
                try:
                    servers_html_dub = get_elements_html_by_class(
                        "server-item", servers_containers_html[1]
                    )
                except Exception:
                    logger.warn("AniWatch: dub not found")
                    servers_html_dub = None

                if translation_type == "dub":
                    servers_html = servers_html_dub
                else:
                    servers_html = servers_html_sub
                if not servers_html:
                    return
                for server_name, server_html in zip(
                    cycle(SERVERS_AVAILABLE), servers_html
                ):
                    try:
                        # keys: [ data-type: translation_type, data-id: embed_id, data-server-id: server_id ]
                        servers_info = extract_attributes(server_html)
                        embed_url = f"https://hianime.to/ajax/v2/episode/sources?id={servers_info['data-id']}"
                        embed_response = self.session.get(embed_url)
                        if embed_response.status_code == 200:
                            embed_json = embed_response.json()
                            raw_link_to_streams = embed_json["link"]
                            match = LINK_TO_STREAMS_REGEX.match(raw_link_to_streams)
                            if not match:
                                continue
                            provider_domain = match.group(1)
                            embed_type = match.group(2)
                            episode_number = match.group(3)
                            source_id = match.group(4)

                            link_to_streams = f"https://{provider_domain}/embed-{embed_type}/ajax/e-{episode_number}/getSources?id={source_id}"
                            link_to_streams_response = self.session.get(link_to_streams)
                            if link_to_streams_response.status_code == 200:
                                juicy_streams_json: "AniWatchStream" = (
                                    link_to_streams_response.json()
                                )
                                yield {
                                    "headers": {},
                                    "subtitles": [
                                        {
                                            "url": track["file"],
                                            "language": track["label"],
                                        }
                                        for track in juicy_streams_json["tracks"]
                                        if track["kind"] == "captions"
                                    ],
                                    "server": server_name,
                                    "episode_title": episode_details["title"],
                                    "links": give_random_quality(
                                        [
                                            {"link": link["file"], "type": link["type"]}
                                            for link in juicy_streams_json["sources"]
                                        ]
                                    ),
                                }
                    except Exception as e:
                        logger.error(e)
        except Exception as e:
            logger.error(e)
