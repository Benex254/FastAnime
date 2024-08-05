from .allanime.api import AllAnimeAPI
from .animepahe.api import AnimePaheApi
from .aniwatch.api import AniWatchApi

anime_sources = {
    "allanime": AllAnimeAPI,
    "animepahe": AnimePaheApi,
    "aniwatch": AniWatchApi,
}
