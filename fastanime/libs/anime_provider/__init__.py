from .allanime.api import AllAnimeAPI
from .animepahe.api import AnimePaheApi

anime_sources = {"allanime": AllAnimeAPI, "animepahe": AnimePaheApi}


class Anime_Provider:
    def search_for_anime(self):
        pass

    def get_anime(self):
        pass

    def get_episode_streams(self):
        pass
