"""
This is the core module availing all the abstractions of the anilist api
"""

import logging
from typing import TYPE_CHECKING

import requests

from .queries_graphql import (
    airing_schedule_query,
    anime_characters_query,
    anime_query,
    anime_relations_query,
    delete_list_entry_query,
    get_logged_in_user_query,
    get_medialist_item_query,
    get_user_info,
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

if TYPE_CHECKING:
    from .types import (
        AnilistDataSchema,
        AnilistMediaLists,
        AnilistMediaListStatus,
        AnilistNotifications,
        AnilistUser_,
        AnilistUserData,
        AnilistViewerData,
    )
logger = logging.getLogger(__name__)
ANILIST_ENDPOINT = "https://graphql.anilist.co"


class AniListApi:
    """An abstraction over the anilist api offering an easy and simple interface

    Attributes:
        session: [TODO:attribute]
        session: [TODO:attribute]
        token: [TODO:attribute]
        headers: [TODO:attribute]
        user_id: [TODO:attribute]
        token: [TODO:attribute]
        headers: [TODO:attribute]
        user_id: [TODO:attribute]
    """

    session: requests.Session

    def __init__(self) -> None:
        self.session = requests.session()

    def login_user(self, token: str):
        """methosd used to login a new user enabling authenticated requests

        Args:
            token: anilist app token

        Returns:
            the logged in user
        """
        self.token = token
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.session.headers.update(self.headers)
        success, user = self.get_logged_in_user()
        if not user:
            return
        if not success or not user:
            return
        user_info: "AnilistUser_" = user["data"]["Viewer"]
        self.user_id = user_info["id"]
        return user_info

    def get_notification(
        self,
    ) -> tuple[bool, "AnilistNotifications"] | tuple[bool, None]:
        """get the top five latest notifications for anime thats airing

        Returns:
            airing notifications
        """
        return self._make_authenticated_request(notification_query)

    def update_login_info(self, user: "AnilistUser_", token: str):
        """method used to login a user enabling authenticated requests

        Args:
            user: an anilist user object
            token: the login token
        """
        self.token = token
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.session.headers.update(self.headers)
        self.user_id = user["id"]

    def get_user_info(self) -> tuple[bool, "AnilistUserData"] | tuple[bool, None]:
        """get the details of the user who is currently logged in

        Returns:
            an anilist user
        """

        return self._make_authenticated_request(get_user_info, {"userId": self.user_id})

    def get_logged_in_user(
        self,
    ) -> tuple[bool, "AnilistViewerData"] | tuple[bool, None]:
        """get the details of the user who is currently logged in

        Returns:
            an anilist user
        """
        if not self.headers:
            return (False, None)
        return self._make_authenticated_request(get_logged_in_user_query)

    def update_anime_list(self, values_to_update: dict):
        """a powerful method for managing mediaLists giving full power to the user

        Args:
            values_to_update: a dict containing valid media list options

        Returns:
            an anilist object indicating success
        """
        variables = {"userId": self.user_id, **values_to_update}
        return self._make_authenticated_request(media_list_mutation, variables)

    def get_anime_list(
        self,
        status: "AnilistMediaListStatus",
        type="ANIME",
    ) -> tuple[bool, "AnilistMediaLists"] | tuple[bool, None]:
        """gets an anime list from your media list given the list status

        Args:
            status: the mediaListStatus of the anime list

        Returns:
            a media list
        """
        variables = {"status": status, "userId": self.user_id, "type": type}
        return self._make_authenticated_request(media_list_query, variables)

    def get_medialist_entry(
        self, mediaId: int
    ) -> tuple[bool, dict] | tuple[bool, None]:
        """Get the id entry of the items in an Anilist MediaList

        Args:
            mediaId: The mediaList item entry mediaId

        Returns:
            a boolean indicating whether the request succeeded and either a dict object containing the id of the media list entry
        """
        variables = {"mediaId": mediaId}
        return self._make_authenticated_request(get_medialist_item_query, variables)

    def delete_medialist_entry(self, mediaId: int):
        """Deletes a mediaList item given its mediaId

        Args:
            mediaId: the media id of the anime

        Returns:
            a tuple containing a boolean whether the operation was successful and either an anilist object or none depending on success
        """
        result = self.get_medialist_entry(mediaId)
        data = result[1]
        if not result[0] or not data:
            return result
        id = data["data"]["MediaList"]["id"]
        variables = {"id": id}
        return self._make_authenticated_request(delete_list_entry_query, variables)

    # TODO: unify the _make_authenticated_request with original since sessions are now in use
    def _make_authenticated_request(self, query: str, variables: dict = {}):
        """the abstraction over all authenticated requests

        Args:
            query: the anilist query to make
            variables: the anilist variables to use

        Returns:
            an anilist object containing the queried data or none and a boolean indicating whether the request was successful
        """
        try:
            response = self.session.post(
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

    def get_data(
        self, query: str, variables: dict = {}
    ) -> tuple[bool, "AnilistDataSchema"]:
        """the abstraction over all none authenticated requests and that returns data of a similar type

        Args:
            query: the anilist query
            variables: the anilist api variables

        Returns:
            a boolean indicating success and none or an anilist object depending on success
        """
        try:
            response = self.session.post(
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
        startDate_greater: int | None = None,
        startDate_lesser: int | None = None,
        startDate: str | None = None,
        seasonYear: str | None = None,
        page: int | None = None,
        season: str | None = None,
        format_in: list[str] | None = None,
        on_list: bool | None = None,
        type="ANIME",
        **kwargs,
    ):
        """
        A powerful method abstracting all of anilist media queries
        """
        variables = {}
        for key, val in list(locals().items())[1:]:
            if (val or val is False) and key not in ["variables"]:
                variables[key] = val
        search_results = self.get_data(search_query, variables=variables)
        return search_results

    def get_anime(self, id: int):
        """
        Gets a single anime by a valid anilist anime id
        """
        variables = {"id": id}
        return self.get_data(anime_query, variables)

    def get_trending(self, type="ANIME", *_, **kwargs):
        """
        Gets the currently trending anime
        """
        variables = {"type": type}
        trending = self.get_data(trending_query, variables)
        return trending

    def get_most_favourite(self, type="ANIME", *_, **kwargs):
        """
        Gets the most favoured anime on anilist
        """
        variables = {"type": type}
        most_favourite = self.get_data(most_favourite_query, variables)
        return most_favourite

    def get_most_scored(self, type="ANIME", *_, **kwargs):
        """
        Gets most scored anime on anilist
        """
        variables = {"type": type}
        most_scored = self.get_data(most_scored_query, variables)
        return most_scored

    def get_most_recently_updated(self, type="ANIME", *_, **kwargs):
        """
        Gets most recently updated anime from anilist
        """
        variables = {"type": type}
        most_recently_updated = self.get_data(most_recently_updated_query, variables)
        return most_recently_updated

    def get_most_popular(
        self,
        type="ANIME",
    ):
        """
        Gets most popular anime on anilist
        """
        variables = {"type": type}
        most_popular = self.get_data(most_popular_query, variables)
        return most_popular

    def get_upcoming_anime(self, type="ANIME", page: int = 1, *_, **kwargs):
        """
        Gets upcoming anime from anilist
        """
        variables = {"page": page, "type": type}
        upcoming_anime = self.get_data(upcoming_anime_query, variables)
        return upcoming_anime

    # NOTE: THe following methods will probably be scraped soon
    def get_recommended_anime_for(self, id: int, type="ANIME", *_, **kwargs):
        variables = {"type": type}
        recommended_anime = self.get_data(recommended_query, variables)
        return recommended_anime

    def get_charcters_of(self, id: int, type="ANIME", *_, **kwargs):
        variables = {"id": id}
        characters = self.get_data(anime_characters_query, variables)
        return characters

    def get_related_anime_for(self, id: int, type="ANIME", *_, **kwargs):
        variables = {"id": id}
        related_anime = self.get_data(anime_relations_query, variables)
        return related_anime

    def get_airing_schedule_for(self, id: int, type="ANIME", *_, **kwargs):
        variables = {"id": id}
        airing_schedule = self.get_data(airing_schedule_query, variables)
        return airing_schedule
