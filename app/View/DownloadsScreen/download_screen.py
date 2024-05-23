from kivy.properties import ObjectProperty
from View.base_screen import BaseScreenView
from kivy.uix.modalview import ModalView

class DownloadAnimePopup(ModalView):
    pass

class DownloadsScreenView(BaseScreenView):
    main_container = ObjectProperty()
    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """

