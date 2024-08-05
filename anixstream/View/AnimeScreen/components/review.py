from kivy.clock import Clock
from kivy.properties import ListProperty, ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout


class AnimeReview(MDBoxLayout):
    review = ObjectProperty({"username": "", "avatar": "", "summary": ""})


class AnimeReviews(MDBoxLayout):
    """anime reviews"""

    reviews = ListProperty()
    container = ObjectProperty()

    def on_reviews(self, *args):
        Clock.schedule_once(lambda _: self.update_reviews_card(*args))

    def update_reviews_card(self, instance, reviews):
        self.container.clear_widgets()
        for review in reviews:
            review_ = AnimeReview()
            review_.review = {
                "username": review["user"]["name"],
                "avatar": review["user"]["avatar"]["medium"],
                "summary": review["summary"],
            }
            self.container.add_widget(review_)
