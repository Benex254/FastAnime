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
        self.caller = caller
        super(MediaPopup,self).__init__(*args,**kwarg)

    def on_leave(self,*args):
        def _leave(dt):
            if not self.hovering:
                self.dismiss()
        Clock.schedule_once(_leave,2)


class MediaCard(ButtonBehavior,HoverBehavior,MDBoxLayout):
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
    # screen_name = StringProperty()
    screen = ObjectProperty()
    anime_id = NumericProperty()
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

    def on_enter(self):
        def _open_popup(dt):
            if self.hovering:
                window = self.get_parent_window()
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
# if __name__ == "__main__":
#     from kivymd.app import MDApp
#     from kivy.lang import Builder
#     import json
#     import os
#     import tracemalloc
#     tracemalloc.start()
#     data = {}
#     with open(os.path.join(os.curdir,"View","components","media_card","data.json"),"r") as file:
#         data = json.loads(file.read())

#     cache = {}
#     def fetch_data(key):
#         yt = YouTube(key)
#         preview_image = yt.thumbnail_url 
#         video_stream_url = yt.streams.filter(progressive=True,file_extension="mp4")[-1].url
#         return preview_image,video_stream_url

#     def cached_fetch_data(key):
#         if key not in cache:
#             cache[key] = fetch_data(key)
#         return cache[key]


#     class MediaCardApp(MDApp):
#         def build(self):
#             self.theme_cls.primary_palette = "Magenta"
#             self.theme_cls.theme_style = "Dark"
#             ui = Builder.load_file("./media_card.kv")

#             for item in data["data"]["Page"]["media"]:
#                 media_card = MediaCard()
#                 if item["title"]["english"]:
#                     media_card.title =  item["title"]["english"]
#                 else:
#                     media_card.title =  item["title"]["romaji"]
#                 media_card.cover_image_url =  item["coverImage"]["medium"]
#                 media_card.popularity =  str(item["popularity"])
#                 media_card.favourites =  str(item["favourites"])
#                 media_card.episodes =  str(item["episodes"])
#                 media_card.description =  item["description"]
#                 media_card.first_aired_on =  str(item["startDate"])
#                 media_card.studios =  str(item["studios"]["nodes"])
#                 media_card.tags =  str(item["tags"])
#                 media_card.media_status =  item["status"]
#                 if item["trailer"]:
#                     try:
#                         url = cached_fetch_data("https://youtube.com/watch?v="+item["trailer"]["id"])[1]
#                         media_card.trailer_url =url  
#                     except:
#                         pass
                    
#                 media_card.genres = ",".join(item["genres"])
                
#                 stars = int(item["averageScore"]/100*6)
#                 if stars:
#                     for i in range(stars):
#                         media_card.stars[i] = 1
                
#                 ui.ids.cards.add_widget(media_card) # type: ignore
#             return ui

#     MediaCardApp().run()
#     snapshot = tracemalloc.take_snapshot()
#     print("-----------------------------------------------")
#     for stat in snapshot.statistics("lineno")[:10]:
#         print(stat)