"""
This is the core module availing all the abstractions of the anilist api
"""

import requests

from .anilist_data_schema import AnilistDataSchema
from .queries_graphql import (
    airing_schedule_query,
    anime_characters_query,
    anime_query,
    anime_relations_query,
    most_favourite_query,
    most_popular_query,
    most_recently_updated_query,
    most_scored_query,
    recommended_query,
    search_query,
    trending_query,
    upcoming_anime_query,
)

# from kivy.network.urlrequest import UrlRequestRequests


class AniList:
    """
    This class provides an abstraction for the anilist api
    """

    @classmethod
    def get_data(
        cls, query: str, variables: dict = {}
    ) -> tuple[bool, AnilistDataSchema]:
        """
        The core abstraction for getting data from the anilist api

        Parameters:
        ----------
        query:str
            a valid anilist graphql query
        variables:dict
            variables to pass to the anilist api
        """
        url = "https://graphql.anilist.co"
        # req=UrlRequestRequests(url, cls.got_data,)
        try:
            # TODO: check if data is as expected
            response = requests.post(
                url, json={"query": query, "variables": variables}, timeout=10
            )
            anilist_data: AnilistDataSchema = response.json()
            return (True, anilist_data)
        except requests.exceptions.Timeout:
            return (
                False,
                {
                    "Error": "Timeout Exceeded for connection there might be a problem with your internet or anilist is down."
                },
            )  # type: ignore
        except requests.exceptions.ConnectionError:
            return (
                False,
                {
                    "Error": "There might be a problem with your internet or anilist is down."
                },
            )  # type: ignore
        except Exception as e:
            return (False, {"Error": f"{e}"})  # type: ignore

    @classmethod
    def search(
        cls,
        query: str | None = None,
        sort: str | None = None,
        genre_in: list[str] | None = None,
        id_in: list[int] | None = None,
        genre_not_in: list[str] = ["hentai"],
        popularity_greater: int | None = None,
        popularity_lesser: int | None = None,
        averageScore_greater: int | None = None,
        averageScore_lesser: int | None = None,
        tag_in: list[str] | None = None,
        tag_not_in: list[str] | None = None,
        status: str | None = None,
        status_in: list[str] | None = None,
        status_not_in: list[str] | None = None,
        endDate_greater: int | None = None,
        endDate_lesser: int | None = None,
        start_greater: int | None = None,
        start_lesser: int | None = None,
        page: int | None = None,
        **kwargs,
    ):
        """
        A powerful method for searching anime using the anilist api availing most of its options
        """
        variables = {}
        for key, val in list(locals().items())[1:]:
            if val is not None and key not in ["variables"]:
                variables[key] = val
        search_results = cls.get_data(search_query, variables=variables)
        return search_results

    @classmethod
    def get_anime(cls, id: int):
        """
        Gets a single anime by a valid anilist anime id
        """
        variables = {"id": id}
        return cls.get_data(anime_query, variables)

    @classmethod
    def get_trending(cls, *_, **kwargs):
        """
        Gets the currently trending anime
        """
        trending = cls.get_data(trending_query)
        return trending

    @classmethod
    def get_most_favourite(cls, *_, **kwargs):
        """
        Gets the most favoured anime on anilist
        """
        most_favourite = cls.get_data(most_favourite_query)
        return most_favourite

    @classmethod
    def get_most_scored(cls, *_, **kwargs):
        """
        Gets most scored anime on anilist
        """
        most_scored = cls.get_data(most_scored_query)
        return most_scored

    @classmethod
    def get_most_recently_updated(cls, *_, **kwargs):
        """
        Gets most recently updated anime from anilist
        """
        most_recently_updated = cls.get_data(most_recently_updated_query)
        return most_recently_updated

    @classmethod
    def get_most_popular(cls, *_, **kwargs):
        """
        Gets most popular anime on anilist
        """
        most_popular = cls.get_data(most_popular_query)
        return most_popular

    # FIXME:dont know why its not giving useful data
    @classmethod
    def get_recommended_anime_for(cls, id: int, *_, **kwargs):
        recommended_anime = cls.get_data(recommended_query)
        return recommended_anime

    @classmethod
    def get_charcters_of(cls, id: int, *_, **kwargs):
        variables = {"id": id}
        characters = cls.get_data(anime_characters_query, variables)
        return characters

    @classmethod
    def get_related_anime_for(cls, id: int, *_, **kwargs):
        variables = {"id": id}
        related_anime = cls.get_data(anime_relations_query, variables)
        return related_anime

    @classmethod
    def get_airing_schedule_for(cls, id: int, *_, **kwargs):
        variables = {"id": id}
        airing_schedule = cls.get_data(airing_schedule_query, variables)
        return airing_schedule

    @classmethod
    def get_upcoming_anime(cls, page: int = 1, *_, **kwargs):
        """
        Gets upcoming anime from anilist
        """
        variables = {"page": page}
        upcoming_anime = cls.get_data(upcoming_anime_query, variables)
        return upcoming_anime
