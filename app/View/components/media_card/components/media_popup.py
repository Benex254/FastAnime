from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.modalview import ModalView

from kivymd.theming import ThemableBehavior
from kivymd.uix.behaviors import (
    BackgroundColorBehavior,
    StencilBehavior,
    CommonElevationBehavior,
    HoverBehavior,
)


class MediaPopup(
    ThemableBehavior,
    HoverBehavior,
    StencilBehavior,
    CommonElevationBehavior,
    BackgroundColorBehavior,
    ModalView,
):
    caller = ObjectProperty()
    player = ObjectProperty()

    def __init__(self, caller, *args, **kwarg):
        self.caller = caller
        super(MediaPopup, self).__init__(*args, **kwarg)
        self.player.bind(fullscreen=self.handle_clean_fullscreen_transition)

    def open(self, *_args, **kwargs):
        """Display the modal in the Window.

        When the view is opened, it will be faded in with an animation. If you
        don't want the animation, use::

            view.open(animation=False)

        """
        from kivy.core.window import Window

        if self._is_open:
            return
        self._window = Window
        self._is_open = True
        self.dispatch("on_pre_open")
        Window.add_widget(self)
        Window.bind(on_resize=self._align_center, on_keyboard=self._handle_keyboard)
        self.center = self.caller.to_window(*self.caller.center)
        self.fbind("center", self._align_center)
        self.fbind("size", self._align_center)
        if kwargs.get("animation", True):
            ani = Animation(_anim_alpha=1.0, d=self._anim_duration)
            ani.bind(on_complete=lambda *_args: self.dispatch("on_open"))
            ani.start(self)
        else:
            self._anim_alpha = 1.0
            self.dispatch("on_open")

    def _align_center(self, *_args):
        if self._is_open:
            self.center = self.caller.to_window(*self.caller.center)

    def on_leave(self, *args):
        def _leave(dt):
            self.player.state = "stop"
            if self.player._video:
                self.player._video.unload()

            if not self.hovering:
                self.dismiss()

        Clock.schedule_once(_leave, 2)

    def handle_clean_fullscreen_transition(self,instance,fullscreen):
        if not fullscreen:
            if not self._is_open:
                instance.state = "stop"
                if vid:=instance._video:
                    vid.unload()
            else:
                instance.state = "stop"
                if vid:=instance._video:
                    vid.unload()
                self.dismiss()

                
