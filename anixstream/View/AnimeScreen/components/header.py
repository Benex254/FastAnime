from kivy.properties import StringProperty

from kivymd.uix.boxlayout import MDBoxLayout


class AnimeHeader(MDBoxLayout):
    titles = StringProperty()
    banner_image = StringProperty()
