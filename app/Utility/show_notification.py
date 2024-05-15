from kivymd.uix.snackbar import MDSnackbar,MDSnackbarText,MDSnackbarSupportingText
from kivy.clock import Clock

def show_notification(title,details):
    def _show(dt):
        MDSnackbar(
            MDSnackbarText(
                text=title,
            ),
            MDSnackbarSupportingText(
                text=details,
                shorten=False,
                max_lines=0,
                adaptive_height=True
            ),
            duration=5,
            y="10dp",
            pos_hint={"bottom": 1,"right":.99},
            padding=[0, 0, "8dp", "8dp"],
            size_hint_x=.4
        ).open()
    Clock.schedule_once(_show,1)