from inspect import isgenerator
from math import ceil

from kivy.logger import Logger

# from kivy.clock import Clock
from kivy.utils import difference

from ..Model.my_list_screen import MyListScreenModel
from ..Utility import user_data_helper
from ..View.MylistScreen.my_list_screen import MyListScreenView


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
        self.requested_update_my_list_screen()

    def get_view(self) -> MyListScreenView:
        return self.view

    def requested_update_my_list_screen(self):
        _user_anime_list = user_data_helper.get_user_anime_list()
        if animes_to_add := difference(
            _user_anime_list, self.model.already_in_user_anime_list
        ):
            no_of_updates = ceil(len(animes_to_add) / 30)
            Logger.info("MyList Screen:Change detected updating screen")
            for i in range(no_of_updates):
                _animes_to_add = animes_to_add[i * 30 : (i + 1) * 30]
                anime_cards = self.model.update_my_anime_list_view(_animes_to_add)

                if isgenerator(anime_cards):
                    for result_card in anime_cards:
                        result_card["screen"] = self.view
                        self.view.update_layout(result_card)
            self.model.already_in_user_anime_list = _user_anime_list
            return animes_to_add


__all__ = ["MyListScreenController"]
