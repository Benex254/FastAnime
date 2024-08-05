
from inspect import isgenerator
from View.HomeScreen.home_screen import HomeScreenView
from Model.home_screen import HomeScreenModel
from View.components.media_card.media_card import MediaCardsContainer
from Utility import show_notification
from kivy.clock import Clock

class HomeScreenController:
    """
    The `MainScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """
    populate_errors = []

    def __init__(self, model:HomeScreenModel):
        self.model = model  # Model.main_screen.MainScreenModel
        self.view = HomeScreenView(controller=self, model=self.model)
        Clock.schedule_once(lambda _:self.populate_home_screen())
    def get_view(self) -> HomeScreenView:
        return self.view

    def popular_anime(self):
        most_popular_cards_container = MediaCardsContainer()
        most_popular_cards_container.list_name = "Most Popular"
        most_popular_cards_generator = self.model.get_most_popular_anime()
        if isgenerator(most_popular_cards_generator):
            for card in most_popular_cards_generator:
                card.screen = self.view
                most_popular_cards_container.container.add_widget(card)
            self.view.main_container.add_widget(most_popular_cards_container)
        else:
            self.populate_errors.append("Most Popular Anime")

    def favourite_anime(self):
        most_favourite_cards_container = MediaCardsContainer()
        most_favourite_cards_container.list_name = "Most Favourites"
        most_favourite_cards_generator = self.model.get_most_favourite_anime()
        if isgenerator(most_favourite_cards_generator):
            for card in most_favourite_cards_generator:
                card.screen = self.view
                most_favourite_cards_container.container.add_widget(card)
            self.view.main_container.add_widget(most_favourite_cards_container)
        else:
            self.populate_errors.append("Most favourite Anime")

    def trending_anime(self):
        trending_cards_container = MediaCardsContainer()
        trending_cards_container.list_name = "Trending"
        trending_cards_generator = self.model.get_trending_anime()
        if isgenerator(trending_cards_generator):
            for card in trending_cards_generator:
                card.screen = self.view
                trending_cards_container.container.add_widget(card)
            self.view.main_container.add_widget(trending_cards_container)
        else:
            self.populate_errors.append("trending Anime")

    def highest_scored_anime(self):        
        most_scored_cards_container = MediaCardsContainer()
        most_scored_cards_container.list_name = "Most Scored"
        most_scored_cards_generator = self.model.get_most_scored_anime()
        if isgenerator(most_scored_cards_generator):
            for card in most_scored_cards_generator:
                card.screen = self.view
                most_scored_cards_container.container.add_widget(card)
            self.view.main_container.add_widget(most_scored_cards_container)
        else:
            self.populate_errors.append("Most scored Anime")

    def recently_updated_anime(self):
        
        most_recently_updated_cards_container = MediaCardsContainer()
        most_recently_updated_cards_container.list_name = "Most Recently Updated"
        most_recently_updated_cards_generator = self.model.get_most_recently_updated_anime()
        if isgenerator(most_recently_updated_cards_generator):
            for card in most_recently_updated_cards_generator:
                card.screen = self.view
                most_recently_updated_cards_container.container.add_widget(card)
            self.view.main_container.add_widget(most_recently_updated_cards_container)
        else:
            self.populate_errors.append("Most recently updated Anime")

    def upcoming_anime(self):        
        upcoming_cards_container = MediaCardsContainer()
        upcoming_cards_container.list_name = "Upcoming Anime"
        upcoming_cards_generator = self.model.get_upcoming_anime()
        if isgenerator(upcoming_cards_generator):
            for card in upcoming_cards_generator:
                card.screen = self.view
                upcoming_cards_container.container.add_widget(card)
            self.view.main_container.add_widget(upcoming_cards_container)
        else:
            self.populate_errors.append("upcoming Anime")

    def populate_home_screen(self):
        self.populate_errors = []
        self.trending_anime()
        self.highest_scored_anime()
        self.popular_anime()
        self.favourite_anime()
        self.recently_updated_anime()
        self.upcoming_anime()

        if self.populate_errors:
            show_notification(f"Failed to fetch all home screen data",f"Theres probably a problem with your internet connection or anilist servers are down.\nFailed include:{', '.join(self.populate_errors)}")


    def update_my_list(self,*args):
        self.model.update_user_anime_list(*args)
    
