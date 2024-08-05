from ...anilist.anilist_data_schema import AnilistBaseMediaDataSchema
from ..base_provider import AnimeProvider

"""
"Zoro": {
    "27": {
        "identifier": "27",
        "image": "https://cdn.noitatnemucod.net/thumbnail/300x400/100/ce5e539af63e42431621fc66a47fbec1.jpg",
        "malId": 1,
        "aniId": 1,
        "page": "Zoro",
        "title": "Cowboy Bebop",
        "type": "anime",
        "url": "https://hianime.to/cowboy-bebop-27"
    }
},

episode info =  https://hianime.to/ajax/v2/episode/list/27
"""


# TODO: complete this
class AniWatchApi(AnimeProvider):
    def search_for_anime(
        self, anilist_selected_anime: AnilistBaseMediaDataSchema, *args
    ):
        return {
            "pageInfo": 1,
            "results": [
                {
                    "id": anilist_selected_anime["id"],
                    "title": anilist_selected_anime["title"],
                    "availableEpisodes": [],
                }
            ],
        }

    def get_anime(self, id: int):
        url = f"https://raw.githubusercontent.com/bal-mackup/mal-backup/master/anilist/anime/{id}.json"
        response = self.session.get(url)
        if response.status_code == 200:
            data = response.json()
            data["Sites"]["Zoro"]
            return {"id": ""}
        else:
            return {}

    def get_episode_streams(self, id: int, episode: str, translation_type: str):
        pass
