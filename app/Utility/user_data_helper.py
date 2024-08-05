"""
Contains Helper functions to read and write the user data files
"""


from kivy.storage.jsonstore import JsonStore
from datetime import date,datetime


today = date.today()
now = datetime.now()

user_data = JsonStore("user_data.json")
yt_cache = JsonStore("yt_cache.json")


# Get the user data
def get_user_animelist():
    try:
        return user_data.get("my_list")["list"] # returns a list of anime ids
    except:
        return []

def update_user_anime_list(new_list:list):
    try:
        user_data.put("my_list",list=set(new_list))
    except:
        pass
    
def get_anime_trailer_cache():
    try:
        name_of_yt_cache = f"{today}{0 if now.hour>=12 else 1}"
        return yt_cache["yt_stream_links"][f"{name_of_yt_cache}"]
    except:
        return []
    
def update_anime_trailer_cache(yt_stream_links:list):
    try:
        name_of_yt_cache = f"{today}{0 if now.hour>=12 else 1}"
        yt_cache.put("yt_stream_links",**{f"{name_of_yt_cache}":yt_stream_links})
    except:
        pass
