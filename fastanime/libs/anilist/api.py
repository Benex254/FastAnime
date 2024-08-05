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


class AniListApi:
    """
    This class provides an abstraction for the anilist api
    """

    def get_data(
        self, query: str, variables: dict = {}
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
        # req=UrlRequestRequests(url, self.got_data,)
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

    def search(
        self,
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
        search_results = self.get_data(search_query, variables=variables)
        return search_results

    def get_anime(self, id: int):
        """
        Gets a single anime by a valid anilist anime id
        """
        variables = {"id": id}
        return self.get_data(anime_query, variables)

    def get_trending(self, *_, **kwargs):
        """
        Gets the currently trending anime
        """
        trending = self.get_data(trending_query)
        return trending

    def get_most_favourite(self, *_, **kwargs):
        """
        Gets the most favoured anime on anilist
        """
        most_favourite = self.get_data(most_favourite_query)
        return most_favourite

    def get_most_scored(self, *_, **kwargs):
        """
        Gets most scored anime on anilist
        """
        most_scored = self.get_data(most_scored_query)
        return most_scored

    def get_most_recently_updated(self, *_, **kwargs):
        """
        Gets most recently updated anime from anilist
        """
        most_recently_updated = self.get_data(most_recently_updated_query)
        return most_recently_updated

    def get_most_popular(self):
        """
        Gets most popular anime on anilist
        """
        most_popular = self.get_data(most_popular_query)
        return most_popular

    # FIXME:dont know why its not giving useful data
    def get_recommended_anime_for(self, id: int, *_, **kwargs):
        recommended_anime = self.get_data(recommended_query)
        return recommended_anime

    def get_charcters_of(self, id: int, *_, **kwargs):
        variables = {"id": id}
        characters = self.get_data(anime_characters_query, variables)
        return characters

    def get_related_anime_for(self, id: int, *_, **kwargs):
        variables = {"id": id}
        related_anime = self.get_data(anime_relations_query, variables)
        return related_anime

    def get_airing_schedule_for(self, id: int, *_, **kwargs):
        variables = {"id": id}
        airing_schedule = self.get_data(airing_schedule_query, variables)
        return airing_schedule

    def get_upcoming_anime(self, page: int = 1, *_, **kwargs):
        """
        Gets upcoming anime from anilist
        """
        variables = {"page": page}
        upcoming_anime = self.get_data(upcoming_anime_query, variables)
        return upcoming_anime
