from  pypresence import Presence
import time

def discord_connect(show, episode, switch):
    presence = Presence(client_id = '1292070065583165512')
    if not switch.is_set():
        presence.update(
                details = show,
                state = "Watching "+episode
        )
        time.sleep(10)