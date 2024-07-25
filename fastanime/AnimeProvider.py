from typing import Iterator

from .libs.anime_provider import anime_sources
from .libs.anime_provider.types import Anime, SearchResults, Server


class AnimeProvider:
    """
    Class that manages all anime sources adding some extra functionality to them.
    """

    PROVIDERS = list(anime_sources.keys())
    provider = PROVIDERS[0]

    def __init__(self, provider, dynamic=False, retries=0) -> None:
        self.provider = provider
        self.dynamic = dynamic
        self.retries = retries
        self.load_provider_obj()

    def load_provider_obj(self):
        anime_provider = anime_sources[self.provider]()
        self.anime_provider = anime_provider

    def search_for_anime(
        self, user_query, translation_type: str = "sub", nsfw=True, unknown=True
    ) -> SearchResults | None:
        anime_provider = self.anime_provider
        try:
            results = anime_provider.search_for_anime(
                user_query, translation_type, nsfw, unknown
            )
        except Exception as e:
            print(e)
            results = None
        return results  # pyright:ignore

    def get_anime(self, anime_id: str) -> Anime | None:
        anime_provider = self.anime_provider
        try:
            results = anime_provider.get_anime(anime_id)
        except Exception as e:
            print(e)
            results = None
        return results

    def get_episode_streams(
        self, anime, episode: str, translation_type: str
    ) -> Iterator[Server] | None:
        anime_provider = self.anime_provider
        try:
            results = anime_provider.get_episode_streams(
                anime, episode, translation_type
            )
        except Exception as e:
            print(e)
            results = None
        return results  # pyright:ignore
