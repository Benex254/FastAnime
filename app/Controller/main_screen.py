
from inspect import isgenerator
from View.MainScreen.main_screen import MainScreenView
from Model.main_screen import MainScreenModel
from View.components.media_card.media_card import MediaCardsContainer
from Utility import show_notification

class MainScreenController:
    """
    The `MainScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.
    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model:MainScreenModel):
        self.model = model  # Model.main_screen.MainScreenModel
        self.view = MainScreenView(controller=self, model=self.model)
        self.populate_home_screen()
    def get_view(self) -> MainScreenView:
        return self.view

    def populate_home_screen(self):
        errors = []
        most_popular_cards_container = MediaCardsContainer()
        most_popular_cards_container.list_name = "Most Popular"
        most_popular_cards_generator = self.model.get_most_popular_anime()
        if isgenerator(most_popular_cards_generator):
            for card in most_popular_cards_generator:
                card.screen = self.view
                most_popular_cards_container.container.add_widget(card)
            self.view.main_container.add_widget(most_popular_cards_container)
        else:
            errors.append("Most Popular Anime")

        most_favourite_cards_container = MediaCardsContainer()
        most_favourite_cards_container.list_name = "Most Favourites"
        most_favourite_cards_generator = self.model.get_most_favourite_anime()
        if isgenerator(most_favourite_cards_generator):
            for card in most_favourite_cards_generator:
                card.screen = self.view
                most_favourite_cards_container.container.add_widget(card)
            self.view.main_container.add_widget(most_favourite_cards_container)
        else:
            errors.append("Most favourite Anime")

        trending_cards_container = MediaCardsContainer()
        trending_cards_container.list_name = "Trending"
        trending_cards_generator = self.model.get_trending_anime()
        if isgenerator(trending_cards_generator):
            for card in trending_cards_generator:
                card.screen = self.view
                trending_cards_container.container.add_widget(card)
            self.view.main_container.add_widget(trending_cards_container)
        else:
            errors.append("trending Anime")

        most_scored_cards_container = MediaCardsContainer()
        most_scored_cards_container.list_name = "Most Scored"
        most_scored_cards_generator = self.model.get_most_scored_anime()
        if isgenerator(most_scored_cards_generator):
            for card in most_scored_cards_generator:
                card.screen = self.view
                most_scored_cards_container.container.add_widget(card)
            self.view.main_container.add_widget(most_scored_cards_container)
        else:
            errors.append("Most scored Anime")

        most_recently_updated_cards_container = MediaCardsContainer()
        most_recently_updated_cards_container.list_name = "Most Recently Updated"
        most_recently_updated_cards_generator = self.model.get_most_recently_updated_anime()
        if isgenerator(most_recently_updated_cards_generator):
            for card in most_recently_updated_cards_generator:
                card.screen = self.view
                most_recently_updated_cards_container.container.add_widget(card)
            self.view.main_container.add_widget(most_recently_updated_cards_container)
        else:
            errors.append("Most recently updated Anime")

        upcoming_cards_container = MediaCardsContainer()
        upcoming_cards_container.list_name = "Upcoming Anime"
        upcoming_cards_generator = self.model.get_upcoming_anime()
        if isgenerator(upcoming_cards_generator):
            for card in upcoming_cards_generator:
                card.screen = self.view
                upcoming_cards_container.container.add_widget(card)
            self.view.main_container.add_widget(upcoming_cards_container)
        else:
            errors.append("upcoming Anime")

        if errors:
            show_notification(f"Failed to get the following  {', '.join(errors)}","Theres probably a problem with your internet connection or anilist servers are down")
    def update_my_list(self,*args):
        self.model.update_user_anime_list(*args)
    
