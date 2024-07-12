from typing import TypedDict


class PageInfo(TypedDict):
    total: int


# search data
class SearchResult(TypedDict):
    id: str
    title: str
    availableEpisodes: list[str]
    type: str


class SearchResults(TypedDict):
    pageInfo: PageInfo
    results: list[SearchResult]


# anime data
class EpisodesDetail(TypedDict):
    dub: int
    sub: int
    raw: int


class Anime(TypedDict):
    id: str
    title: str
    availableEpisodesDetail: EpisodesDetail
    type: str
