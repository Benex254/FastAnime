import os
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.tooltip import MDTooltip 
from kivymd.uix.behaviors import BackgroundColorBehavior,StencilBehavior,CommonElevationBehavior,HoverBehavior
from kivymd.uix.button import MDIconButton
from kivymd.theming import ThemableBehavior
from kivy.uix.modalview import ModalView
from kivy.properties import ObjectProperty,StringProperty,BooleanProperty,ListProperty,NumericProperty
from kivy.uix.video import Video
from kivy.animation import Animation
class Tooltip(MDTooltip):
    pass


class TooltipMDIconButton(Tooltip,MDIconButton):
    tooltip_text = StringProperty()


class MediaPopupVideoPlayer(Video):
    # self.prev
    pass


class MediaPopup(ThemableBehavior,HoverBehavior,StencilBehavior,CommonElevationBehavior,BackgroundColorBehavior,ModalView):
    caller = ObjectProperty()
    player = ObjectProperty()

    def __init__(self, caller,*args,**kwarg):
        self.caller:MediaCard = caller
        super(MediaPopup,self).__init__(*args,**kwarg)

    
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
        self.dispatch('on_pre_open')
        Window.add_widget(self)
        Window.bind(
            on_resize=self._align_center,
            on_keyboard=self._handle_keyboard)
        self.center = self.caller.to_window(*self.caller.center)
        self.fbind('center', self._align_center)
        self.fbind('size', self._align_center)
        if kwargs.get('animation', True):
            ani = Animation(_anim_alpha=1., d=self._anim_duration)
            ani.bind(on_complete=lambda *_args: self.dispatch('on_open'))
            ani.start(self)
        else:
            self._anim_alpha = 1.
            self.dispatch('on_open')

    def _align_center(self, *_args):
        if self._is_open:
            self.center = self.caller.to_window(*self.caller.center)


    def on_leave(self,*args):
        def _leave(dt):
            if not self.hovering:
                self.dismiss()
        Clock.schedule_once(_leave,2)


class MediaCard(ButtonBehavior,HoverBehavior,MDBoxLayout):
    anime_id = NumericProperty()
    title = StringProperty()
    is_play = ObjectProperty()
    trailer_url = StringProperty()
    episodes = StringProperty()
    favourites = StringProperty()
    popularity = StringProperty()
    media_status = StringProperty("Releasing")
    is_in_my_list = BooleanProperty(False)
    is_in_my_notify = BooleanProperty(False)
    genres = StringProperty()
    first_aired_on = StringProperty()
    description = StringProperty()
    author = StringProperty()
    studios = StringProperty()
    characters = StringProperty()
    tags = StringProperty()
    stars = ListProperty([0,0,0,0,0,0])
    cover_image_url = StringProperty()
    preview_image = StringProperty()
    screen = ObjectProperty()
    has_trailer_color = ListProperty([1,1,1,0])
    def __init__(self,trailer_url=None,**kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        if trailer_url:
            self.trailer_url = trailer_url
        self.adaptive_size = True

        # self.app = MDApp.get_running_app()
    # def on_screen_name(self,instance,value):
    #     if self.app:
    #         self.screen = self.app.manager_screens.get_screen(value)
    # def 
    def on_enter(self):
        def _open_popup(dt):
            if self.hovering:
                window = self.get_parent_window()
                if window:
                    for widget in window.children: # type: ignore
                        if isinstance(widget,MediaPopup):
                            return
                    self.open()
        Clock.schedule_once(_open_popup,5)
        
    def on_popup_open(self,popup:MediaPopup):
        popup.center = self.center

    def on_dismiss(self,popup:MediaPopup):
        popup.player.unload()

    def set_preview_image(self,image):
        self.preview_image = image
    def set_trailer_url(self,trailer_url):
        self.trailer_url = trailer_url
        self.has_trailer_color = self.theme_cls.primaryColor

    def open(self,*_):
        popup = MediaPopup(self)
        popup.title = self.title
        popup.bind(on_dismiss=self.on_dismiss,on_open=self.on_popup_open)
        popup.open(self)

    # ---------------respond to user actions and call appropriate model-------------------------
    def on_is_in_my_list(self,instance,value):
        
        if self.screen:
            self.screen.controller.update_my_list(self.anime_id,value)

    def on_trailer_url(self,*args):
        pass


class MediaCardsContainer(MDBoxLayout):
    container = ObjectProperty()
    list_name = StringProperty()
