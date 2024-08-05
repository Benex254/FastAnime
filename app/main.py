# from kivy.config import Config
# Config.set('kivy', 'window_icon', "logo.ico")
# Config.write()
import os
from kivy.loader import Loader
Loader.num_workers = 5
Loader.max_upload_per_frame = 5
from libs.animdl.animdl_api import AnimdlApi
os.environ["KIVY_VIDEO"] = "ffpyplayer"
from kivymd.icon_definitions import md_icons
import json
from queue import Queue
from threading import Thread
import plyer
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager,FadeTransition
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore
from datetime import date
from subprocess import Popen

user_data = JsonStore("user_data.json")
today = date.today()
if not(user_data.exists("my_list")):
    user_data.put("my_list",list=[])

yt_cache = JsonStore("yt_cache.json")
if not(yt_cache.exists("yt_stream_links")):
    yt_cache.put("yt_stream_links",**{f"{today}":[]})
elif not( yt_cache.get("yt_stream_links").get(f"{today}")):
    yt_cache.put("yt_stream_links",**{f"{today}":[]})
    

from View.screens import screens
# plyer.
class AniXStreamApp(MDApp):
    queue = Queue()
    animdl_streaming_subprocess:Popen|None = None
    def worker(self,queue:Queue):
        while True:
            task = queue.get() # task should be a function
            task()
            self.queue.task_done()


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_all_kv_files(self.directory)
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Lightcoral"
        self.manager_screens = ScreenManager()
        self.manager_screens.transition = FadeTransition()

        # initialize worker
        self.worker_thread = Thread(target=self.worker,args=(self.queue,))
        self.worker_thread.daemon = True
        self.worker_thread.start()

    def build(self) -> ScreenManager:
        self.generate_application_screens()
        self.anime_screen = self.manager_screens.get_screen("anime screen")
        self.search_screen = self.manager_screens.get_screen("search screen")
        return self.manager_screens
    
    def on_start(self,*args):
        super().on_start(*args)

    def generate_application_screens(self) -> None:
        for i, name_screen in enumerate(screens.keys()):
            model = screens[name_screen]["model"]()
            controller = screens[name_screen]["controller"](model)
            view = controller.get_view()
            view.manager_screens = self.manager_screens
            view.name = name_screen
            self.manager_screens.add_widget(view)
    # others
    def search_for_anime(self,search_field,**kwargs):
        if self.manager_screens.current != "search screen":
            self.manager_screens.current = "search screen"
        self.search_screen.handle_search_for_anime(search_field,**kwargs)

    def show_anime_screen(self,id):
        self.manager_screens.current = "anime screen"
        self.anime_screen.controller.update_anime_view(id)        

    def stream_anime_with_animdl(self,title):
        self.animdl_streaming_subprocess = AnimdlApi.stream_anime_by_title(title)
        self.stop_streaming = False
        
    def watch_on_animdl(self,title_dict:dict):
        if self.animdl_streaming_subprocess:
            self.animdl_streaming_subprocess.terminate()
        if title:=title_dict.get("japanese"):
            stream_func = lambda: self.stream_anime_with_animdl(title)
            self.queue.put(stream_func)
        elif title:=title_dict.get("english"):
            stream_func = lambda:self.stream_anime_with_animdl(title)
            self.queue.put(stream_func)

if __name__ == "__main__":
    AniXStreamApp().run()
