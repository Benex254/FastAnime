from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from ...config import Config


@click.command(help="Check for notifications on anime you currently watching")
@click.pass_obj
def notifier(config: "Config"):
    import json
    import logging
    import os
    import time
    from sys import exit

    import requests

    try:
        from plyer import notification
    except ImportError:
        print("Please install plyer to use this command")
        exit(1)

    from ....anilist import AniList
    from ....constants import APP_CACHE_DIR, APP_DATA_DIR, APP_NAME, ICON_PATH, PLATFORM

    logger = logging.getLogger(__name__)

    notified = os.path.join(APP_DATA_DIR, "last_notification.json")
    anime_image_path = os.path.join(APP_CACHE_DIR, "notification_image")
    notification_duration = config.notification_duration * 60
    notification_image_path = ""

    if not config.user:
        print("Not Authenticated")
        print("Run the following to get started: fastanime anilist loggin")
        exit(1)
    run = True
    # WARNING: Mess around with this value at your own risk
    timeout = 2  # time is in minutes
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
                logger.warning(
                    "Something went wrong this could mean anilist is down or you have lost internet connection"
                )
                logger.info("sleeping...")
                time.sleep(timeout * 60)
                continue
            data = result[1]
            if not data:
                logger.warning(
                    "Something went wrong this could mean anilist is down or you have lost internet connection"
                )
                logger.info("sleeping...")
                time.sleep(timeout * 60)
                continue

            notifications = data["data"]["Page"]["notifications"]
            if not notifications:
                logger.info("Nothing to notify")
            else:
                for notification_ in notifications:
                    anime_episode = notification_["episode"]
                    anime_title = notification_["media"]["title"][
                        config.preferred_language
                    ]
                    title = f"{anime_title} Episode {anime_episode} just aired"
                    # pyright:ignore
                    message = "Be sure to watch so you are not left out of the loop."
                    # message = str(textwrap.wrap(message, width=50))

                    id = notification_["media"]["id"]
                    if past_notifications.get(str(id)) == notification_["episode"]:
                        logger.info(
                            f"skipping id={id} title={anime_title} episode={anime_episode} already notified"
                        )

                    else:
                        # windows only supports ico,
                        # and you still ask why linux
                        if PLATFORM != "Windows":
                            image_link = notification_["media"]["coverImage"]["medium"]
                            logger.info("Downloading image...")

                            resp = requests.get(image_link)
                            if resp.status_code == 200:
                                with open(anime_image_path, "wb") as f:
                                    f.write(resp.content)
                                notification_image_path = anime_image_path
                            else:
                                logger.warn(
                                    f"Failed to get image response_status={resp.status_code} response_content={resp.content}"
                                )
                                notification_image_path = ICON_PATH
                        else:
                            notification_image_path = ICON_PATH

                        past_notifications[f"{id}"] = notification_["episode"]
                        with open(notified, "w") as f:
                            json.dump(past_notifications, f)
                        logger.info(message)
                        notification.notify(  # pyright:ignore
                            title=title,
                            message=message,
                            app_name=APP_NAME,
                            app_icon=notification_image_path,
                            hints={
                                "image-path": notification_image_path,
                                "desktop-entry": f"{APP_NAME}.desktop",
                            },
                            timeout=notification_duration,
                        )
                        time.sleep(30)
        except Exception as e:
            logger.error(e)
        logger.info("sleeping...")
        time.sleep(timeout * 60)
