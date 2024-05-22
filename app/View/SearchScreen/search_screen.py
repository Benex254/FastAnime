from kivy.properties import ObjectProperty,StringProperty,DictProperty,NumericProperty
from View.base_screen import BaseScreenView
from kivymd.uix.dropdownitem import MDDropDownItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.clock import Clock


class FilterDropDown(MDDropDownItem):
    text = StringProperty()
    
class Filters(MDBoxLayout):
    filters = DictProperty({
        "sort":"SEARCH_MATCH"
    })
    def open_filter_menu(self, menu_item,filter_name):
        items = []
        match filter_name:
            case "sort":
                items = ["ID","ID_DESC", "TITLE_ROMANJI", "TITLE_ROMANJI_DESC", "TITLE_ENGLISH", "TITLE_ENGLISH_DESC", "TITLE_NATIVE", "TITLE_NATIVE_DESC", "TYPE", "TYPE_DESC", "FORMAT", "FORMAT_DESC", "START_DATE", "START_DATE_DESC", "END_DATE", "END_DATE_DESC", "SCORE", "SCORE_DESC", "TRENDING", "TRENDING_DESC", "EPISODES", "EPISODES_DESC", "DURATION", "DURATION_DESC", "STATUS", "STATUS_DESC", "UPDATED_AT", "UPDATED_AT_DESC", "SEARCH_MATCH" "POPULARITY","POPULARITY_DESC","FAVOURITES","FAVOURITES_DESC"]
            case "status":
                items = ["FINISHED", "RELEASING", "NOT_YET_RELEASED", "CANCELLED", "HIATUS"] 
            case _:
                items = []
        if items:                
            menu_items = [
                {
                    "text": f"{item}",
                    "on_release": lambda filter_value=f"{item}": self.filter_menu_callback(filter_name,filter_value),
                } for item in items
            ]
            MDDropdownMenu(caller=menu_item, items=menu_items).open()

    def filter_menu_callback(self, filter_name,filter_value):
        match filter_name:
            case "sort":
                self.ids.sort_filter.text = filter_value
                self.filters["sort"] = filter_value
            case "status":
                self.ids.status_filter.text = filter_value
                self.filters["status"] = filter_value
            

class SearchResultsPagination(MDBoxLayout):
    current_page = NumericProperty()
    total_pages = NumericProperty()
    search_view = ObjectProperty()
    
class TrendingAnimeSideBar(MDBoxLayout):
    pass

class SearchScreenView(BaseScreenView): 
    search_results_container = ObjectProperty()
    trending_anime_sidebar = ObjectProperty()
    search_results_pagination = ObjectProperty()
    search_term = StringProperty()
    filters = ObjectProperty() 
    is_searching = False
    has_next_page = False
    current_page = 0
    total_pages = 0
    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
    
    def handle_search_for_anime(self,search_widget=None,page=None):
        if search_widget:
            search_term = search_widget.text
        elif page:
            search_term = self.search_term
        else:
            return
        
        if search_term and not(self.is_searching):
            self.search_term = search_term
            self.search_results_container.clear_widgets()
            if filters:=self.filters.filters:
                Clock.schedule_once(lambda _:self.controller.requested_search_for_anime(search_term,**filters,page=page))
            else:
                Clock.schedule_once(lambda _:self.controller.requested_search_for_anime(search_term,page=page))
 
    def update_layout(self,widget):
        self.search_results_container.add_widget(widget)

    def update_pagination(self,pagination_info):
        self.search_results_pagination.current_page =self.current_page = pagination_info["currentPage"]
        self.search_results_pagination.total_pages = self.total_pages = pagination_info["total"]
        self.has_next_page = pagination_info["hasNextPage"]

    def next_page(self):
        if self.has_next_page:
            page = self.current_page + 1
            self.handle_search_for_anime(page=page)

    def previous_page(self):
        if self.current_page > 1:
            page = self.current_page - 1
            self.handle_search_for_anime(page=page)

    def update_trending_sidebar(self,trending_anime):
        self.trending_anime_sidebar.add_widget(trending_anime)
