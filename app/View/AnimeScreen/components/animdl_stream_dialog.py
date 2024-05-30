from kivy.clock import Clock
from kivy.uix.modalview import ModalView

from kivymd.uix.behaviors import (
    StencilBehavior,
    CommonElevationBehavior,
    BackgroundColorBehavior,
)
from kivymd.theming import ThemableBehavior


class AnimdlStreamDialog(
    ThemableBehavior,
    StencilBehavior,
    CommonElevationBehavior,
    BackgroundColorBehavior,
    ModalView,
):
    """The anime streaming dialog"""

    def __init__(self, data, mpv, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.mpv = mpv
        if title := data["title"].get("romaji"):
            self.ids.title_field.text = title
        elif title := data["title"].get("english"):
            self.ids.title_field.text = title

        self.ids.quality_field.text = "best"

    def _stream_anime(self, app):
        if self.mpv:
            streaming_cmds = {}
            title = self.ids.title_field.text
            streaming_cmds["title"] = title

            episodes_range = self.ids.range_field.text
            if episodes_range:
                streaming_cmds["episodes_range"] = episodes_range

            quality = self.ids.quality_field.text
            if quality:
                streaming_cmds["quality"] = quality
            else:
                streaming_cmds["quality"] = "best"

            app.watch_on_animdl(streaming_cmds)
        else:
            cmds = []
            title = self.ids.title_field.text
            cmds.append(title)

            episodes_range = self.ids.range_field.text
            if episodes_range:
                cmds = [*cmds, "-r", episodes_range]

            latest = self.ids.latest_field.text
            if latest:
                cmds = [*cmds, "-s", latest]

            quality = self.ids.quality_field.text
            if quality:
                cmds = [*cmds, "-q", quality]

            app.watch_on_animdl(custom_options=cmds)

    def stream_anime(self, app):
        Clock.schedule_once(lambda _: self._stream_anime(app))
