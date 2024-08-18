from .allanime import SERVERS_AVAILABLE as ALLANIME_SERVERS
from .animepahe import SERVERS_AVAILABLE as ANIMEPAHESERVERS
from .aniwatch import SERVERS_AVAILABLE as ANIWATCHSERVERS

anime_sources = {
    "allanime": "api.AllAnimeAPI",
    "animepahe": "api.AnimePaheApi",
    "aniwatch": "api.AniWatchApi",
}
SERVERS_AVAILABLE = [*ALLANIME_SERVERS, *ANIMEPAHESERVERS, *ANIWATCHSERVERS]
