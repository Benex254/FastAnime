
from inspect import isgenerator
from View import HelpScreenView
from Model import HelpScreenModel
from View.components import MediaCardsContainer
from Utility import show_notification
from kivy.clock import Clock
class HelpScreenController:
    def __init__(self, model:HelpScreenModel):
        self.model = model
        self.view = HelpScreenView(controller=self, model=self.model)
        # self.update_anime_view()

    def get_view(self) -> HelpScreenView:
        return self.view
