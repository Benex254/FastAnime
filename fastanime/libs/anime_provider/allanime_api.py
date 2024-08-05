import json
import re

import requests

# TODO: move constants to own file
ALLANIME_BASE = "allanime.day"
ALLANIME_REFERER = "https://allanime.to/"
ALLANIME_API_ENDPOINT = "https://api.{}/api/".format(ALLANIME_BASE)


# TODO: move th gql queries to own files
ALLANIME_SEARCH_GQL = """
query(
        $search: SearchInput
        $limit: Int
        $page: Int
        $translationType: VaildTranslationTypeEnumType
        $countryOrigin: VaildCountryOriginEnumType
    ) {
    shows(
        search: $search
        limit: $limit
        page: $page
        translationType: $translationType
        countryOrigin: $countryOrigin
    ) {
        pageInfo {
            total
        }
        edges {    
        _id
        name
        availableEpisodes
        __typename
        }
    }
}
"""


ALLANIME_EPISODES_GQL = """\
query ($showId: String!, $translationType: VaildTranslationTypeEnumType!, $episodeString: String!) {
    episode(
        showId: $showId
        translationType: $translationType
        episodeString: $episodeString
    ) {
        
        episodeString
        sourceUrls
        notes
    }
}"""

ALLANIME_SHOW_GQL = """
query ($showId: String!) {
    show(
        _id: $showId
    ) {

        _id
        name
        availableEpisodesDetail
        
    }
}
"""


# TODO: creat a utility module for this
# Dictionary to map hex values to characters
hex_to_char = {
    "01": "9",
    "08": "0",
    "05": "=",
    "0a": "2",
    "0b": "3",
    "0c": "4",
    "07": "?",
    "00": "8",
    "5c": "d",
    "0f": "7",
    "5e": "f",
    "17": "/",
    "54": "l",
    "09": "1",
    "48": "p",
    "4f": "w",
    "0e": "6",
    "5b": "c",
    "5d": "e",
    "0d": "5",
    "53": "k",
    "1e": "&",
    "5a": "b",
    "59": "a",
    "4a": "r",
    "4c": "t",
    "4e": "v",
    "57": "o",
    "51": "i",
}


def decode_hex_string(hex_string):
    # Split the hex string into pairs of characters
    hex_pairs = re.findall("..", hex_string)

    # Decode each hex pair
    decoded_chars = [hex_to_char.get(pair.lower(), pair) for pair in hex_pairs]

    return "".join(decoded_chars)


# TODO: create tests for the api
#
class AllAnimeAPI:
    """
    Provides a fast and effective interface to AllAnime site.
    """

    api_endpoint = ALLANIME_API_ENDPOINT

    def _fetch_gql(self, query: str, variables: dict):
        response = requests.get(
            self.api_endpoint,
            params={
                "variables": json.dumps(variables),
                "query": query,
            },
            headers={
                "Referer": ALLANIME_REFERER,
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
            },
        )
        if response.status_code != 200:
            print(response.content)
            return {}
        return response.json().get("data", {})

    def search_for_anime(self, user_query: str, translation_type: str = "sub"):
        search = {"allowAdult": False, "allowUnknown": False, "query": user_query}
        limit = 40
        translationtype = translation_type
        countryorigin = "all"
        page = 1
        variables = {
            "search": search,
            "limit": limit,
            "page": page,
            "translationtype": translationtype,
            "countryorigin": countryorigin,
        }
        return self._fetch_gql(ALLANIME_SEARCH_GQL, variables)

    def get_anime(self, allanime_show_id: str):
        variables = {"showId": allanime_show_id}
        return anime_provider._fetch_gql(ALLANIME_SHOW_GQL, variables)

    def get_anime_episode(
        self, allanime_show_id: str, episode_string: str, translation_type: str = "sub"
    ):
        variables = {
            "showId": allanime_show_id,
            "translationType": translation_type,
            "episodeString": episode_string,
        }
        return anime_provider._fetch_gql(ALLANIME_EPISODES_GQL, variables)

    def get_episode_streams(self, allanime_episode_embeds_data):
        embeds = allanime_episode_embeds_data["episode"]["sourceUrls"]
        for embed in embeds:
            # filter the working streams
            if embed.get("sourceName", "") not in ("Sak", "Kir", "S-mp4", "Luf-mp4"):
                continue
            url = embed.get("sourceUrl")

            if not url:
                continue
            if url.startswith("--"):
                url = url[2:]

            # get the stream url for an episode of the defined source names
            parsed_url = decode_hex_string(url)
            embed_url = (
                f"https://{ALLANIME_BASE}{parsed_url.replace('clock','clock.json')}"
            )
            resp = requests.get(
                embed_url,
                headers={
                    "Referer": ALLANIME_REFERER,
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
                },
            )
            if resp.status_code == 200:
                match embed["sourceName"]:
                    case "Luf-mp4":
                        yield "gogoanime", resp.json()
                    case "Kir":
                        yield "wetransfer", resp.json()
                    case "S-mp4":
                        yield "sharepoint", resp.json()
                    case "Sak":
                        yield "dropbox", resp.json()
                    case _:
                        yield "Unknown", resp.json()
            else:
                return None


anime_provider = AllAnimeAPI()


if __name__ == "__main__":
    # lets see if it works :)
    import subprocess
    import sys

    def run_fzf(options):
        """
        Run fzf with a list of options and return the selected option.
        """
        # Join the list of options into a single string with newlines
        options_str = "\n".join(options)

        # Run fzf as a subprocess
        result = subprocess.run(
            ["fzf"],
            input=options_str,
            text=True,
            stdout=subprocess.PIPE,
        )

        # Check if fzf was successful
        if result.returncode == 0:
            # Return the selected option
            return result.stdout.strip()
        else:
            # Handle the case where fzf fails or is canceled
            print("fzf was canceled or failed")
            return None

    anime = input("Enter the anime name: ")
    translation = input("Enter the translation type: ")

    search_results = anime_provider.search_for_anime(
        anime, translation_type=translation.strip()
    )
    print(search_results)
    if not search_results:
        raise Exception("No results found")

    search_results = search_results["shows"]["edges"]
    options = [show["name"] for show in search_results]
    anime = run_fzf(options)
    if anime is None:
        print("No anime was selected")
        sys.exit(1)

    anime_result = list(filter(lambda x: x["name"] == anime, search_results))[0]
    anime_data = anime_provider.get_anime(anime_result["_id"])
    print(anime_data)
    if anime_data is None:
        raise Exception("Anime not found")
    availableEpisodesDetail = anime_data["show"]["availableEpisodesDetail"]
    if not availableEpisodesDetail.get(translation.strip()):
        raise Exception("No episodes found")

    print("select episode")
    stream_link = True
    while stream_link != "quit":
        episode = run_fzf(availableEpisodesDetail[translation.strip()])
        if episode is None:
            print("No episode was selected")
            sys.exit(1)

        episode_data = anime_provider.get_anime_episode(anime_result["_id"], episode)
        if episode_data is None:
            raise Exception("Episode not found")

        episode_streams = anime_provider.get_episode_streams(episode_data)

        if not episode_streams:
            raise Exception("No streams found")
        episode_streams = list(episode_streams)
        print(episode_streams)

        stream_links = [stream["link"] for stream in episode_streams[2][1]["links"]]
        stream_link = run_fzf([*stream_links, "quit"])
        print(stream_link)
        if stream_link == "quit":
            print("Have a nice day")
            sys.exit()
        if not stream_link:
            raise Exception("No stream was selected")

        subprocess.run(["mpv", stream_link])
