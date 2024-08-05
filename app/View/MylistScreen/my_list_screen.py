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
    
   
    def update_layout(self,widget):
        pass
    def add_pagination(self,pagination_info):
        pass