from .base_model import BaseScreenModel
from anixstream.libs.anilist import AniList

class AnimeScreenModel(BaseScreenModel):
    """the Anime screen model
    """
    data = {}
    anime_id = 0
    
    def get_anime_data(self,id:int):
        return AniList.get_anime(id)
    
    
