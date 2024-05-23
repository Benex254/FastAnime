
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
