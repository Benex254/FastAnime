from kivy.properties import ObjectProperty,StringProperty,DictProperty,ListProperty
from kivy.utils import get_hex_from_color
from kivy.factory import Factory

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel


class HeaderLabel(MDBoxLayout):
    text = StringProperty()
    halign = StringProperty("center")

Factory.register("HeaderLabel", HeaderLabel)
class SideBarLabel(MDLabel):
    pass


class AnimeSideBar(MDBoxLayout):
    screen = ObjectProperty()
    image = StringProperty()
    alternative_titles = DictProperty({
        "synonyms":"",
        "english":"",
        "japanese":"",
    })
    information = DictProperty({
        "episodes":"",
        "status":"",
        "aired":"",
        "nextAiringEpisode":"",
        "premiered":"",
        "broadcast":"",
        "countryOfOrigin":"",
        "hashtag":"",
        "studios":"", # { "name": "Sunrise", "isAnimationStudio": true }
        "source":"",
        "genres":"",
        "duration":"",
        "producers":"",
    })
    statistics = ListProperty()
    statistics_container = ObjectProperty()
    external_links = ListProperty()
    external_links_container = ObjectProperty()
    tags = ListProperty()
    tags_container = ObjectProperty()

    def on_statistics(self,instance,value):
        self.statistics_container.clear_widgets()
        header = HeaderLabel()
        header.text = "Rankings"
        self.statistics_container.add_widget(header)
        for stat in value:
            # stat (rank,context)
            label = SideBarLabel()
            label.text = "[color={}]{}:[/color] {}".format(
                get_hex_from_color(label.theme_cls.primaryColor),
                stat[0].capitalize(),
                f"{stat[1]}")
            self.statistics_container.add_widget(label)

    def on_tags(self,instance,value):
        self.tags_container.clear_widgets()
        header = HeaderLabel()
        header.text = "Tags"
        self.tags_container.add_widget(header)
        for tag in value:
            label = SideBarLabel()
            label.text = "[color={}]{}:[/color] {}".format(
                get_hex_from_color(label.theme_cls.primaryColor),
                tag[0].capitalize(),
                f"{tag[1]} %")
            self.tags_container.add_widget(label)


    def on_external_links(self,instance,value):
        self.external_links_container.clear_widgets()
        header = HeaderLabel()
        header.text = "External Links"
        self.external_links_container.add_widget(header)
        for site in value:
            # stat (rank,context)
            label = SideBarLabel()
            label.text = "[color={}]{}:[/color] {}".format(
                get_hex_from_color(label.theme_cls.primaryColor),
                site[0].capitalize(),
                site[1])
            self.external_links_container.add_widget(label)
