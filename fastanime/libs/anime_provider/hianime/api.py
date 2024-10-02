import logging
import re
from html.parser import HTMLParser
from itertools import cycle
from urllib.parse import quote_plus

from yt_dlp.utils import (
    clean_html,
    extract_attributes,
    get_element_by_class,
    get_element_html_by_class,
    get_elements_by_class,
    get_elements_html_by_class,
)

from ..base_provider import AnimeProvider
from ..decorators import debug_provider
from ..utils import give_random_quality
from .constants import SERVERS_AVAILABLE
from .types import HiAnimeStream

logger = logging.getLogger(__name__)

LINK_TO_STREAMS_REGEX = re.compile(r".*://(.*)/embed-(2|4|6)/e-([0-9])/(.*)\?.*")
IMAGE_HTML_ELEMENT_REGEX = re.compile(r"<img.*?>")


class ParseAnchorAndImgTag(HTMLParser):
    def __init__(self):
        super().__init__()
        self.img_tag = None
        self.a_tag = None

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.img_tag = {attr[0]: attr[1] for attr in attrs}
        if tag == "a":
            self.a_tag = {attr[0]: attr[1] for attr in attrs}


class HiAnimeApi(AnimeProvider):
    # HEADERS = {"Referer": "https://hianime.to/home"}

    PROVIDER = "hianime"

    @debug_provider(PROVIDER.upper())
    def search_for_anime(self, anime_title: str, *args):
        query = quote_plus(anime_title)
        url = f"https://hianime.to/search?keyword={query}"
        response = self.session.get(url)
        if not response.ok:
            return
        search_page = response.text
        search_results_html_items = get_elements_by_class("flw-item", search_page)
        results = []
        for search_results_html_item in search_results_html_items:
            film_poster_html = get_element_by_class(
                "film-poster", search_results_html_item
            )

            if not film_poster_html:
                continue
            # get availableEpisodes
            episodes_html = get_element_html_by_class("tick-sub", film_poster_html)
            episodes = clean_html(episodes_html) or 12

            # get anime id and poster image url
            parser = ParseAnchorAndImgTag()
            parser.feed(film_poster_html)
            image_data = parser.img_tag
            anime_link_data = parser.a_tag
            if not image_data or not anime_link_data:
                continue

            episodes = int(episodes)

            # finally!!
            image_link = image_data["data-src"]
            anime_id = anime_link_data["data-id"]
            title = anime_link_data["title"]

            result = {
                "availableEpisodes": list(range(1, episodes)),
                "id": anime_id,
                "title": title,
                "poster": image_link,
            }

            results.append(result)

            self.store.set(result["id"], "search_result", result)
        return {"pageInfo": {}, "results": results}

    @debug_provider(PROVIDER.upper())
    def get_anime(self, hianime_id, *args):
        anime_result = {}
        if d := self.store.get(str(hianime_id), "search_result"):
            anime_result = d
            anime_url = f"https://hianime.to/ajax/v2/episode/list/{hianime_id}"
            response = self.session.get(anime_url, timeout=10)
            if response.ok:
                response_json = response.json()
                hianime_anime_page = response_json["html"]
                episodes_info_container_html = get_element_html_by_class(
                    "ss-list", hianime_anime_page
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
                episodes_info = [
                    {
                        "id": episode["data-id"],
                        "title": (
                            (episode["title"] or "").replace(
                                f"Episode {episode['data-number']}", ""
                            )
                            or anime_result["title"]
                        )
                        + f"; Episode {episode['data-number']}",
                        "episode": episode["data-number"],
                    }
                    for episode in episodes_info_dicts
                ]
                self.store.set(
                    str(hianime_id),
                    "anime_info",
                    episodes_info,
                )
                return {
                    "id": hianime_id,
                    "availableEpisodesDetail": {
                        "dub": episodes,
                        "sub": episodes,
                        "raw": episodes,
                    },
                    "poster": anime_result["poster"],
                    "title": anime_result["title"],
                    "episodes_info": episodes_info,
                }

    @debug_provider(PROVIDER.upper())
    def get_episode_streams(self, anime_id, episode, translation_type, *args):
        if d := self.store.get(str(anime_id), "anime_info"):
            episodes_info = d
            episode_details = [
                episode_details
                for episode_details in episodes_info
                if episode_details["episode"] == episode
            ]
            if not episode_details:
                return
            episode_details = episode_details[0]
            episode_url = f"https://hianime.to/ajax/v2/episode/servers?episodeId={episode_details['id']}"
            response = self.session.get(episode_url)
            if response.ok:
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
                    logger.warning("HiAnime: sub not found")
                    servers_html_sub = None

                # dub servers
                try:
                    servers_html_dub = get_elements_html_by_class(
                        "server-item", servers_containers_html[1]
                    )
                except Exception:
                    logger.warning("HiAnime: dub not found")
                    servers_html_dub = None

                if translation_type == "dub":
                    servers_html = servers_html_dub
                else:
                    servers_html = servers_html_sub
                if not servers_html:
                    return

                @debug_provider(self.PROVIDER.upper())
                def _get_server(server_name, server_html):
                    # keys: [ data-type: translation_type, data-id: embed_id, data-server-id: server_id ]
                    servers_info = extract_attributes(server_html)
                    embed_url = f"https://hianime.to/ajax/v2/episode/sources?id={servers_info['data-id']}"
                    embed_response = self.session.get(embed_url)
                    if embed_response.ok:
                        embed_json = embed_response.json()
                        raw_link_to_streams = embed_json["link"]
                        match = LINK_TO_STREAMS_REGEX.match(raw_link_to_streams)
                        if not match:
                            return
                        provider_domain = match.group(1)
                        embed_type = match.group(2)
                        episode_number = match.group(3)
                        source_id = match.group(4)

                        link_to_streams = f"https://{provider_domain}/embed-{embed_type}/ajax/e-{episode_number}/getSources?id={source_id}"
                        link_to_streams_response = self.session.get(link_to_streams)
                        if link_to_streams_response.ok:
                            juicy_streams_json: "HiAnimeStream" = (
                                link_to_streams_response.json()
                            )
                            # TODO: Hianime decided to fucking encrypt shit
                            # so got to fix it later
                            return {
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
                                        {"link": link["file"]}
                                        for link in juicy_streams_json["tracks"]
                                    ]
                                ),
                            }

                for server_name, server_html in zip(
                    cycle(SERVERS_AVAILABLE), servers_html
                ):
                    if server := _get_server(server_name, server_html):
                        yield server
