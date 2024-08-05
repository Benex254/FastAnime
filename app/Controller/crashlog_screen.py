
from inspect import isgenerator
from View import CrashLogScreenView
from Model import CrashLogScreenModel
from View.components import MediaCardsContainer
from Utility import show_notification
from kivy.clock import Clock
class CrashLogScreenController:
    def __init__(self, model:CrashLogScreenModel):
        self.model = model
        self.view = CrashLogScreenView(controller=self, model=self.model)
        # self.update_anime_view()

    def get_view(self) -> CrashLogScreenView:
        return self.view
