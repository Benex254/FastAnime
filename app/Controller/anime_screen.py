
from inspect import isgenerator
from View import AnimeScreenView
from Model import AnimeScreenModel
from View.components import MediaCardsContainer
from Utility import show_notification
from kivy.clock import Clock
class AnimeScreenController:
    def __init__(self, model:AnimeScreenModel):
        self.model = model
        self.view = AnimeScreenView(controller=self, model=self.model)

    def get_view(self) -> AnimeScreenView:
        return self.view

    def update_anime_view(self,id:int):
        if self.model.anime_id != id:
            data = self.model.get_anime_data(id)
            if data[0]:
                self.model.anime_id = id
                Clock.schedule_once(lambda _:self.view.update_layout(data[1]["data"]["Page"]["media"][0]))
                
    def update_my_list(self,*args):
        self.model.update_user_anime_list(*args)
    
