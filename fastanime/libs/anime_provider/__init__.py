from .allanime.constants import SERVERS_AVAILABLE as ALLANIME_SERVERS
from .animepahe.constants import SERVERS_AVAILABLE as ANIMEPAHESERVERS
from .aniwatch.constants import SERVERS_AVAILABLE as ANIWATCHSERVERS

anime_sources = {
    "allanime": "api.AllAnimeAPI",
    "animepahe": "api.AnimePaheApi",
    "aniwatch": "api.AniWatchApi",
}
SERVERS_AVAILABLE = [*ALLANIME_SERVERS, *ANIMEPAHESERVERS, *ANIWATCHSERVERS]
