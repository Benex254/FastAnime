import os
os.environ["KIVY_VIDEO"] = "ffpyplayer"
from kivymd.icon_definitions import md_icons
import json

import plyer
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager,FadeTransition
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore

user_data = JsonStore("user_data.json")

if not(user_data.exists("my_list")):
    user_data.put("my_list",list=[])

if not(user_data.exists("yt_stream_links")):
    user_data.put("yt_stream_links",links=[])

from View.screens import screens
# plyer.
class AninformaApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_all_kv_files(self.directory)
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        self.manager_screens = ScreenManager()
        self.manager_screens.transition = FadeTransition()

    def build(self) -> ScreenManager:
        self.generate_application_screens()
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
                  
if __name__ == "__main__":
    AninformaApp().run()
