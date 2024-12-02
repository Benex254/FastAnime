import json
import logging
from typing import TYPE_CHECKING
from ...anime_provider.base_provider import AnimeProvider
from ..decorators import debug_provider
from ..utils import give_random_quality, one_digit_symmetric_xor
from .constants import API_ENDPOINT, API_BASE_URL, API_REFERER
from .gql_queries import EPISODES_GQL, SEARCH_GQL, SHOW_GQL

if TYPE_CHECKING:
    from .types import AllAnimeEpisode
logger = logging.getLogger(__name__)


class AllAnime(AnimeProvider):
    """
    AllAnime is a provider class for fetching anime data from the AllAnime API.
    Attributes:
        HEADERS (dict): Default headers for API requests.
    Methods:
        _execute_graphql_query(query: str, variables: dict) -> dict:
            Executes a GraphQL query and returns the response data.
        search_for_anime(
            **kwargs
        ) -> dict:
            Searches for anime based on the provided keywords and other parameters.
        get_anime(show_id: str) -> dict:
            Retrieves detailed information about a specific anime by its ID.
        _get_anime_episode(
            show_id: str, episode, translation_type: str = "sub"
            Retrieves information about a specific episode of an anime.
        get_episode_streams(
        ) -> generator:
            Retrieves streaming links for a specific episode of an anime.
    """

    HEADERS = {
        "Referer": API_REFERER,
    }

    def _execute_graphql_query(self, query: str, variables: dict):
        """
        Executes a GraphQL query using the provided query string and variables.

        Args:
            query (str): The GraphQL query string to be executed.
            variables (dict): A dictionary of variables to be used in the query.

        Returns:
            dict: The JSON response data from the GraphQL API.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request returned an unsuccessful status code.
        """

        response = self.session.get(
            API_ENDPOINT,
            params={
                "variables": json.dumps(variables),
                "query": query,
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()["data"]

    @debug_provider
    def search_for_anime(
        self,
        search_keywords: str,
        translation_type: str = "sub",
        *,
        limit=40,
        page=1,
        country_of_origin="all",
        nsfw=True,
        unknown=True,
        **kwargs,
    ):
        """
        Search for anime based on given keywords and filters.
        Args:
            search_keywords (str): The keywords to search for.
            translation_type (str, optional): The type of translation to search for (e.g., "sub" or "dub"). Defaults to "sub".
            limit (int, optional): The maximum number of results to return. Defaults to 40.
            page (int, optional): The page number to return. Defaults to 1.
            country_of_origin (str, optional): The country of origin filter. Defaults to "all".
            nsfw (bool, optional): Whether to include adult content in the search results. Defaults to True.
            unknown (bool, optional): Whether to include unknown content in the search results. Defaults to True.
            **kwargs: Additional keyword arguments.
        Returns:
            dict: A dictionary containing the page information and a list of search results. Each result includes:
                - id (str): The ID of the anime.
                - title (str): The title of the anime.
                - type (str): The type of the anime.
                - availableEpisodes (int): The number of available episodes.
        """
        search_results = self._execute_graphql_query(
            SEARCH_GQL,
            variables={
                "search": {
                    "allowAdult": nsfw,
                    "allowUnknown": unknown,
                    "query": search_keywords,
                },
                "limit": limit,
                "page": page,
                "translationtype": translation_type,
                "countryorigin": country_of_origin,
            },
        )
        return {
            "pageInfo": search_results["shows"]["pageInfo"],
            "results": [
                {
                    "id": result["_id"],
                    "title": result["name"],
                    "type": result["__typename"],
                    "availableEpisodes": result["availableEpisodes"],
                }
                for result in search_results["shows"]["edges"]
            ],
        }

    @debug_provider
    def get_anime(self, id: str):
        """
        Fetches anime details using the provided show ID.
        Args:
            id (str): The ID of the anime show to fetch details for.
        Returns:
            dict: A dictionary containing the anime details, including:
                - id (str): The unique identifier of the anime show.
                - title (str): The title of the anime show.
                - availableEpisodesDetail (list): A list of available episodes details.
                - type (str, optional): The type of the anime show.
        """

        anime = self._execute_graphql_query(SHOW_GQL, variables={"showId": id})
        self.store.set(id, "anime_info", {"title": anime["show"]["name"]})
        return {
            "id": anime["show"]["_id"],
            "title": anime["show"]["name"],
            "availableEpisodesDetail": anime["show"]["availableEpisodesDetail"],
            "type": anime.get("__typename"),
        }

    @debug_provider
    def _get_anime_episode(
        self, anime_id: str, episode, translation_type: str = "sub"
    ) -> "AllAnimeEpisode":
        """
        Fetches a specific episode of an anime by its ID and episode number.
        Args:
            anime_id (str): The unique identifier of the anime.
            episode (str): The episode number or string identifier.
            translation_type (str, optional): The type of translation for the episode. Defaults to "sub".
        Returns:
            AllAnimeEpisode: The episode details retrieved from the GraphQL query.
        """
        return self._execute_graphql_query(
            EPISODES_GQL,
            variables={
                "showId": anime_id,
                "translationType": translation_type,
                "episodeString": episode,
            },
        )["episode"]

    @debug_provider
    def get_episode_streams(
        self, anime_id, episode_number: str, translation_type="sub"
    ):
        """
        Retrieve streaming information for a specific episode of an anime.
        Args:
            anime_id (str): The unique identifier for the anime.
            episode_number (str): The episode number to retrieve streams for.
            translation_type (str, optional): The type of translation for the episode (e.g., "sub" for subtitles). Defaults to "sub".
        Yields:
            dict: A dictionary containing streaming information for the episode, including:
                - server (str): The name of the streaming server.
                - episode_title (str): The title of the episode.
                - headers (dict): HTTP headers required for accessing the stream.
                - subtitles (list): A list of subtitles available for the episode.
                - links (list): A list of dictionaries containing streaming links and their quality.
        """
        anime_title = (self.store.get(anime_id, "anime_info", "") or {"title": ""})[
            "title"
        ]
        allanime_episode = self._get_anime_episode(
            anime_id, episode_number, translation_type
        )

        @debug_provider
        def _get_server(embed):
            """
            Retrieves the streaming server information based on the provided embed data.

            Args:
                embed (dict): A dictionary containing the embed data with keys such as "sourceUrl" and "sourceName".

            Returns:
                dict or None: A dictionary containing server information, headers, subtitles, episode title, and links if a valid URL is found and processed.
                              Returns None if the URL is not valid or not found.

            The function performs the following steps:
            1. Extracts the URL from the embed data.
            2. Decodes the URL if it starts with "--".
            3. Checks if the URL contains specific server identifiers and returns the corresponding server information.
            4. Fetches the stream URL for an episode from the defined source names and returns the server information based on the source name.
            """

            url = embed.get("sourceUrl")
            #
            if not url:
                return
            if url.startswith("--"):
                url = one_digit_symmetric_xor(56, url[2:])

            if "tools.fast4speed.rsvp" in url:
                logger.debug("Found streams from Yt")
                return {
                    "server": "Yt",
                    "episode_title": f"{anime_title}; Episode {episode_number}",
                    "headers": {"Referer": f"https://{API_BASE_URL}/"},
                    "subtitles": [],
                    "links": [
                        {
                            "link": url,
                            "quality": "1080",
                        }
                    ],
                }

            # get the stream url for an episode of the defined source names
            response = self.session.get(
                f"https://{API_BASE_URL}{url.replace('clock', 'clock.json')}",
                timeout=10,
            )

            response.raise_for_status()
            match embed["sourceName"]:
                case "Luf-mp4":
                    logger.debug("Found streams from gogoanime")
                    return {
                        "server": "gogoanime",
                        "headers": {"Referer": f"https://{API_BASE_URL}/"},
                        "subtitles": [],
                        "episode_title": (allanime_episode["notes"] or f"{anime_title}")
                        + f"; Episode {episode_number}",
                        "links": give_random_quality(response.json()["links"]),
                    }
                case "Kir":
                    logger.debug("Found streams from wetransfer")
                    return {
                        "server": "weTransfer",
                        "headers": {"Referer": f"https://{API_BASE_URL}/"},
                        "subtitles": [],
                        "episode_title": (allanime_episode["notes"] or f"{anime_title}")
                        + f"; Episode {episode_number}",
                        "links": give_random_quality(response.json()["links"]),
                    }
                case "S-mp4":
                    logger.debug("Found streams from sharepoint")
                    return {
                        "server": "sharepoint",
                        "headers": {"Referer": f"https://{API_BASE_URL}/"},
                        "subtitles": [],
                        "episode_title": (allanime_episode["notes"] or f"{anime_title}")
                        + f"; Episode {episode_number}",
                        "links": give_random_quality(response.json()["links"]),
                    }
                case "Sak":
                    logger.debug("Found streams from dropbox")
                    return {
                        "server": "dropbox",
                        "headers": {"Referer": f"https://{API_BASE_URL}/"},
                        "subtitles": [],
                        "episode_title": (allanime_episode["notes"] or f"{anime_title}")
                        + f"; Episode {episode_number}",
                        "links": give_random_quality(response.json()["links"]),
                    }
                case "Default":
                    logger.debug("Found streams from wixmp")
                    return {
                        "server": "wixmp",
                        "headers": {"Referer": f"https://{API_BASE_URL}/"},
                        "subtitles": [],
                        "episode_title": (allanime_episode["notes"] or f"{anime_title}")
                        + f"; Episode {episode_number}",
                        "links": give_random_quality(response.json()["links"]),
                    }

        for embed in allanime_episode["sourceUrls"]:
            # filter the working streams no need to get all since the others are mostly hsl
            # TODO: should i just get all the servers and handle the hsl??
            if embed.get("sourceName", "") not in (
                # priorities based on death note
                "Sak",  #  7
                "S-mp4",  # 7.9
                "Luf-mp4",  # 7.7
                "Default",  # 8.5
                "Yt-mp4",  # 7.9
                "Kir",  # NA
                # "Vid-mp4"  # 4
                # "Ok",  # 3.5
                # "Ss-Hls",  #  5.5
                # "Mp4",  # 4
            ):
                continue
            if server := _get_server(embed):
                yield server

if __name__=="__main__":
    import subprocess

    allanime=AllAnime(cache_requests="True",use_persistent_provider_store="False")
    search_term = input("Enter the search term for the anime: ")
    translation_type = input("Enter the translation type (sub/dub): ")

    search_results = allanime.search_for_anime(search_keywords=search_term, translation_type=translation_type)

    if not search_results["results"]:
        print("No results found.")
        exit()

    print("Search Results:")
    for idx, result in enumerate(search_results["results"], start=1):
        print(f"{idx}. {result['title']} (ID: {result['id']})")

    anime_choice = int(input("Enter the number of the anime you want to watch: ")) - 1
    anime_id = search_results["results"][anime_choice]["id"]

    anime_details = allanime.get_anime(anime_id)
    print(f"Selected Anime: {anime_details['title']}")

    print("Available Episodes:")
    for idx, episode in enumerate(sorted(anime_details["availableEpisodesDetail"][translation_type],key=float), start=1):
        print(f"{idx}. Episode {episode}")

    episode_choice = int(input("Enter the number of the episode you want to watch: ")) - 1
    episode_number = anime_details["availableEpisodesDetail"][translation_type][episode_choice]

    streams = list(allanime.get_episode_streams(anime_id, episode_number, translation_type))
    if not streams:
        print("No streams available.")
        exit()

    print("Available Streams:")
    for idx, stream in enumerate(streams, start=1):
        print(f"{idx}. Server: {stream['server']}")

    server_choice = int(input("Enter the number of the server you want to use: ")) - 1
    selected_stream = streams[server_choice]

    stream_link = selected_stream["links"][0]["link"]
    print(f"Streaming from {selected_stream['server']}...")

    subprocess.run(["mpv", stream_link])