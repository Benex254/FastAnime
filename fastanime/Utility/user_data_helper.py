import json
import logging
import os

from .. import USER_DATA_PATH

logger = logging.getLogger(__name__)


class UserData:
    user_data = {"watch_history": {}, "animelist": []}

    def __init__(self):
        try:
            if os.path.isfile(USER_DATA_PATH):
                with open(USER_DATA_PATH, "r") as f:
                    user_data = json.load(f)
                    self.user_data.update(user_data)
        except Exception as e:
            logger.error(e)

    def update_watch_history(self, watch_history: dict):
        self.user_data["watch_history"] = watch_history
        self._update_user_data()

    def update_animelist(self, anime_list: list):
        self.user_data["animelist"] = list(set(anime_list))
        self._update_user_data()

    def _update_user_data(self):
        with open(USER_DATA_PATH, "w") as f:
            json.dump(self.user_data, f)


user_data_helper = UserData()
