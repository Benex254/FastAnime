"""
This module defines the shape of the anilist data that can be received in order to enhance dev experience
"""

from typing import TypedDict


class AnilistMediaTitle(TypedDict):
    english: str
    romaji: str


class AnilistImage(TypedDict):
    medium: str
    extraLarge: str
    small: str
    large: str


class AnilistMediaTrailer(TypedDict):
    id: str
    site: str


class AnilistStudio(TypedDict):
    name: str
    favourites: int
    isAnimationStudio: bool


class AnilistStudioNodes(TypedDict):
    nodes: list[AnilistStudio]


class AnilistMediaTag(TypedDict):
    name: str
    rank: int


class AnilistDateObject(TypedDict):
    day: int
    month: int
    year: int


class AnilistMediaNextAiringEpisode(TypedDict):
    timeUntilAiring: int
    airingAt: int
    episode: int


class AnilistUser(TypedDict):
    name: str
    avatar: AnilistImage


class AnilistReview(TypedDict):
    summary: str
    user: AnilistUser


class AnilistReviewNodes(TypedDict):
    nodes: list[AnilistReview]


class AnilistMediaRanking(TypedDict):
    rank: int
    context: str


class AnilistExternalLink(TypedDict):
    url: str
    site: str
    icon: str


class AnilistName(TypedDict):
    full: str


class AnilistCharacter(TypedDict):
    name: AnilistName
    gender: str | None
    dateOfBirth: AnilistDateObject | None
    age: int
    image: AnilistImage
    description: str


# class AnilistCharacterNode(TypedDict):
#     node


class AnilistVoiceActor(TypedDict):
    name: AnilistName
    image: AnilistImage


class AnilistCharactersEdge(TypedDict):
    node: list[AnilistCharacter]
    voiceActors: list[AnilistVoiceActor]


class AnilistCharactersEdges(TypedDict):
    edges: list[AnilistCharactersEdge]


class AnilistBaseMediaDataSchema(TypedDict):
    """
    This a convenience class is used to type the received Anilist data to enhance dev experience
    """

    id: str
    title: AnilistMediaTitle
    coverImage: AnilistImage
    trailer: AnilistMediaTrailer | None
    popularity: int
    favourites: int
    averageScore: int
    genres: list[str]
    episodes: int | None
    description: str | None
    studios: AnilistStudioNodes
    tags: list[AnilistMediaTag]
    startDate: AnilistDateObject
    endDate: AnilistDateObject
    status: str
    nextAiringEpisode: AnilistMediaNextAiringEpisode
    season: str
    seasonYear: int
    duration: int
    synonyms: list[str]
    countryOfOrigin: str
    source: str
    hashtag: str | None
    siteUrl: str
    reviews: AnilistReviewNodes
    bannerImage: str | None
    rankings: list[AnilistMediaRanking]
    externalLinks: list[AnilistExternalLink]
    characters: AnilistCharactersEdges
    format: str


class AnilistPageInfo(TypedDict):
    total: int
    perPage: int
    currentPage: int
    hasNextPage: bool


class AnilistPage(TypedDict):
    media: list[AnilistBaseMediaDataSchema]
    pageInfo: AnilistPageInfo


class AnilistPages(TypedDict):
    Page: AnilistPage


class AnilistDataSchema(TypedDict):
    data: AnilistPages
    Error: str
