
from inspect import isgenerator
from Utility import show_notification
from View import SearchScreenView
from Model import SearchScreenModel
from kivy.clock import Clock

class SearchScreenController:

    def __init__(self, model:SearchScreenModel):
        self.model = model  # Model.main_screen.MainScreenModel
        self.view = SearchScreenView(controller=self, model=self.model)
    def get_view(self) -> SearchScreenView:
        return self.view
    def update_trending_anime(self):
        trending_cards_generator = self.model.get_trending_anime()
        if isgenerator(trending_cards_generator):
            self.view.trending_anime_sidebar.clear_widgets()
            for card in trending_cards_generator:
                card.screen = self.view
                card.pos_hint =  {'center_x': 0.5}
                self.view.update_trending_sidebar(card)
        else:
            self.populate_errors.append("trending Anime")

    def requested_search_for_anime(self,anime_title,**kwargs):
        self.view.is_searching = True
        search_Results = self.model.search_for_anime(anime_title,**kwargs)
        if isgenerator(search_Results):
            for result_card in search_Results:
                result_card.screen = self.view
                self.view.update_layout(result_card)
            Clock.schedule_once(lambda _:self.view.update_pagination(self.model.pagination_info))
            Clock.schedule_once(lambda _:self.update_trending_anime())
        else:
            show_notification("Failed to search",f"{search_Results.get('Error')}")
        self.view.is_searching = False
