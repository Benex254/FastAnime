import json
import logging
from typing import TYPE_CHECKING

from ...anime_provider.base_provider import AnimeProvider
from ..decorators import debug_provider
from ..utils import give_random_quality, one_digit_symmetric_xor
from .constants import (
    API_BASE_URL,
    API_ENDPOINT,
    API_REFERER,
    DEFAULT_COUNTRY_OF_ORIGIN,
    DEFAULT_NSFW,
    DEFAULT_PAGE,
    DEFAULT_PER_PAGE,
    DEFAULT_UNKNOWN,
    MP4_SERVER_JUICY_STREAM_REGEX,
)
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
        translation_type: str,
        *,
        nsfw=DEFAULT_NSFW,
        unknown=DEFAULT_UNKNOWN,
        limit=DEFAULT_PER_PAGE,
        page=DEFAULT_PAGE,
        country_of_origin=DEFAULT_COUNTRY_OF_ORIGIN,
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
    def get_anime(self, id: str, **kwargs):
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
    def _get_server(
        self,
        embed,
        anime_title: str,
        allanime_episode: "AllAnimeEpisode",
        episode_number,
    ):
        """
        Retrieves the streaming server information for a given anime episode based on the provided embed data.
        Args:
            embed (dict): A dictionary containing the embed data, including the source URL and source name.
            anime_title (str): The title of the anime.
            allanime_episode (AllAnimeEpisode): An object representing the episode details.
        Returns:
            dict: A dictionary containing server information, headers, subtitles, episode title, and links to the stream.
                    Returns None if no valid URL or stream is found.
        Raises:
            requests.exceptions.RequestException: If there is an issue with the HTTP request.
        """

        url = embed.get("sourceUrl")
        #
        if not url:
            return
        if url.startswith("--"):
            url = one_digit_symmetric_xor(56, url[2:])

        # FIRST CASE
        match embed["sourceName"]:
            case "Yt-mp4":
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
            case "Mp4":
                logger.debug("Found streams from Mp4")
                response = self.session.get(
                    url,
                    fresh=1,  # pyright: ignore
                    timeout=10,
                )
                response.raise_for_status()
                embed_html = response.text.replace(" ", "").replace("\n", "")
                vid = MP4_SERVER_JUICY_STREAM_REGEX.search(embed_html)
                if not vid:
                    return
                return {
                    "server": "mp4-upload",
                    "headers": {"Referer": "https://www.mp4upload.com/"},
                    "subtitles": [],
                    "episode_title": (allanime_episode["notes"] or f"{anime_title}")
                    + f"; Episode {episode_number}",
                    "links": [{"link": vid.group(1), "quality": "1080"}],
                }
            case "Fm-Hls":
                # TODO: requires decoding obsfucated js (filemoon)
                logger.debug("Found streams from Fm-Hls")
                response = self.session.get(
                    url,
                    timeout=10,
                )
                response.raise_for_status()
                embed_html = response.text.replace(" ", "").replace("\n", "")
                vid = MP4_SERVER_JUICY_STREAM_REGEX.search(embed_html)
                if not vid:
                    return
                return {
                    "server": "filemoon",
                    "headers": {"Referer": "https://www.mp4upload.com/"},
                    "subtitles": [],
                    "episode_title": (allanime_episode["notes"] or f"{anime_title}")
                    + f"; Episode {episode_number}",
                    "links": [{"link": vid.group(1), "quality": "1080"}],
                }
            case "Ok":
                # TODO: requires decoding the obsfucated js (filemoon)
                response = self.session.get(
                    url,
                    timeout=10,
                )
                response.raise_for_status()
                embed_html = response.text.replace(" ", "").replace("\n", "")
                vid = MP4_SERVER_JUICY_STREAM_REGEX.search(embed_html)
                logger.debug("Found streams from Ok")
                return {
                    "server": "filemoon",
                    "headers": {"Referer": f"https://{API_BASE_URL}/"},
                    "subtitles": [],
                    "episode_title": (allanime_episode["notes"] or f"{anime_title}")
                    + f"; Episode {episode_number}",
                    "links": give_random_quality(response.json()["links"]),
                }
            case "Vid-mp4":
                # TODO: requires some serious work i think : )
                response = self.session.get(
                    url,
                    timeout=10,
                )
                response.raise_for_status()
                embed_html = response.text.replace(" ", "").replace("\n", "")
                logger.debug("Found streams from vid-mp4")
                return {
                    "server": "Vid-mp4",
                    "headers": {"Referer": f"https://{API_BASE_URL}/"},
                    "subtitles": [],
                    "episode_title": (allanime_episode["notes"] or f"{anime_title}")
                    + f"; Episode {episode_number}",
                    "links": give_random_quality(response.json()["links"]),
                }
            case "Ss-Hls":
                # TODO: requires some serious work i think : )
                response = self.session.get(
                    url,
                    timeout=10,
                )
                response.raise_for_status()
                embed_html = response.text.replace(" ", "").replace("\n", "")
                logger.debug("Found streams from Ss-Hls")
                return {
                    "server": "StreamSb",
                    "headers": {"Referer": f"https://{API_BASE_URL}/"},
                    "subtitles": [],
                    "episode_title": (allanime_episode["notes"] or f"{anime_title}")
                    + f"; Episode {episode_number}",
                    "links": give_random_quality(response.json()["links"]),
                }

        # get the stream url for an episode of the defined source names
        response = self.session.get(
            f"https://{API_BASE_URL}{url.replace('clock', 'clock.json')}",
            timeout=10,
        )

        response.raise_for_status()

        # SECOND CASE
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

            case "Ak":
                # TODO: works but needs further probing
                logger.debug("Found streams from Ak")
                return {
                    "server": "Ak",
                    "headers": {"Referer": f"https://{API_BASE_URL}/"},
                    "subtitles": [],
                    "episode_title": (allanime_episode["notes"] or f"{anime_title}")
                    + f"; Episode {episode_number}",
                    "links": give_random_quality(response.json()["links"]),
                }

    @debug_provider
    def get_episode_streams(
        self, anime_id, episode_number: str, translation_type="sub", **kwargs
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

        for embed in allanime_episode["sourceUrls"]:
            if embed.get("sourceName", "") not in (
                # priorities based on death note
                "Sak",  #  7
                "S-mp4",  # 7.9
                "Luf-mp4",  # 7.7
                "Default",  # 8.5
                "Yt-mp4",  # 7.9
                "Kir",  # NA
                "Mp4",  # 4
                # "Ak",#
                # "Vid-mp4",  # 4
                # "Ok",  # 3.5
                # "Ss-Hls",  #  5.5
                # "Fm-Hls",#
            ):
                logger.debug(f"Found  {embed['sourceName']} but ignoring")
                continue
            if server := self._get_server(
                embed, anime_title, allanime_episode, episode_number
            ):
                yield server


if __name__ == "__main__":
    import subprocess

    allanime = AllAnime(cache_requests="True", use_persistent_provider_store="False")
    search_term = input("Enter the search term for the anime: ")
    translation_type = input("Enter the translation type (sub/dub): ")

    search_results = allanime.search_for_anime(
        search_keywords=search_term, translation_type=translation_type
    )

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
    for idx, episode in enumerate(
        sorted(anime_details["availableEpisodesDetail"][translation_type], key=float),
        start=1,
    ):
        print(f"{idx}. Episode {episode}")

    episode_choice = (
        int(input("Enter the number of the episode you want to watch: ")) - 1
    )
    episode_number = anime_details["availableEpisodesDetail"][translation_type][
        episode_choice
    ]

    streams = list(
        allanime.get_episode_streams(anime_id, episode_number, translation_type)
    )
    if not streams:
        print("No streams available.")
        exit()

    print("Available Streams:")
    for idx, stream in enumerate(streams, start=1):
        print(f"{idx}. Server: {stream['server']}")

    server_choice = int(input("Enter the number of the server you want to use: ")) - 1
    selected_stream = streams[server_choice]

    stream_link = selected_stream["links"][0]["link"]
    mpv_args = ["mpv", stream_link]
    headers = selected_stream["headers"]
    if headers:
        mpv_headers = "--http-header-fields="
        for header_name, header_value in headers.items():
            mpv_headers += f"{header_name}:{header_value},"
        mpv_args.append(mpv_headers)
    subprocess.run(mpv_args)
