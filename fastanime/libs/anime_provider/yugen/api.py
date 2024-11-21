import base64
from itertools import cycle
from yt_dlp.utils import (
    get_element_text_and_html_by_tag,
    get_elements_text_and_html_by_attribute,
    extract_attributes,
    get_element_by_attribute,
)
import re

from yt_dlp.utils.traversal import get_element_html_by_attribute
from .constants import YUGEN_ENDPOINT, SEARCH_URL
from ..decorators import debug_provider
from ..base_provider import AnimeProvider


# ** Adapted from anipy-cli **
class YugenApi(AnimeProvider):
    """
    Provides a fast and effective interface to YugenApi site.
    """

    PROVIDER = "yugen"
    api_endpoint = YUGEN_ENDPOINT
    # HEADERS = {
    #     "Referer": ALLANIME_REFERER,
    # }

    @debug_provider(PROVIDER.upper())
    def search_for_anime(
        self,
        user_query: str,
        translation_type: str = "sub",
        nsfw=True,
        unknown=True,
        **kwargs,
    ):
        results = []
        has_next = True
        page = 0
        while has_next:
            page += 1
            response = self.session.get(
                SEARCH_URL, params={"q": user_query, "page": page}
            )
            search_results = response.json()
            has_next = search_results["hasNext"]

            results_html = search_results["query"]
            anime = get_elements_text_and_html_by_attribute(
                "class", "anime-meta", results_html, tag="a"
            )
            id_regex = re.compile(r"(\d+)\/([^\/]+)")
            for _a in anime:
                if not _a:
                    continue
                a = extract_attributes(_a[1])

                if not a:
                    continue
                uri = a["href"]
                identifier = id_regex.search(uri)  # pyright:ignore
                if identifier is None:
                    continue

                if len(identifier.groups()) != 2:
                    continue

                identifier = base64.b64encode(
                    f"{identifier.group(1)}/{identifier.group(2)}".encode()
                ).decode()

                anime_title = a["title"]
                languages = {"sub": 1, "dub": 0}
                excl = get_element_by_attribute(
                    "class", "ani-exclamation", _a[1], tag="div"
                )
                if excl is not None:
                    if "dub" in excl.lower():
                        languages["dub"] = 1
                #
                results.append(
                    {
                        "id": identifier,
                        "title": anime_title,
                        "availableEpisodes": languages,
                    }
                )

            page += 1

        return {
            "pageInfo": {"total": len(results)},
            "results": results,
        }

    @debug_provider(PROVIDER.upper())
    def get_anime(self, anime_id: str, **kwargs):
        identifier = base64.b64decode(anime_id).decode()
        response = self.session.get(f"{YUGEN_ENDPOINT}/anime/{identifier}")
        html_page = response.text
        data_map = {
            "id": anime_id,
            "title": None,
            "poster": None,
            "genres": [],
            "synopsis": None,
            "release_year": None,
            "status": None,
            "otherTitles": [],
            "availableEpisodesDetail": {},
        }

        sub_match = re.search(
            r'<div class="ap-.+?">Episodes</div><span class="description" .+?>(\d+)</span></div>',
            html_page,
        )

        if sub_match:
            eps = int(sub_match.group(1))
            data_map["availableEpisodesDetail"]["sub"] = list(map(str,range(1, eps + 1)))

        dub_match = re.search(
            r'<div class="ap-.+?">Episodes \(Dub\)</div><span class="description" .+?>(\d+)</span></div>',
            html_page,
        )

        if dub_match:
            eps = int(dub_match.group(1))
            data_map["availableEpisodesDetail"]["dub"] = list(map(str,range(1, eps + 1)))

        name = get_element_text_and_html_by_tag("h1", html_page)
        if name is not None:
            data_map["title"] = name[0].strip()

        synopsis = get_element_by_attribute("class", "description", html_page, tag="p")
        if synopsis is not None:
            data_map["synopsis"] = synopsis

        # FIXME: This is not working because ytdl is too strict on also getting a closing tag
        try:
            image = get_element_html_by_attribute(
                "class", "cover", html_page, tag="img"
            )
            img_attrs = extract_attributes(image)
            if img_attrs is not None:
                data_map["image"] = img_attrs.get("src")
        except Exception:
            pass

        data = get_elements_text_and_html_by_attribute(
            "class", "data", html_page, tag="div"
        )
        for d in data:
            title = get_element_text_and_html_by_tag("div", d[1])
            desc = get_element_text_and_html_by_tag("span", d[1])
            if title is None or desc is None:
                continue
            title = title[0]
            desc = desc[0]
            if title in ["Native", "Romaji"]:
                data_map["alternative_names"].append(desc)
            elif title == "Synonyms":
                data_map["alternative_names"].extend(desc.split(","))
            elif title == "Premiered":
                try:
                    data_map["release_year"] = int(desc.split()[-1])
                except (ValueError, TypeError):
                    pass
            elif title == "Status":
                data_map["status"] = title
            elif title == "Genres":
                data_map["genres"].extend([g.strip() for g in desc.split(",")])

        return data_map

    @debug_provider(PROVIDER.upper())
    def get_episode_streams(
        self, anime_id, episode_number: str, translation_type="sub"
    ):
        """get the streams of an episode

        Args:
            translation_type ([TODO:parameter]): [TODO:description]
            anime: [TODO:description]
            episode_number: [TODO:description]

        Yields:
            [TODO:description]
        """

        identifier = base64.b64decode(anime_id).decode()

        id_num, anime_title = identifier.split("/")
        if translation_type == "dub":
            video_query = f"{id_num}|{episode_number}|dub"
        else:
            video_query = f"{id_num}|{episode_number}"
        #

        res = self.session.post(
            f"{YUGEN_ENDPOINT}/api/embed/",
            data={
                "id": base64.b64encode(video_query.encode()).decode(),
                "ac": "0",
            },
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        res = res.json()
        yield {
            "server": "gogoanime",
            "episode_title": f"{anime_title}; Episode {episode_number}",
            "headers": {},
            "subtitles": [],
            "links": [{"quality": quality, "link": link} for quality,link in zip(cycle(["1080","720","480","360"]),res["hls"])],
        }
