from .base_model import BaseScreenModel
from anixstream.libs.anilist import AniList
from anixstream.Utility.media_card_loader import MediaCardLoader


class HomeScreenModel(BaseScreenModel):
    """The home screen model"""

    def get_trending_anime(self):
        success, data = AniList.get_trending()
        if success:

            def _data_generator():
                for anime_item in data["data"]["Page"]["media"]:
                    yield MediaCardLoader.media_card(anime_item)

            return _data_generator()
        else:
            return data

    def get_most_favourite_anime(self):
        success, data = AniList.get_most_favourite()
        if success:

            def _data_generator():
                for anime_item in data["data"]["Page"]["media"]:
                    yield MediaCardLoader.media_card(anime_item)

            return _data_generator()
        else:
            return data

    def get_most_recently_updated_anime(self):
        success, data = AniList.get_most_recently_updated()
        if success:

            def _data_generator():
                for anime_item in data["data"]["Page"]["media"]:
                    yield MediaCardLoader.media_card(anime_item)

            return _data_generator()
        else:
            return data

    def get_most_popular_anime(self):
        success, data = AniList.get_most_popular()
        if success:

            def _data_generator():
                for anime_item in data["data"]["Page"]["media"]:
                    yield MediaCardLoader.media_card(anime_item)

            return _data_generator()
        else:
            return data

    def get_most_scored_anime(self):
        success, data = AniList.get_most_scored()
        if success:

            def _data_generator():
                for anime_item in data["data"]["Page"]["media"]:
                    yield MediaCardLoader.media_card(anime_item)

            return _data_generator()
        else:
            return data

    def get_upcoming_anime(self):
        success, data = AniList.get_upcoming_anime(1)
        if success:

            def _data_generator():
                for anime_item in data["data"]["Page"]["media"]:
                    yield MediaCardLoader.media_card(anime_item)

            return _data_generator()
        else:
            return data
