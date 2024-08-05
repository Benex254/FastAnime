"""
This is the core module availing all the abstractions of the anilist api
"""

import logging
from typing import Literal

import requests

from .anilist_data_schema import (
    AnilistDataSchema,
    AnilistMediaLists,
    AnilistNotifications,
    AnilistUser,
)
from .queries_graphql import (
    airing_schedule_query,
    anime_characters_query,
    anime_query,
    anime_relations_query,
    delete_list_entry_query,
    get_logged_in_user_query,
    get_medialist_item_query,
    mark_as_read_mutation,
    media_list_mutation,
    media_list_query,
    most_favourite_query,
    most_popular_query,
    most_recently_updated_query,
    most_scored_query,
    notification_query,
    recommended_query,
    search_query,
    trending_query,
    upcoming_anime_query,
)

logger = logging.getLogger(__name__)
# from kivy.network.urlrequest import UrlRequestRequests
ANILIST_ENDPOINT = "https://graphql.anilist.co"


class AniListApi:
    """
    This class provides an abstraction for the anilist api
    """

    def login_user(self, token: str):
        self.token = token
        self.headers = {"Authorization": f"Bearer {self.token}"}
        user = self.get_logged_in_user()
        if not user:
            return
        if not user[0]:
            return
        user_info: AnilistUser = user[1]["data"]["Viewer"]  # pyright:ignore
        self.user_id = user_info["id"]  # pyright:ignore
        return user_info

    def get_notification(
        self,
    ) -> tuple[bool, AnilistNotifications] | tuple[bool, None]:
        return self._make_authenticated_request(notification_query)

    def reset_notification_count(self):
        return self._make_authenticated_request(mark_as_read_mutation)

    def update_login_info(self, user: AnilistUser, token: str):
        self.token = token
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.user_id = user["id"]

    def get_logged_in_user(self):
        if not self.headers:
            return
        return self._make_authenticated_request(get_logged_in_user_query)

    def update_anime_list(self, values_to_update: dict):
        variables = {"userId": self.user_id, **values_to_update}
        return self._make_authenticated_request(media_list_mutation, variables)

    def get_anime_list(
        self,
        status: Literal[
            "CURRENT", "PLANNING", "COMPLETED", "DROPPED", "PAUSED", "REPEATING"
        ],
    ) -> tuple[bool, AnilistMediaLists] | tuple[bool, None]:
        variables = {"status": status, "userId": self.user_id}
        return self._make_authenticated_request(media_list_query, variables)

    def get_medialist_entry(
        self, mediaId: int
    ) -> tuple[bool, dict] | tuple[bool, None]:
        variables = {"mediaId": mediaId}
        return self._make_authenticated_request(get_medialist_item_query, variables)

    def delete_medialist_entry(self, mediaId: int):
        result = self.get_medialist_entry(mediaId)
        data = result[1]
        if not result[0] or not data:
            return result
        id = data["data"]["MediaList"]["id"]
        variables = {"id": id}
        return self._make_authenticated_request(delete_list_entry_query, variables)

    def _make_authenticated_request(self, query: str, variables: dict = {}):
        """
        The core abstraction for getting authenticated data from the anilist api

        Parameters:
        ----------
        query:str
            a valid anilist graphql query
        variables:dict
            variables to pass to the anilist api
        """
        # req=UrlRequestRequests(url, self.got_data,)
        try:
            # TODO: check if data is as expected
            response = requests.post(
                ANILIST_ENDPOINT,
                json={"query": query, "variables": variables},
                timeout=10,
                headers=self.headers,
            )
            anilist_data = response.json()

            # ensuring you dont get blocked
            if (
                int(response.headers.get("X-RateLimit-Remaining", 0)) < 30
                and not response.status_code == 500
            ):
                print(
                    "Warning you are exceeding the allowed number of calls per minute"
                )
                logger.warning(
                    "You are exceeding the allowed number of calls per minute for the AniList api enforcing timeout"
                )
                print("Forced timeout will now be initiated")
                import time

                print("sleeping...")
                time.sleep(1 * 60)
            if response.status_code == 200:
                return (True, anilist_data)
            else:
                return (False, anilist_data)
        except requests.exceptions.Timeout:
            logger.warning(
                "Timeout has been exceeded this could mean anilist is down or you have lost internet connection"
            )
            return (False, None)
        except requests.exceptions.ConnectionError:
            logger.warning(
                "ConnectionError this could mean anilist is down or you have lost internet connection"
            )
            return (False, None)

        except Exception as e:
            logger.error(f"Something unexpected occured {e}")
            return (False, None)  # type: ignore

    def get_watchlist(self):
        variables = {"status": "CURRENT", "userId": self.user_id}
        return self._make_authenticated_request(media_list_query, variables)

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
        # req=UrlRequestRequests(url, self.got_data,)
        try:
            # TODO: check if data is as expected
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
                print(
                    "Warning you are exceeding the allowed number of calls per minute"
                )
                logger.warning(
                    "You are exceeding the allowed number of calls per minute for the AniList api enforcing timeout"
                )
                print("Forced timeout will now be initiated")
                import time

                print("sleeping...")
                time.sleep(1 * 60)
            if response.status_code == 200:
                return (True, anilist_data)
            else:
                return (False, anilist_data)
        except requests.exceptions.Timeout:
            logger.warning(
                "Timeout has been exceeded this could mean anilist is down or you have lost internet connection"
            )
            return (
                False,
                {
                    "Error": "Timeout Exceeded for connection there might be a problem with your internet or anilist is down."
                },
            )  # type: ignore
        except requests.exceptions.ConnectionError:
            logger.warning(
                "ConnectionError this could mean anilist is down or you have lost internet connection"
            )
            return (
                False,
                {
                    "Error": "There might be a problem with your internet or anilist is down."
                },
            )  # type: ignore
        except Exception as e:
            logger.error(f"Something unexpected occured {e}")
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
