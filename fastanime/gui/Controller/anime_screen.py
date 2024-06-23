from kivy.cache import Cache

from ..Model.anime_screen import AnimeScreenModel
from ..View.AnimeScreen.anime_screen import AnimeScreenView

Cache.register("data.anime", limit=20, timeout=600)


class AnimeScreenController:
    """The controller for the anime screen"""

    def __init__(self, model: AnimeScreenModel):
        self.model = model
        self.view = AnimeScreenView(controller=self, model=self.model)

    def get_view(self) -> AnimeScreenView:
        return self.view

    def fetch_streams(self, anime_title, is_dub=False, episode="1"):
        if self.view.is_dub:
            is_dub = self.view.is_dub.active
            if anime_data := self.model.get_anime_data_from_provider(
                anime_title, is_dub
            ):
                self.view.current_anime_data = anime_data
        if current_links := self.model.get_episode_streams(episode, is_dub):
            self.view.current_links = current_links
        # TODO: add auto start
        #
        # self.view.current_link = self.view.current_links[0]["gogoanime"][0]

    def update_anime_view(self, id, title, caller_screen_name):
        self.fetch_streams(title)
        self.view.current_title = title
        self.view.caller_screen_name = caller_screen_name


__all__ = ["AnimeScreenController"]
