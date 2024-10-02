import os
import re
from logging import getLogger

from yt_dlp.utils import (
    extract_attributes,
    get_element_html_by_attribute,
    get_element_html_by_class,
    get_element_text_and_html_by_tag,
    get_elements_html_by_class,
)

from ...common.mini_anilist import search_for_anime_with_anilist
from ..base_provider import AnimeProvider
from ..decorators import debug_provider
from ..types import SearchResults
from .constants import NYAA_ENDPOINT

logger = getLogger(__name__)

EXTRACT_USEFUL_INFO_PATTERN_1 = re.compile(
    r"\[(\w+)\] (.+) - (\d+) [\[\(](\d+)p[\]\)].*"
)

EXTRACT_USEFUL_INFO_PATTERN_2 = re.compile(
    r"\[(\w+)\] (.+)E(\d+) [\[\(]?(\d+)p.*[\]\)]?.*"
)


class NyaaApi(AnimeProvider):
    search_results: SearchResults
    PROVIDER = "nyaa"

    @debug_provider(PROVIDER.upper())
    def search_for_anime(self, user_query: str, *args, **_):
        self.search_results = search_for_anime_with_anilist(
            user_query, True
        )  # pyright: ignore
        self.user_query = user_query
        return self.search_results

    @debug_provider(PROVIDER.upper())
    def get_anime(self, anilist_id: str, *_):
        for anime in self.search_results["results"]:
            if anime["id"] == anilist_id:
                self.titles = [anime["title"], *anime["otherTitles"], self.user_query]
                return {
                    "id": anime["id"],
                    "title": anime["title"],
                    "poster": anime["poster"],
                    "availableEpisodesDetail": {
                        "dub": anime["availableEpisodes"],
                        "sub": anime["availableEpisodes"],
                        "raw": anime["availableEpisodes"],
                    },
                }

    @debug_provider(PROVIDER.upper())
    def get_episode_streams(
        self,
        anime_id: str,
        episode_number: str,
        translation_type: str,
        trusted_only=bool(int(os.environ.get("FA_NYAA_TRUSTED_ONLY", "0"))),
        allow_dangerous=bool(int(os.environ.get("FA_NYAA_ALLOW_DANGEROUS", "0"))),
        sort_by="seeders",
        *args,
    ):
        anime_title = self.titles[0]
        logger.debug(f"Searching nyaa for query: '{anime_title} {episode_number}'")
        servers = {}

        torrents_table = ""
        for title in self.titles:
            try:
                url_arguments: dict[str, str] = {
                    "c": "1_2",  # Language (English)
                    "q": f"{title} {'0' if len(episode_number)==1 else ''}{episode_number}",  # Search Query
                }
                # url_arguments["q"] = anime_title

                # if trusted_only:
                # url_arguments["f"] = "2"  # Trusted uploaders only

                # What to sort torrents by
                if sort_by == "seeders":
                    url_arguments["s"] = "seeders"
                elif sort_by == "date":
                    url_arguments["s"] = "id"
                elif sort_by == "size":
                    url_arguments["s"] = "size"
                elif sort_by == "comments":
                    url_arguments["s"] = "comments"

                logger.debug(f"URL Arguments: {url_arguments}")

                response = self.session.get(NYAA_ENDPOINT, params=url_arguments)
                if not response.ok:
                    logger.error(f"[NYAA]: {response.text}")
                    return

                try:
                    torrents_table = get_element_text_and_html_by_tag(
                        "table", response.text
                    )
                except Exception as e:
                    logger.error(f"[NYAA]: {e}")
                    continue

                if not torrents_table:
                    continue

                for anime_torrent in get_elements_html_by_class(
                    "success", torrents_table[1]
                ):
                    td_title = get_element_html_by_attribute(
                        "colspan", "2", anime_torrent
                    )
                    if not td_title:
                        continue
                    title_anchor_tag = get_element_text_and_html_by_tag("a", td_title)

                    if not title_anchor_tag:
                        continue
                    title_anchor_tag_attrs = extract_attributes(title_anchor_tag[1])
                    if not title_anchor_tag_attrs:
                        continue
                    if "class" in title_anchor_tag_attrs:
                        td_title = td_title.replace(title_anchor_tag[1], "")
                        title_anchor_tag = get_element_text_and_html_by_tag(
                            "a", td_title
                        )

                        if not title_anchor_tag:
                            continue
                        title_anchor_tag_attrs = extract_attributes(title_anchor_tag[1])
                        if not title_anchor_tag_attrs:
                            continue
                    anime_title_info = title_anchor_tag_attrs["title"]
                    if not anime_title_info:
                        continue
                    match = EXTRACT_USEFUL_INFO_PATTERN_1.search(
                        anime_title_info.strip()
                    )
                    if not match:
                        continue
                    server = match[1]
                    match[2]
                    _episode_number = match[3]
                    quality = match[4]
                    if float(episode_number) != float(_episode_number):
                        continue

                    links_td = get_element_html_by_class("text-center", anime_torrent)
                    if not links_td:
                        continue
                    torrent_anchor_tag = get_element_text_and_html_by_tag("a", links_td)
                    if not torrent_anchor_tag:
                        continue
                    torrent_anchor_tag_atrrs = extract_attributes(torrent_anchor_tag[1])
                    if not torrent_anchor_tag_atrrs:
                        continue
                    torrent_file_url = (
                        f'{NYAA_ENDPOINT}{torrent_anchor_tag_atrrs["href"]}'
                    )
                    if server in servers:
                        link = {
                            "translation_type": "sub",
                            "link": torrent_file_url,
                            "quality": quality,
                        }
                        if link not in servers[server]["links"]:
                            servers[server]["links"].append(link)
                    else:
                        servers[server] = {
                            "server": server,
                            "headers": {},
                            "episode_title": f"{anime_title}; Episode {episode_number}",
                            "subtitles": [],
                            "links": [
                                {
                                    "translation_type": "sub",
                                    "link": torrent_file_url,
                                    "quality": quality,
                                }
                            ],
                        }
                for anime_torrent in get_elements_html_by_class(
                    "default", torrents_table[1]
                ):
                    td_title = get_element_html_by_attribute(
                        "colspan", "2", anime_torrent
                    )
                    if not td_title:
                        continue
                    title_anchor_tag = get_element_text_and_html_by_tag("a", td_title)

                    if not title_anchor_tag:
                        continue
                    title_anchor_tag_attrs = extract_attributes(title_anchor_tag[1])
                    if not title_anchor_tag_attrs:
                        continue
                    if "class" in title_anchor_tag_attrs:
                        td_title = td_title.replace(title_anchor_tag[1], "")
                        title_anchor_tag = get_element_text_and_html_by_tag(
                            "a", td_title
                        )

                        if not title_anchor_tag:
                            continue
                        title_anchor_tag_attrs = extract_attributes(title_anchor_tag[1])
                        if not title_anchor_tag_attrs:
                            continue
                    anime_title_info = title_anchor_tag_attrs["title"]
                    if not anime_title_info:
                        continue
                    match = EXTRACT_USEFUL_INFO_PATTERN_2.search(
                        anime_title_info.strip()
                    )
                    if not match:
                        continue
                    server = match[1]
                    match[2]
                    _episode_number = match[3]
                    quality = match[4]
                    if float(episode_number) != float(_episode_number):
                        continue

                    links_td = get_element_html_by_class("text-center", anime_torrent)
                    if not links_td:
                        continue
                    torrent_anchor_tag = get_element_text_and_html_by_tag("a", links_td)
                    if not torrent_anchor_tag:
                        continue
                    torrent_anchor_tag_atrrs = extract_attributes(torrent_anchor_tag[1])
                    if not torrent_anchor_tag_atrrs:
                        continue
                    torrent_file_url = (
                        f'{NYAA_ENDPOINT}{torrent_anchor_tag_atrrs["href"]}'
                    )
                    if server in servers:
                        link = {
                            "translation_type": "sub",
                            "link": torrent_file_url,
                            "quality": quality,
                        }
                        if link not in servers[server]["links"]:
                            servers[server]["links"].append(link)
                    else:
                        servers[server] = {
                            "server": server,
                            "headers": {},
                            "episode_title": f"{anime_title}; Episode {episode_number}",
                            "subtitles": [],
                            "links": [
                                {
                                    "translation_type": "sub",
                                    "link": torrent_file_url,
                                    "quality": quality,
                                }
                            ],
                        }
                if not allow_dangerous:
                    break
                for anime_torrent in get_elements_html_by_class(
                    "danger", torrents_table[1]
                ):
                    td_title = get_element_html_by_attribute(
                        "colspan", "2", anime_torrent
                    )
                    if not td_title:
                        continue
                    title_anchor_tag = get_element_text_and_html_by_tag("a", td_title)

                    if not title_anchor_tag:
                        continue
                    title_anchor_tag_attrs = extract_attributes(title_anchor_tag[1])
                    if not title_anchor_tag_attrs:
                        continue
                    if "class" in title_anchor_tag_attrs:
                        td_title = td_title.replace(title_anchor_tag[1], "")
                        title_anchor_tag = get_element_text_and_html_by_tag(
                            "a", td_title
                        )

                        if not title_anchor_tag:
                            continue
                        title_anchor_tag_attrs = extract_attributes(title_anchor_tag[1])
                        if not title_anchor_tag_attrs:
                            continue
                    anime_title_info = title_anchor_tag_attrs["title"]
                    if not anime_title_info:
                        continue
                    match = EXTRACT_USEFUL_INFO_PATTERN_2.search(
                        anime_title_info.strip()
                    )
                    if not match:
                        continue
                    server = match[1]
                    match[2]
                    _episode_number = match[3]
                    quality = match[4]
                    if float(episode_number) != float(_episode_number):
                        continue

                    links_td = get_element_html_by_class("text-center", anime_torrent)
                    if not links_td:
                        continue
                    torrent_anchor_tag = get_element_text_and_html_by_tag("a", links_td)
                    if not torrent_anchor_tag:
                        continue
                    torrent_anchor_tag_atrrs = extract_attributes(torrent_anchor_tag[1])
                    if not torrent_anchor_tag_atrrs:
                        continue
                    torrent_file_url = (
                        f'{NYAA_ENDPOINT}{torrent_anchor_tag_atrrs["href"]}'
                    )
                    if server in servers:
                        link = {
                            "translation_type": "sub",
                            "link": torrent_file_url,
                            "quality": quality,
                        }
                        if link not in servers[server]["links"]:
                            servers[server]["links"].append(link)
                    else:
                        servers[server] = {
                            "server": server,
                            "headers": {},
                            "episode_title": f"{anime_title}; Episode {episode_number}",
                            "subtitles": [],
                            "links": [
                                {
                                    "translation_type": "sub",
                                    "link": torrent_file_url,
                                    "quality": quality,
                                }
                            ],
                        }
            except Exception as e:
                logger.error(f"[NYAA]: {e}")
                continue

        for server in servers:
            yield servers[server]
