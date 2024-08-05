from kivy.properties import StringProperty

from ...Utility.kivy_markup_helper import bolden, color_text
from ...Utility.utils import read_crash_file
from ...View.base_screen import BaseScreenView


class CrashLogScreenView(BaseScreenView):
    """The crash log screen"""

    crash_text = StringProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        if crashes := read_crash_file():
            self.crash_text = crashes
        else:
            self.crash_text = color_text(
                f"No Crashes so far :) and if there are any in the future {bolden('please report! Okay?')}",
                self.theme_cls.primaryColor,
            )
