from .allanime.constants import SERVERS_AVAILABLE as ALLANIME_SERVERS
from .animepahe.constants import SERVERS_AVAILABLE as ANIMEPAHE_SERVERS
from .hianime.constants import SERVERS_AVAILABLE as HIANIME_SERVERS

anime_sources = {
    "allanime": "api.AllAnimeAPI",
    "animepahe": "api.AnimePaheApi",
    "hianime": "api.HiAnimeApi",
    "nyaa": "api.NyaaApi",
    "yugen": "api.YugenApi"
}
SERVERS_AVAILABLE = [*ALLANIME_SERVERS, *ANIMEPAHE_SERVERS, *HIANIME_SERVERS]
