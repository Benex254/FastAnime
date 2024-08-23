import requests
from yt_dlp.utils.networking import random_user_agent


class MangaProvider:
    session: requests.Session

    USER_AGENT = random_user_agent()
    HEADERS = {}

    def __init__(self) -> None:
        self.session = requests.session()
        self.session.headers.update({"User-Agent": self.USER_AGENT, **self.HEADERS})
