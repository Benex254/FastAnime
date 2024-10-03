"""An abstraction over all providers offering added features with a simple and well typed api"""

import importlib
import logging
import os
from typing import TYPE_CHECKING

from .libs.anime_provider import anime_sources

if TYPE_CHECKING:
    from typing import Iterator

    from .libs.anime_provider.types import Anime, SearchResults, Server

logger = logging.getLogger(__name__)


# TODO: improve performance of this class and add cool features like auto retry
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

    def __init__(
        self,
        provider,
        cache_requests=os.environ.get("FASTANIME_CACHE_REQUESTS", "false"),
        use_persistent_provider_store=os.environ.get(
            "FASTANIME_USE_PERSISTENT_PROVIDER_STORE", "false"
        ),
        dynamic=False,
        retries=0,
    ) -> None:
        self.provider = provider
        self.dynamic = dynamic
        self.retries = retries
        self.cache_requests = cache_requests
        self.use_persistent_provider_store = use_persistent_provider_store
        self.lazyload_provider(self.provider)

    def lazyload_provider(self, provider):
        """updates the current provider being used"""
        try:
            self.anime_provider.session.kill_connection_to_db()
        except Exception:
            pass
        _, anime_provider_cls_name = anime_sources[provider].split(".", 1)
        package = f"fastanime.libs.anime_provider.{provider}"
        provider_api = importlib.import_module(".api", package)
        anime_provider = getattr(provider_api, anime_provider_cls_name)
        self.anime_provider = anime_provider(
            self.cache_requests, self.use_persistent_provider_store
        )

    def search_for_anime(
        self,
        user_query,
        translation_type,
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
        results = anime_provider.search_for_anime(
            user_query, translation_type, nsfw, unknown
        )

        return results

    def get_anime(
        self,
        anime_id: str,
    ) -> "Anime | None":
        """core abstraction over getting info of an anime from all providers

        Args:
            anime_id: [TODO:description]
            anilist_obj: [TODO:description]

        Returns:
            [TODO:return]
        """
        anime_provider = self.anime_provider
        results = anime_provider.get_anime(anime_id)

        return results

    def get_episode_streams(
        self,
        anime_id,
        episode: str,
        translation_type: str,
    ) -> "Iterator[Server] | None":
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
        results = anime_provider.get_episode_streams(
            anime_id, episode, translation_type
        )
        return results
