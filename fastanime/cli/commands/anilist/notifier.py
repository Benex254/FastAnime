import json
import logging
import os
import time

import click
from plyer import notification

from ....anilist import AniList
from ....constants import APP_DATA_DIR, APP_NAME
from ..config import Config

logger = logging.getLogger(__name__)


# plyer.notification(title="anime",message="Update",app_name=APP_NAME)
@click.command(help="Check for notifications on anime you currently watching")
@click.pass_obj
def notifier(config: Config):
    notified = os.path.join(APP_DATA_DIR, "last_notification.json")
    if not config.user:
        print("Not Authenticated")
        print("Run the following to get started: fastanime anilist loggin")
        return
    run = True
    timeout = 2
    if os.path.exists(notified):
        with open(notified, "r") as f:

            past_notifications = json.load(f)
    else:
        past_notifications = {}
        with open(notified, "w") as f:
            json.dump(past_notifications, f)

    while run:
        try:
            logger.info("checking for notifications")
            result = AniList.get_notification()
            if not result[0]:
                logger.warning("Something went wrong", result[1])
                continue
            data = result[1]
            notifications = data["data"]["Page"]["notifications"]  # pyright:ignore
            if not notifications:
                logger.info("Nothing to notify")
            for notification_ in notifications:
                title = "New episode just aired"
                anime_episode = notification_["episode"]
                anime_title = notification_["media"]["title"][config.preferred_language]
                message = f"{anime_title} episode {anime_episode} has just aired, be sure to watch it so you are not left out of the loop"  # pyright:ignore

                id = notification_["media"]["id"]
                if past_notifications.get(str(id)) == notification_["episode"]:
                    logger.info(
                        f"skipping id={id} title={anime_title} episode={anime_episode} already notified"
                    )

                else:
                    past_notifications[f"{id}"] = notification_["episode"]
                    with open(notified, "w") as f:
                        json.dump(past_notifications, f)
                    logger.info(message)
                    notification.notify(  # pyright:ignore
                        title=title, message=message, app_name=APP_NAME
                    )
        except Exception as e:
            logger.error(e)
        logger.info("sleeping...")
        time.sleep(timeout * 60)
