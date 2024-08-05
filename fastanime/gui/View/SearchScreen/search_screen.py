from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty

from ...View.base_screen import BaseScreenView
from .components.filters import Filters
from .components.pagination import SearchResultsPagination
from .components.trending_sidebar import TrendingAnimeSideBar


class SearchScreenView(BaseScreenView):
    trending_anime_sidebar: TrendingAnimeSideBar = ObjectProperty()
    search_results_pagination: SearchResultsPagination = ObjectProperty()
    filters: Filters = ObjectProperty()

    search_results_container = ObjectProperty()
    search_term: str = StringProperty()
    is_searching = False
    has_next_page = False
    current_page = 0
    total_pages = 0

    def handle_search_for_anime(self, search_widget=None, page=None):
        if search_widget:
            search_term = search_widget.text
        elif page:
            search_term = self.search_term
        else:
            return

        if search_term and not (self.is_searching):
            self.search_term = search_term
            self.search_results_container.data = []
            if filters := self.filters.filters:
                Clock.schedule_once(
                    lambda _: self.controller.requested_search_for_anime(
                        search_term, **filters, page=page
                    )
                )
            else:
                Clock.schedule_once(
                    lambda _: self.controller.requested_search_for_anime(
                        search_term, page=page
                    )
                )

    def update_layout(self, widget):
        self.search_results_container.data.append(widget)

    def update_pagination(self, pagination_info):
        self.search_results_pagination.current_page = self.current_page = (
            pagination_info["currentPage"]
        )
        self.search_results_pagination.total_pages = self.total_pages = max(
            int(pagination_info["total"] / 30), 1
        )
        self.has_next_page = pagination_info["hasNextPage"]

    def next_page(self):
        if self.has_next_page:
            page = self.current_page + 1
            self.handle_search_for_anime(page=page)

    def previous_page(self):
        if self.current_page > 1:
            page = self.current_page - 1
            self.handle_search_for_anime(page=page)

    def update_trending_sidebar(self, trending_anime):
        self.trending_anime_sidebar.data.append(trending_anime)


__all__ = ["SearchScreenView"]
