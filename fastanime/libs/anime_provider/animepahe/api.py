import re
import shutil
import subprocess

from yt_dlp.utils import (
    extract_attributes,
    get_element_by_id,
    get_element_text_and_html_by_tag,
    get_elements_html_by_class,
)

from ..base_provider import AnimeProvider
from .constants import (
    ANIMEPAHE_BASE,
    ANIMEPAHE_ENDPOINT,
    REQUEST_HEADERS,
    SERVER_HEADERS,
)

JUICY_STREAM_REGEX = re.compile(r"source='(.*)';")


# TODO: hack this to completion
class AnimePaheApi(AnimeProvider):
    def search_for_anime(self, user_query, *args):
        try:
            url = f"{ANIMEPAHE_ENDPOINT}m=search&q={user_query}"
            headers = {**REQUEST_HEADERS}
            response = self.session.get(url, headers=headers)
            if not response.status_code == 200:
                return
            data = response.json()

            return {
                "pageInfo": {"total": data["total"]},
                "results": [
                    {
                        "id": result["session"],
                        "title": result["title"],
                        "availableEpisodes": result["episodes"],
                        "type": result["type"],
                    }
                    for result in data["data"]
                ],
            }

        except Exception as e:
            print(e)
            input()

    def get_anime(self, session_id: str, *args):
        url = f"{ANIMEPAHE_ENDPOINT}m=release&id={session_id}&sort=episode_asc&page=1"
        response = self.session.get(url, headers=REQUEST_HEADERS)
        if not response.status_code == 200:
            return
        data = response.json()
        self.current = data
        episodes = list(map(str, range(data["total"])))
        return {
            "id": session_id,
            "title": "none",
            "availableEpisodesDetail": {
                "sub": episodes,
                "dub": episodes,
                "raw": episodes,
            },
        }

    def get_episode_streams(self, anime, episode, *args):
        episode_id = self.current["data"][int(episode)]["session"]
        anime_id = anime["id"]
        url = f"{ANIMEPAHE_BASE}/play/{anime_id}/{episode_id}"
        # response = requests.get(url, headers=REQUEST_HEADERS)
        response = self.session.get(url, headers=REQUEST_HEADERS)
        # print(clean_html(response.text))
        c = get_element_by_id("resolutionMenu", response.text)
        resolutionMenuItems = get_elements_html_by_class("dropdown-item", c)
        res_dicts = [extract_attributes(item) for item in resolutionMenuItems]

        streams = {"server": "kwik", "links": [], "episode_title": f"{episode}"}
        for res_dict in res_dicts:
            # get embed url
            embed_url = res_dict["data-src"]
            if not embed_url:
                return
            embed_response = self.session.get(embed_url, headers=SERVER_HEADERS)
            embed = embed_response.text
            # search for the encoded js
            encoded_js = None
            for _ in range(7):
                content, html = get_element_text_and_html_by_tag("script", embed)
                if not content:
                    embed = embed.replace(html, "")
                    continue
                encoded_js = content
                break
            if not encoded_js:
                return
            # execute the encoded js with node for now or maybe forever
            NODE = shutil.which("node")
            if not NODE:
                return
            result = subprocess.run(
                [NODE, "-e", encoded_js],
                text=True,
                capture_output=True,
            )
            evaluted_js = result.stderr
            if not evaluted_js:
                return
            # get that juicy stream
            match = JUICY_STREAM_REGEX.search(evaluted_js)
            if not match:
                return
            juicy_stream = match.group(1)
            streams["links"].append(
                {
                    "quality": res_dict["data-resolution"],
                    "audio_language": res_dict["data-audio"],
                    "link": juicy_stream,
                }
            )
        yield streams
