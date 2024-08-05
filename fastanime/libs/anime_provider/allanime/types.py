from typing import Literal, TypedDict


class AllAnimeEpisodesInfo(TypedDict):
    dub: int
    sub: int
    raw: int


class AllAnimePageInfo(TypedDict):
    total: int


class AllAnimeShow(TypedDict):
    _id: str
    name: str
    availableEpisodesDetail: AllAnimeEpisodesInfo
    __typename: str


class AllAnimeSearchResult(TypedDict):
    _id: str
    name: str
    availableEpisodes: list[str]
    __typename: str | None


class AllAnimeShows(TypedDict):
    pageInfo: AllAnimePageInfo
    edges: list[AllAnimeSearchResult]


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


Server = Literal["gogoanime", "dropbox", "wetransfer", "sharepoint"]


class AllAnimeEpisode(TypedDict):
    episodeString: str
    sourceUrls: list[AllAnimeSources]
    notes: str | None


class AllAnimeStream:
    link: str
    mp4: bool
    hls: bool | None
    resolutionStr: str
    fromCache: str
    priority: int
    headers: dict | None


class AllAnimeStreams:
    links: list[AllAnimeStream]
