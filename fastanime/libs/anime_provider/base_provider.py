import os

import requests
from yt_dlp.utils.networking import random_user_agent

from ...constants import APP_CACHE_DIR
from .providers_store import ProviderStore


class AnimeProvider:
    session: requests.Session

    USER_AGENT = random_user_agent()
    HEADERS = {}

    def __init__(self, cache_requests, use_persistent_provider_store) -> None:
        if cache_requests.lower() == "true":
            from ..common.requests_cacher import CachedRequestsSession

            self.session = CachedRequestsSession(
                os.path.join(APP_CACHE_DIR, "cached_requests.db"),
                max_lifetime=int(
                    os.environ.get("FASTANIME_MAX_CACHE_LIFETIME", 259200)
                ),
            )
        else:
            self.session = requests.session()
        self.session.headers.update({"User-Agent": self.USER_AGENT, **self.HEADERS})
        if use_persistent_provider_store.lower() == "true":
            self.store = ProviderStore(
                "persistent",
                self.__class__.__name__,
                os.path.join(APP_CACHE_DIR, "anime_providers_store.db"),
            )
        else:
            self.store = ProviderStore("memory")
