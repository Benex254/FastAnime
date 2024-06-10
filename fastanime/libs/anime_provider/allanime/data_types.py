from typing import TypedDict


class AllAnimeEpisodesInfo(TypedDict):
    dub: int
    sub: int
    raw: int


class AllAnimePageInfo(TypedDict):
    total: int


class AllAnimeShow(TypedDict):
    _id: str
    name: str
    availableEpisodes: AllAnimeEpisodesInfo
    __typename: str


class AllAnimeShows(TypedDict):
    pageInfo: AllAnimePageInfo
    edges: list[AllAnimeShow]


class AllAnimeSearchResults(TypedDict):
    shows: AllAnimeShows


class AllAnimeSourcesDownloads(TypedDict):
    sourceName: str
    dowloadUrl: str


class AllAnimeSources(TypedDict):
    sourceUrl: str
    priority: float
    sandbox: str
    sourceName: str
    type: str
    className: str
    streamerId: str
    downloads: AllAnimeSourcesDownloads


class AllAnimeEpisode(TypedDict):
    episodeString: str
    sourceUrls: list[AllAnimeSources]
    notes: str | None
