import os
from Model.base_model import BaseScreenModel
from Utility import show_notification
from libs.anilist import AniList
from Utility.media_card_loader import MediaCardLoader
from kivy.storage.jsonstore import JsonStore

user_data= JsonStore("user_data.json")
class SearchScreenModel(BaseScreenModel):
    data = {}
    def search_for_anime(self,anime_title,**kwargs):
        success,self.data = AniList.search(query=anime_title,**kwargs)
        if success:    
            return self.media_card_generator()
        else:
            show_notification(f"Failed to search for {anime_title}",self.data["Error"])
        
    def media_card_generator(self):
        for anime_item in self.data["data"]["Page"]["media"]:
            yield MediaCardLoader.media_card(anime_item)
        self.pagination_info = self.extract_pagination_info()

    def extract_pagination_info(self):
        pagination_info = None
        return pagination_info
