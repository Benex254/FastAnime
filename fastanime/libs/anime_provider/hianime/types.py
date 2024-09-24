from typing import Literal, TypedDict


class HiAnimeSkipTime(TypedDict):
    start: int
    end: int


class HiAnimeSource(TypedDict):
    file: str
    type: str


class HiAnimeTrack(TypedDict):
    file: str
    label: str
    kind: Literal["captions", "thumbnails", "audio"]


class HiAnimeStream(TypedDict):
    sources: list[HiAnimeSource]
    tracks: list[HiAnimeTrack]
    encrypted: bool
    intro: HiAnimeSkipTime
    outro: HiAnimeSkipTime
    server: int
