from inspect import isgenerator

from kivy.logger import Logger

# from kivy.clock import Clock
from kivy.utils import difference

from ..Model import MyListScreenModel
from ..Utility import user_data_helper
from ..View import MyListScreenView


class MyListScreenController:
    """
    The `MyListScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model: MyListScreenModel):
        self.model = model
        self.view = MyListScreenView(controller=self, model=self.model)
        # if len(self.requested_update_my_list_screen()) > 30:
        # self.requested_update_my_list_screen(2)

    def get_view(self) -> MyListScreenView:
        return self.view

    def requested_update_my_list_screen(self, page=None):
        user_anime_list = user_data_helper.get_user_anime_list()
        if animes_to_add := difference(
            user_anime_list, self.model.already_in_user_anime_list
        ):
            Logger.info("My List Screen:User anime list change;updating screen")
            # if thirty:=len(animes_to_add)>30:
            #     self.model.already_in_user_anime_list = user_anime_list[:30]
            # else:

            anime_cards = self.model.update_my_anime_list_view(animes_to_add, page)
            self.model.already_in_user_anime_list = user_anime_list

            if isgenerator(anime_cards):
                for result_card in anime_cards:
                    result_card.screen = self.view
                    self.view.update_layout(result_card)
            return animes_to_add
        elif page:
            anime_cards = self.model.update_my_anime_list_view(
                self.model.already_in_user_anime_list, page
            )
            # self.model.already_in_user_anime_list = user_anime_list
            if isgenerator(anime_cards):
                for result_card in anime_cards:
                    result_card.screen = self.view
                    self.view.update_layout(result_card)
            return []
        else:
            return []
