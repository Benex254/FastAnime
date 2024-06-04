from kivy.properties import DictProperty
from kivymd.uix.boxlayout import MDBoxLayout


class RankingsBar(MDBoxLayout):
    rankings = DictProperty(
        {
            "Popularity": 0,
            "Favourites": 0,
            "AverageScore": 0,
        }
    )
