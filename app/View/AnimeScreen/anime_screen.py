from kivy.properties import ObjectProperty,StringProperty,DictProperty,ListProperty
from datetime import datetime
from View.base_screen import BaseScreenView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivy.utils import QueryDict,get_hex_from_color
from collections import defaultdict

from . import AnimdlStreamDialog

# TODO:move the rest of the classes to their own files

class RankingsBar(MDBoxLayout):
    rankings = DictProperty(
        {
            "Popularity":0,
            "Favourites":0,
            "AverageScore":0,
        }
    )


class AnimeDescription(MDBoxLayout):
    description = StringProperty()


class AnimeCharacter(MDBoxLayout):
    voice_actors = ObjectProperty({
        "name":"",
        "image":""
    })
    character = ObjectProperty({
        "name":"",
        "gender":"",
        "dateOfBirth":"",
        "image":"",
        "age":"",
        "description":""
    })


class AnimeCharacters(MDBoxLayout):
    container = ObjectProperty()
    characters = ListProperty()
    def on_characters(self,instance,characters):
        format_date = lambda date_:  f"{date_['day']}/{date_['month']}/{date_['year']}" if date_ else ""
        self.container.clear_widgets()
        for character_ in characters: # character (character,actor)
            character = character_[0]
            actors = character_[1]

            anime_character = AnimeCharacter()
            anime_character.character = {
                "name":character["name"]["full"],
                "gender":character["gender"],
                "dateOfBirth":format_date(character["dateOfBirth"]),
                "image":character["image"]["medium"],
                "age":character["age"],
                "description":character["description"]
            }
            anime_character.voice_actors = {
                "name":", ".join([actor["name"]["full"] for actor in actors])
            }

            # anime_character.voice_actor =
            self.container.add_widget(anime_character)


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


class AnimeHeader(MDBoxLayout):
    titles = StringProperty()
    banner_image = StringProperty()


class SideBarLabel(MDLabel):
    pass


class SideBarHeaderLabel(MDLabel):
    pass


class AnimeSideBar(MDBoxLayout):
    screen = ObjectProperty()
    image = StringProperty()
    alternative_titles = DictProperty({
        "synonyms":"",
        "english":"",
        "japanese":"",
    })
    information = DictProperty({
        "episodes":"",
        "status":"",
        "aired":"",
        "nextAiringEpisode":"",
        "premiered":"",
        "broadcast":"",
        "countryOfOrigin":"",
        "hashtag":"",
        "studios":"", # { "name": "Sunrise", "isAnimationStudio": true }
        "source":"",
        "genres":"",
        "duration":"",
        "producers":"",
    })
    statistics = ListProperty()
    statistics_container = ObjectProperty()
    external_links = ListProperty()
    external_links_container = ObjectProperty()
    tags = ListProperty()
    tags_container = ObjectProperty()

    def on_statistics(self,instance,value):
        self.statistics_container.clear_widgets()
        header = SideBarHeaderLabel()
        header.text = "Rankings"
        self.statistics_container.add_widget(header)
        for stat in value:
            # stat (rank,context)
            label = SideBarLabel()
            label.text = "[color={}]{}:[/color] {}".format(
                get_hex_from_color(label.theme_cls.primaryColor),
                stat[0].capitalize(),
                f"{stat[1]}")
            self.statistics_container.add_widget(label)

    def on_tags(self,instance,value):
        self.tags_container.clear_widgets()
        header = SideBarHeaderLabel()
        header.text = "Tags"
        self.tags_container.add_widget(header)
        for tag in value:
            label = SideBarLabel()
            label.text = "[color={}]{}:[/color] {}".format(
                get_hex_from_color(label.theme_cls.primaryColor),
                tag[0].capitalize(),
                f"{tag[1]} %")
            self.tags_container.add_widget(label)


    def on_external_links(self,instance,value):
        self.external_links_container.clear_widgets()
        header = SideBarHeaderLabel()
        header.text = "External Links"
        self.external_links_container.add_widget(header)
        for site in value:
            # stat (rank,context)
            label = SideBarLabel()
            label.text = "[color={}]{}:[/color] {}".format(
                get_hex_from_color(label.theme_cls.primaryColor),
                site[0].capitalize(),
                site[1])
            self.external_links_container.add_widget(label)

