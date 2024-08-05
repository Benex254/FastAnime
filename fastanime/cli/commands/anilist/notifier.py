import json
import logging
import os
import time

import click
import requests
from plyer import notification

from ....anilist import AniList
from ....constants import APP_CACHE_DIR, APP_DATA_DIR, APP_NAME, PLATFORM
from ..config import Config

logger = logging.getLogger(__name__)


# plyer.notification(title="anime",message="Update",app_name=APP_NAME)
@click.command(help="Check for notifications on anime you currently watching")
@click.pass_obj
def notifier(config: Config):
    notified = os.path.join(APP_DATA_DIR, "last_notification.json")
    anime_image = os.path.join(APP_CACHE_DIR, "notification_image")
    notification_duration = config.notification_duration * 60

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
                print(result)
                logger.warning(
                    "Something went wrong this could mean anilist is down or you have lost internet connection"
                )
                logger.info("sleeping...")
                time.sleep(timeout * 60)
                continue
            data = result[1]
            # pyright:ignore
            notifications = data["data"]["Page"]["notifications"]
            if not notifications:
                logger.info("Nothing to notify")
            else:
                for notification_ in notifications:
                    anime_episode = notification_["episode"]
                    title = f"Episode {anime_episode} just aired"
                    anime_title = notification_["media"]["title"][
                        config.preferred_language
                    ]
                    # pyright:ignore
                    message = f"{anime_title}\nBe sure to watch so you are not left out of the loop."
                    # message = str(textwrap.wrap(message, width=50))

                    id = notification_["media"]["id"]
                    if past_notifications.get(str(id)) == notification_["episode"]:
                        logger.info(
                            f"skipping id={id} title={anime_title} episode={
                                anime_episode} already notified"
                        )

                    else:
                        if PLATFORM != "Windows":
                            image_link = notification_["media"]["coverImage"]["medium"]
                            print(image_link)
                            logger.info("Downloading image")

                            resp = requests.get(image_link)
                            if resp.status_code == 200:
                                with open(anime_image, "wb") as f:
                                    f.write(resp.content)
                                ICON_PATH = anime_image

                        past_notifications[f"{id}"] = notification_["episode"]
                        with open(notified, "w") as f:
                            json.dump(past_notifications, f)
                        logger.info(message)
                        notification.notify(  # pyright:ignore
                            title=title,
                            message=message,
                            app_name=APP_NAME,
                            app_icon=ICON_PATH,
                            hints={"image-path": ICON_PATH},
                            timeout=notification_duration,
                        )
                        time.sleep(30)
        except Exception as e:
            logger.error(e)
        logger.info("sleeping...")
        time.sleep(timeout * 60)
