from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from ...libs.anilist.types import AnilistDataSchema

import logging

logger = logging.getLogger(__name__)

ANILIST_ENDPOINT = "https://graphql.anilist.co"


anime_title_query = """
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


def get_anime_titles(query: str, variables: dict = {}):
    """the abstraction over all none authenticated requests and that returns data of a similar type

    Args:
        query: the anilist query
        variables: the anilist api variables

    Returns:
        a boolean indicating success and none or an anilist object depending on success
    """
    try:
        response = requests.post(
            ANILIST_ENDPOINT,
            json={"query": query, "variables": variables},
            timeout=10,
        )
        anilist_data: AnilistDataSchema = response.json()

        # ensuring you dont get blocked
        if (
            int(response.headers.get("X-RateLimit-Remaining", 0)) < 30
            and not response.status_code == 500
        ):
            print("Warning you are exceeding the allowed number of calls per minute")
            logger.warning(
                "You are exceeding the allowed number of calls per minute for the AniList api enforcing timeout"
            )
            print("Forced timeout will now be initiated")
            import time

            print("sleeping...")
            time.sleep(1 * 60)
        if response.status_code == 200:
            eng_titles = [
                anime["title"]["english"]
                for anime in anilist_data["data"]["Page"]["media"]
                if anime["title"]["english"]
            ]
            romaji_titles = [
                anime["title"]["romaji"]
                for anime in anilist_data["data"]["Page"]["media"]
                if anime["title"]["romaji"]
            ]
            return [*eng_titles, *romaji_titles]
        else:
            return ["non 200 status code"]
    except requests.exceptions.Timeout:
        logger.warning(
            "Timeout has been exceeded this could mean anilist is down or you have lost internet connection"
        )
        return ["timeout exceeded"]
    except requests.exceptions.ConnectionError:
        logger.warning(
            "ConnectionError this could mean anilist is down or you have lost internet connection"
        )
        return ["connection error"]
    except Exception as e:
        logger.error(f"Something unexpected occured {e}")
        return ["unexpected error"]


def anime_titles_shell_complete(ctx, param, incomplete):
    return [name for name in get_anime_titles(anime_title_query, {"query": incomplete})]
