from typing import Literal, TypedDict


class AniWatchSkipTime(TypedDict):
    start: int
    end: int


class AniWatchSource(TypedDict):
    file: str
    type: str


class AniWatchTrack(TypedDict):
    file: str
    label: str
    kind: Literal["captions", "thumbnails", "audio"]


class AniWatchStream(TypedDict):
    sources: list[AniWatchSource]
    tracks: list[AniWatchTrack]
    encrypted: bool
    intro: AniWatchSkipTime
    outro: AniWatchSkipTime
    server: int
