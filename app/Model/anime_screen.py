import json
import os
from Model.base_model import BaseScreenModel
from libs.anilist import AniList
from Utility.media_card_loader import MediaCardLoader
from kivy.storage.jsonstore import JsonStore

user_data= JsonStore("user_data.json")
class AnimeScreenModel(BaseScreenModel):
    data = {}
    anime_id = 0
    
    def media_card_generator(self):
        for anime_item in self.data["data"]["Page"]["media"]:
            yield MediaCardLoader.media_card(anime_item)

    def get_anime_data(self,id:int):
        return AniList.get_anime(id)
    
    