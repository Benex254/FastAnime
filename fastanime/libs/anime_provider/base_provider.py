import requests


class AnimeProvider:
    session: requests.Session

    def __init__(self) -> None:
        self.session = requests.session()
