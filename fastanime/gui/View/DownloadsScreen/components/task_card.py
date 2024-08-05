from kivy.properties import StringProperty, ListProperty
from kivymd.uix.boxlayout import MDBoxLayout


class TaskCard(MDBoxLayout):
    file = ListProperty(("", ""))
    eta = StringProperty()

    def __init__(self, file: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file = file
        # self.eta = eta
        #
