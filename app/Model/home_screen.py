from Model.base_model import BaseScreenModel
from libs.anilist import AniList
from Utility.media_card_loader import MediaCardLoader
from kivy.storage.jsonstore import JsonStore

user_data= JsonStore("user_data.json")


class HomeScreenModel(BaseScreenModel):
    def get_trending_anime(self):
        success,data = AniList.get_trending()
        if success:
            def _data_generator():
                for anime_item in data["data"]["Page"]["media"]:
                    yield MediaCardLoader.media_card(anime_item)
            return _data_generator()
        else:
            return data

    def get_most_favourite_anime(self):
        success,data = AniList.get_most_favourite()
        if success:
            def _data_generator():
                for anime_item in data["data"]["Page"]["media"]:
                    yield MediaCardLoader.media_card(anime_item)
            return _data_generator()
        else:
            return data

    def get_most_recently_updated_anime(self):
        success,data = AniList.get_most_recently_updated()
        if success:
            def _data_generator():
                for anime_item in data["data"]["Page"]["media"]:
                    yield MediaCardLoader.media_card(anime_item)
            return _data_generator()
        else:
            return data
    def get_most_popular_anime(self):
        success,data = AniList.get_most_popular()
        if success:
            def _data_generator():
                for anime_item in data["data"]["Page"]["media"]:
                    yield MediaCardLoader.media_card(anime_item)
            return _data_generator()
        else:
            return data
    def get_most_scored_anime(self):
        success,data = AniList.get_most_scored()
        if success:
            def _data_generator():
                for anime_item in data["data"]["Page"]["media"]:
                    yield MediaCardLoader.media_card(anime_item)
            return _data_generator()
        else:
            return data
    def get_upcoming_anime(self):
        success,data = AniList.get_upcoming_anime(1)
        if success:
            def _data_generator():
                for anime_item in data["data"]["Page"]["media"]:
                    yield MediaCardLoader.media_card(anime_item)
            return _data_generator()
        else:
            return data
    def update_user_anime_list(self,anime_id,is_add):
        my_list:list = user_data.get("my_list")["list"]
        if is_add:
            my_list.append(anime_id)
        elif not(is_add) and my_list:
            my_list.remove(anime_id)
        user_data.put("my_list",list=my_list)
            