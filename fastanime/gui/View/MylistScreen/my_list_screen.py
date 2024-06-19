from kivy.clock import Clock
from kivy.properties import ObjectProperty

from ...View.base_screen import BaseScreenView


class MyListScreenView(BaseScreenView):
    user_anime_list_container = ObjectProperty()

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """

    def on_enter(self):
        Clock.schedule_once(lambda _: self.controller.requested_update_my_list_screen())

    def update_layout(self, widget):
        self.user_anime_list_container.data.append(widget)
