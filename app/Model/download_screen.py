from Model.base_model import BaseScreenModel


class DownloadsScreenModel(BaseScreenModel):
    """
    Handles the download screen logic
    """
    
    # already_in_user_anime_list = []
    # def update_my_anime_list_view(self,not_yet_in_user_anime_list:list,**kwargs):
    #     success,self.data = AniList.search(id_in=not_yet_in_user_anime_list)
    #     if success:    
    #         return self.media_card_generator()
    #     else:
    #         show_notification(f"Failed to update my list screen view",self.data["Error"])
    #         return None
        
    # def media_card_generator(self):
    #     for anime_item in self.data["data"]["Page"]["media"]:
    #         yield MediaCardLoader.media_card(anime_item)
