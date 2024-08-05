from inspect import isgenerator

from kivy.logger import Logger
from kivy.clock import Clock
from kivy.utils import difference

from View import MyListScreenView
from Model import MyListScreenModel
from Utility import show_notification,user_data_helper

class MyListScreenController:
    """
    The `MainScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model:MyListScreenModel):
        self.model = model  
        self.view = MyListScreenView(controller=self, model=self.model)
        self.requested_update_my_list_screen()
    def get_view(self) -> MyListScreenView:
        return self.view

    def requested_update_my_list_screen(self):
        user_anime_list = user_data_helper.get_user_anime_list()
        if animes_to_add:=difference(user_anime_list,self.model.already_in_user_anime_list):
            Logger.info("My List Screen:User anime list change;updating screen")
            anime_cards = self.model.update_my_anime_list_view(animes_to_add)
            self.model.already_in_user_anime_list = user_anime_list
            if isgenerator(anime_cards):
                for result_card in anime_cards:
                    result_card.screen = self.view
                    self.view.update_layout(result_card)

            
