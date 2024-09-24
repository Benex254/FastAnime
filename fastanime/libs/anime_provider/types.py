from typing import Literal, TypedDict


class PageInfo(TypedDict):
    total: int
    perPage: int
    currentPage: int


#
# class EpisodesDetail(TypedDict):
#     dub: int
#     sub: int
#     raw: int
#


# search data
class SearchResult(TypedDict):
    id: str
    title: str
    otherTitles: list[str]
    availableEpisodes: list[str]
    type: str
    score: int
    status: str
    season: str
    poster: str


class SearchResults(TypedDict):
    pageInfo: PageInfo
    results: list[SearchResult]


# anime data
class AnimeEpisodeDetails(TypedDict):
    dub: list[str]
    sub: list[str]
    raw: list[str]


#
# class AnimeEpisode(TypedDict):
#     id: str
#     title: str
#


class AnimeEpisodeInfo(TypedDict):
    id: str
    title: str
    episode: str
    poster: str | None
    duration: str | None
    translation_type: str | None


class Anime(TypedDict):
    id: str
    title: str
    availableEpisodesDetail: AnimeEpisodeDetails
    type: str | None
    episodesInfo: list[AnimeEpisodeInfo] | None
    poster: str
    year: str


class EpisodeStream(TypedDict):
    resolution: str | None
    link: str
    hls: bool | None
    mp4: bool | None
    priority: int | None
    quality: Literal["360", "720", "1080", "unknown"]
    translation_type: Literal["dub", "sub"]


class Subtitle(TypedDict):
    url: str
    language: str


class Server(TypedDict):
    headers: dict
    subtitles: list[Subtitle]
    audio: list
    server: str
    episode_title: str
    links: list[EpisodeStream]
