from kivy.properties import NumericProperty, ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout


class SearchResultsPagination(MDBoxLayout):
    current_page = NumericProperty()
    total_pages = NumericProperty()
    search_view = ObjectProperty()
