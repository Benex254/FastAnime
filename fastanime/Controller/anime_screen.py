from kivy.cache import Cache

from ..Model import AnimeScreenModel
from ..View import AnimeScreenView

Cache.register("data.anime", limit=20, timeout=600)


class AnimeScreenController:
    """The controller for the anime screen"""

    def __init__(self, model: AnimeScreenModel):
        self.model = model
        self.view = AnimeScreenView(controller=self, model=self.model)

    def get_view(self) -> AnimeScreenView:
        return self.view

    def fetch_streams(self, anime_title, episode="1"):
        self.view.current_anime_data = self.model.get_anime_data_from_provider(
            anime_title
        )
        self.view.current_links = self.model.get_episode_streams(episode)

    def update_anime_view(self, id, title, caller_screen_name):
        self.fetch_streams(title)
        self.view.current_title = title
        self.view.caller_screen_name = caller_screen_name
