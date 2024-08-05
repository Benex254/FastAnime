from kivy.properties import ObjectProperty,ListProperty

from kivymd.uix.boxlayout import MDBoxLayout


class AnimeReview(MDBoxLayout):
    review = ObjectProperty({
        "username":"",
        "avatar":"",
        "summary":""
    })


class AnimeReviews(MDBoxLayout):
    reviews = ListProperty()
    container = ObjectProperty()
    def on_reviews(self,instance,reviews):
        self.container.clear_widgets()
        for review in reviews:
            review_ = AnimeReview()
            review_.review = {
                "username":review["user"]["name"],
                "avatar":review["user"]["avatar"]["medium"],
                "summary":review["summary"]
            }
            self.container.add_widget(review_)
