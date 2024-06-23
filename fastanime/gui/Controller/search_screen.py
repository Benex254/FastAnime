from inspect import isgenerator

from kivy.clock import Clock
from kivy.logger import Logger

from ..Model.search_screen import SearchScreenModel
from ..View.SearchScreen.search_screen import SearchScreenView


class SearchScreenController:
    """The search screen controller"""

    def __init__(self, model: SearchScreenModel):
        self.model = model
        self.view = SearchScreenView(controller=self, model=self.model)

    def get_view(self) -> SearchScreenView:
        return self.view

    def update_trending_anime(self):
        """Gets and adds the trending anime to the search screen"""
        trending_cards_generator = self.model.get_trending_anime()
        if isgenerator(trending_cards_generator):
            # self.view.trending_anime_sidebar.data = []
            for card in trending_cards_generator:
                card["screen"] = self.view
                # card["pos_hint"] = {"center_x": 0.5}
                self.view.update_trending_sidebar(card)
        else:
            Logger.error("Home Screen:Failed to load trending anime")

    def requested_search_for_anime(self, anime_title, **kwargs):
        self.view.is_searching = True
        search_Results = self.model.search_for_anime(anime_title, **kwargs)
        if isgenerator(search_Results):
            for result_card in search_Results:
                result_card["screen"] = self.view
                self.view.update_layout(result_card)
            Clock.schedule_once(
                lambda _: self.view.update_pagination(self.model.pagination_info)
            )
            self.update_trending_anime()
        else:
            Logger.error(f"Home Screen:Failed to search for {anime_title}")
        self.view.is_searching = False


__all__ = ["SearchScreenController"]
