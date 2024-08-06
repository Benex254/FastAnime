"""An abstraction over all providers offering added features with a simple and well typed api

[TODO:description]
"""

import logging
from typing import TYPE_CHECKING, Iterator

from .libs.anime_provider import anime_sources

if TYPE_CHECKING:
    from typing import Union

    from .libs.anilist.anilist_data_schema import AnilistBaseMediaDataSchema
    from .libs.anime_provider.types import Anime, SearchResults, Server

logger = logging.getLogger(__name__)


class AnimeProvider:
    """Class that manages all anime sources adding some extra functionality to them.
    Attributes:
        PROVIDERS: [TODO:attribute]
        provider: [TODO:attribute]
        provider: [TODO:attribute]
        dynamic: [TODO:attribute]
        retries: [TODO:attribute]
        anime_provider: [TODO:attribute]
    """

    PROVIDERS = list(anime_sources.keys())
    provider = PROVIDERS[0]

    def __init__(self, provider, dynamic=False, retries=0) -> None:
        self.provider = provider
        self.dynamic = dynamic
        self.retries = retries
        self.load_provider_obj()

    def load_provider_obj(self):
        """updates the current provider being used"""
        anime_provider = anime_sources[self.provider]()
        self.anime_provider = anime_provider

    def search_for_anime(
        self,
        user_query,
        translation_type,
        anilist_obj: "Union[AnilistBaseMediaDataSchema ,None]" = None,
        nsfw=True,
        unknown=True,
    ) -> "SearchResults | None":
        """core abstraction over all providers search functionality

        Args:
            user_query ([TODO:parameter]): [TODO:description]
            translation_type ([TODO:parameter]): [TODO:description]
            nsfw ([TODO:parameter]): [TODO:description]
            unknown ([TODO:parameter]): [TODO:description]
            anilist_obj: [TODO:description]

        Returns:
            [TODO:return]
        """
        anime_provider = self.anime_provider
        try:
            results = anime_provider.search_for_anime(
                user_query, translation_type, nsfw, unknown
            )
        except Exception as e:
            logging.error(e)
            results = None
        return results

    def get_anime(
        self,
        anime_id: str,
        anilist_obj: "Union[AnilistBaseMediaDataSchema,None]" = None,
    ) -> "Anime | None":
        """core abstraction over getting info of an anime from all providers

        Args:
            anime_id: [TODO:description]
            anilist_obj: [TODO:description]

        Returns:
            [TODO:return]
        """
        anime_provider = self.anime_provider
        try:
            results = anime_provider.get_anime(anime_id)
        except Exception as e:
            logging.error(e)
            results = None
        return results

    def get_episode_streams(
        self,
        anime,
        episode: str,
        translation_type: str,
        anilist_obj: "Union[AnilistBaseMediaDataSchema,None]" = None,
    ) -> Iterator["Server"] | None:
        """core abstractions for getting juicy streams from all providers

        Args:
            anime ([TODO:parameter]): [TODO:description]
            episode: [TODO:description]
            translation_type: [TODO:description]
            anilist_obj: [TODO:description]

        Returns:
            [TODO:return]
        """
        anime_provider = self.anime_provider
        try:
            results = anime_provider.get_episode_streams(
                anime, episode, translation_type
            )
        except Exception as e:
            logging.error(e)
            results = None
        return results  # pyright:ignore