class Controls(MDBoxLayout):
    screen = ObjectProperty()


class AnimeScreenView(BaseScreenView):
    header:AnimeHeader = ObjectProperty()
    side_bar:AnimeSideBar = ObjectProperty()
    rankings_bar:RankingsBar = ObjectProperty()
    anime_description:AnimeDescription = ObjectProperty()
    anime_characters:AnimeCharacters = ObjectProperty()
    anime_reviews:AnimeReviews = ObjectProperty()
    data = DictProperty()
    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """
    
    def update_layout(self,data):
        self.data = data
        # uitlity functions
        format_date = lambda date_:  f"{date_['day']}/{date_['month']}/{date_['year']}" if date_ else ""
        format_list_with_comma = lambda list_: ", ".join(list_) if list_ else ""
        to_human_date = lambda utc_date: datetime.fromtimestamp(utc_date).strftime("%d/%m/%Y %H:%M:%S")
        extract_next_airing_episode = lambda airing_episode: f"Episode: {airing_episode['episode']} on {to_human_date(airing_episode['airingAt'])}"  if airing_episode else "Completed"

        # variables
        english_title = data["title"]["english"]
        jp_title = data["title"]["romaji"]
        studios = data["studios"]["nodes"]

        # update header
        self.header.titles = f"{english_title}\n{jp_title}"
        if banner_image:=data["bannerImage"]:
            self.header.banner_image = banner_image


        # -----side bar-----

        # update image
        self.side_bar.image = data["coverImage"]["extraLarge"]

        # update alternative titles
        alternative_titles = {
            "synonyms":format_list_with_comma(data["synonyms"]), # list 
            "japanese":jp_title,
            "english":english_title,
        }
        self.side_bar.alternative_titles = alternative_titles
        
        # update information
        information = {
            "episodes":data["episodes"],
            "status":data["status"],
            "nextAiringEpisode":extract_next_airing_episode(data["nextAiringEpisode"]),
            "aired":f"{format_date(data['startDate'])} to {format_date(data['endDate'])}",
            "premiered":f"{data['season']} {data['seasonYear']}",
            "broadcast":data["format"],
            "countryOfOrigin":data["countryOfOrigin"],
            "hashtag":data["hashtag"],
            "studios": format_list_with_comma([studio["name"] for studio in studios if studio["isAnimationStudio"]]), # { "name": "Sunrise", "isAnimationStudio": true }
            "producers": format_list_with_comma([studio["name"] for studio in studios if not studio["isAnimationStudio"]]), # { "name": "Sunrise", "isAnimationStudio": true }
            "source":data["source"],
            "genres": format_list_with_comma(data["genres"]),
            "duration":data["duration"],
            # "rating":data["rating"],
        }
        self.side_bar.information = information


        # update statistics
        statistics = [
            # { "rank": 44, "context": "highest rated all time" }
            *[(stat["context"],stat["rank"]) for stat in data["rankings"]]
        ]
        self.side_bar.statistics = statistics

        # update tags
        self.side_bar.tags = [
            (tag["name"],tag["rank"])
            for tag in data["tags"]
            ]
        
        # update external links

        external_links = [
            ("AniList",data["siteUrl"]),
            *[(site["site"],site["url"]) for site in data["externalLinks"]]
        ]
        self.side_bar.external_links = external_links


        self.rankings_bar.rankings = {
            "Popularity":data["popularity"],
            "Favourites":data["favourites"],
            "AverageScore":data["averageScore"] if data["averageScore"] else 0,
        }

        self.anime_description.description = data["description"]

        self.anime_characters.characters = [(character["node"],character["voiceActors"])for character in data["characters"]["edges"]] #  list (character,actor)

        self.anime_reviews.reviews = data["reviews"]["nodes"]

        # for r in data["recommendation"]["nodes"]:
        #     r["mediaRecommendation"]

    def stream_anime_with_custom_cmds_dialog(self):
        """
        Called when user wants to stream with custom commands
        """
        AnimdlStreamDialog(self.data).open()