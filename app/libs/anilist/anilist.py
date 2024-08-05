from .queries_graphql import (
    most_favourite_query,
    most_recently_updated_query,
    most_popular_query,
    trending_query,
    most_scored_query,
    recommended_query,
    search_query,
    anime_characters_query,
    anime_relations_query,
    airing_schedule_query,
    upcoming_anime_query
    )
import requests
# from kivy.network.urlrequest import UrlRequestRequests

class AniList:
    @classmethod
    def get_data(cls,query:str,variables:dict = {})->tuple[bool,dict]:
        url = "https://graphql.anilist.co"
        # req=UrlRequestRequests(url, cls.got_data,)
        try:
            response = requests.post(url,json={"query":query,"variables":variables},timeout=5)
            return (True,response.json())
        except requests.exceptions.Timeout:
            return (False,{"Error":"Timeout Exceeded for connection there might be a problem with your internet or anilist is down."})
        except requests.exceptions.ConnectionError:
            return (False,{"Error":"There might be a problem with your internet or anilist is down."})
        except Exception as e:
            return (False,{"Error":f"{e}"})

    @classmethod
    def got_data(cls):
        pass
    @classmethod
    def search(cls,
               query:str|None=None,
               sort:list[str]|None=None,
               genre_in:list[str]|None=None,
               genre_not_in:list[str]|None=None,
               popularity_greater:int|None=None,
               popularity_lesser:int|None=None,
               averageScore_greater:int|None=None,
               averageScore_lesser:int|None=None,
               tag_in:list[str]|None=None,
               tag_not_in:list[str]|None=None,
               status_in:list[str]|None=None,
               status_not_in:list[str]|None=None,
               endDate_greater:int|None=None,
               endDate_lesser:int|None=None,
               start_greater:int|None=None,
               start_lesser:int|None=None,
               page:int|None=None
               )->tuple[bool,dict]:
        
        variables = {} 
        for key, val in list(locals().items())[1:]:
            if val is not None and key not in ["variables"]:
                variables[key] = val
        search_results = cls.get_data(search_query,variables=variables)
        return search_results

    @classmethod
    def get_trending(cls)->tuple[bool,dict]:
        trending = cls.get_data(trending_query)
        return trending

    @classmethod
    def get_most_favourite(cls)->tuple[bool,dict]:
        most_favourite = cls.get_data(most_favourite_query)
        return most_favourite

    @classmethod
    def get_most_scored(cls)->tuple[bool,dict]:
        most_scored = cls.get_data(most_scored_query)
        return most_scored

    @classmethod
    def get_most_recently_updated(cls)->tuple[bool,dict]:
        most_recently_updated = cls.get_data(most_recently_updated_query)
        return most_recently_updated

    @classmethod
    def get_most_popular(cls)->tuple[bool,dict]:
        most_popular = cls.get_data(most_popular_query)
        return most_popular
    
    # FIXME:dont know why its not giving useful data
    @classmethod
    def get_recommended_anime_for(cls,id:int)->tuple[bool,dict]:
        recommended_anime = cls.get_data(recommended_query)
        return recommended_anime
    
    @classmethod
    def get_charcters_of(cls,id:int)->tuple[bool,dict]:
        variables = {"id":id}
        characters = cls.get_data(anime_characters_query,variables)
        return characters
    
    
    @classmethod
    def get_related_anime_for(cls,id:int)->tuple[bool,dict]:
        variables = {"id":id}
        related_anime = cls.get_data(anime_relations_query,variables)
        return related_anime        
    
    @classmethod
    def get_airing_schedule_for(cls,id:int)->tuple[bool,dict]:
        variables = {"id":id}
        airing_schedule = cls.get_data(airing_schedule_query,variables)
        return airing_schedule
    
    @classmethod
    def get_upcoming_anime(cls,page:int)->tuple[bool,dict]:
        variables = {"page":page}
        upcoming_anime = cls.get_data(upcoming_anime_query,variables)
        return upcoming_anime


if __name__ == "__main__":
    import json
    # data = AniList.get_most_popular()
    # data = AniList.get_most_favourite()
    # data = AniList.get_most_recently_updated()
    # data = AniList.get_trending()
    # data = AniList.get_most_scored()
    # term = input("enter term: ")
    data = AniList.search(query="Ninja")
    # data = AniList.get_recommended_anime_for(21)
    # data = AniList.get_related_anime_for(21)
    # data = AniList.get_airing_schedule_for(21)
    # data = AniList.get_upcoming_anime(1)
    print(json.dumps(data,indent=4))
    pass