from kivy.properties import StringProperty

from kivymd.uix.boxlayout import MDBoxLayout


class AnimeDescription(MDBoxLayout):
    """The anime description"""

    description = StringProperty()
