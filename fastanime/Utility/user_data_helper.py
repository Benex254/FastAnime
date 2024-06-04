"""
Contains Helper functions to read and write the user data files
"""

import os
from datetime import date, datetime

from kivy.logger import Logger

from kivy.storage.jsonstore import JsonStore

app_dir = os.path.dirname(__file__)
data_folder = os.path.join(app_dir, "data")
today = date.today()
now = datetime.now()

if os.path.exists(os.path.join(data_folder, "user_data.json")):
    user_data = JsonStore(os.path.join(data_folder, "user_data.json"))
else:
    # os.makedir(data_folder, exist_ok=True)
    print("op2")
    user_data_path = os.path.join(data_folder, "user_data.json")
    user_data = JsonStore(user_data_path)

    print("op2")


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
