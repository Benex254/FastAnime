from kivy.properties import ObjectProperty,StringProperty,DictProperty
from View.base_screen import BaseScreenView


class MyListScreenView(BaseScreenView):
    my_list_container = ObjectProperty()
    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
    
    def handle_search_for_anime(self,search_widget):
        search_term = search_widget.text
        if search_term and not(self.is_searching):
            self.search_term = search_term
            self.search_results_container.clear_widgets()
            if self.filters:
                self.controller.requested_search_for_anime(search_term,**self.filters)
            else:
                self.controller.requested_search_for_anime(search_term)
 
    def update_layout(self,widget):
        self.search_results_container.add_widget(widget)

    def add_pagination(self,pagination_info):
        pass