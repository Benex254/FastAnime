from kivy.uix.videoplayer import VideoPlayer


class MediaPopupVideoPlayer(VideoPlayer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # FIXME: find way to make fullscreen stable
        #
        self.allow_fullscreen = False

    def on_fullscreen(self, instance, value):
        super().on_fullscreen(instance, value)
        # self.state = "pause"
