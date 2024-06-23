from kivy.properties import ObjectProperty

from ...View.base_screen import BaseScreenView


class HomeScreenView(BaseScreenView):
    main_container = ObjectProperty()


__all__ = ["HomeScreenView"]
