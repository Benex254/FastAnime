
from inspect import isgenerator
from View import MyListScreenView
from Model import MyListScreenModel
from View.components.media_card.media_card import MediaCardsContainer
from Utility import show_notification

class MyListScreenController:
    """
    The `MainScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model:MyListScreenModel):
        self.model = model  # Model.main_screen.MyListScreenModel
        self.view = MyListScreenView(controller=self, model=self.model)
        # self.populate_home_screen()
    def get_view(self) -> MyListScreenView:
        return self.view
