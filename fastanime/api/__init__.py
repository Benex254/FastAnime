from typing import Literal

from fastapi import FastAPI
from requests import post
from thefuzz import fuzz

from ..AnimeProvider import AnimeProvider
from ..Utility.data import anime_normalizer

app = FastAPI()
anime_provider = AnimeProvider("allanime", "true", "true")
ANILIST_ENDPOINT = "https://graphql.anilist.co"


@app.get("/search")
def search_for_anime(title: str, translation_type: Literal["dub", "sub"] = "sub"):
    return anime_provider.search_for_anime(title, translation_type)


@app.get("/anime/{anime_id}")
def get_anime(anime_id: str):
    return anime_provider.get_anime(anime_id)


@app.get("/anime/{anime_id}/watch")
def get_episode_streams(
    anime_id: str, episode: str, translation_type: Literal["sub", "dub"]
):
    return anime_provider.get_episode_streams(anime_id, episode, translation_type)


def get_anime_by_anilist_id(anilist_id: int):
    query = f"""
    query {{
        Media(id: {anilist_id}) {{
            id
            title {{
                romaji
                english
                native
            }}
            synonyms
            episodes
            duration
        }}
    }}
    """
    response = post(ANILIST_ENDPOINT, json={"query": query}).json()
    return response["data"]["Media"]


@app.get("/watch/{anilist_id}")
def get_episode_streams_by_anilist_id(
    anilist_id: int, episode: str, translation_type: Literal["sub", "dub"]
):
    anime = get_anime_by_anilist_id(anilist_id)
    if not anime:
        return
    if search_results := anime_provider.search_for_anime(
        str(anime["title"]["romaji"] or anime["title"]["english"]), translation_type
    ):
        if not search_results["results"]:
            return

        def match_title(possible_user_requested_anime_title):
            possible_user_requested_anime_title = anime_normalizer.get(
                possible_user_requested_anime_title, possible_user_requested_anime_title
            )
            title_a = str(anime["title"]["romaji"])
            title_b = str(anime["title"]["english"])
            percentage_ratio = max(
                *[
                    fuzz.ratio(
                        title.lower(), possible_user_requested_anime_title.lower()
                    )
                    for title in anime["synonyms"]
                ],
                fuzz.ratio(
                    title_a.lower(), possible_user_requested_anime_title.lower()
                ),
                fuzz.ratio(
                    title_b.lower(), possible_user_requested_anime_title.lower()
                ),
            )
            return percentage_ratio

        provider_anime = max(
            search_results["results"], key=lambda x: match_title(x["title"])
        )
        anime_provider.get_anime(provider_anime["id"])
        return anime_provider.get_episode_streams(
            provider_anime["id"], episode, translation_type
        )
