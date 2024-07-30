import requests

from .constants import ANIMEPAHE_BASE, ANIMEPAHE_ENDPOINT, REQUEST_HEADERS


class AnimePaheApi:
    def search_for_anime(self, user_query, *args):
        try:
            url = f"{ANIMEPAHE_ENDPOINT}m=search&q={user_query}"
            headers = {**REQUEST_HEADERS}
            response = requests.get(url, headers=headers)
            if not response.status_code == 200:
                return
            data = response.json()
            return {
                "pageInfo": {"total": data["total"]},
                "results": [
                    {
                        "id": result["session"],
                        "title": result["title"],
                        "availableEpisodes": result["episodes"],
                        "type": result["type"],
                    }
                    for result in data["data"]
                ],
            }

        except Exception as e:
            print(e)
            input()

    def get_anime(self, session_id: str, *args):
        url = "https://animepahe.ru/api?m=release&id=&sort=episode_asc&page=1"
        url = f"{ANIMEPAHE_ENDPOINT}m=release&id={session_id}&sort=episode_asc&page=1"
        response = requests.get(url, headers=REQUEST_HEADERS)
        if not response.status_code == 200:
            return
        data = response.json()
        self.current = data
        episodes = list(map(str, range(data["total"])))
        return {
            "id": session_id,
            "title": "none",
            "availableEpisodesDetail": {
                "sub": episodes,
                "dub": episodes,
                "raw": episodes,
            },
        }

    def get_episode_streams(self, anime, episode, *args):
        episode_id = self.current["data"][int(episode)]["session"]
        anime_id = anime["id"]
        url = f"{ANIMEPAHE_BASE}play/{anime_id}{episode_id}"
        response = requests.get(url, headers=REQUEST_HEADERS)
        print(response.status_code)
        input()
        if not response.status_code == 200:
            print(response.text)
            return
        print(response.text)
        input()
