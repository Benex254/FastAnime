import logging

logger = logging.getLogger(__name__)

ANILIST_ENDPOINT = "https://graphql.anilist.co"


anime_title_query = """
query ($query: String) {
  Page(perPage: 50) {
    pageInfo {
      total
    }
    media(search: $query, type: ANIME) {
      id
      idMal
      title {
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
    from requests import post

    try:
        response = post(
            ANILIST_ENDPOINT,
            json={"query": query, "variables": variables},
            timeout=10,
        )
        anilist_data = response.json()

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
            return []
    except Exception as e:
        logger.error(f"Something unexpected occured {e}")
        return []


def downloaded_anime_titles(ctx, param, incomplete):
    import os

    from ..constants import USER_VIDEOS_DIR

    try:
        titles = [
            title
            for title in os.listdir(USER_VIDEOS_DIR)
            if title.lower().startswith(incomplete.lower()) or not incomplete
        ]
        return titles
    except Exception:
        return []


def anime_titles_shell_complete(ctx, param, incomplete):
    incomplete = incomplete.strip()
    if not incomplete:
        incomplete = None
        variables = {}
    else:
        variables = {"query": incomplete}
    return get_anime_titles(anime_title_query, variables)


if __name__ == "__main__":
    t = input("Enter title")
    results = get_anime_titles(anime_title_query, {"query": t})
    print(results)
