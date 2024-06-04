from kivy.properties import DictProperty, StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dropdownitem import MDDropDownItem
from kivymd.uix.menu import MDDropdownMenu


class FilterDropDown(MDDropDownItem):
    text: str = StringProperty()


class Filters(MDBoxLayout):
    filters: dict = DictProperty({"sort": "SEARCH_MATCH", "status": "FINISHED"})

    def open_filter_menu(self, menu_item, filter_name):
        items = []
        match filter_name:
            case "sort":
                items = [
                    "ID",
                    "ID_DESC",
                    "TITLE_ROMANJI",
                    "TITLE_ROMANJI_DESC",
                    "TITLE_ENGLISH",
                    "TITLE_ENGLISH_DESC",
                    "TITLE_NATIVE",
                    "TITLE_NATIVE_DESC",
                    "TYPE",
                    "TYPE_DESC",
                    "FORMAT",
                    "FORMAT_DESC",
                    "START_DATE",
                    "START_DATE_DESC",
                    "END_DATE",
                    "END_DATE_DESC",
                    "SCORE",
                    "SCORE_DESC",
                    "TRENDING",
                    "TRENDING_DESC",
                    "EPISODES",
                    "EPISODES_DESC",
                    "DURATION",
                    "DURATION_DESC",
                    "STATUS",
                    "STATUS_DESC",
                    "UPDATED_AT",
                    "UPDATED_AT_DESC",
                    "SEARCH_MATCH",
                    "POPULARITY",
                    "POPULARITY_DESC",
                    "FAVOURITES",
                    "FAVOURITES_DESC",
                ]
            case "status":
                items = [
                    "FINISHED",
                    "RELEASING",
                    "NOT_YET_RELEASED",
                    "CANCELLED",
                    "HIATUS",
                ]
            case _:
                items = []
        if items:
            menu_items = [
                {
                    "text": f"{item}",
                    "on_release": lambda filter_value=f"{item}": self.filter_menu_callback(
                        filter_name, filter_value
                    ),
                }
                for item in items
            ]
            MDDropdownMenu(caller=menu_item, items=menu_items).open()

    def filter_menu_callback(self, filter_name, filter_value):
        match filter_name:
            case "sort":
                self.ids.sort_filter.text = filter_value
                self.filters["sort"] = filter_value
            case "status":
                self.ids.status_filter.text = filter_value
                self.filters["status"] = filter_value
