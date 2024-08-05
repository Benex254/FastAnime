from kivy.uix.modalview import ModalView

from kivymd.uix.behaviors import StencilBehavior,CommonElevationBehavior,BackgroundColorBehavior
from kivymd.theming import ThemableBehavior

class AnimdlStreamDialog(ThemableBehavior,StencilBehavior,CommonElevationBehavior,BackgroundColorBehavior,ModalView):
    def __init__(self,data,**kwargs):
        super(AnimdlStreamDialog,self).__init__(**kwargs)
        self.data = data
        if title:=data["title"].get("romaji"):
            self.ids.title_field.text = title
        elif title:=data["title"].get("english"):
            self.ids.title_field.text = title

        self.ids.quality_field.text = "best"
    def stream_anime(self,app):
        cmds = []
        title = self.ids.title_field.text
        cmds.append(title)

        episodes_range = self.ids.range_field.text
        if episodes_range:
            cmds = [*cmds,"-r",episodes_range]

        latest = self.ids.latest_field.text
        if latest:
            cmds = [*cmds,"-s",latest]

        quality = self.ids.quality_field.text
        if quality:
            cmds = [*cmds,"-q",quality]

        app.watch_on_animdl(custom_options = cmds)