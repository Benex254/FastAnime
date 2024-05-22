from kivy.properties import ObjectProperty
from View.base_screen import BaseScreenView


class HomeScreenView(BaseScreenView):
    main_container = ObjectProperty()
    def write_data(self):
        self.controller.write_data()

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
    
