from html.parser import HTMLParser

from yt_dlp.utils import clean_html, get_element_by_class, get_elements_by_class

from ..base_provider import AnimeProvider
from .constants import ANIWAVE_BASE, SEARCH_HEADERS


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


class AniWaveApi(AnimeProvider):
    def search_for_anime(self, anime_title, *args):
        self.session.headers.update(SEARCH_HEADERS)
        search_url = f"{ANIWAVE_BASE}/filter"
        params = {"keyword": anime_title}
        res = self.session.get(search_url, params=params)
        search_page = res.text
        search_results_html_list = get_elements_by_class("item", search_page)
        results = []
        for result_html in search_results_html_list:
            aniposter_html = get_element_by_class("poster", result_html)
            episode_html = get_element_by_class("sub", aniposter_html)
            episodes = clean_html(episode_html) or 12
            if not aniposter_html:
                return
            parser = ParseAnchorAndImgTag()
            parser.feed(aniposter_html)
            image_data = parser.img_tag
            anime_link_data = parser.a_tag
            if not image_data or not anime_link_data:
                continue

            episodes = int(episodes)

            # finally!!
            image_link = image_data["src"]
            title = image_data["alt"]
            anime_id = anime_link_data["href"]

            results.append(
                {
                    "availableEpisodes": list(range(1, episodes)),
                    "id": anime_id,
                    "title": title,
                    "poster": image_link,
                }
            )
        self.search_results = results
        return {"pageInfo": {}, "results": results}

    def get_anime(self, anime_id, *args):
        anime_page_url = f"{ANIWAVE_BASE}{anime_id}"
        self.session.get(anime_page_url)
        # TODO: to be continued; mostly js so very difficult
