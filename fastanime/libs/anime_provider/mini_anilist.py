import logging
from typing import TYPE_CHECKING

from requests import post
from thefuzz import fuzz

if TYPE_CHECKING:
    from ..anilist.types import AnilistDataSchema
logger = logging.getLogger(__name__)

ANILIST_ENDPOINT = "https://graphql.anilist.co"
"""
query($query:String){
    Page(perPage:50){
        pageInfo{
            total
            currentPage
            hasNextPage
        }
        media(search:$query,type:ANIME){
        id
        idMal
        title{
            romaji
            english
        }
        episodes
        status
        nextAiringEpisode {
            timeUntilAiring
            airingAt
            episode
        }
    }
  }
}
"""


def search_for_anime_with_anilist(anime_title: str):
    query = """
    query($query:String){
        Page(perPage:50){
            pageInfo{
                total
                currentPage
                hasNextPage
            }
            media(search:$query,type:ANIME){
                id
                idMal
                title{
                    romaji
                    english
                }
                episodes
                status
                nextAiringEpisode {
                    timeUntilAiring
                    airingAt
                    episode
                }
            }
        }
    }
    """
    response = post(
        ANILIST_ENDPOINT,
        json={"query": query, "variables": {"query": anime_title}},
        timeout=10,
    )
    if response.status_code == 200:
        anilist_data: "AnilistDataSchema" = response.json()
        return {
            "pageInfo": anilist_data["data"]["Page"]["pageInfo"],
            "results": [
                {
                    "id": anime_result["id"],
                    "title": anime_result["title"]["romaji"]
                    or anime_result["title"]["english"],
                    "type": "anime",
                    "availableEpisodes": list(
                        range(
                            1,
                            (
                                anime_result["episodes"]
                                if not anime_result["status"] == "RELEASING"
                                and anime_result["episodes"]
                                else (
                                    anime_result["nextAiringEpisode"]["episode"] - 1
                                    if anime_result["nextAiringEpisode"]
                                    else 0
                                )
                            ),
                        )
                    ),
                }
                for anime_result in anilist_data["data"]["Page"]["media"]
            ],
        }


def get_mal_id_and_anilist_id(anime_title: str) -> "dict[str,int] | None":
    """the abstraction over all none authenticated requests and that returns data of a similar type

    Args:
        query: the anilist query
        variables: the anilist api variables

    Returns:
        a boolean indicating success and none or an anilist object depending on success
    """
    query = """
    query($query:String){
        Page(perPage:50){
            pageInfo{
                total
                currentPage
                hasNextPage
            }
            media(search:$query,type:ANIME){
                    id
                    idMal
                title{
                    romaji
                    english
                }
            }
        }
    }
    """

    try:
        variables = {"query": anime_title}
        response = post(
            ANILIST_ENDPOINT,
            json={"query": query, "variables": variables},
            timeout=10,
        )
        anilist_data: "AnilistDataSchema" = response.json()
        if response.status_code == 200:
            anime = max(
                anilist_data["data"]["Page"]["media"],
                key=lambda anime: max(
                    (
                        fuzz.ratio(anime, str(anime["title"]["romaji"])),
                        fuzz.ratio(anime_title, str(anime["title"]["english"])),
                    )
                ),
            )
            return {"id_anilist": anime["id"], "id_mal": anime["idMal"]}
    except Exception as e:
        logger.error(f"Something unexpected occured {e}")
