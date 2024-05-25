from datetime import datetime

from kivy.properties import ObjectProperty,DictProperty,StringProperty

from Utility import anilist_data_helper
from View.base_screen import BaseScreenView
from .components import (AnimeHeader,AnimeSideBar,AnimeDescription,AnimeReviews,AnimeCharacters,AnimdlStreamDialog,DownloadAnimeDialog,RankingsBar)


class AnimeScreenView(BaseScreenView):
    caller_screen_name = StringProperty()
    header:AnimeHeader = ObjectProperty()
    side_bar:AnimeSideBar = ObjectProperty()
    rankings_bar:RankingsBar = ObjectProperty()
    anime_description:AnimeDescription = ObjectProperty()
    anime_characters:AnimeCharacters = ObjectProperty()
    anime_reviews:AnimeReviews = ObjectProperty()
    data = DictProperty()
    anime_id = 0
    def update_layout(self,data:dict,caller_screen_name:str):
        self.caller_screen_name = caller_screen_name
        self.data = data
        # uitlity functions
        
        extract_next_airing_episode = lambda airing_episode: f"Episode: {airing_episode['episode']} on {anilist_data_helper.format_anilist_timestamp(airing_episode['airingAt'])}"  if airing_episode else "Completed"

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
            "synonyms":anilist_data_helper.format_list_data_with_comma(data["synonyms"]), # list 
            "japanese":jp_title,
            "english":english_title,
        }
        self.side_bar.alternative_titles = alternative_titles
        
        # update information
        information = {
            "episodes":data["episodes"],
            "status":data["status"],
            "nextAiringEpisode":extract_next_airing_episode(data["nextAiringEpisode"]),
            "aired":f"{anilist_data_helper.format_anilist_date_object(data['startDate'])} to {anilist_data_helper.format_anilist_date_object(data['endDate'])}",
            "premiered":f"{data['season']} {data['seasonYear']}",
            "broadcast":data["format"],
            "countryOfOrigin":data["countryOfOrigin"],
            "hashtag":data["hashtag"],
            "studios": anilist_data_helper.format_list_data_with_comma([studio["name"] for studio in studios if studio["isAnimationStudio"]]), # { "name": "Sunrise", "isAnimationStudio": true }
            "producers": anilist_data_helper.format_list_data_with_comma([studio["name"] for studio in studios if not studio["isAnimationStudio"]]), # { "name": "Sunrise", "isAnimationStudio": true }
            "source":data["source"],
            "genres": anilist_data_helper.format_list_data_with_comma(data["genres"]),
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

    def stream_anime_with_custom_cmds_dialog(self):
        """
        Called when user wants to stream with custom commands
        """

        AnimdlStreamDialog(self.data).open()

    def open_download_anime_dialog(self):
        """
        Opens the download anime dialog
        """

        DownloadAnimeDialog(self.data).open()

    def add_to_user_anime_list(self,*args):
        self.app.add_anime_to_user_anime_list(self.model.anime_id)