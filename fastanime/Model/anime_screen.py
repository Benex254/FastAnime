from ..libs.anilist import AniList
from .base_model import BaseScreenModel
from ..libs.anime_provider.allanime_api import anime_provider
from kivy.cache import Cache
from fuzzywuzzy import fuzz


def anime_title_percentage_match(
    possible_user_requested_anime_title: str, title: str
) -> int:
    """Returns the percentage match between the possible title and user title

    Args:
        possible_user_requested_anime_title (str): an Animdl search result title
        title (str): the anime title the user wants

    Returns:
        int: the percentage match
    """
    print(locals())

    percentage_ratio = fuzz.ratio(title, possible_user_requested_anime_title)
    print(percentage_ratio)
    return percentage_ratio


Cache.register("streams.anime", limit=10)


class AnimeScreenModel(BaseScreenModel):
    """the Anime screen model"""

    data = {}
    anime_id = 0
    current_anime_data = None
    current_anime_id = "0"
    current_title = ""

    def get_anime_data_from_provider(self, anime_title: str, id=None):
        if self.current_title == anime_title and self.current_anime_data:
            return self.current_anime_data

        search_results = anime_provider.search_for_anime(anime_title)

        if search_results:
            _search_results = search_results["shows"]["edges"]
            result = max(
                _search_results,
                key=lambda x: anime_title_percentage_match(x["name"], anime_title),
            )
            self.current_anime_id = result["_id"]
            self.current_anime_data = anime_provider.get_anime(result["_id"])
            self.current_title = anime_title
            return self.current_anime_data

    def get_episode_streams(self, episode):
        if self.current_anime_data:
            episode_streams = anime_provider.get_anime_episode(
                self.current_anime_id, episode
            )
            streams = anime_provider.get_episode_streams(episode_streams)

            if streams:
                _streams = list(streams)
                streams = []
                for stream in _streams:
                    streams.append(
                        {
                            f"{stream[0]}": [
                                _stream["link"] for _stream in stream[1]["links"]
                            ]
                        }
                    )
                return streams

        # should return {type:{provider:streamlink}}

    def get_anime_data(self, id: int):
        return AniList.get_anime(id)
