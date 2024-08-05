from kivy.uix.modalview import ModalView
from kivymd.uix.behaviors import StencilBehavior,CommonElevationBehavior,BackgroundColorBehavior
from kivymd.theming import ThemableBehavior
# from main import AniXStreamApp
class DownloadAnimeDialog(ThemableBehavior,StencilBehavior,CommonElevationBehavior,BackgroundColorBehavior,ModalView):
    def __init__(self,data,**kwargs):
        super(DownloadAnimeDialog,self).__init__(**kwargs)
        self.data = data
        self.anime_id = self.data["id"]
        if title:=data["title"].get("romaji"):
            self.ids.title_field.text = title
        elif title:=data["title"].get("english"):
            self.ids.title_field.text = title
        self.ids.quality_field.text = "best"
    def download_anime(self,app):
        default_cmds = {}
        title=self.ids.title_field.text
        default_cmds["title"] = title
        if episodes_range:=self.ids.range_field.text:
            default_cmds["episodes_range"] = episodes_range

        if quality:=self.ids.range_field.text:
            default_cmds["quality"] = quality

        # print(title,episodes_range,latest,quality)
        app.download_anime(self.anime_id,default_cmds)