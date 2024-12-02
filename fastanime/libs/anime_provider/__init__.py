from .allanime.constants import SERVERS_AVAILABLE as ALLANIME_SERVERS
from .animepahe.constants import SERVERS_AVAILABLE as ANIMEPAHE_SERVERS
from .hianime.constants import SERVERS_AVAILABLE as HIANIME_SERVERS

anime_sources = {
    "allanime": "api.AllAnime",
    "animepahe": "api.AnimePahe",
    "hianime": "api.HiAnime",
    "nyaa": "api.Nyaa",
    "yugen": "api.Yugen",
}
SERVERS_AVAILABLE = [*ALLANIME_SERVERS, *ANIMEPAHE_SERVERS, *HIANIME_SERVERS]
