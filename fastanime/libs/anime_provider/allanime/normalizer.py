from ..types import Anime, EpisodesDetail, SearchResults
from .types import AllAnimeEpisode, AllAnimeSearchResults, AllAnimeShow


def normalize_search_results(search_results: AllAnimeSearchResults) -> SearchResults:
    page_info = search_results["shows"]["pageInfo"]
    results = []
    for result in search_results["shows"]["edges"]:
        normalized_result = {
            "id": result["_id"],
            "title": result["name"],
            "type": result["__typename"],
            "availableEpisodes": result["availableEpisodes"],
        }
        results.append(normalized_result)

    normalized_search_results: SearchResults = {
        "pageInfo": page_info,
        "results": results,
    }

    return normalized_search_results


def normalize_anime(anime: AllAnimeShow) -> Anime:
    id: str = anime["_id"]
    title: str = anime["name"]
    availableEpisodesDetail: EpisodesDetail = anime["availableEpisodesDetail"]
    type = anime.get("__typename")
    normalized_anime: Anime = {
        "id": id,
        "title": title,
        "availableEpisodesDetail": availableEpisodesDetail,
        "type": type,
    }
    return normalized_anime


def normalize_episode(episode: AllAnimeEpisode):
    pass
