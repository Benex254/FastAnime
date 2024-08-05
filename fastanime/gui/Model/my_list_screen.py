from ...libs.anilist.anilist import AniList
from ...Utility.show_notification import show_notification
from ..Utility.media_card_loader import media_card_loader
from .base_model import BaseScreenModel


class MyListScreenModel(BaseScreenModel):
    already_in_user_anime_list = []

    def update_my_anime_list_view(self, not_yet_in_user_anime_list: list):
        success, self.data = AniList.search(
            id_in=not_yet_in_user_anime_list, sort="SCORE_DESC"
        )
        if success:
            return self.media_card_generator()
        else:
            show_notification(
                "Failed to update my list screen view", self.data["Error"]
            )
            return None

    def media_card_generator(self):
        for anime_item in self.data["data"]["Page"]["media"]:
            yield media_card_loader.media_card(anime_item)
