from typing import Literal

from fastapi import FastAPI

from ..AnimeProvider import AnimeProvider

app = FastAPI()
anime_provider = AnimeProvider("allanime", "true", "true")


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
