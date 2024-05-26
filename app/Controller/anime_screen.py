from kivy.clock import Clock
from kivy.logger import Logger
from kivy.cache import Cache

from Model import AnimeScreenModel
from View import AnimeScreenView

Cache.register("data.anime", limit=20, timeout=600)


class AnimeScreenController:
    def __init__(self, model: AnimeScreenModel):
        self.model = model
        self.view = AnimeScreenView(controller=self, model=self.model)

    def get_view(self) -> AnimeScreenView:
        return self.view

    def update_anime_view(self, id: int, caller_screen_name: str):
        if self.model.anime_id != id:
            if cached_anime_data := Cache.get("data.anime", f"{id}"):
                data = cached_anime_data
            else:
                data = self.model.get_anime_data(id)

            if data[0]:

                self.model.anime_id = id
                Clock.schedule_once(
                    lambda _: self.view.update_layout(
                        data[1]["data"]["Page"]["media"][0], caller_screen_name
                    )
                )
                Logger.info(f"Anime Screen:Success in opening anime of id: {id}")
                Cache.append("data.anime", f"{id}", data)
