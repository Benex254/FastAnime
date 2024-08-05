from kivy.properties import ListProperty, ObjectProperty, StringProperty

from ...libs.anilist import AnilistBaseMediaDataSchema
from ...View.base_screen import BaseScreenView


class AnimeScreenView(BaseScreenView):
    """The anime screen view"""

    current_link = StringProperty(
        "https://uc951f724c20bbec8df447bac605.dl.dropboxusercontent.com/cd/0/get/CUdx6k2qw-zqY86ftfFHqkmPqGuVrfjpE68B_EkcvZXcZLnjim_ZTHd-qNVb_mEbos9UsuhY8FJGdgf86RUZ-IJqZtz3tt8_CUVTloQAeZ47HtNiKjQ0ESvYdLuwqDjqwK2rNfsfiZI2cXBaKiUyJtljEeRL8whSff2wA9Z4tX1cow/file"
    )
    current_links = ListProperty([])
    current_anime_data = ObjectProperty()
    caller_screen_name = ObjectProperty()
    current_title = StringProperty()

    def update_layout(self, data: AnilistBaseMediaDataSchema, caller_screen_name: str):
        return

    def update_current_video_stream(self, server, is_dub=False):
        for link in self.current_links:
            if stream_link := link.get(server):
                print(link)
                self.current_link = stream_link[0]
                break
            # print(link)

    def update_current_link(self, field):
        self.controller.fetch_streams(self.current_title, field.text)

    def add_to_user_anime_list(self, *args):
        self.app.add_anime_to_user_anime_list(self.model.anime_id)
