from inspect import isgenerator

from kivy.clock import Clock
from kivy.logger import Logger

from ...Utility.show_notification import show_notification
from ..Model.home_screen import HomeScreenModel
from ..View.components.media_card.media_card import MediaCardsContainer
from ..View.HomeScreen.home_screen import HomeScreenView


# TODO:Move the update home screen to homescreen.py
class HomeScreenController:
    """
    The `HomeScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    populate_errors = []
    _discover_anime_list = []

    def __init__(self, model: HomeScreenModel):
        self.model = model  # Model.main_screen.MainScreenModel
        self.view = HomeScreenView(controller=self, model=self.model)

        self._discover_anime_list = [
            self.highest_scored_anime,
            self.popular_anime,
            self.favourite_anime,
            self.upcoming_anime,
            self.recently_updated_anime,
            self.trending_anime,
        ]

        self.get_more_anime()

    def get_view(self) -> HomeScreenView:
        return self.view

    def popular_anime(self):
        most_popular_cards_container = MediaCardsContainer()
        most_popular_cards_container.list_name = "Most Popular"
        most_popular_cards_generator = self.model.get_most_popular_anime()
        if isgenerator(most_popular_cards_generator):
            for card in most_popular_cards_generator:
                card["screen"] = self.view
                card["viewclass"] = "MediaCard"
                most_popular_cards_container.container.data.append(card)
            self.view.main_container.add_widget(most_popular_cards_container)
        else:
            Logger.error("Home Screen:Failed to load most popular anime")
            self.populate_errors.append("Most Popular Anime")

    def favourite_anime(self):
        most_favourite_cards_container = MediaCardsContainer()
        most_favourite_cards_container.list_name = "Most Favourites"
        most_favourite_cards_generator = self.model.get_most_favourite_anime()
        if isgenerator(most_favourite_cards_generator):
            for card in most_favourite_cards_generator:
                card["screen"] = self.view
                card["viewclass"] = "MediaCard"
                most_favourite_cards_container.container.data.append(card)
            self.view.main_container.add_widget(most_favourite_cards_container)
        else:
            Logger.error("Home Screen:Failed to load most favourite anime")
            self.populate_errors.append("Most favourite Anime")

    def trending_anime(self):
        trending_cards_container = MediaCardsContainer()
        trending_cards_container.list_name = "Trending"
        trending_cards_generator = self.model.get_trending_anime()
        if isgenerator(trending_cards_generator):
            for card in trending_cards_generator:
                card["screen"] = self.view
                card["viewclass"] = "MediaCard"
                trending_cards_container.container.data.append(card)
            self.view.main_container.add_widget(trending_cards_container)
        else:
            Logger.error("Home Screen:Failed to load trending anime")
            self.populate_errors.append("trending Anime")

    def highest_scored_anime(self):
        most_scored_cards_container = MediaCardsContainer()
        most_scored_cards_container.list_name = "Most Scored"
        most_scored_cards_generator = self.model.get_most_scored_anime()
        if isgenerator(most_scored_cards_generator):
            for card in most_scored_cards_generator:
                card["screen"] = self.view
                card["viewclass"] = "MediaCard"
                most_scored_cards_container.container.data.append(card)
            self.view.main_container.add_widget(most_scored_cards_container)
        else:
            Logger.error("Home Screen:Failed to load highest scored anime")
            self.populate_errors.append("Most scored Anime")

    def recently_updated_anime(self):
        most_recently_updated_cards_container = MediaCardsContainer()
        most_recently_updated_cards_container.list_name = "Most Recently Updated"
        most_recently_updated_cards_generator = (
            self.model.get_most_recently_updated_anime()
        )
        if isgenerator(most_recently_updated_cards_generator):
            for card in most_recently_updated_cards_generator:
                card["screen"] = self.view
                card["viewclass"] = "MediaCard"
                most_recently_updated_cards_container.container.data.append(card)
            self.view.main_container.add_widget(most_recently_updated_cards_container)
        else:
            Logger.error("Home Screen:Failed to load recently updated anime")
            self.populate_errors.append("Most recently updated Anime")

    def upcoming_anime(self):
        upcoming_cards_container = MediaCardsContainer()
        upcoming_cards_container.list_name = "Upcoming Anime"
        upcoming_cards_generator = self.model.get_upcoming_anime()
        if isgenerator(upcoming_cards_generator):
            for card in upcoming_cards_generator:
                card["screen"] = self.view
                card["viewclass"] = "MediaCard"
                upcoming_cards_container.container.data.append(card)
            self.view.main_container.add_widget(upcoming_cards_container)
        else:
            Logger.error("Home Screen:Failed to load upcoming anime")
            self.populate_errors.append("upcoming Anime")

    def get_more_anime(self):
        self.populate_errors = []
        if self._discover_anime_list:
            task = self._discover_anime_list.pop()
            Clock.schedule_once(lambda _: task())
        else:
            show_notification("Home Screen Info", "No more anime to load")

        if self.populate_errors:
            show_notification(
                "Failed to fetch all home screen data",
                f"Theres probably a problem with your internet connection or anilist servers are down.\nFailed include:{', '.join(self.populate_errors)}",
            )
        self.populate_errors = []


__all__ = ["HomeScreenController"]
