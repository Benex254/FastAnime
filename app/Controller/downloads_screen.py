
from inspect import isgenerator
from View import DownloadsScreenView
from Model import DownloadsScreenModel
from View.components import MediaCardsContainer
from Utility import show_notification
from kivy.clock import Clock
class DownloadsScreenController:
    def __init__(self, model:DownloadsScreenModel):
        self.model = model
        self.view = DownloadsScreenView(controller=self, model=self.model)
        # self.update_anime_view()

    def get_view(self) -> DownloadsScreenView:
        return self.view

    # def requested_update_my_list_screen(self):
    #     user_anime_list = user_data_helper.get_user_anime_list()
    #     if animes_to_add:=difference(user_anime_list,self.model.already_in_user_anime_list):
    #         Logger.info("My List Screen:User anime list change;updating screen")
    #         anime_cards = self.model.update_my_anime_list_view(animes_to_add)
    #         self.model.already_in_user_anime_list = user_anime_list
    #         if isgenerator(anime_cards):
    #             for result_card in anime_cards:
    #                 result_card.screen = self.view
    #                 self.view.update_layout(result_card)

            
