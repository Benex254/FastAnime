from kivy.properties import ListProperty, ObjectProperty, StringProperty

from kivy.uix.widget import Factory
from kivymd.uix.button import MDButton

from ...libs.anilist import AnilistBaseMediaDataSchema
from ...View.base_screen import BaseScreenView


class EpisodeButton(MDButton):
    text = StringProperty()
    change_episode_callback = ObjectProperty()


Factory.register("EpisodeButton", cls=EpisodeButton)


class AnimeScreenView(BaseScreenView):
    """The anime screen view"""

    current_link = StringProperty()
    current_links = ListProperty([])
    current_anime_data = ObjectProperty()
    caller_screen_name = ObjectProperty()
    current_title = ()
    episodes_container = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.update_episodes(100)

    def update_episodes(self, episodes_list):
        self.episodes_container.data = []
        for episode in episodes_list:
            self.episodes_container.data.append(
                {
                    "viewclass": "EpisodeButton",
                    "text": str(episode),
                    "change_episode_callback": lambda x=episode: self.update_current_episode(
                        x
                    ),
                }
            )

    def on_current_anime_data(self, instance, value):
        data = value["show"]
        self.update_episodes(data["availableEpisodesDetail"]["sub"][::-1])

    def update_current_episode(self, episode):
        self.controller.fetch_streams(self.current_title, episode)
        # self.current_link = self.current_links[0]["gogoanime"][0]

    def update_current_video_stream(self, server, is_dub=False):
        for link in self.current_links:
            if stream_link := link.get(server):
                self.current_link = stream_link[0]
                break

    def add_to_user_anime_list(self, *args):
        self.app.add_anime_to_user_anime_list(self.model.anime_id)
