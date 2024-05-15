
from inspect import isgenerator
from View import SearchScreenView
from Model import SearchScreenModel

class SearchScreenController:

    def __init__(self, model:SearchScreenModel):
        self.model = model  # Model.main_screen.MainScreenModel
        self.view = SearchScreenView(controller=self, model=self.model)
    def get_view(self) -> SearchScreenView:
        return self.view
    
    def requested_search_for_anime(self,anime_title,**kwargs):
        self.view.is_searching = True
        data = self.model.search_for_anime(anime_title,**kwargs)
        if isgenerator(data):
            for result_card in data:
                self.view.update_layout(result_card)
        else:
            print(data)
        # self.view.add_pagination()
        self.view.is_searching = False
