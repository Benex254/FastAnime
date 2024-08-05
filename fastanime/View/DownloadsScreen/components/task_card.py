from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout


# TODO: add a progress bar to show the individual progress of each task
class TaskCard(MDBoxLayout):
    anime_task_name = StringProperty()
    episodes_to_download = StringProperty()

    def __init__(self, anime_title: str, episodes: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.anime_task_name = f"{anime_title}"
        self.episodes_to_download = f"Episodes: {episodes}"
