from ...libs.anilist.anilist import AniList
from ...Utility.show_notification import show_notification
from ..Utility.media_card_loader import media_card_loader
from .base_model import BaseScreenModel


class SearchScreenModel(BaseScreenModel):
    data = {}

    def get_trending_anime(self):
        success, data = AniList.get_trending()
        if success:

            def _data_generator():
                for anime_item in data["data"]["Page"]["media"]:
                    yield media_card_loader.media_card(anime_item)

            return _data_generator()
        else:
            return data

    def search_for_anime(self, anime_title, **kwargs):
        success, self.data = AniList.search(query=anime_title, **kwargs)
        if success:
            return self.media_card_generator()
        else:
            show_notification(
                f"Failed to search for {anime_title}", self.data.get("Error")
            )

    def media_card_generator(self):
        for anime_item in self.data["data"]["Page"]["media"]:
            yield media_card_loader.media_card(anime_item)
        self.pagination_info = self.data["data"]["Page"]["pageInfo"]


__all__ = ["SearchScreenModel"]
