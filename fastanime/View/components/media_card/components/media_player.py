from kivy.uix.videoplayer import VideoPlayer


# TODO: make fullscreen exp better
class MediaPopupVideoPlayer(VideoPlayer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_fullscreen(self, instance, value):
        super().on_fullscreen(instance, value)
        # self.state = "pause"
