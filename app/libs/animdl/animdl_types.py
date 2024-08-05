from typing import NamedTuple, TypedDict


class AnimdlAnimeUrlAndTitle(NamedTuple):
    anime_title: str
    animdl_anime_url: str

class AnimdlEpisodeStream(TypedDict):
    stream_url:str
    quality:int
    subtitle:list[str] | None
    audio_tracks: list[str] | None
    title:str|None


class AnimdlAnimeEpisode(TypedDict):
    episode:int
    streams:list[AnimdlEpisodeStream]
    
class AnimdlData(NamedTuple):
    anime_title:str
    episodes:list[AnimdlAnimeEpisode]

