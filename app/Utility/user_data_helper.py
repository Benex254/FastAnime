"""
Contains Helper functions to read and write the user data files
"""

from kivy.storage.jsonstore import JsonStore
from datetime import date, datetime
from kivy.logger import Logger
from kivy.resources import resource_find

today = date.today()
now = datetime.now()

user_data = JsonStore(resource_find("user_data.json"))
yt_cache = JsonStore(resource_find("yt_cache.json"))


# Get the user data
def get_user_anime_list() -> list:
    try:
        return user_data.get("user_anime_list")[
            "user_anime_list"
        ]  # returns a list of anime ids
    except Exception as e:
        Logger.warning(f"User Data:Read failure:{e}")
        return []


def update_user_anime_list(updated_list: list):
    try:
        updated_list_ = list(set(updated_list))
        user_data.put("user_anime_list", user_anime_list=updated_list_)
    except Exception as e:
        Logger.warning(f"User Data:Update failure:{e}")


# Get the user data
def get_user_downloads() -> list:
    try:
        return user_data.get("user_downloads")[
            "user_downloads"
        ]  # returns a list of anime ids
    except Exception as e:
        Logger.warning(f"User Data:Read failure:{e}")
        return []


def update_user_downloads(updated_list: list):
    try:
        user_data.put("user_downloads", user_downloads=list(set(updated_list)))
    except Exception as e:
        Logger.warning(f"User Data:Update failure:{e}")


# Yt persistent anime trailer cache
t = 1
if now.hour <= 6:
    t = 1
elif now.hour <= 12:
    t = 2
elif now.hour <= 18:
    t = 3
else:
    t = 4

yt_anime_trailer_cache_name = f"{today}{t}"


def get_anime_trailer_cache() -> list:
    try:
        return yt_cache["yt_stream_links"][f"{yt_anime_trailer_cache_name}"]
    except Exception as e:
        Logger.warning(f"User Data:Read failure:{e}")
        return []


def update_anime_trailer_cache(yt_stream_links: list):
    try:
        yt_cache.put(
            "yt_stream_links", **{f"{yt_anime_trailer_cache_name}": yt_stream_links}
        )
    except Exception as e:
        Logger.warning(f"User Data:Update failure:{e}")
