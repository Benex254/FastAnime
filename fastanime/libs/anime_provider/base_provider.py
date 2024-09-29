import os

import requests
from yt_dlp.utils.networking import random_user_agent


class AnimeProvider:
    session: requests.Session

    USER_AGENT = random_user_agent()
    HEADERS = {}

    def __init__(
        self, cache_requests=os.environ.get("FASTANIME_CACHE_REQUESTS", "false")
    ) -> None:
        if cache_requests.lower() == "true":
            from ...constants import APP_CACHE_DIR
            from ..common.requests_cacher import CachedRequestsSession

            self.session = CachedRequestsSession(
                os.path.join(APP_CACHE_DIR, "cached_requests.db"),
                os.path.join(APP_CACHE_DIR, "cached_requests.lock"),
            )
        else:
            self.session = requests.session()
        self.session.headers.update({"User-Agent": self.USER_AGENT, **self.HEADERS})
