from typing import Literal, TypedDict


class AnimePaheSearchResult(TypedDict):
    id: int
    title: str
    type: str
    episodes: int
    status: str
    season: str
    year: int
    score: int
    poster: str
    session: str


class AnimePaheSearchPage(TypedDict):
    total: int
    per_page: int
    current_page: int
    last_page: int
    _from: int
    to: int
    data: list[AnimePaheSearchResult]


class Episode(TypedDict):
    id: int
    anime_id: int
    episode: int
    episode2: int
    edition: str
    title: str
    snapshot: str  # episode image
    disc: str
    audio: Literal["eng", "jpn"]
    duration: str  # time 00:00:00
    session: str
    filler: int
    created_at: str


class AnimePaheAnimePage(TypedDict):
    total: int
    per_page: int
    current_page: int
    last_page: int
    next_page_url: str | None
    prev_page_url: str | None
    _from: int
    to: int
    data: list[Episode]


class Server:
    type: str
    data_src = "https://kwik.si/e/PImJ0u7Y3M0G"
    data_fansub: str
    data_resolution: Literal["360", "720", "1080"]
    data_audio: Literal["eng", "jpn"]
    data_av1: str
